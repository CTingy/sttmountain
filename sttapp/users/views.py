import datetime
import re

from flask import flash, Blueprint, session, request, url_for, render_template, redirect, current_app
from flask_login import login_user, current_user, login_required
from mongoengine.queryset.visitor import Q

from .models import SttUser
from sttapp.base.enums import FlashCategory, Position, Group, Level, Identity
from sttapp.auth.forms import PostSignupForm
from sttapp.members.models import CHOICES, Member


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
            if str(current_user.id) == user_id:
                invitation_info = user.invitation_info
                invitation_info.invited_by = None
                SttUser.objects(id=user_id).update_one(
                    updated_at=datetime.datetime.utcnow(),
                    updated_by=current_user.id,
                    invitation_info=invitation_info
                )
    member = None
    if user.member_id:
        try:
            member = Member.objects.get(id=user.member_id)
        except Member.DoesNotExist:
            if str(current_user.id) == user_id:
                SttUser.objects(id=user_id).update_one(
                    updated_at=datetime.datetime.utcnow(),
                    updated_by=current_user.id,
                    member_id=None
                )
    return render_template('users/detail.html', user=user, invited_by=invited_by, member=member)


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


@bp.route('/create_member/')
@login_required
def create_member():
    # populate info
    member = Member()
    member.nickname = current_user.username
    member.inputted_birthday = current_user.birthday_str or ""
    member.cellphone_number = current_user.cellphone_number or ""
    member.name = current_user.name or ""
    member.group = current_user.group
    member.level = current_user.level
    if current_user.department in (Identity.OB, Identity.OUT_NCKU):
        member.department_and_grade = current_user.department

    flash("請填寫額外資訊", FlashCategory.INFO)
    return render_template("members/members.html", member=member, 
                            for_updating=False, errors=None, choices=CHOICES)


@bp.route('/connect_member/', methods=["POST"])
@login_required
def connect_member():

    security_number = request.form.get("security_number").strip()
    if not re.match("[A-Z][0-9]{9}", security_number):
        flash("身份證字號輸入格式錯誤，請再試一次", FlashCategory.ERROR)
        return redirect(url_for("user.detail", user_id=current_user.id))
    try:
        member = Member.objects.get(security_number=security_number)
    except Member.DoesNotExist:
        flash("找不到此身份證字號的出隊資料，請重新建立一個", FlashCategory.WARNING)
        return redirect(url_for("user.create_member"))
    
    Member.objects(security_number=security_number).update_one(
        updated_at=datetime.datetime.utcnow(),
        updated_by=current_user.id,
        user_id=current_user.id
    )
    SttUser.objects(id=current_user.id).update_one(
        updated_at=datetime.datetime.utcnow(),
        updated_by=current_user.id,
        member_id=member.id
    )
    flash("連結出隊用資料完成！", FlashCategory.SUCCESS)
    return redirect(url_for("user.detail", user_id=current_user.id))
