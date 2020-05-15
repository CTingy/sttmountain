from flask import flash, Blueprint, Response, request, render_template, redirect

from sttapp.users.models import SttUser
from .forms import SignupForm, InvitationForm


bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/invite/', methods=["GET", "POST"])
def invite():
    form = InvitationForm(request.form)
    if form.validate_on_submit():       
        flash('已寄出邀請信，請於七天內申請帳號', 'success')
        return redirect('/')
    return render_template('auth/invitation.html', form=form)


@bp.route('/signup/', methods=["GET", "POST"])
def auth_register():
    form = SignupForm(request.form)
    if form.validate_on_submit():       
        user = SttUser(
            username = form.username.data,
            email='aaa@myhome.com',
        )
        user.password = form.password.data
        user.save() 
        flash('恭喜註冊成功！歡迎光臨成大山協網站～～～', 'success')
        return redirect('/')
    return render_template('auth/signup.html', form=form)
