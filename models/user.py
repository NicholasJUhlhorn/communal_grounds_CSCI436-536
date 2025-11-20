# Nicholas J Uhlhorn
# November 2025

from extensions import db 
from sqlalchemy import func

class User(db.Model):
    __tablename__ = 'users'
    uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    hashed_password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())

    # --- Relationships ---
    # 1. One-to-Many: User to Projects (Projects owned by the user)
    # 'owner' in Project will point back to this User object
    owned_projects = db.relationship('Project', back_populates='owner', lazy=True)

    # 2. Many-to-Many (Self-Referential): User to Friend_Requests
    # We define 'requested_friends' (requests sent by this user) 
    # and 'received_requests' (requests received by this user).
    requested_friends = db.relationship(
        'FriendRequest', 
        primaryjoin="User.uid == FriendRequest.requestor_uid", 
        back_populates='requestor', 
        lazy=True,
        cascade="all, delete-orphan"
    )

    received_requests = db.relationship(
        'FriendRequest',
        primaryjoin="User.uid == FriendRequest.recipient_uid",
        back_populates='recipient',
        lazy=True,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f'<User {self.username}>'
