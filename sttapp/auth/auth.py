from flask import flash, Blueprint, Response, request, render_template, redirect

from sttapp.users.models import User
from .forms import SignupForm


bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/signup/', methods=["GET", "POST"])
def auth_register():
    # form = SignupForm(formdata=None)
    form = SignupForm(request.form)
    print(form.data)
    if form.validate_on_submit():
        flash('Thanks for registering', 'success')
        return redirect('/')
    return render_template('auth/signup.html', form=form)
