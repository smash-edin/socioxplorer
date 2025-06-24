from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from uuid import uuid4
from datetime import datetime
from utils import create_logger, print_this
logger = create_logger(f"DB Model", file=f"db_models")

db = SQLAlchemy()

def get_uuid():
    return uuid4().hex

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(32), primary_key = True, unique=True, default=get_uuid)
    username = db.Column(db.String(345), unique=True)
    password = db.Column(db.Text, nullable=False)
    roles = db.Column(db.Text, nullable=False)
    refreshToken = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, server_default='true')
    
    communities = db.relationship("SNAUsersCommunitiesMap", back_populates="user", cascade="all, delete")
    searches = db.relationship("Search", back_populates="user", cascade="all, delete")

    
    @property
    def rolenames(self):
        try:
            return self.roles.split(',')
        except Exception:
            return []

    @classmethod
    def lookup(cls, username):
        return cls.query.filter_by(username=username).one_or_none()

    @classmethod
    def identify(cls, id):
        return cls.query.get(id)

    @property
    def identity(self):
        return self.id

    def is_valid(self):
        return self.is_active
    
    def getUsername(self):
        return self.username
    
    def getUsersCommunities(self):
        return self.communities
    
class Search(db.Model):
    """
    This class is used to store the search queries of the users
    """
    __tablename__ = "search"
    id = db.Column(db.String(32), primary_key =  True, unique=True, default=get_uuid)
    user_id = db.Column(db.String(32), ForeignKey('users.id'), nullable=False)
    token = db.Column(db.Text, unique=False, nullable=False)
    reportName = db.Column(db.Text, unique=False, nullable=False)
    creationTime = db.Column(db.Text, unique=False, nullable=True)
    dataPath = db.Column(db.Text, unique=False, nullable=True)
    
    user = db.relationship("User")
    
    @classmethod
    def find_by_username(cls, username):
        return cls.query.join(User).filter(User.username == username).all()


class SNAUsersCommunitiesMap(db.Model):
    """
    This class is used to store the communities of the users
    """
    __tablename__ = "snauserscommunitiesmap"
    id = db.Column(db.String(32), unique=True, default=get_uuid)
    user_id = db.Column(db.String(32), ForeignKey('users.id'), nullable=False)
    snaCommunityType = db.Column(db.String(345), nullable=False)
    snaCommunityKey = db.Column(db.String(345), nullable=False)
    snaCommunityValue = db.Column(db.String(345), nullable=False)
    __table_args__ = (PrimaryKeyConstraint(user_id, snaCommunityType,snaCommunityKey), {})
    
    user = db.relationship("User", back_populates="communities")
    
    @classmethod
    def find_by_username_with_interaction(cls, username, interactionType):
        """
        This method is used to retrieve the communities of a user.
        """
        return (
            db.session.query(cls)
            .join(User)
            .filter(User.username == username, cls.snaCommunityType == interactionType)
            .all()
        )