from flask import flash, Blueprint, Response, request, render_template


bp = Blueprint('home', __name__)


@bp.route('/')
def index():
    return render_template('index.html')
