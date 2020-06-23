import datetime
import os

from flask import flash, Blueprint, session, request, url_for, render_template, redirect, current_app
from flask_login import login_user, current_user, login_required
from mongoengine.queryset.visitor import Q

from sttapp.base.enums import FlashCategory, Level, Gender, EventType
from sttapp.base.utils import get_local_dt
from sttapp.events.models import Event
from .forms import ProposalForm
from .models import Proposal, Itinerary
from .service import GoogleDriveService

import iso8601


bp = Blueprint('proposal', __name__, url_prefix='/proposal')


@bp.route('/proposals/')
@login_required
def proposals():
    return render_template('proposals/proposals.html', proposals=Proposal.objects.all())


@bp.route('/create/', methods=["GET", "POST"])
@login_required
def create():
   
    if request.method == "GET":
        return render_template("proposals/basic_form.html", prop=None, 
                                for_updating=False, errors=None, types=EventType.get_choices())

    info_dict = dict(request.form)
    # extract user inputs that needs to be returned after fail form validation
    _, inputted_leader, inputted_guide, inputted_attendees, inputted_start_date = (
        info_dict.pop(field) for field in ("csrf_token", "leader", "guide", "attendees", "start_date")
    )
    prop = Proposal(**info_dict)
    form = ProposalForm(request.form)

    if form.validate_on_submit():
        prop.created_by = prop.updated_by = current_user.id
        prop.created_at = prop.updated_at = datetime.datetime.utcnow()
        prop.start_date = form.start_date_dt
        prop.end_date = form.start_date_dt + datetime.timedelta(days=prop.days-1)
        prop.leader = form.leader_id
        prop.guide = form.guide_id
        prop.attendees = form.attendees_ids
        prop.buffer_days = form.buffer_days.data or None
        # generate itinerary_list
        prop.itinerary_list = [
            Itinerary(day_number=i) for i in range(1, prop.days+1)
        ]
        if prop.has_d0:
            prop.itinerary_list.insert(0, Itinerary(day_number=0))
        prop.save()
        flash("基本資料完成，請接著編輯預計行程", FlashCategory.INFO)
        return redirect(url_for("proposal.update_itinerary", prop_id=prop.id))

    errors = dict()
    for field, errs in form.errors.items():
        errors[field] = errs[0]

    prop.inputted_leader = inputted_leader
    prop.inputted_guide = inputted_guide
    prop.inputted_attendees = inputted_attendees
    prop.inputted_start_date = inputted_start_date
    flash("表單格式有誤，請重新填寫", FlashCategory.ERROR)
    return render_template("proposals/basic_form.html", prop=prop, for_updating=False,
                            errors=errors, types=EventType.get_choices(True))


@bp.route('/detail/<string:prop_id>')
@login_required
def detail(prop_id):
    prop = Proposal.objects.get_or_404(id=prop_id)
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

    return render_template('proposals/detail.html', prop=prop)


