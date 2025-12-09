# Nicholas J Uhlhorn
# November 2025

from flask import Blueprint
from flask import Flask, render_template, session, request, redirect, url_for, flash
from controller import controller
from services import user_service, project_service
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

        if not user:
            return redirect(url_for('main.profile_creation'))

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

    if not curr_uid or not user:
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

@main_bp.route("/project_application/<pid>", methods=['GET', 'POST'])
def project_application(pid):
    # Make sure the session has a logged user first.
    try:
        uid = session['current_uid']
    except:
       return redirect(url_for('main.profile_creation'))

    project = None
    try:
        project = project_service.get_project_with_related_data(pid) 
    except Exception as e:
        print(f'Error grabing project: {e}', flush=True)
        return render_template('something_went_wrong.html')

    if project is None:
        return render_template('something_went_wrong.html')

    member_uids = [pm.member.uid for pm in project.members]
    is_member = uid in member_uids

    if is_member:
        return render_template('project.html', project=project)
    
    project_service.add_project_member(pid, uid, role="PETITION")

    return render_template('project_application.html')

@main_bp.route("/edit_profile")
def edit_profile():
    return render_template('edit_profile.html')

@main_bp.route("/submit_login", methods=['GET', 'POST'])
def submit_login():
    uid = controller.handle_login(request.form)
    if not uid:
        print(f'NO UDI: {uid}', flush=True)
        flash("Login Failed: Invalid username and/or password.", 'error')
        return redirect(url_for('main.profile_creation'))

    session['current_uid'] = uid
    print(session['current_uid'], uid, flush=True)
    return profile()
