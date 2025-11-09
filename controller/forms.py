# class containing information in an account creation form
class AccountCreationForm:
    '''
    FIELDS
    email: str
    username: str
    password_hash: str
    '''
    def __init__(self, email: str, username: str, password_hash: str):
        self.email = email
        self.username = username
        self.password_hash = password_hash

# class containing information in a project creation form
class ProjectCreationForm:
    '''
    FIELDS
    owner_uid: int
    name: str
    description: str
    '''
    def __init__(self, owner_uid: int, name: str, description: str = None):
        self.owner_uid = owner_uid
        self.name = name
        self.description = description
