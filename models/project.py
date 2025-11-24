# Nicholas J Uhlhorn
# November 2025

from extensions import db 
from sqlalchemy import func

class Project(db.Model):
    __tablename__ = 'projects'
    pid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default='DRAFT')
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    
    # ForeignKey for the owner (Many-to-One)
    owner_uid = db.Column(db.Integer, db.ForeignKey('users.uid'), nullable=False)

    # --- Relationships ---
    # Many-to-One: Projects to Owner User
    owner = db.relationship('User', back_populates='owned_projects')
    
    # Many-to-Many: Projects to Members (via ProjectMember)
    members = db.relationship('ProjectMember', back_populates='project', lazy=True, cascade="all, delete-orphan")

    # One-to-Many: Projects to Reactions
    reactions = db.relationship('Reaction', back_populates='project', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Project {self.name}>'

class ProjectMember(db.Model):
    __tablename__ = 'project_members'
    
    # Composite Primary Key (FKs also act as PK)
    pid = db.Column(db.Integer, db.ForeignKey('projects.pid'), primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('users.uid'), primary_key=True)
    
    role = db.Column(db.String(20), nullable=False, default='VIEWER') # e.g., 'EDITOR', 'VIEWER'

    # --- Relationships ---
    # Bi-directional relationships to access the related objects
    project = db.relationship('Project', back_populates='members')
    member = db.relationship('User') # Relationship to the user object
    
    def __repr__(self):
        return f'<ProjectMember PID:{self.pid} UID:{self.uid} Role:{self.role}>'
