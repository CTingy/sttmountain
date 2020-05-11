from ..users.models import User

from flask import Blueprint, Response, request, render_template
from flask_mongoengine.wtf import model_form


bp = Blueprint('auth', __name__, url_prefix='/auth')


# RegisterForm = model_form(
#     User, field_args={
#         'title': {'textarea': True}
#     }
# )


RegisterForm = model_form(User)


@bp.route('/signup/')
def auth_register():
    form = RegisterForm
    if request.method == 'POST' and form.validate():
        # do something
        print("hey POST!")
        # redirect('/')
    return render_template('signup.html', form=form)
