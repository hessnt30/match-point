from config import db
from uuid import uuid4
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import relationship

def get_uuid():
    return uuid4().hex

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(32), primary_key=True, unique=True, default=get_uuid)
    email = db.Column(db.String(345), unique=True, nullable=False)
    username = db.Column(db.String(150), unique=False, nullable=False)
    password = db.Column(db.Text, nullable=False)
    group_role = db.Column(db.String(32), nullable=True)
    group_points = relationship("UserGroupPoints", back_populates="user")
    events_participated = relationship("Event", secondary="event_contestants", backref="participants")


class Group(db.Model):
    __tablename__ = "groups"
    id = db.Column(db.String(32), primary_key=True, unique=True, default=get_uuid)
    group_name = db.Column(db.String(20), unique=False, nullable=False)
    password = db.Column(db.Text, nullable=False)
    owner_id = db.Column(db.String(32), db.ForeignKey('users.id'), nullable=False)
    owner = relationship("User", backref="owned_groups", foreign_keys=[owner_id])
    members = relationship("User", secondary="group_membership", backref="groups")
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    user_points = relationship("UserGroupPoints", back_populates="group")

class GroupMembership(db.Model):
    __tablename__ = "group_membership"
    user_id = db.Column(db.String(32), db.ForeignKey('users.id'), primary_key=True)
    group_id = db.Column(db.String(32), db.ForeignKey('groups.id'), primary_key=True)
    date_joined = db.Column(db.DateTime(timezone=True), default=func.now())
    points = db.Column(db.Integer, nullable=True)

class Event(db.Model):
    __tablename__ = "events"
    id = db.Column(db.String(32), primary_key=True, unique=True, default=get_uuid)
    event_type = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    group_id = db.Column(db.String(32), db.ForeignKey('groups.id'), nullable=False)
    group = relationship("Group", backref="events")
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    contestants = relationship("User", secondary="event_contestants", backref="events", cascade="all, delete")
    score_1 = db.Column(db.Integer, nullable=True)
    score_2 = db.Column(db.Integer, nullable=True)
    winners = relationship("User", secondary="winner", backref="won_events", cascade="all, delete")
    losers = relationship("User", secondary="loser", backref="lost_events", cascade="all, delete")

class EventContestants(db.Model):
    __tablename__ = "event_contestants"
    event_id = db.Column(db.String(32), db.ForeignKey('events.id'), primary_key=True)
    user_id = db.Column(db.String(32), db.ForeignKey('users.id'), primary_key=True)
    user = relationship("User", backref="contesting_events")

class Winner(db.Model):
    __tablename__ = "winner"
    event_id = db.Column(db.String(32), db.ForeignKey('events.id'), primary_key=True)
    user_id = db.Column(db.String(32), db.ForeignKey('users.id'), primary_key=True)
    event_won = relationship("Event", backref="event_winners")
    user = relationship("User", backref="won_event")

class Loser(db.Model):
    __tablename__ = "loser"
    event_id = db.Column(db.String(32), db.ForeignKey('events.id'), primary_key=True)
    user_id = db.Column(db.String(32), db.ForeignKey('users.id'), primary_key=True)
    event_lost = relationship("Event", backref="event_losers")
    user = relationship("User", backref="lost_event")

class UserGroupPoints(db.Model):
    __tablename__ = "user_group_points"
    user_id = db.Column(db.String(32), db.ForeignKey('users.id'), primary_key=True)
    group_id = db.Column(db.String(32), db.ForeignKey('groups.id'), primary_key=True)
    points = db.Column(db.Integer, nullable=True)
    user = relationship("User", back_populates="group_points")
    group = relationship("Group", back_populates="user_points")

# When adding a user to a group, also set their initial points
def add_user_to_group(user_id, group_id, points=None):
    membership = GroupMembership(user_id=user_id, group_id=group_id, points=points)
    db.session.add(membership)
    db.session.commit()
