# Nicholas J Uhlhorn
# November 2025

from flask import Blueprint
from flask import Flask, render_template, session, request, redirect, url_for
from controller import controller
from services import user_service
from models.project import Project
from models.user import User
from models.project import Project

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def home():
    all_projects = Project.query.all()
    return render_template('home.html',all_projects=all_projects)

@main_bp.route("/about")
def about():
    return render_template('about.html')

@main_bp.route("/profile_creation")
def profile_creation():
    return render_template('profile_creation.html')

@main_bp.route("/my_projects")
def my_projects():
    uid = session.get('current_uid')
    if not uid:
        return redirect(url_for('main.profile_creation'))
    else:
        user = User.query.get(uid)
        return render_template('my_projects.html',my_projects=user.owned_projects)

@main_bp.route("/submit_profile_creation", methods=['POST'])
def submit_profile_creation():
    uname = request.form.get('username')
    eml = request.form.get('email')
    if not User.query.filter_by(username=uname).first() and not User.query.filter_by(email=eml).first():
        new_user = controller.handle_account_creation(request.form)
        session['current_uid'] = new_user.uid
        return profile()
    return profile_creation()

@main_bp.route("/profile")
def profile():
    curr_uid = session.get('current_uid')
    user = User.query.filter_by(uid=curr_uid).first()
    if not curr_uid:
        return redirect(url_for('main.profile_creation'))
    return render_template('profile.html', friends_list=user_service.get_friends_list(curr_uid),username=user.username)

@main_bp.route("/signout")
def signout():
    session.pop('current_uid')
    return profile_creation()

@main_bp.route("/project/<pid>")
def project(pid):
    selected_project = Project.query.filter_by(pid=pid).first()
    return render_template('project.html',project=selected_project)

@main_bp.route("/submit_login", methods=['POST'])
def submit_login():
    uid = controller.handle_login(request.form)
    if not uid:
        return redirect(url_for('main.profile_creation'))
    session['current_uid'] = uid
    return profile()

@main_bp.route("/edit_profile")
def edit_profile():
    return render_template('edit_profile.html')
