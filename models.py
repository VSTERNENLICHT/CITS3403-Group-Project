from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager
import pytz

db = SQLAlchemy()
AWST = pytz.timezone('Australia/Perth')  # Define timezone

class User(UserMixin, db.Model):
  id: so.Mapped[int] = so.mapped_column(primary_key=True)
  email: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
  password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

  def set_password(self, password):
    self.password_hash = generate_password_hash(password)

  def check_password(self, password):
    return check_password_hash(self.password_hash, password)

  def __repr__(self):
    return '<User {}>'.format(self.username)

class SharedGraph(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    shared_with_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    token = db.Column(db.String(64), unique=True, nullable=False)
    include_marks = db.Column(db.Boolean, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(AWST))  # Apply AWST timezone

class Goal(db.Model):
    user_id = db.Column(db.String(120), db.ForeignKey('user.id'), primary_key=True)
    wam = db.Column(db.Float, nullable=False)
    gpa = db.Column(db.Float, nullable=False)

class GPA(db.Model):
    user_id = db.Column(db.String(120), db.ForeignKey('user.id'), nullable=False, primary_key=True)
    final_gpa = db.Column(db.Float, nullable=False)
    year_1_semester_1 = db.Column(db.Float, nullable=False)
    year_1_semester_2 = db.Column(db.Float, nullable=False)
    year_2_semester_1 = db.Column(db.Float, nullable=False)
    year_2_semester_2 = db.Column(db.Float, nullable=False)
    year_3_semester_1 = db.Column(db.Float, nullable=False)
    year_3_semester_2 = db.Column(db.Float, nullable=False)
    year_4_semester_1 = db.Column(db.Float, nullable=False)
    year_4_semester_2 = db.Column(db.Float, nullable=False)
    year_5_semester_1 = db.Column(db.Float, nullable=False)
    year_5_semester_2 = db.Column(db.Float, nullable=False)

class WAM(db.Model):
    user_id = db.Column(db.String(120), db.ForeignKey('user.id'), nullable=False, primary_key=True)
    final_wam = db.Column(db.Float, nullable=False)
    year_1_semester_1 = db.Column(db.Float, nullable=False)
    year_1_semester_2 = db.Column(db.Float, nullable=False)
    year_2_semester_1 = db.Column(db.Float, nullable=False)
    year_2_semester_2 = db.Column(db.Float, nullable=False)
    year_3_semester_1 = db.Column(db.Float, nullable=False)
    year_3_semester_2 = db.Column(db.Float, nullable=False)
    year_4_semester_1 = db.Column(db.Float, nullable=False)
    year_4_semester_2 = db.Column(db.Float, nullable=False)
    year_5_semester_1 = db.Column(db.Float, nullable=False)
    year_5_semester_2 = db.Column(db.Float, nullable=False)