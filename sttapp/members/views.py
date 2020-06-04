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

    members = Member.objects.filter(name__startswith=keyword)
    name_list = []

    for m in members:
        name = m.name
        if m.department_and_grade:
            name += "|{}".format(m.department_and_grade)
        name_list.append(name)

    return jsonify(name_list)