from flask import flash, Blueprint, request, url_for, render_template, redirect

from sttapp.users.models import SttUser
from sttapp.base.enums import FlashCategory
from .forms import SignupForm, InvitationForm
from .enums import INVITATION_EXPIRE_DAYS
from .services.mail import send_mail


bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/invite/', methods=["GET", "POST"])
def invite():
    form = InvitationForm(request.form)
    if form.validate_on_submit():
        send_mail(
            subject="邀請您註冊成大山協網站帳號",
            sender="stt@mymail.com",
            recipients=[form.email.data, ],
            html_body=render_template(
                "auth/invitation_email.html",
                url=request.host_url + url_for("auth.signup"),
                days=INVITATION_EXPIRE_DAYS)
        )
        flash(
            '已寄出邀請信，請於{}天內申請帳號'.format(INVITATION_EXPIRE_DAYS), 
            FlashCategory.info
        )
        return redirect(url_for('auth.invite'))
    return render_template('auth/invitation_form.html', form=form)


@bp.route('/signup/', methods=["GET", "POST"])
def signup():
    form = SignupForm(request.form)
    if form.validate_on_submit():       
        user = SttUser(
            username = form.username.data,
            email='aaa@myhome.com',
        )
        user.password = form.password.data
        user.save() 
        flash('恭喜註冊成功！歡迎光臨成大山協網站，請登入~~~', FlashCategory.success)
        return redirect('/')
    return render_template('auth/signup.html', form=form)
