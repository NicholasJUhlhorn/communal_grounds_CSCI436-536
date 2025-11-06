# Nicholas J Uhlhorn
# November 2025

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

