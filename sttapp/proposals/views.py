import datetime

from flask import flash, Blueprint, session, request, url_for, render_template, redirect, current_app
from flask_login import login_user, current_user, login_required
# from mongoengine.queryset.visitor import Q

from sttapp.base.enums import FlashCategory
from .forms import ProposalForm
from .models import Proposal, Itinerary


import iso8601


bp = Blueprint('proposal', __name__, url_prefix='/proposal')


@bp.route('/proposals/', methods=["GET", "POST"])
@login_required
def proposals():

    return render_template("proposals/proposals.html", proposals=Proposal.objects.all())


@bp.route('/create/', methods=["GET", "POST"])
@login_required
def create():
    form = ProposalForm(request.form)
    if request.method == "POST":
        if form.validate_on_submit():
            days = form.days.data
            proposal = Proposal(
                title=form.title.data,
                start_date=form.start_date_dt,
                days=form.days.data,
                end_date=form.start_date_dt + datetime.timedelta(days=days),
                return_plan=form.return_plan.data,
                buffer_days=form.buffer_days.data,
                approach_way=form.approach_way.data,
                radio=form.radio.data,
                satellite_telephone=form.satellite_telephone.data,
                gathering_point=form.gathering_point.data,
                gathering_time=form.gathering_at_dt,
                created_by=current_user.id
            )
            proposal.itinerary_list = [
                Itinerary(day_number=i) for i in range(0, days+1)
            ]
            proposal.save()
            return redirect(url_for("proposal.update_itinerary", prop_id=proposal.id))
        else:
            flash("格式錯誤", FlashCategory.error)

    return render_template("proposals/proposal_detail.html", form=form)


@bp.route('/update/<string:prop_id>', methods=["GET", "POST"])
@login_required
def update(prop_id):

    prop = Proposal.objects.get_or_404(id=prop_id)
    if request.method == "GET":
        form = ProposalForm(
            title=prop.title,
            start_date=prop.start_date.strftime("%Y/%m/%d"),
            end_date=prop.end_date.strftime("%Y/%m/%d"),
            leader=None,
            guide=None,
            supporter=None,
            return_plan=prop.return_plan,
            buffer_days=prop.buffer_days,
            radio=prop.radio,
            satellite_telephone=prop.satellite_telephone,
            gathering_point=prop.gathering_point,
            gathering_time=prop.gathering_time.strftime(
                "%Y/%m/%d %H/%M") if prop.gathering_time else ""
        )
    else:
        form = ProposalForm(request.form)
        if form.validate_on_submit():
            proposal = Proposal(
                id=prop.id,
                title=form.title.data,
                start_date=form.start_date_dt,
                end_date=form.end_date_dt,
                return_plan=form.return_plan.data,
                buffer_days=form.buffer_days.data,
                approach_way=form.approach_way.data,
                radio=form.radio.data,
                satellite_telephone=form.satellite_telephone.data,
                gathering_point=form.gathering_point.data,
                gathering_time=form.gathering_at_dt,
                created_by=current_user.id
            )
            proposal.save()
            flash("更新成功！", FlashCategory.success)
            return redirect(url_for('proposal.proposals'))
        else:
            flash("欄位錯誤", FlashCategory.error)
            return redirect(url_for('proposal.update', prop_id=prop_id))

    return render_template('proposals/proposal_detail.html', form=form)


@bp.route('/update_itinerary/<string:prop_id>', methods=["GET", "POST"])
@login_required
def update_itinerary(prop_id):

    prop = Proposal.objects.get_or_404(id=prop_id)

    if request.method == "POST":
        updated_list = []
        for itinerary in prop.itinerary_list:
            print(
                itinerary.day_number,
                request.form.get("content{}".format(itinerary.day_number)),
                request.form.get("water_info{}".format(itinerary.day_number)),
                request.form.get(
                    "communication_info{}".format(itinerary.day_number))
            )
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

        flash("行程更新成功", FlashCategory.success)
        Proposal.objects(id=prop_id).update_one(
            updated_at=datetime.datetime.utcnow(),
            itinerary_list=updated_list
        )
        return redirect(url_for('proposal.proposals'))

    return render_template("proposals/itinerary.html", itinerary_list=prop.itinerary_list)


@bp.route('/delete/<string:prop_id>', methods=["POST"])
@login_required
def delete(prop_id):
    prop = Proposal.objects.get_or_404(id=prop_id)
    if prop.created_by.id != current_user.id:
        flash("只有張貼者能夠刪除隊伍提案", FlashCategory.error)
        return redirect(url_for('proposal.proposals'))
    prop.delete()
    flash("已經為您刪除隊伍提案：{}".format(prop.title), FlashCategory.success)
    return redirect(url_for("proposal.proposals"))
