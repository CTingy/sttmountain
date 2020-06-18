import datetime

from flask import flash, Blueprint, session, request, url_for, render_template, redirect, current_app
from flask_login import login_user, current_user, login_required
from mongoengine.queryset.visitor import Q

from .models import SttUser
from sttapp.base.enums import FlashCategory, Position, Group, Level
from sttapp.auth.forms import PostSignupForm


bp = Blueprint('user', __name__, url_prefix="/user")


@bp.route('/detail/<string:user_id>')
@login_required
def detail(user_id):

    user = SttUser.objects.get_or_404(id=user_id)
    invited_by = ""
    if user.invitation_info.invited_by:
        try:
            invited_by = SttUser.objects.get(id=user.invitation_info.invited_by).username
        except SttUser.DoesNotExist:
            pass
    return render_template('users/detail.html', user=user, invited_by=invited_by)


@bp.route('/update/', methods=["GET", "POST"])
@login_required
def update():

    user = SttUser.objects.get_or_404(id=current_user.id)
    if request.method == "GET":
        form = PostSignupForm(obj=user)
        form.birthday.data = user.birthday_str
        return render_template('auth/post_signup.html', form=form)
    
    form = PostSignupForm(request.form)
    if form.validate_on_submit():
        SttUser.objects(id=current_user.id).update_one(
            username=form.username.data,
            name=form.name.data or None,
            birthday=form.birthday_dt or None,
            cellphone_number=form.cellphone_number.data or None,
            department=form.department.data or None,
            graduation_year=form.graduation_year.data or None,
            group=form.group.data,
            position=form.position.data,
            level=form.level.data,
            identity=form.identity.data,
            updated_at=datetime.datetime.utcnow(),
            updated_by=current_user.id
        )
        flash("更新成功！", FlashCategory.SUCCESS)
        return redirect(url_for('user.detail', user_id=current_user.id))
    else:
        flash("表單格式錯誤", FlashCategory.ERROR)
        return render_template('auth/post_signup.html', form=form)
