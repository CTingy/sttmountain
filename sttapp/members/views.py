import datetime

from flask import flash, Blueprint, session, request, jsonify, url_for, render_template, redirect, current_app
from flask_login import login_user, current_user, login_required
# from mongoengine.queryset.visitor import Q

from sttapp.base.enums import FlashCategory, Level, Difficulty, Gender
from .models import Member
from .forms import MemberForm


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


@bp.route('/search_for_updating/')
@login_required
def search_for_updating():
    return render_template("members/members.html", member=None, 
                            for_updating=True, errors=None)


@bp.route('/search_one/', methods=["POST"])
@login_required
def search_one():

    name = request.form.get("name")
    security_number = request.form.get("security_number")

    if not name or not security_number:
        flash("姓名與身份證字號都必須輸入喔！", FlashCategory.ERROR)
        return redirect(url_for("member.members"))
    if not security_number[0].isupper():
        flash("身份證字號第一碼需為英文字母大寫", FlashCategory.ERROR)
        return redirect(url_for("member.members"))
    try:
        member = Member.objects.get(name=name, security_number=security_number)
    except Member.DoesNotExist:
        flash("查無此姓名或查無此身份證字號，請建立新的人員資料", FlashCategory.WARNING)
        return redirect(url_for("member.members"))
    flash("已查到資料，可進一步修改資料", FlashCategory.SUCCESS)
    return redirect(url_for('member.update', member_id=member.id))


@bp.route('/update/<string:member_id>', methods=["GET", "POST"])
@login_required
def update(member_id):
    
    member = Member.objects.get_or_404(id=member_id)
    errors = dict()

    if request.method == "POST":
        info_dict = dict(request.form)
        info_dict.pop('csrf_token', None)
        member = Member(**info_dict)
        member.id = member_id
        form = MemberForm(request.form)
        if form.validate_on_submit():
            member.created_by = current_user.id
            member.birthday = form.birthday_dt
            member.gender = Gender.get_map().get(form.gender.data)
            member.level = Level.get_map().get(form.level.data)
            member.highest_difficulty = Level.get_map().get(form.highest_difficulty.data)
            member.save()
            flash("修改成功，請檢查", FlashCategory.SUCCESS)
            return redirect(url_for('member.update', member_id=member_id))
        else:
            for field, errs in form.errors.items():
                errors[field] = errs[0]    
            flash("表單格式有誤，請重新填寫", FlashCategory.ERROR)
    return render_template("members/members.html", member=member, 
                            for_updating=True, errors=errors)        


@bp.route('/create/', methods=["GET", "POST"])
@login_required
def create():
    if request.method == "GET":
        return render_template("members/members.html", member=None, 
                                for_updating=False, errors=None)
    
    info_dict = dict(request.form)
    info_dict.pop('csrf_token', None)
    member = Member(**info_dict)
    form = MemberForm(request.form)
    
    if form.validate_on_submit():
        member.created_by = current_user.id
        member.birthday = form.birthday_dt
        member.gender = Gender.get_map().get(form.gender.data)
        member.level = Level.get_map().get(form.level.data)
        member.highest_difficulty = Level.get_map().get(form.highest_difficulty.data)
        member.save()
        flash("出隊人員資料新增成功", FlashCategory.SUCCESS)
        return redirect(url_for('member.update', member_id=member.id))
    else:
        errors = dict()
        for field, errs in form.errors.items():
            errors[field] = errs[0]    
        flash("表單格式有誤，請重新填寫", FlashCategory.ERROR)
        return render_template("members/members.html", member=member, errors=errors, for_updating=False)
    

@bp.route('/delete/<string:member_id>', methods=["POST"])
@login_required
def delete(member_id):
    member = Member.objects.get_or_404(id=member_id)
    if member_id.created_by.id != current_user.id:
        flash("只有此筆資料創建者能夠刪除", FlashCategory.ERROR)
    member.delete()
    flash("已經為您刪除人員：{}".format(member.name), FlashCategory.SUCCESS)
    return redirect(url_for('member.search_for_updating'))
