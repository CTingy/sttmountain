import datetime

from flask import flash, Blueprint, session, request, url_for, render_template, redirect, current_app
from flask_login import login_user, current_user, login_required
from mongoengine.queryset.visitor import Q

from sttapp.base.enums import FlashCategory
from sttapp.proposals.models import Itinerary, Proposal


bp = Blueprint('event', __name__, url_prefix='/event')


@bp.route('/create/<string:prop_id>', methods=["POST", "GET"])
@login_required
def create(prop_id):
    pass

