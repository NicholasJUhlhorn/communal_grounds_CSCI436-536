# Nicholas J Uhlhorn
# November 2025

from extensions import db
from models.project import Project, ProjectMember
from sqlalchemy.orm import selectinload

# --- PROJECT CRUD ---

def create_new_project(owner_uid: int, name: str, description: str = None, status = 0.0) -> Project:
    """Creates a new project and sets the owner."""
    project = Project(
        owner_uid=owner_uid,
        name=name,
        description=description,
        visibility='PUBLISHED',
        status=status,
    )
    db.session.add(project)
    db.session.commit()

    owner_member = ProjectMember(pid=project.pid, uid=owner_uid, role='OWNER')
    db.session.add(owner_member)
    db.session.commit() 

    return project

def get_project_details(pid: int) -> Project:
    """Retrieves a single project."""
    project = db.session.get(Project, pid)
    if not project:
        raise ValueError(f"Project with ID {pid} not found.")
    return project

def get_all_published_projects() -> list[Project]:
    """Retrieves all projects with status 'PUBLISHED'."""
    return db.session.execute(db.select(Project).where(Project.visibility == 'PUBLISHED')).scalars().all()


def get_project_with_related_data(pid: int) -> Project:
    """
    Retrieves a project and eagerly loads (joins) its members and owner data 
    for efficient retrieval.
    """
    project = db.session.execute(
        db.select(Project)
        .where(Project.pid == pid)
        # Load the owner details
        .options(selectinload(Project.owner))
        # Load the member junction table objects and the Users associated with them
        .options(selectinload(Project.members).selectinload(ProjectMember.member)) 
    ).scalar_one_or_none()

    if not project:
        raise ValueError(f"Project with ID {pid} not found.")
    return project

# --- MEMBERSHIP MANAGEMENT ---

def add_project_member(pid: int, uid: int, role: str = 'VIEWER') -> ProjectMember:
    """Adds a user to a project with a specified role."""
    # Check if a user and project exists (implicitly done by FK constraints, but good practice)
    # Check for duplicates
    existing_member = db.session.execute(
        db.select(ProjectMember).where(
            (ProjectMember.pid == pid) & (ProjectMember.uid == uid)
        )
    ).scalar_one_or_none()

    if existing_member:
        raise ValueError("User is already a member of this project.")

    member = ProjectMember(pid=pid, uid=uid, role=role)
    db.session.add(member)
    db.session.commit()
    return member

def update_project_member(pid: int, uid: int, role: str) -> ProjectMember:
    """Update a user in a project with a new role, adds user if they are not present on the project already"""
    existing_member = db.session.execute(
        db.select(ProjectMember).where(
            (ProjectMember.pid == pid) & (ProjectMember.uid == uid)
        )
    ).scalar_one_or_none()

    if not existing_member:
        return add_project_member(pid, uid, role)

    existing_member.role = role
    db.session.commit()
    return existing_member

