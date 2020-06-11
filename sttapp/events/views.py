import datetime

from flask import flash, Blueprint, session, request, url_for, render_template, redirect, current_app
from flask_login import login_user, current_user, login_required
from mongoengine.queryset.visitor import Q
from mongoengine.errors import NotUniqueError

from sttapp.base.enums import FlashCategory
from sttapp.proposals.models import Itinerary, Proposal
from .models import Event


bp = Blueprint('event', __name__, url_prefix='/event')


@bp.route('/create/<string:prop_id>', methods=["POST", "GET"])
@login_required
def create(prop_id):

    prop = Proposal.objects.get_or_404(id=prop_id)

    if request.method == "GET":
        itinerary_list = prop.itinerary_list
    else:
        form = request.form
        print(form)
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


@bp.route('/events/')
@login_required
def events():
    events = Event.objects.all()
    return render_template('events/events.html', events=events)
