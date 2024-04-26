from config import app, db
from flask import Flask, request, jsonify, session
from flask_bcrypt import Bcrypt
from flask_session import Session
from flask_cors import cross_origin
from models import User, Group, Event
from datetime import datetime
import urllib.request
import json

bcrypt = Bcrypt(app)
server_session = Session(app)


# start authorization ---------------------------------------------------------

@app.route("/register", methods=["POST"])
def register_user():
     email = request.json["email"]
     username = request.json["username"]
     password = request.json["password"]

     user_exists = User.query.filter_by(email=email).first() is not None

     if user_exists:
          return jsonify({"error" : "User already exists with that email"}), 409
     
     hashed_password = bcrypt.generate_password_hash(password)
     new_user = User(email=email, username=username, password=hashed_password, group_role=None, points=None)

     db.session.add(new_user)
     db.session.commit()

     session["user_id"] = new_user.id

     return jsonify({
          "id": new_user.id,
          "username" : new_user.username,
          "email": new_user.email
     })

@app.route("/login", methods=["POST"])
def login():
     email = request.json["email"]
     password = request.json["password"]

     user = User.query.filter_by(email=email).first()

     if user is None:
        return jsonify({"error": "Unauthorized"}), 401
     
     if not bcrypt.check_password_hash(user.password, password):
          return jsonify({"error": "Unauthorized"}), 401
     
     session["user_id"] = user.id
     
     return jsonify({
          "id" : user.id,
          "email" : user.email
     })

@app.route("/logout", methods=["POST"])
def logout():
     session.pop("user_id")
     return "200"

# end authorization ---------------------------------------------------------

# start user ---------------------------------------------------------

@app.route("/@me")
def get_current_user():
     user_id = session.get("user_id")

     if not user_id:
          return jsonify({"error": "Unauthorized"}), 401
     
     user = User.query.filter_by(id=user_id).first()
          
     return jsonify({
          "id" : user.id,
          "email" : user.email
     })

@app.route("/points/<username>")
def get_user_points(username):
     user = User.query.filter_by(username=username).first()

     if user is None:
        return jsonify({"error": "Unauthorized"}), 401
     
     return jsonify({
          "username" : user.username,
          "points" : user.points
     })

# end user ---------------------------------------------------------

# start group ---------------------------------------------------------

@app.route("/create-group", methods=["POST"])
def create_group():
     # get current user
     user_id = session.get("user_id")

     if not user_id:
          return jsonify({"error": "Unauthorized"}), 401
     
     current_user = User.query.get(user_id)

     # set role of current user
     current_user.group_role = "owner"

     # make group
     group_name = request.json["groupName"]
     password = request.json["password"]
     
     hashed_password = bcrypt.generate_password_hash(password)
     new_group = Group(group_name=group_name, password=hashed_password, owner=current_user)

     # Add user to the group
     new_group.members.append(current_user)

     db.session.add(new_group)
     db.session.commit()

     return jsonify({
          "id": new_group.id,
          "groupName": new_group.group_name,
          "owner" : new_group.owner.username,
          "members": [member.username for member in new_group.members]
     })

@app.route("/join-group", methods=["POST"])
def join_group():
     group_name = request.json["groupName"]
     password = request.json["password"]

     # get group
     group = Group.query.filter_by(group_name=group_name).first()

     if not group:
          return jsonify({"error": "Group does not exist"}), 401
     
     if not bcrypt.check_password_hash(group.password, password):
          return jsonify({"error": "Incorrect password"}), 401

     # get current user
     user_id = session.get("user_id")

     if not user_id:
          return jsonify({"error": "Unauthorized"}), 401
     
     current_user = User.query.get(user_id)

     # Add user to the group
     if current_user not in group.members:
          group.members.append(current_user)

     # set role of current user
     current_user.group_role = "member"

     db.session.commit()

     return jsonify({
          "groupName": group.group_name,
          "owner" : group.owner.username,
          "currentUser" : current_user.username,
          "members": [member.username for member in group.members]
     })

