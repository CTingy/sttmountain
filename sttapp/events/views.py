import datetime

from flask import flash, Blueprint, session, request, url_for, render_template, redirect, current_app
from flask_login import login_user, current_user, login_required
from mongoengine.queryset.visitor import Q
from mongoengine.errors import NotUniqueError

from sttapp.base.enums import FlashCategory, EventStatus, Level, Gender
from sttapp.proposals.models import Itinerary, Proposal
from .models import Event


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
    if prop.created_by.id != current_user.id:
        flash("只有張貼者能夠發佈出隊文", FlashCategory.WARNING)
        return redirect(url_for('proposal.proposals'))
    
    if not check_before_create_event(prop):
        return redirect(url_for('proposal.update', prop_id=prop_id))

    try:
        dt = datetime.datetime.strptime(request.form.get("gathering_time"), "%Y/%m/%d %H:%M")
    except ValueError:
        flash("集合時間格式錯誤，需為: YYYY/MM/DD hh:mm", FlashCategory.ERROR)
        return redirect(url_for('proposal.proposals'))
    else:
        if dt > prop.start_date + datetime.timedelta(days=1):
            flash("集合時間格式錯誤，不可比出發日期晚", FlashCategory.ERROR)
            return redirect(url_for('proposal.proposals'))

    e = Event(
        proposal=prop_id,
        created_by=current_user.id,
        created_at=datetime.datetime.utcnow(),
        gathering_point=request.form.get("gathering_point"),
        gathering_time=dt
    )
    try:
        e.save()
    except NotUniqueError:
        flash("此企劃已經發佈過出隊文，請勿重複發佈", FlashCategory.ERROR)
        return redirect(url_for('event.events'))
    Proposal.objects(id=prop_id).update_one(event=e.id, updated_at=datetime.datetime.utcnow(),
                                            updated_by=current_user.id)
    flash("發佈成功！", FlashCategory.SUCCESS)
    return redirect(url_for('event.events'))


@bp.route('/mark_back/<string:prop_id>', methods=["POST", "GET"])
@login_required
def mark_back(prop_id):

    prop = Proposal.objects.get_or_404(id=prop_id)

    if request.method == "GET":
        itinerary_list = prop.itinerary_list
    else:
        form = request.form
        max_itinerary_num = int(form.get("itinerary_len"))
        itinerary_list = []

        for i in range(max_itinerary_num+1):
            itinerary = Itinerary(
                day_number=i,
                content=form.get("content{}".format(i)),
                water_info=form.get("water_info{}".format(i)),
                communication_info=form.get("communication_info{}".format(i))
            )
            itinerary_list.append(itinerary)
        
        event = Event(
            proposal=prop_id,
            itinerary_list=itinerary_list,
            feedback=form.get("feedback"),
            created_by=current_user.id
        )
        try:
            event.save()
        except NotUniqueError:
            if not prop.is_back and Event.objects.get(proposal=prop_id):
                Proposal.objects(id=prop_id).update_one(is_back=True)
            flash("該出隊文已經回報下山囉，請勿重複回報", FlashCategory.WARNING)
            return redirect(url_for('event.events'))
        
        Proposal.objects(id=prop_id).update_one(
            is_back=True,
            updated_at=datetime.datetime.utcnow(),
            updated_by=current_user.id
        )
        flash("RE：出隊文建立完成！", FlashCategory.SUCCESS)
        return redirect(url_for('event.events'))
    return render_template('events/create.html', itinerary_list=itinerary_list, 
                            max_day=prop.itinerary_list[-1].day_number)


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

    return render_template('events/detail.html', prop=prop, event=event)


@bp.route('/events/')
def events():
    events = Event.objects.all()
    return render_template('events/events.html', events=events, page_name="出隊文總覽")


@bp.route('/not_back_events/')
def not_back():
    events = Event.objects.filter(status=EventStatus.NORM)
    return render_template('events/events.html', events=events, page_name="出隊文（即將上山、進行中）")


@bp.route('/back_events/')
def is_back():
    events = Event.objects.filter(status=EventStatus.BACK)
    return render_template('events/events.html', events=events, page_name="出隊文（已下山）")
