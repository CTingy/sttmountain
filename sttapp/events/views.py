import datetime

from flask import flash, Blueprint, session, request, url_for, render_template, redirect, current_app
from flask_login import login_user, current_user, login_required
from mongoengine.queryset.visitor import Q

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
        request.form.get()

    return render_template('events/create.html', itinerary_list=itinerary_list)
