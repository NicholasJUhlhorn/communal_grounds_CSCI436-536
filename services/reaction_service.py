# Nicholas J Uhlhorn
# November 2025

from extensions import db
from models.reaction import Reaction
from sqlalchemy import func

# --- READ/CALCULATION OPERATIONS ---

def get_reaction_count_by_type(pid: int, reaction_type: str) -> int:
    """
    Returns the count of a specific reaction type for a given project.
    """
    count = db.session.execute(
        db.select(func.count(Reaction.rid))
        .where(
            (Reaction.pid == pid) & 
            (Reaction.type == reaction_type)
        )
    ).scalar_one() 
    
    return count

def get_total_reactions(pid: int) -> int:
    """Returns the total number of all reactions on a project."""
    count = db.session.execute(
        db.select(func.count(Reaction.rid))
        .where(Reaction.pid == pid)
    ).scalar_one()
    
    return count

# --- WRITE OPERATIONS ---

def add_reaction(pid: int, uid: int, reaction_type: str) -> Reaction:
    """
    Adds a reaction or updates an existing one if the user has already reacted.
    The unique constraint on (pid, uid) prevents duplicates.
    """
    
    # Check if a reaction already exists (due to the unique constraint)
    existing_reaction = db.session.execute(
        db.select(Reaction).where(
            (Reaction.pid == pid) & 
            (Reaction.uid == uid)
        )
    ).scalar_one_or_none()

    if existing_reaction:
        # Update the existing reaction type if different
        if existing_reaction.type != reaction_type:
            existing_reaction.type = reaction_type
            db.session.commit()
        return existing_reaction

    # If no reaction exists, create a new one
    new_reaction = Reaction(
        pid=pid,
        uid=uid,
        type=reaction_type
    )
    db.session.add(new_reaction)
    db.session.commit()
    return new_reaction
