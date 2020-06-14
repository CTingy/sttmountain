import datetime

from flask import flash, Blueprint, session, request, url_for, render_template, redirect, current_app
from flask_login import login_user, current_user, login_required
from mongoengine.queryset.visitor import Q

from sttapp.base.enums import FlashCategory, Level, Gender, EventType
from .forms import ProposalForm
from .models import Proposal, Itinerary

import iso8601


bp = Blueprint('proposal', __name__, url_prefix='/proposal')


@bp.route('/proposals/')
@login_required
def proposals():
    return render_template('proposals/proposals.html', proposals=Proposal.objects.all())


@bp.route('/create/', methods=["GET", "POST"])
@login_required
def create():

    types = EventType.get_map(True)
    
    if request.method == "GET":
        return render_template("proposals/basic_form.html", prop=None, 
                                for_updating=False, errors=None, types=types)
    
    info_dict = dict(request.form)
    info_dict.pop('csrf_token', None)
    prop = Proposal(**info_dict)
    form = ProposalForm(request.form)

    if form.validate_on_submit():
        prop.created_by = current_user.id
        prop.created_at = datetime.datetime.utcnow()
        prop.start_date = form.start_date_dt
        prop.has_d0 = form.has_d0.data
        prop.end_date = form.start_date_dt + datetime.timedelta(days=prop.days-1)
        prop.buffer_days = form.buffer_days.data or None
        prop.leader = form.leader_id
        prop.guide = form.guide_id
        prop.attendees = form.attendees_ids
        prop.event_type = EventType.get_map()[form.event_type.data]

        # generate itinerary_list
        prop.itinerary_list = [
            Itinerary(day_number=i) for i in range(1, prop.days+1)
        ]
        if prop.has_d0:
            prop.itinerary_list.insert(0, Itinerary(day_number=0))
        prop.save()
        flash("基本資料完成，請接著編輯預計行程", FlashCategory.INFO)
        return redirect(url_for("proposal.update_itinerary", prop_id=prop.id))

    else:
        errors = dict()
        for field, errs in form.errors.items():
            errors[field] = errs[0]    
        flash("表單格式有誤，請重新填寫", FlashCategory.ERROR)
        return render_template("proposals/basic_form.html", prop=prop, 
                                for_updating=False, errors=errors, types=types)


@bp.route('/detail/<string:prop_id>', methods=["GET", "POST"])
@login_required
def detail(prop_id):
    prop = Proposal.objects.get_or_404(id=prop_id)
    gender_dict = prop.gender_structure
    level_dict = prop.level_structure
    prop.gender_ratio = "{} / {}".format(
        gender_dict[Gender.get_map()[Gender.MALE]], 
        gender_dict[Gender.get_map()[Gender.FEMALE]]
    )
    prop.level_ratio = "{} / {} / {}".format(
        level_dict[Level.get_map()[Level.CADRE]],
        level_dict[Level.get_map()[Level.MEDIUM]],
        level_dict[Level.get_map()[Level.NEWBIE]],
    )
    return render_template('proposals/detail.html', prop=prop)


@bp.route('/update/<string:prop_id>', methods=["GET", "POST"])
@login_required
def update(prop_id):

    prop = Proposal.objects.get_or_404(id=prop_id)
    if prop.start_date.date() <= (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).date():
        flash("已開始之隊伍提案不可編輯", FlashCategory.WARNING)
        return redirect(url_for('proposal.proposals'))
    if current_user.id != prop.created_by.id:
        flash("僅隊伍提案創建者可編輯", FlashCategory.WARNING)
        return redirect(url_for('proposal.proposals'))  

    if request.method == "GET":
        form = ProposalForm(
            title=prop.title,
            start_date=prop.start_date.strftime("%Y/%m/%d"),
            days=prop.days,
            supporter=prop.supporter,
            event_type=prop.event_type,
            return_plan=prop.return_plan,
            buffer_days=prop.buffer_days,
            radio=prop.radio,
            satellite_telephone=prop.satellite_telephone,
            gathering_point=prop.gathering_point,
            gathering_time=prop.gathering_time.strftime(
                "%Y/%m/%d %H:%M") if prop.gathering_time else ""
        )
    else:
        form = ProposalForm(request.form)

        if form.validate_on_submit():

            # update itinerary count number
            days = int(form.days.data)
            itinerary_list = prop.itinerary_list
            if days > prop.days:
                for i in range(prop.days+1, days+1):
                    itinerary_list.append(Itinerary(day_number=i))
            elif days < prop.days:
                itinerary_list = itinerary_list[:days+1]
            if form.has_d0.data and not prop.has_d0:
                itinerary_list.insert(0, Itinerary(day_number=0))
            elif not form.has_d0.data and prop.has_d0:
                itinerary_list.pop(0)

            proposal = Proposal(
                id=prop.id,
                title=form.title.data,
                start_date=form.start_date_dt,
                end_date=form.start_date_dt + datetime.timedelta(days=days),
                days=days,
                event_type=form.event_type.data,
                return_plan=form.return_plan.data,
                buffer_days=form.buffer_days.data,
                approach_way=form.approach_way.data,
                radio=form.radio.data,
                satellite_telephone=form.satellite_telephone.data,
                gathering_point=form.gathering_point.data,
                gathering_time=form.gathering_time_dt,
                created_by=current_user.id,
                itinerary_list=itinerary_list,
                leader=form.leader_id,
                guide=form.guide_id,
                attendees=form.attendees_ids,
                supporter=form.supporter.data,
                updated_at=datetime.datetime.utcnow(),
                updated_by=current_user.id
            )
            proposal.save()
            return redirect(url_for('proposal.update_itinerary', prop_id=prop_id))
        else:
            flash("欄位錯誤", FlashCategory.ERROR)
            return redirect(url_for('proposal.update', prop_id=prop_id))
    
    attendees_list = [a.selected_name for a in prop.attendees]
    return render_template(
        'proposals/basic_form.html', for_updating=True, 
        prop=prop, 
        attendees=", ".join(attendees_list),
        leader=prop.leader.selected_name if prop.leader else "", 
        guide=prop.guide.selected_name if prop.guide else "")


