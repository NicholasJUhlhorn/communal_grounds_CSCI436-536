# Nicholas J Uhlhorn
# November 2025

from extensions import db
from models.user import User
from models.friend import FriendRequest
from sqlalchemy import or_

# --- WRITE OPERATIONS ---

def create_new_user(email: str, username: str, password_hash: str) -> User:
    """Creates a new user, handles validation, and commits to DB."""
    if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
        raise ValueError("Email or Username already in use.")

    new_user = User(
        email=email,
        username=username,
        hashed_password=password_hash,
    )
    db.session.add(new_user)
    db.session.commit()
    return new_user

# --- READ OPERATIONS ---

def get_user_by_id(user_id: int) -> User:
    """Retrieves a user object by UID."""
    user = db.session.get(User, user_id) 
    if not user:
        raise ValueError(f"User with ID {user_id} not found.")
    return user

def get_all_users(limit: int = 100) -> list[User]:
    """Retrieves a list of all users."""
    return db.session.execute(db.select(User).limit(limit)).scalars().all()

# --- FRIENDSHIP OPERATIONS ---

def get_friends_list(uid: int) -> list[User]:
    """
    Returns a list of User objects who have 'ACCEPTED' the friend request 
    (either sent by or received by the current user).
    """
    # 1. Find all accepted friend requests involving the user
    accepted_requests = db.session.execute(
        db.select(FriendRequest.requestor_uid, FriendRequest.recipient_uid)
        .where(
            (FriendRequest.status == 'ACCEPTED') & 
            ((FriendRequest.requestor_uid == uid) | (FriendRequest.recipient_uid == uid))
        )
    ).all()
    
    # 2. Extract unique friend UIDs
    friend_uids = set()
    for req, rec in accepted_requests:
        # Add the UID that is NOT the current user's UID
        friend_uids.add(req if req != uid else rec)
        
    # 3. Retrieve User objects for those UIDs
    if friend_uids:
        return db.session.execute(db.select(User).where(User.uid.in_(friend_uids))).scalars().all()
    
    return []

def send_friend_request(requestor_id: int, recipient_id: int) -> FriendRequest:
    """Creates a new 'PENDING' friend request."""
    if requestor_id == recipient_id:
        raise ValueError("Cannot send a friend request to yourself.")

    # Check for existing request (in either direction)
    existing_request = db.session.execute(
        db.select(FriendRequest).where(
            or_(
                (FriendRequest.requestor_uid == requestor_id) & (FriendRequest.recipient_uid == recipient_id),
                (FriendRequest.requestor_uid == recipient_id) & (FriendRequest.recipient_uid == requestor_id)
            )
        )
    ).scalar_one_or_none()

    if existing_request:
        if existing_request.status == 'ACCEPTED':
             raise ValueError("Friendship already established.")
        raise ValueError(f"Friend request already exists with status: {existing_request.status}")

    new_request = FriendRequest(
        requestor_uid=requestor_id,
        recipient_uid=recipient_id,
        status='PENDING'
    )
    db.session.add(new_request)
    db.session.commit()
    return new_request

def accept_friend_request(requestor_id: int, recipient_id: int) -> FriendRequest:
    """Updates a PENDING request to ACCEPTED."""
    request = db.session.execute(
        db.select(FriendRequest).where(
            (FriendRequest.requestor_uid == requestor_id) & (FriendRequest.recipient_uid == recipient_id)
        )
    ).scalar_one_or_none()

    if not request:
        raise ValueError("Pending friend request not found.")
    
    request.status = 'ACCEPTED'
    db.session.commit()
    return request
