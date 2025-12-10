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

@main_bp.route("/profile_creation", methods=['POST'])
def profile_creation():
    return render_template('profile_creation.html')

@main_bp.route("/my_projects")
def my_projects():
    uid = session.get('current_uid')
    if not uid:
        flash("Please log in first.", 'warning')
        return redirect(url_for('main.login'))
    else:
        user = User.query.get(uid)

        if not user:
            flash("Please log in first.", 'warning')
            return redirect(url_for('main.login'))
        print(f'Joined Projects: {user.joined_projects}', flush=True)

        return render_template('my_projects.html',my_projects=user.owned_projects,joined_projects=user.joined_projects)

@main_bp.route("/submit_profile_creation", methods=['POST'])
def submit_profile_creation():
    uname = request.form.get('username')
    eml = request.form.get('email')
    if not User.query.filter_by(username=uname).first() and not User.query.filter_by(email=eml).first():
        new_user = controller.handle_account_creation(request.form)
        session['current_uid'] = new_user.uid
        return profile()
    else:
        flash("Profile Creation Failed: User profile name already exists.", 'error')

    return profile_creation()

@main_bp.route("/profile")
def profile():
    curr_uid = session.get('current_uid')
    user = User.query.filter_by(uid=curr_uid).first()

    if not curr_uid or not user:
        flash("Please log in first.", 'warning')
        return redirect(url_for('main.login'))

    return render_template('profile.html', friends_list=user_service.get_friends_list(curr_uid),username=user.username)

@main_bp.route("/login", methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@main_bp.route("/signout")
def signout():
    session.pop('current_uid')
    return login()

@main_bp.route("/project/<pid>", methods=['GET', 'POST'])
def project(pid):
    try:
        uid = session.get('current_uid')
    except:
        flash("Please log in first.", 'warning')
        return redirect(url_for('main.login'))

    project = None
    try:
        project = project_service.get_project_with_related_data(pid) 
    except Exception as e:
        print(f'Error grabing project: {e}', flush=True)
        return render_template('something_went_wrong.html')

    member_uids = [pm.member.uid for pm in project.members]
    member_roles = [pm.role for pm in project.members]
    member_dict = dict(zip(member_uids, member_roles))
    is_owner = uid == project.owner.uid
    is_member = uid in member_uids
    has_joined = is_member and member_dict[uid] != 'PETITION'
    can_view = is_owner or (is_member and has_joined) 

    if not is_member:
        flash('You are not part of this project, send a petition and wait for approval to view.', 'warning')
        return redirect(url_for('main.home'))
    elif not has_joined:
        flash('Your petition is pending, wait for approval to view.', 'warning')
        return redirect(url_for('main.my_projects'))


    selected_project = Project.query.filter_by(pid=pid).first()
    
    return render_template('project.html',project=selected_project, is_owner=is_owner)

@main_bp.route('/project/<pid>/edit')
def edit_project(pid):
    try:
        uid = session.get('current_uid')
    except:
        flash("Please log in first.", 'warning')
        return redirect(url_for('main.login'))

    project = None
    try:
        project = project_service.get_project_with_related_data(pid) 
    except Exception as e:
        print(f'Error grabing project: {e}', flush=True)
        return render_template('something_went_wrong.html')

    is_owner = uid == project.owner.uid
    if not is_owner:
        flash("You are not the owner of that project!", 'error')
        return redirect(url_for('main.my_projects'))

    return render_template('project_edit.html', project=project)

@main_bp.route("/create_project")
def create_project():
    return render_template('project_creation.html')

@main_bp.route("/addmember", methods=['POST'])
def add_member():
    pid = request.form.get('pid')
    uid = request.form.get('uid')
    role = request.form.get('role')

    if not pid:
        flash("Please log in first.", 'warning')
        return redirect(url_for('main.login'))

    if pid and uid and role:
        selected_project = Project.query.filter_by(pid=pid).first()
        project_service.update_project_member(pid, uid, role)
        return render_template('project.html', project=selected_project)
    else:
        print(f'Error adding member: {e}', flush=True)
        return render_template('something_went_wrong.html')

@main_bp.route("/project_application/<pid>", methods=['GET', 'POST'])
def project_application(pid):
    # Make sure the session has a logged user first.
    try:
        uid = session.get('current_uid')
    except:
        flash("Please log in first.", 'warning')
        return redirect(url_for('main.login'))

    project = None
    try:
        project = project_service.get_project_with_related_data(pid) 
    except Exception as e:
        print(f'Error grabing project: {e}', flush=True)
        return render_template('something_went_wrong.html')

    if project is None:
        return render_template('something_went_wrong.html')

    member_uids = [pm.member.uid for pm in project.members]
    member_roles = [pm.role for pm in project.members]
    member_dict = dict(zip(member_uids, member_roles))
    is_owner = uid == project.owner.uid
    is_member = uid in member_uids
    has_joined = is_member and member_dict[uid] != 'PETITION'
    can_view = is_owner or (is_member and has_joined) 

    if can_view:
        return render_template('project.html', project=project, is_owner=is_owner)
    elif is_member:
        flash('Your petition is pending, wait for approval to view.', 'warning')
        return redirect(url_for('main.my_projects'))
    
    project_service.add_project_member(pid, uid, role="PETITION")

    flash('Petetion for project submitted!', 'success')
    return redirect(url_for('main.my_projects'))

@main_bp.route("/process_project_edit", methods=['GET', 'POST'])
def process_project_edit():
    pid = request.form.get('pid')
    action = request.form.get('save-action')
    name = request.form.get('name')
    description = request.form.get('description')
    status = request.form.get('status')

    if action == 'cancel':
        flash('Edits not committed.', 'warning')
        return redirect(url_for('main.project', pid=pid))

    project_service.update_project(pid, name, description, status)
    flash('Project information updated.', 'success')
    return redirect(url_for('main.project', pid=pid))

@main_bp.route("/process_project_create", methods=['GET','POST'])
def process_project_create():
    action = request.form.get('save-action')
    name = request.form.get('name')
    description = request.form.get('description')
    status = request.form.get('status')

    uid = session.get('current_uid')
    if not uid:
        flash("Please log in first.", 'warning')
        return redirect(url_for('main.login'))

    if action == 'cancel':
        flash("Project creation canceled.", "warning")
        return redirect(url_for('main.my_projects'))

    new_project = project_service.create_new_project(uid, name, description, status)
    flash("Project Created!", "success")
    return redirect(url_for('main.project', pid=new_project.pid))

@main_bp.route("/edit_profile")
def edit_profile():
    return render_template('edit_profile.html')

@main_bp.route("/submit_login", methods=['GET', 'POST'])
def submit_login():
    uid = controller.handle_login(request.form)
    if not uid:
        flash("Login Failed: Invalid username and/or password.", 'error')
        return redirect(url_for('main.login'))

    session['current_uid'] = uid
    return redirect(url_for('main.my_projects'))

