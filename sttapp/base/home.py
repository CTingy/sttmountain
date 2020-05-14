from flask import flash, Blueprint, Response, request, render_template


bp = Blueprint('home', __name__)


@bp.route('/')
def index():
    flash("lalala", "success")
    return render_template('index.html')

#   <!-- <form method="POST" action="/">
#     {{ form.csrf_token }}
#     {{ form.username.label }} {{ form.username(size=20) }}
#     <input type="submit" value="Go">
#   </form> -->