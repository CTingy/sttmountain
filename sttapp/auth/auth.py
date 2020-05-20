import datetime

from flask import flash, Blueprint, request, url_for, render_template, redirect
from mongoengine.queryset.visitor import Q
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity, decode_token
)
from jwt.exceptions import ExpiredSignatureError

from sttapp.users.models import SttUser
from sttapp.base.enums import FlashCategory
from .forms import SignupForm, InvitationForm
from .enums import INVITATION_EXPIRE_DAYS
from .services.mail import send_mail


bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/invite/', methods=["GET", "POST"])
# @jwt_required
def invite():
    form = InvitationForm(request.form)
    if form.validate_on_submit():
        
        invite_token = create_access_token(
            identity=form.email.data,
            expires_delta=datetime.timedelta(days=INVITATION_EXPIRE_DAYS)
        )

        send_mail(
            subject="邀請您註冊成大山協網站帳號",
            recipients=[form.email.data, ],
            html_body=render_template(
                "auth/invitation_email.html",
                url=request.host_url + url_for("auth.signup", invite_token=invite_token),
                days=INVITATION_EXPIRE_DAYS)
        )
        flash(
            '已寄出邀請信，請於{}天內申請帳號'.format(INVITATION_EXPIRE_DAYS), 
            FlashCategory.info
        )
        return redirect(url_for('auth.invite'))
    return render_template('auth/invitation_form.html', form=form)


@bp.route('/signup/<string:invite_token>', methods=["GET", "POST"])
def signup(invite_token):

    try:
        email = decode_token(invite_token)['identity']
    except ExpiredSignatureError:
        flash("該連結已經過期~請申請新的註冊連結", FlashCategory.error)
        return redirect("/")
    except Exception:
        flash("該連結為無效連結~請重新申請", FlashCategory.error)
        return redirect("/")
    
    form = SignupForm(request.form)
    
    # 避免同一token被重複註冊的情況
    if SttUser.objects(invitation_token=invite_token):
        flash("該連結已經被註冊過了喔~請申請新的註冊連結", FlashCategory.warn)
        return redirect("/")

    if request.method == "POST":
        if form.validate_on_submit():
            user = SttUser(
                username = form.username.data,
                invitation_email = email,
                invitation_token = invite_token,
            )
            user.password = form.password.data
            user.signup_at = user.created_at = datetime.datetime.utcnow()
            user.save()
            flash('恭喜註冊成功！歡迎光臨成大山協網站，請登入~~~', FlashCategory.success)
            return redirect('/')
        else:
            flash('格式錯誤', FlashCategory.error)
    return render_template('auth/signup.html', form=form)
