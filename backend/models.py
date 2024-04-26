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
    points = db.Column(db.Integer, nullable=True)

class Group(db.Model):
    __tablename__ = "groups"
    id = db.Column(db.String(32), primary_key=True, unique=True, default=get_uuid)
    group_name = db.Column(db.String(20), unique=False, nullable=False)
    password = db.Column(db.Text, nullable=False)
    owner_id = db.Column(db.String(32), db.ForeignKey('users.id'), nullable=False)
    owner = relationship("User", backref="owned_groups", foreign_keys=[owner_id])
    members = relationship("User", secondary="group_membership", backref="groups")
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())

class GroupMembership(db.Model):
    __tablename__ = "group_membership"
    user_id = db.Column(db.String(32), db.ForeignKey('users.id'), primary_key=True)
    group_id = db.Column(db.String(32), db.ForeignKey('groups.id'), primary_key=True)
    date_joined = db.Column(db.DateTime(timezone=True), default=func.now())

class Event(db.Model):
    __tablename__ = "events"
    id = db.Column(db.String(32), primary_key=True, unique=True, default=get_uuid)
    event_type = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    group_id = db.Column(db.String(32), db.ForeignKey('groups.id'), nullable=False)
    group = relationship("Group", backref="events")
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    contestants = relationship("User", secondary="event_contestants", backref="events")
    score = db.Column(db.Integer, nullable=True)
    winner = relationship("User", secondary="winner", backref="events")
    loser = relationship("User", secondary="loser", backref="events")

class EventContestants(db.Model):
    __tablename__ = "event_contestants"
    event_id = db.Column(db.String(32), db.ForeignKey('events.id'), primary_key=True)
    user_id = db.Column(db.String(32), db.ForeignKey('users.id'), primary_key=True)
    user = relationship("User", backref="contesting_events")

