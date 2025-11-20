# Nicholas J Uhlhorn
# November 2025

from extensions import db 
from sqlalchemy import func

class FriendRequest(db.Model):
    __tablename__ = 'friend_requests'
    
    # Composite Primary Key (FKs also act as PK)
    requestor_uid = db.Column(db.Integer, db.ForeignKey('users.uid'), primary_key=True)
    recipient_uid = db.Column(db.Integer, db.ForeignKey('users.uid'), primary_key=True)
    
    status = db.Column(db.String(20), nullable=False, default='PENDING') # 'PENDING', 'ACCEPTED', 'REJECTED'
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())

    # --- Relationships ---
    # Links back to the User model, using primaryjoin to distinguish sender/receiver
    requestor = db.relationship('User', primaryjoin="User.uid == FriendRequest.requestor_uid", back_populates='requested_friends')
    recipient = db.relationship('User', primaryjoin="User.uid == FriendRequest.recipient_uid", back_populates='received_requests')
    
    def __repr__(self):
        return f'<FriendRequest {self.requestor_uid} -> {self.recipient_uid} ({self.status})>'
