import datetime

from flask import flash, Blueprint, session, request, url_for, render_template, redirect, current_app
from flask_login import login_user, current_user, login_required
from mongoengine.queryset.visitor import Q

from sttapp.base.enums import FlashCategory, Level, Gender
from .forms import ProposalForm
from .models import Proposal, Itinerary

import iso8601


bp = Blueprint('proposal', __name__, url_prefix='/proposal')


@bp.route('/proposals/')
@login_required
def proposals():
    return render_template("proposals/proposals.html", proposals=Proposal.objects.all())


@bp.route('/create/', methods=["GET", "POST"])
@login_required
def create():
    form = ProposalForm(request.form)
    if request.method == "POST":
        if form.validate_on_submit():
            days = int(form.days.data)
            proposal = Proposal(
                title=form.title.data,
                start_date=form.start_date_dt,
                days=days,
                end_date=form.start_date_dt + datetime.timedelta(days=days-1),
                return_plan=form.return_plan.data,
                buffer_days=int(
                    form.buffer_days.data) if form.buffer_days.data else None,
                approach_way=form.approach_way.data,
                radio=form.radio.data,
                satellite_telephone=form.satellite_telephone.data,
                gathering_point=form.gathering_point.data,
                gathering_time=form.gathering_time_dt,
                created_by=current_user.id,
                leader=form.leader_id,
                guide=form.guide_id,
                attendees=form.attendees_ids,
                supporter=form.supporter.data
            )
            proposal.itinerary_list = [
                Itinerary(day_number=i) for i in range(0, days+1)
            ]
            proposal.save()
            flash("基本資料完成，請確認以下資訊，再下一步編輯預計行程", FlashCategory.INFO)
            return redirect(url_for("proposal.update", prop_id=proposal.id))
        else:
            flash("格式錯誤", FlashCategory.ERROR)

    return render_template("proposals/proposal_detail.html", form=form, update_itinerary=False)


@bp.route('/update/<string:prop_id>', methods=["GET", "POST"])
@login_required
def update(prop_id):

    prop = Proposal.objects.get_or_404(id=prop_id)
    if prop.is_back:
        flash("已下山之隊伍提案不可編輯", FlashCategory.WARNING)
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
        'proposals/proposal_detail.html', 
        form=form, 
        attendees=", ".join(attendees_list),
        update_itinerary=True, 
        leader=prop.leader.selected_name if prop.leader else "", 
        guide=prop.guide.selected_name if prop.guide else "")


@bp.route('/update_itinerary/<string:prop_id>/', methods=["GET", "POST"])
@login_required
def update_itinerary(prop_id):

    prop = Proposal.objects.get_or_404(id=prop_id)
    if prop.is_back:
        flash("已下山之隊伍提案不可編輯", FlashCategory.WARNING)
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
        
        gender_dict = {field: 0 for field, display in Gender.get_choices()}
        level_dict = {field: 0 for field, display in Level.get_choices()}
        for a in prop.attendees:
            if getattr(a, 'gender'):
                gender_dict[getattr(a, 'gender')] += 1
            if getattr(a, 'level'):
                level_dict[getattr(a, 'level')] +=1
        
        prop.total_members = len(prop.attendees)
        prop.gender_ratio = "{}/{}".format(gender_dict["Y"], gender_dict["X"])
        prop.struct_ratio = "{}/{}/{}".format(level_dict["cadre"], level_dict["medium"], level_dict["newbie"])

    return render_template('proposals/published.html', proposals=props, now=datetime.datetime.utcnow())
