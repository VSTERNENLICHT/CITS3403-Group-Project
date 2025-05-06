from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import pytz

from flask_login import UserMixin   # TESTING ONLY

db = SQLAlchemy()
AWST = pytz.timezone('Australia/Perth')  # Define timezone

# TESTING ONLY
class User(db.Model, UserMixin):
    id = db.Column(db.String(120), primary_key=True)
# TESTING ONLY END

class SharedGraph(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(120), db.ForeignKey('user.id'), nullable=False)
    shared_with_id = db.Column(db.String(120), db.ForeignKey('user.id'), nullable=False)

    token = db.Column(db.String(64), unique=True, nullable=False)
    include_marks = db.Column(db.Boolean, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(AWST))  # Apply AWST timezone

class Goal(db.Model):
    user_id = db.Column(db.String(120), db.ForeignKey('user.id'), primary_key=True)
    wam = db.Column(db.Float, nullable=False)
    gpa = db.Column(db.Float, nullable=False)
