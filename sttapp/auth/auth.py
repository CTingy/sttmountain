from flask import Blueprint, Response, request, render_template

from ..users.models import User
from .froms import SignupForm


bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/signup/', methods=["GET", "POST"])
def auth_register():
    form = SignupForm()
    if form.validate_on_submit():
        return redirect('/')
    return render_template('auth/signup.html', form=form)
