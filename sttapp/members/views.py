import datetime

from flask import flash, Blueprint, session, request, jsonify, url_for, render_template, redirect, current_app
from flask_login import login_user, current_user, login_required
# from mongoengine.queryset.visitor import Q

from sttapp.base.enums import FlashCategory
from .models import Member


import iso8601


bp = Blueprint('member', __name__, url_prefix='/member')


@bp.route('/search/')
@login_required
def search():

    keyword = request.args.get('keyword')
    if not keyword:
        return jsonify([])

    members = Member.objects.filter(name__contains=keyword)
    name_list = ["{}|{}".format(m.name, m.security_number) for m in members]
    return jsonify(name_list)
