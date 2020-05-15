from flask import flash, Blueprint, Response, request, render_template, redirect

from sttapp.users.models import SttUser
from .forms import SignupForm


bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/signup/', methods=["GET", "POST"])
def auth_register():
    form = SignupForm(request.form)
    if form.validate_on_submit():
        # user = SttUser(

        # )
        flash('恭喜註冊成功！歡迎光臨成大山協網站～～～', 'success')
        return redirect('/')
    return render_template('auth/signup.html', form=form)
