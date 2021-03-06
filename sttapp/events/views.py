import datetime
import itertools

from flask import flash, Blueprint, request, url_for, render_template, redirect, current_app
from flask_login import current_user, login_required
from mongoengine.queryset.visitor import Q
from mongoengine.errors import NotUniqueError

from sttapp.base.enums import FlashCategory, EventStatus, Level, Gender
from sttapp.proposals.models import Itinerary, Proposal
from sttapp.members.models import Member
from .models import Event
from .tasks import connect_member_and_history


bp = Blueprint('event', __name__, url_prefix='/event')


def check_before_create_event(prop):
    failed_fields, failed_itinerary = prop.validate_for_publishing()
    if failed_fields or failed_itinerary:
        if failed_fields:
            flash("無法發佈，欄位有缺少：{}，請填寫完成再試一次".format("、".join(failed_fields)),
                  FlashCategory.WARNING)
        if failed_itinerary:
            flash("無法發佈，預定行程中{}的內容是空白的，請填寫完成再試一次".format("、".join(failed_itinerary)),
                  FlashCategory.WARNING)
        return False
    return True


@bp.route('/create/<string:prop_id>', methods=["POST"])
@login_required
def create(prop_id):

    prop = Proposal.objects.get_or_404(id=prop_id)

    if not check_before_create_event(prop):
        return redirect(url_for('proposal.update', prop_id=prop_id))

    try:
        dt = datetime.datetime.strptime(request.form.get("gathering_time"), "%Y/%m/%d %H:%M")
    except ValueError:
        flash("集合時間格式錯誤，需為: YYYY/MM/DD hh:mm", FlashCategory.ERROR)
        return redirect(url_for('proposal.detail', prop_id=prop_id))
    else:
        if dt > prop.start_date + datetime.timedelta(days=1):
            flash("集合時間{}比上山日期({})晚，請重新填寫集合時間".format(
                request.form.get("gathering_time"), 
                prop.start_date_str
            ), FlashCategory.ERROR)
            return redirect(url_for('proposal.detail', prop_id=prop_id))

    e = Event(
        proposal=prop_id,
        created_by=current_user.id,
        updated_by=current_user.id,
        created_at=datetime.datetime.utcnow(),
        gathering_point=request.form.get("gathering_point"),
        gathering_time=dt
    )
    e.updated_at = e.created_at
    try:
        e.save()
    except NotUniqueError:
        flash("此企劃已經發佈過出隊文，請勿重複發佈", FlashCategory.ERROR)
        return redirect(url_for('event.events'))
    
    Proposal.objects(id=prop_id).update_one(event_id=e.id, updated_at=datetime.datetime.utcnow(),
                                            updated_by=current_user.id)
    flash("發佈成功！", FlashCategory.SUCCESS)
    return redirect(url_for('event.detail', event_id=e.id))


@bp.route('/cancel/<string:event_id>', methods=["POST"])
@login_required
def cancel(event_id):

    event = Event.objects.get_or_404(id=event_id)

    if current_user.id != event.created_by.id:
        flash("只有出隊文創建者可以標注倒隊", FlashCategory.ERROR)
        return redirect(url_for("event.detail", event_id=event_id))
    
    Event.objects(id=event_id).update_one(
        status=EventStatus.get_map()[EventStatus.CANCEL],
        updated_at=datetime.datetime.utcnow(),
        updated_by=current_user.id
    )
    flash("已標注為倒隊", FlashCategory.SUCCESS)
    return redirect(url_for("event.detail", event_id=event_id))


@bp.route('/update_as_back/<string:event_id>', methods=["GET", "POST"])
@login_required
def update_as_back(event_id):

    event = Event.objects.get_or_404(id=event_id)
    itinerary_list = event.real_itinerary_list or event.proposal.itinerary_list

    if request.method == "GET":
        return render_template('events/update.html', itinerary_list=itinerary_list, 
                               max_day=itinerary_list[-1].day_number, event=event)

    form = request.form
    max_itinerary_num = int(form.get("itinerary_len"))
    inputted_itinerary_list = []
    
    if request.form.get("same_check") != "y":
        for i in range(max_itinerary_num+1):
            if not form.get("content{}".format(i)):
                continue
            itinerary = Itinerary(
                day_number=i,
                content=form.get("content{}".format(i)),
                water_info=form.get("water_info{}".format(i)),
                communication_info=form.get("communication_info{}".format(i))
            )
            inputted_itinerary_list.append(itinerary)

    if inputted_itinerary_list:
        event_real_days = inputted_itinerary_list[-1].day_number
    else:
        event_real_days = None

    Event.objects(id=event_id).update_one(
        status=EventStatus.get_map()[EventStatus.BACK],
        real_itinerary_list=inputted_itinerary_list,
        real_title=form.get("real_title") or None,  # None 為沿用舊名: proposal.title
        feedback=form.get("feedback"),
        updated_by=current_user.id,
        real_days=event_real_days,
        updated_at=datetime.datetime.utcnow()
    )

    if event.status == EventStatus.get_map()[EventStatus.NORM]:
        connect_member_and_history.delay(
            event_id=str(event_id), 
            link=request.host_url.rstrip("/") + url_for("event.detail", event_id=event_id) )

    flash("已修改成功！", FlashCategory.SUCCESS)
    return redirect(url_for('event.detail', event_id=event_id))


