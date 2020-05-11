from flask import Blueprint, Response, request


bp = Blueprint('home', __name__)


@bp.route('/')
def index():
    return 'hello world'