@app.route("/leave-group", methods=["POST"])
def leave_group():
     group_name = request.json["groupName"]

     # get group
     group = Group.query.filter_by(group_name=group_name).first()

     if not group:
          return jsonify({"error": "Group does not exist"}), 401

     # get current user
     user_id = session.get("user_id")

     if not user_id:
          return jsonify({"error": "Unauthorized"}), 401
     
     current_user = User.query.get(user_id)

     # Add user to the group
     if current_user in group.members:
          group.members.remove(current_user)
     
     if current_user.username == group.owner.username:
          if group.members:
               group.owner = group.members[0]

     if len(group.members) == 0:
          db.session.delete(group)
          return jsonify({
               "groupStatus" : "Group deleted"
          })

     # set role of current user
     current_user.group_role = ""

     db.session.commit()

     return jsonify({
          "groupName": group.group_name,
          "owner" : group.owner.username,
          "currentUser" : current_user.username,
          "members": [member.username for member in group.members]
     })

@app.route("/delete-group", methods=["POST"])
def delete_group():
     group_name = request.json["groupName"]
     password = request.json["password"]

     # get group
     group = Group.query.filter_by(group_name=group_name).first()

     if not group:
          return jsonify({"error": "Group does not exist"}), 401
     
     if not bcrypt.check_password_hash(group.password, password):
          return jsonify({"error": "Incorrect password"}), 401

     # get current user
     user_id = session.get("user_id")

     if not user_id:
          return jsonify({"error": "Unauthorized"}), 401
     
     current_user = User.query.get(user_id)

     # reset roles of members
     if current_user.username == group.owner.username:
          # set role of each member to blank
          for member in group.members:
               member.group_role = ""
          # set role of current user
          current_user.group_role = ""
          db.session.delete(group)
          db.session.commit()
          return jsonify({
               "groupStatus" : "Group deleted"
          })

     return jsonify({
          "error" : "Unauthorized access",
          "groupName": group.group_name,
          "owner" : group.owner.username
     }), 401

@app.route("/all-events")
def get_all_events():
     group_name = request.json["groupName"]

     # get group
     group = Group.query.filter_by(group_name=group_name).first()

     if not group:
          return jsonify({
               "error" : "group does not exist"
          }), 401
     
     return jsonify({
          "groupName" : group_name,
          "events" : [event.name for event in group.events]
     })

# end user ---------------------------------------------------------

# start event ---------------------------------------------------------

@app.route("/create-event", methods=["POST"])
def create_event():
     # get current user
     user_id = session.get("user_id")

     if not user_id:
          return jsonify({"error": "Unauthorized"}), 401

     group = Group.query.filter_by(owner_id=user_id).first()

     if group is None:
          return jsonify({ "error" : "Unauthorized"}), 401

     # make event
     event_name = request.json["name"]
     event_type = request.json["type"]
     date_str = request.json["date"]
     date = datetime.strptime(date_str, "%m/%d/%Y").date()
     time_str = request.json["time"]
     time = datetime.strptime(time_str, "%H:%M:%S").time()
     contestants = []  # Initialize contestants list
     winners = []  # Initialize winners list
     losers = []  # Initialize losers list

     for contestant in request.json["contestants"]:
          curr_contestant = User.query.get(contestant)
          if curr_contestant in group.members:
               contestants.append(curr_contestant)

     new_event = Event(name=event_name, event_type=event_type, group=group, date=date, 
                       time=time, contestants=contestants, score_1=None, score_2=None, winners=winners, losers=losers)

     db.session.add(new_event)
     db.session.commit()

     return jsonify({
          "eventName" : event_name,
          "type" : event_type,
          "group" : new_event.group.group_name,
          "date" : str(date),
          "time" : str(time),
          "contestants" : [contestant.username for contestant in new_event.contestants],
          # "scores": {"score1": score1, "score2": score2}
          # "winners" : [winner.username for winner in new_event.winners],
          # "losers" : [loser.username for loser in new_event.losers]     
     })

# end event ---------------------------------------------------------

# run the app
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)