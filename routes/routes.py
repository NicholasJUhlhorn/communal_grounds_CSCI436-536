# Nicholas J Uhlhorn
# November 2025

from flask import Blueprint
from flask import Flask, render_template, session, request
from controller import controller
from services import user_service

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def home():
    return render_template('home.html', available_projects = ['project 1', 'project 2'])

@main_bp.route("/about")
def about():
    return render_template('about.html')

@main_bp.route("/profile_creation")
def profile_creation():
    return render_template('profile_creation.html')

@main_bp.route("/my_projects")
def my_projects():
    return render_template('my_projects.html')

@main_bp.route("/submit_profile_creation", methods=['POST'])
def submit_profile_creation():
    new_user = controller.handle_account_creation(request.form)
    session['current_uid'] = new_user.uid
    return profile()

@main_bp.route("/profile")
def profile():
    curr_uid = session.get('current_uid')
    if not curr_uid:
        return profile_creation()
    return render_template('profile.html', friends_list=user_service.get_friends_list(curr_uid))

@main_bp.route("/signout")
def signout():
    session.pop('current_uid')
    return profile_creation()

@main_bp.route("/project/<pid>")
def project(pid):
    return render_template('project.html')

@main_bp.route("/edit_profile")
def edit_profile():
    return render_template('edit_profile.html')

@main_bp.route("/submit_login", methods=['POST'])
def submit_login():
    uid = controller.handle_login(request.form)
    if not uid:
        return profile_creation()
    session['current_uid'] = uid
    return profile()