@bp.route('/update_itinerary/<string:prop_id>/', methods=["GET", "POST"])
@login_required
def update_itinerary(prop_id):

    prop = Proposal.objects.get_or_404(id=prop_id)
    if prop.start_date.date() <= (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).date():
        flash("已開始之隊伍提案不可編輯", FlashCategory.WARNING)
        return redirect(url_for('proposal.proposals'))
    if current_user.id != prop.created_by.id:
        flash("僅隊伍提案創建者可編輯", FlashCategory.WARNING)
        return redirect(url_for('proposal.proposals'))

    if request.method == "POST":
        updated_list = []
        for itinerary in prop.itinerary_list:
            itinerary.content = request.form.get(
                "content{}".format(itinerary.day_number)
            )
            itinerary.water_info = request.form.get(
                "water_info{}".format(itinerary.day_number)
            )
            itinerary.communication_info = request.form.get(
                "communication_info{}".format(itinerary.day_number)
            )
            updated_list.append(itinerary)

        flash("行程更新成功", FlashCategory.SUCCESS)
        Proposal.objects(id=prop_id).update_one(
            updated_at=datetime.datetime.utcnow(),
            itinerary_list=updated_list,
            updated_by=current_user.id
        )
        return redirect(url_for('proposal.proposals'))

    return render_template("proposals/itinerary.html", itinerary_list=prop.itinerary_list)


@bp.route('/delete/<string:prop_id>', methods=["POST"])
@login_required
def delete(prop_id):
    prop = Proposal.objects.get_or_404(id=prop_id)

    if prop.is_back:
        flash("已下山之隊伍提案不可刪除", FlashCategory.WARNING)
        return redirect(url_for('proposal.proposals'))
    if prop.created_by.id != current_user.id:
        flash("只有張貼者能夠刪除隊伍提案", FlashCategory.WARNING)
        return redirect(url_for('proposal.proposals'))
    prop.delete()
    flash("已經為您刪除隊伍提案：{}".format(prop.title), FlashCategory.SUCCESS)
    return redirect(url_for("proposal.proposals"))


@bp.route('/publish/<string:prop_id>', methods=["POST"])
@login_required
def publish(prop_id):
    prop = Proposal.objects.get_or_404(id=prop_id)
    if prop.created_by.id != current_user.id:
        flash("只有張貼者能夠發佈出隊文", FlashCategory.WARNING)
        return redirect(url_for('proposal.proposals'))

    failed_fields, failed_itinerary = prop.validate_for_publishing()
    if failed_fields or failed_itinerary:
        if failed_fields:
            flash("無法發佈，提案欄位有缺少：{}，請填寫完成再試一次".format("、".join(failed_fields)), 
                   FlashCategory.WARNING)
        if failed_itinerary:
            flash("無法發佈，預定行程中{}的內容是空白的，請填寫完成再試一次".format("、".join(failed_itinerary)), 
                   FlashCategory.WARNING)
        return redirect(url_for('proposal.update', prop_id=prop_id))
   
    Proposal.objects(id=prop_id).update_one(
        updated_at=datetime.datetime.utcnow(),
        published_at=datetime.datetime.utcnow(),
        updated_by=current_user.id
    )
    flash("發佈成功！", FlashCategory.SUCCESS)
    return redirect(url_for("proposal.proposals"))


@bp.route('/published/')
def published():
    props = Proposal.objects.filter(
        Q(published_at__ne=None) & Q(is_back=False)
    )   
    for prop in props:
        gender_dict = prop.gender_structure
        level_dict = prop.level_structure
        prop.gender_ratio = "{}/{}".format(
            gender_dict[Gender.get_map()[Gender.MALE]], 
            gender_dict[Gender.get_map()[Gender.FEMALE]]
        )
        prop.level_ratio = "{}/{}/{}".format(
            level_dict[Level.get_map()[Level.CADRE]],
            level_dict[Level.get_map()[Level.MEDIUM]],
            level_dict[Level.get_map()[Level.NEWBIE]],
        )
    return render_template('proposals/published.html', proposals=props, now=datetime.datetime.utcnow())
