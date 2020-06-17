from flask import flash, Blueprint, session, request, url_for, render_template, redirect, current_app
from flask_login import login_user, current_user, login_required
from mongoengine.queryset.visitor import Q

from .models import SttUser
from sttapp.base.enums import FlashCategory, Position, Group, Level



bp = Blueprint('user', __name__, url_prefix="/user")


@bp.route('/detail/<string:user_id>')
# @login_required
def detail(user_id):

    user = SttUser.objects.get_or_404(id=user_id)
    return render_template('users/detail.html', user=user)


@bp.route('/update/<string:user_id>')
@login_required
def update(user_id):

    user = SttUser.objects.get_or_404(id=user_id)
    if user_id != current_user.id:
        flash("您無權限編輯他人資料", FlashCategory.ERROR)
        return redirect("/")
    
    if request.method == "GET":
        return render_template('users/detail.html', user=user)
