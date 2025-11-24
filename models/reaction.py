# Nicholas J Uhlhorn
# November 2025

from extensions import db 
from sqlalchemy import func

class Reaction(db.Model):
    __tablename__ = 'reactions'
    rid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(50), nullable=False) # e.g., 'UPVOTE', 'LIKE'
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())

    # Foreign Keys
    pid = db.Column(db.Integer, db.ForeignKey('projects.pid'), nullable=False)
    uid = db.Column(db.Integer, db.ForeignKey('users.uid'), nullable=False)

    # --- Relationships ---
    project = db.relationship('Project', back_populates='reactions')
    user = db.relationship('User') # No need for back_populates unless you frequently list all reactions by a user

    # Enforce one reaction per user per project
    __table_args__ = (
        db.UniqueConstraint('pid', 'uid', name='_user_project_uc'),
    )

    def __repr__(self):
        return f'<Reaction {self.type} on Project:{self.pid} by User:{self.uid}>'