@bp.route('/update/<string:prop_id>', methods=["GET", "POST"])
@login_required
def update(prop_id):

    ori_prop = Proposal.objects.get_or_404(id=prop_id)

    if current_user.id != ori_prop.created_by.id:
        flash("僅隊伍企劃創建者可編輯", FlashCategory.WARNING)
        return redirect(url_for('proposal.detail', prop_id=prop_id))

    if ori_prop.event_id and Event.objects.filter(
        id=ori_prop.event_id, status__in=("BACK", "CANCEL")):
        flash("已下山或倒隊之隊伍企劃不可編輯", FlashCategory.WARNING)
        return redirect(url_for('proposal.detail', prop_id=prop_id))

    if request.method == "GET":
        return render_template("proposals/basic_form.html", prop=ori_prop,
                               for_updating=True, errors=None, types=EventType.get_choices(True))

    info_dict = dict(request.form)
    # extract user inputs that needs to be returned after fail form validation
    _, inputted_leader, inputted_guide, inputted_attendees, inputted_start_date = (
        info_dict.pop(field) for field in ("csrf_token", "leader", "guide", "attendees", "start_date")
    )
    prop = Proposal(**info_dict)   

    # populate original data
    prop.id = prop_id
    prop.created_at = ori_prop.created_at
    prop.created_by = ori_prop.created_by
    
    form = ProposalForm(request.form)
    if form.validate_on_submit():
        prop.updated_by = current_user.id
        prop.updated_at = datetime.datetime.utcnow()
        prop.start_date = form.start_date_dt
        prop.end_date = form.start_date_dt + datetime.timedelta(days=prop.days-1)
        prop.leader = form.leader_id
        prop.guide = form.guide_id
        prop.attendees = form.attendees_ids
        prop.buffer_days = form.buffer_days.data or None

        # update itineray obj
        itinerary_list = ori_prop.itinerary_list
        update_itinerary = False
        if ori_prop.days != prop.days:
            update_itinerary = True
            itinerary_list = ori_prop.itinerary_list
            if prop.days > ori_prop.days:
                for i in range(ori_prop.days+1, prop.days+1):
                    itinerary_list.append(Itinerary(day_number=i))
            elif prop.days < ori_prop.days:
                for i in range(prop.days+1, ori_prop.days+1):
                    i = ori_prop.itinerary_list.get(day_number=i)
                    itinerary_list.remove(i)
        if ori_prop.has_d0 != prop.has_d0:
            update_itinerary = True
            if prop.has_d0 and not ori_prop.has_d0:
                itinerary_list.insert(0, Itinerary(day_number=0))
            elif not prop.has_d0 and ori_prop.has_d0:
                itinerary_list.pop(0)

        prop.itinerary_list = itinerary_list
        prop.save()

        flash("修改成功，請檢查", FlashCategory.SUCCESS)
        return redirect(url_for('proposal.{}'.format(
                "update_itinerary" if update_itinerary else "detail"), prop_id=prop_id))

    errors = dict()
    for field, errs in form.errors.items():
        errors[field] = errs[0]

    prop.inputted_leader = inputted_leader
    prop.inputted_guide = inputted_guide
    prop.inputted_attendees = inputted_attendees
    prop.inputted_start_date = inputted_start_date
    flash("表單格式有誤，請重新填寫", FlashCategory.ERROR)

    return render_template("proposals/basic_form.html", prop=prop,
                           for_updating=True, errors=errors, types=EventType.get_choices(True))


@bp.route('/update_itinerary/<string:prop_id>/', methods=["GET", "POST"])
@login_required
def update_itinerary(prop_id):

    prop = Proposal.objects.get_or_404(id=prop_id)
    if prop.start_date.date() < get_local_dt(datetime.datetime.utcnow()).date():
        flash("已開始之隊伍企劃不可編輯", FlashCategory.WARNING)
        return redirect(url_for('proposal.proposals'))
    if current_user.id != prop.created_by.id:
        flash("僅隊伍企劃創建者可編輯", FlashCategory.WARNING)
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

    if prop.event_id:
        flash("已產生出隊文之隊伍企劃不可刪除", FlashCategory.WARNING)
        return redirect(url_for('proposal.proposals'))
    if prop.created_by.id != current_user.id:
        flash("只有張貼者能夠刪除隊伍企劃", FlashCategory.WARNING)
        return redirect(url_for('proposal.proposals'))
    prop.delete()
    flash("已經為您刪除隊伍企劃：{}".format(prop.title), FlashCategory.SUCCESS)
    return redirect(url_for("proposal.proposals"))


@bp.route('/user_posts/')
@login_required
def user_posts():

    proposals = Proposal.objects.filter(created_by=current_user.id)
    return render_template('users/proposals.html', proposals=proposals)


@bp.route('/user_posts/<string:prop_id>', methods=["POST"])
@login_required
def gen_doc(prop_id):

    doc_url = request.form.get("doc_url")

    if doc_url and "folders/" in doc_url:
        folder_id = doc_url.split("/folders/")[1]
    else:
        folder_id = doc_url

    gd = GoogleDriveService(proposal_id=prop_id, google_folder_id=folder_id)
    gd.generate_sheets()
    gd.generate_doc()

    flash("資料產生中，請稍後至資料夾確認", FlashCategory.INFO)
    return redirect(url_for('proposal.detail', prop_id=prop_id))
