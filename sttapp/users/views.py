import datetime
import re

from flask import flash, Blueprint, session, request, url_for, render_template, redirect, current_app, jsonify
from flask_login import login_user, current_user, login_required
from mongoengine.queryset.visitor import Q

from .models import SttUser, MyHistory
from .forms import MyHistoryForm
from sttapp.base.enums import FlashCategory, Position, Group, Level, Identity
from sttapp.auth.forms import PostSignupForm
from sttapp.members.models import CHOICES, Member


bp = Blueprint('user', __name__, url_prefix="/user")


@bp.route('/detail/<string:user_id>')
def detail(user_id):

    user = SttUser.objects.get_or_404(id=user_id)
    invited_by = ""
    history = MyHistory.objects.filter(user_id=user_id)

    if not current_user.is_authenticated:
        return render_template('users/detail.html', user=user, invited_by="", 
                               member=None, history=history)

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
    return render_template('users/detail.html', user=user, invited_by=invited_by, member=member, history=history)


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
            introduction=form.introduction.data,
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
    cellphone_number = request.form.get("cellphone_number").strip()
    if not re.match("[A-Z][0-9]{9}", security_number):
        flash("身份證字號輸入格式錯誤，請再試一次", FlashCategory.ERROR)
        return redirect(url_for("user.detail", user_id=current_user.id))
    try:
        member = Member.objects.get(security_number=security_number)
    except Member.DoesNotExist:
        flash("找不到此身份證字號，請新建立一個", FlashCategory.WARNING)
        return redirect(url_for("user.create_member"))
    else:
        if member.cellphone_number != cellphone_number:
            flash("身份證字號與手機號碼不相符，請檢查是否輸入錯誤後再操作一次", FlashCategory.ERROR)
            return redirect(url_for("user.detail", user_id=current_user.id))
        if member.user_id:
            flash("已經有人連結此身份證字號&手機的出隊資料了，請聯絡系統管理員", FlashCategory.ERROR)
            return redirect(url_for("user.detail", user_id=current_user.id))
    
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


def serialize_my_history(user_id, target_h=None):
    # re-ordering
    if target_h:
        hs_list = list(MyHistory.objects(user_id=user_id, id__ne=target_h.id))
        try:
            hs_list.insert(target_h.order-1, target_h)
        except IndexError:
            hs_list.append(target_h)
    else:
        hs_list = list(MyHistory.objects(user_id=user_id))
    hs = []
    for i, h in enumerate(hs_list, 1):
        h.order = i
        h.save()
        hs.append(serialize_single(h))
    return hs


def serialize_single(h):
    obj = {
        'id': str(h.id),
        'order': h.order,
        'date_str': "{}~{}".format(h.start_date_str, h.end_date_str),
        'title': h.title,
        'event_type': h.event_type or "",
        'days': h.days,
        'difficulty': h.difficulty,
        'link': '''
            <a type="button" class="btn btn-default btn-round-full" 
            href="{}" target="_blank"><i class="tf-attachment"></i></a>
        '''.format(h.link) if h.link else "",
    }
    return obj


@bp.route('/my_history/create/', methods=["POST"])
@login_required
def create_my_history():

    if request.form.get('user_id') != str(current_user.id):
        return jsonify({'objs': None, 'errors': {'message': '您無權進行此操作'}}), 403

    form = MyHistoryForm(request.form)
    errs = form.validate()

    if errs:
        return jsonify({'objs': None, 'errors': errs})
    h = MyHistory(**form.__dict__)
    h.created_at = h.updated_at = datetime.datetime.utcnow()
    h.created_by = h.updated_by = current_user.id
    h.user_id = current_user.id
    try:
        h.save()
    except Exception as e:
        raise(e)
    return jsonify({'objs': serialize_my_history(current_user.id, h), 'errors': None}), 200


@bp.route('/my_history/delete/', methods=["POST"])
@login_required
def delete_my_history():
    
    hid = request.form.get('my_history_id')
    try:
        h = MyHistory.objects.get(id=hid)
    except MyHistory.DoesNotExist:
        return jsonify({'objs': None, 'errors': {'message': '找不到此項目'}}), 404
    
    if h.user_id != current_user.id:
        return jsonify({'objs': None, 'errors': {'message': '您無權進行此操作'}}), 403
    h.delete()

    return jsonify({'objs': serialize_my_history(current_user.id), 'errors': None}), 200


@bp.route('/my_history/')
@login_required
def get_my_history():
    
    hid = request.args.get('my_history_id')

    try:
        h = MyHistory.objects.get(id=hid)
    except MyHistory.DoesNotExist:
        return jsonify({'objs': None, 'errors': {'message': '找不到此項目'}}), 404
    
    return jsonify({'objs': [serialize_single(h)], 'errors': None}), 200


@bp.route('/my_history/update/', methods=["POST"])
@login_required
def update_my_history():

    hid = request.form.get('my_history_id')
    try:
        h = MyHistory.objects.get(id=hid)
    except MyHistory.DoesNotExist:
        return jsonify({'objs': None, 'errors': {'message': '找不到此項目'}}), 404
    if h.user_id != current_user.id:
        return jsonify({'objs': None, 'errors': {'message': '您無權進行此操作'}}), 403

    form = MyHistoryForm(request.form)
    errs = form.validate()

    if errs:
        return jsonify({'objs': None, 'errors': errs})
    
    MyHistory.objects(id=hid).update_one(
        updated_at=datetime.datetime.utcnow(),
        **form.__dict__
    )
    h.reload()
    return jsonify({'objs': serialize_my_history(current_user.id, h), 'errors': None}), 200
