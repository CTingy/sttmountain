from flask import Blueprint, Response, request

from .models import User


bp = Blueprint('user', __name__)


@bp.route('/users/')
def users():
    return "Hello users"
