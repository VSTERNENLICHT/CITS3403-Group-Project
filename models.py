from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import pytz

from flask_login import UserMixin   # TESTING ONLY

db = SQLAlchemy()
AWST = pytz.timezone('Australia/Perth')  # Define timezone

# TESTING ONLY
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
# TESTING ONLY END

class SharedGraph(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(64), unique=True, nullable=False)
    include_marks = db.Column(db.Boolean, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(AWST))  # Apply AWST timezone

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    shared_with_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wam = db.Column(db.Float, nullable=False)
    gpa = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