@bp.route('/detail/<string:event_id>')
def detail(event_id):
    event = Event.objects.get_or_404(id=event_id)
    prop = Proposal.objects.get_or_404(id=event.proposal.id)
    gender_dict = prop.gender_structure
    level_dict = prop.level_structure
    prop.gender_ratio = "{} / {}".format(
        gender_dict[Gender.MALE], 
        gender_dict[Gender.FEMALE]
    )
    prop.level_ratio = "{} / {} / {}".format(
        level_dict[Level.get_map()[Level.CADRE]],
        level_dict[Level.get_map()[Level.MEDIUM]],
        level_dict[Level.get_map()[Level.NEWBIE]],
    )
    # give every itinerary obj a date str
    for i in prop.itinerary_list:
        i.date_str = (prop.start_date + datetime.timedelta(
            days=i.day_number-1)).strftime("%m/%d")
    for i in event.real_itinerary_list:
        i.date_str = (prop.start_date + datetime.timedelta(
            days=i.day_number-1)).strftime("%m/%d")

    return render_template('events/detail.html', prop=prop, event=event)


@bp.route('/events/')
def events():
    event_list = Event.objects.all()
    return render_template('events/events.html', events=event_list, page_name="出隊文總覽")


@bp.route('/not_back_events/')
def not_back():
    event_list = Event.objects.filter(status=EventStatus.get_map()[EventStatus.NORM])
    return render_template('events/events.html', events=event_list, page_name="出隊文（即將上山、進行中）")


@bp.route('/back_events/')
def is_back():
    event_list = Event.objects.filter(status=EventStatus.get_map()[EventStatus.BACK])
    return render_template('events/events.html', events=event_list, page_name="出隊文（已下山）")


@bp.route('/delete/<string:event_id>', methods=["POST"])
@login_required
def delete(event_id):
    event = Event.objects.get_or_404(id=event_id)
    if event.created_by.id != current_user.id:
        flash("只有張貼者能夠刪除出隊文", FlashCategory.WARNING)
        return redirect(url_for('event.detail', event_id=event_id))
    if event.status in ("CANCEL", "BACK"):
        flash("不可刪除已回報下山/已標注撤退之出隊文", FlashCategory.WARNING)
        return redirect(url_for('event.detail', event_id=event_id))
    Proposal.objects(id=event.proposal.id).update_one(
        event_id=None, updated_at=datetime.datetime.utcnow(), updated_by=current_user.id)
    event.delete()
    flash("已經為您刪除出隊文，請繼續編輯企劃書再重新發佈：{}".format(event.proposal.title), FlashCategory.SUCCESS)
    return redirect(url_for("proposal.detail", prop_id=event.proposal.id))


@bp.route('/search/')
def search():

    kw = request.args.get("keyword").strip()
    if not kw:
        flash("請輸入搜尋關鍵字", FlashCategory.WARNING)
        return redirect("/")
    
    generators = []
    for kw in kw.split(" "):
        generators.append(e.id for e in Event.objects.filter(
            Q(feedback__contains=kw) | Q(real_title__contains=kw))
        )
        generators.append(
            filter(
                lambda x: x != None,
                (p.event_id for p in Proposal.objects(title__contains=kw))
            )
        )
    event_ids = itertools.chain(*generators)

    return render_template(
        'events/events.html', events=Event.objects.filter(id__in=set(event_ids)), page_name="出隊文搜尋結果")


@bp.route('/user_posts/')
@login_required
def user_posts():

    event_list = Event.objects.filter(created_by=current_user.id)
    return render_template('users/events.html', events=event_list)


@bp.route('/member_history/<string:member_id>/')
def member_history(member_id):

    member = Member.objects.get_or_404(id=member_id)
    event_list = Event.objects.filter(id__in=member.event_ids)
    return render_template('events/events.html', events=event_list, page_name=member.display_name+"的站內出隊紀錄")
