import datetime
import json

from flask import flash, Blueprint, request, url_for, render_template, redirect
from mongoengine.queryset.visitor import Q
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity, decode_token, create_refresh_token
)
from jwt.exceptions import ExpiredSignatureError

from sttapp.users.models import SttUser, InvitationInfo
from sttapp.base.enums import FlashCategory
from .forms import SignupForm, InvitationForm, LoginForm
from .enums import INVITATION_EXPIRE_DAYS
from .services.mail import send_mail

import iso8601


bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/invite/', methods=["GET", "POST"])
# @jwt_required
def invite():
    form = InvitationForm(request.form)
    if form.validate_on_submit():
        
        invitation_token = create_access_token(
            identity=json.dumps({
                'email': form.email.data,
                # 'user_id': str(user.id),
                'invited_at': datetime.datetime.utcnow().isoformat()
            }),
            expires_delta=datetime.timedelta(days=INVITATION_EXPIRE_DAYS)
        )
        
        if len(invitation_token) >= 1500:
            flash("邀請註冊連結生成發生問題，請洽管理員", FlashCategory.error)
            return redirect(url_for('auth.invite'))

        send_mail(
            subject="邀請您註冊成大山協網站帳號",
            recipients=[form.email.data, ],
            html_body=render_template(
                "auth/invitation_email.html",
                url=request.host_url + url_for("auth.signup", invitation_token=invitation_token),
                days=INVITATION_EXPIRE_DAYS)
        )
        flash(
            '已寄出邀請信，請於{}天內申請帳號'.format(INVITATION_EXPIRE_DAYS), 
            FlashCategory.info
        )
        return redirect(url_for('auth.invite'))
    return render_template('auth/invitation_form.html', form=form)


@bp.route('/signup/<string:invitation_token>', methods=["GET", "POST"])
def signup(invitation_token):

    try:
        invitation_info_dict = json.loads(decode_token(invitation_token)['identity'])
    except ExpiredSignatureError:
        flash("該連結已經過期~請申請新的註冊連結", FlashCategory.error)
        return redirect("/")
    except Exception:
        flash("該連結為無效連結~請重新申請", FlashCategory.error)
        return redirect("/")
    
    form = SignupForm(request.form)
    
    # 避免同一token被重複註冊的情況
    if SttUser.objects(invitation_info__token=invitation_token):
        flash("該連結已經被註冊過了喔~請申請新的註冊連結", FlashCategory.warn)
        return redirect("/")

    if request.method == "POST":
        if form.validate_on_submit():
            user = SttUser()
            user.invitation_info = InvitationInfo(
                email=invitation_info_dict['email'],
                invited_at=iso8601.parse_date(invitation_info_dict['invited_at']),
                # invited_by=invitation_info_dict['user_id'],
                token=invitation_token
            )
            user.email = invitation_info_dict['email']
            user.username = form.username.data
            user.password = form.password.data
            user.signup_at = user.created_at = datetime.datetime.utcnow()
            user.save()
            flash('恭喜註冊成功！歡迎光臨成大山協網站，請登入~~~', FlashCategory.success)
            return redirect('/')
        else:
            flash('格式錯誤', FlashCategory.error)
    return render_template('auth/signup.html', form=form)


@bp.route('/login/', methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST":
        if form.validate_on_submit():
            flash('登入成功！', FlashCategory.success)
            return redirect('/')
        else:
            flash('登入失敗', FlashCategory.error)
    return render_template('auth/login.html', form=form)
