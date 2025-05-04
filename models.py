from flask_sqlalchemy import SQLAlchemy

from flask_login import UserMixin   #TESTING ONLY

db = SQLAlchemy()

#TESTING ONLY
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
#TESTING ONLY END

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(120), unique=True, nullable=False)

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wam = db.Column(db.Float, nullable=False)
    gpa = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class SharedGraph(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(64), unique=True, nullable=False)
    include_marks = db.Column(db.Boolean, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Who is sharing
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # Who it's shared with (must also be a registered user)
    shared_with_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

