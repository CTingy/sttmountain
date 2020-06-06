import datetime

from flask import flash, Blueprint, session, request, jsonify, url_for, render_template, redirect, current_app
from flask_login import login_user, current_user, login_required
# from mongoengine.queryset.visitor import Q

from sttapp.base.enums import FlashCategory
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


@bp.route('/members/')
@login_required
def members():
    return render_template("members/members.html", member=None, for_updating=False)


@bp.route('/search_one/', methods=["POST"])
@login_required
def search_one():

    name = request.form.get("name")
    security_number = request.form.get("security_number")

    if not name or not security_number:
        flash("姓名與身份證字號都必須輸入喔！", FlashCategory.error)
        return redirect(url_for("member.members"))
    if security_number[0].islower():
        flash("身份證字號第一碼請大寫", FlashCategory.error)
        return redirect(url_for("member.members"))
    try:
        member = Member.objects.get(name=name, security_number=security_number)
    except Member.DoesNotExist:
        flash("查無此姓名或查無此身份證字號，請建立新的人員資料", FlashCategory.warn)
        return redirect(url_for("member.members"))
    flash("已查到資料，可進一步修改資料", FlashCategory.success)
    return redirect(url_for('member.update', member_id=member.id))


@bp.route('/update/<string:member_id>', methods=["GET", "POST"])
@login_required
def update(member_id):
    
    member = Member.objects.get_or_404(id=member_id)

    if request.method == "POST":
        form = MemberForm(request.form)
        if form.validate_on_submit():
            member.created_by = current_user.id
            member.save()
            flash("")
            return redirect(url_for('member.update', member_id=member_id))
        else:
            for field, errs in form.errors.items():
                for err in errs:
                    flash("{}格式錯誤: {}".format(field, err), FlashCategory.error)
    return render_template("members/members.html", member=member, for_updating=True)        


@bp.route('/create/', methods=["POST"])
@login_required
def create():
    
    info_dict = dict(request.form)
    info_dict.pop('csrf_token', None)
    member = Member(**info_dict)

    form = MemberForm(request.form)
    if form.validate_on_submit():
        member.created_by = current_user.id
        member.save()
        flash("出隊人員資料新增成功", FlashCategory.success)
        return redirect(url_for('member.update', member_id=member.id))
    else:
        for field, errs in form.errors.items():
            for err in errs:
                flash("{}格式錯誤: {}".format(field, err), FlashCategory.error)
        return render_template("members/members.html", member=member, for_updating=False)
    

@bp.route('/delete/<string:prop_id>', methods=["POST"])
@login_required
def delete(prop_id):
    # prop = Proposal.objects.get_or_404(id=prop_id)
    # if prop.created_by.id != current_user.id:
    #     flash("只有張貼者能夠刪除隊伍提案", FlashCategory.error)
    #     return redirect(url_for('proposal.proposals'))
    # prop.delete()
    # flash("已經為您刪除隊伍提案：{}".format(prop.title), FlashCategory.success)
    # return redirect(url_for("proposal.proposals"))
    pass
