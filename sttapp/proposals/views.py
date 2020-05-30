import datetime

from flask import flash, Blueprint, session, request, url_for, render_template, redirect, current_app
from flask_login import login_user, current_user, login_required
# from mongoengine.queryset.visitor import Q

from sttapp.base.enums import FlashCategory
from .forms import ProposalForm
from .models import Proposal, Itinerary


import iso8601


bp = Blueprint('proposal', __name__, url_prefix='/proposal')


@bp.route('/create/', methods=["GET", "POST"])
@login_required
def create():
    form = ProposalForm(request.form)
    if request.method == "POST":
        if form.validate_on_submit():
            proposal = Proposal(
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
            duration = (form.end_date_dt-form.start_date_dt).days
            proposal.itinerary_list = [
                Itinerary(day_number=i) for i in range(duration+1)
            ]
            proposal.save()
            return redirect(url_for("proposal.update_itinerary", prop_id=proposal.id))
        else:
            flash("格式錯誤", FlashCategory.error)

    return render_template("proposals/create.html", form=form)


@bp.route('/update/<string:prop_id>', methods=["GET", "POST"])
@login_required
def update():
    pass


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
        return redirect("/")

    return render_template("proposals/itinerary.html", itinerary_list=prop.itinerary_list)
