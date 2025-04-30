from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wam = db.Column(db.Float, nullable=False)
    gpa = db.Column(db.Float, nullable=False)
