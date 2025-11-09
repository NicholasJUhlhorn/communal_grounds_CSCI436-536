import forms
import project_service
import reaction_service
import user_service

def handle_page_selection(page_path: str):
    """
    retrieve necessary data from model based on given page, then update view
    """
    ...

# DB FUNCTIONS FOR USER INTERACTIVITY
# TODO: move these functions into their respective service.py programs, eventually

def change_user_email(uid: int, new_email: str):
    ...

def change_user_password(uid: int, new_hashed_password: str):
    ...

def change_project_description(pid: int, new_description: str):
    ...

def find_uid_with_username(username: str):
    ...

def change_project_status(pid: int, new_status: str):
    ...

def remove_project_member(pid: int, uid: int):
    ...

def change_role(pid: int, uid: int, new_role: str):
    ...

# PROJECT ACTION HANDLERS

def handle_project_creation(form: ProjectCreationForm):
    """
    based on given project creation form, instantiate project by calling appropriate service procedures
    """
    project_services.create_new_project(form.owner_uid, form.name, form.description)
    ...

def handle_add_project_member(pid: int, uid: int, role: str = 'VIEWER'):
    """
    handle user request to add project member to given project with given role
    """
    project_services.add_project_member(pid, uid, role)
    ...


# REACTION ACTION HANDLERS

def handle_add_reaction(pid: int, uid: int, reaction_type: str):
    """
    based on given reaction type, call appropriate service procedure to add reaction, then update view
    """
    reaction_service.add_reaction(pid, uid, reaction_type)
    ...


# USER ACTION HANDLERS

def handle_account_creation(form: AccountCreationForm):
    """
    based on given account creation form, instantiate account by calling appropriate service procedures
    """
    user_service.create_new_user(form.email, form.username, form.password_hash)
    ...
