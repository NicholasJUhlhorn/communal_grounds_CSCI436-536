# Nicholas J Uhlhorn
# November 2025

from flask import Blueprint

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def hello_world():
    return "<p>Hello, World!</p?>"


