from flask import Blueprint, render_template


err_handler = Blueprint("err_handler", __name__)


@err_handler.app_errorhandler(404)
def page_not_found(err):
    return render_template("status/404.html"), 404
