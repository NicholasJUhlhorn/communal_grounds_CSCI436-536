# import forms
from services import project_service
from services import reaction_service
from services import user_service
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session

# DB FUNCTIONS FOR USER INTERACTIVITY
# TODO: move these functions into their respective service.py programs, eventually

def change_user_email(uid: int, new_email: str):
    """Updates a user's email"""

    user = db.session.execute(
        db.select(User).where(
            (User.uid == uid)
        )
    ).scalar_one_or_none()

    if not user:
        raise ValueError("User not found")

    user.email = new_email

    db.session.commit()
    return user

def change_project_description(pid: int, new_description: str):
    """Updates a project's description"""

    proj = db.session.execute(
        db.select(Project).where(
            (Project.pid == pid)
        )
    ).scalar_one_or_none()

    if not proj:
        raise ValueError("Project not found")

    proj.description = new_description

    db.session.commit()
    return proj

def change_project_status(pid: int, new_status: str):
    """Updates a project's status"""

    proj = db.session.execute(
        db.select(Project).where(
            (Project.pid == pid)
        )
    ).scalar_one_or_none()

    if not proj:
        raise ValueError("Project not found")

    proj.status = new_status

    db.session.commit()
    return proj

def remove_project_member(pid: int, uid: int):
    ...

def change_role(pid: int, uid: int, new_role: str):
    ...

# PROJECT ACTION HANDLERS

def handle_project_creation(form):
    """
    based on given project creation form, instantiate project by calling appropriate service procedures
    """
    new_project = project_services.create_new_project(form.owner_uid, form.name, form.description)
    return render_template('project.html')

def handle_add_project_member(pid: int, uid: int, role: str = 'VIEWER'):
    """
    handle user request to add project member to given project with given role
    """
    project_services.add_project_member(pid, uid, role)
    return render_template('project.html')


# REACTION ACTION HANDLERS

def handle_add_reaction(pid: int, uid: int, reaction_type: str):
    """
    based on given reaction type, call appropriate service procedure to add reaction, then update view
    """
    reaction_service.add_reaction(pid, uid, reaction_type)
    ...


# USER ACTION HANDLERS

def handle_account_creation(form):
    """
    based on given account creation form, instantiate account by calling appropriate service procedures
    """
    hashed_password = generate_password_hash(form.get("password"))
    return user_service.create_new_user(form.get("email"), form.get("username"), hashed_password)

def handle_update_username(uid: int, form):
    '''
    Given a uid and an input form, handles updating a user's username.
    form is expected to have an attribute form.new_username
    '''
    new_username = form.get("new_username")
    return user_service.change_username(uid, new_username)

def handle_update_password(uid: int, form):
    '''
    Given a uid and an input form, handles updating a user's password.
    form is expected to have an attribute form.new_password
    '''
    new_password = form.get("new_password")
    new_hashed_password = generate_password_hash(new_password)
    return user_service.change_user_password(uid, new_hashed_password)

def get_available_projects():
    '''
    Retrieves all PUBLISHED projects which the current user
    is not already a part of
    '''
    ...

def handle_login(form):
    '''
    attempts to login user based on given form info. 
    returns uid for user if successful, returns None if unsuccessful
    '''
    username = form.get("username")
    password = form.get("password")
    user = user_service.find_user_with_username(username)
    if not user:
        return None
    if not check_password_hash(user.hashed_password, password):
        return None
    return user.uid
