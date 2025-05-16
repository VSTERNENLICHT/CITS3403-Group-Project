from flask import Flask, request, jsonify, render_template, abort, flash, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask_migrate import Migrate
from werkzeug.exceptions import HTTPException
from forms import LoginForm, Sign_upForm, CalcForm
from models import db, Goal, User, SharedGraph, GPA, WAM, Calculations
import matplotlib.pyplot as plt
import secrets
import json
import sqlalchemy as sa
import email_validator
from urllib.parse import urlparse, urljoin
import os

login_manager = LoginManager()

def create_app(config=None):
    app = Flask(__name__)
    app.secret_key = 'dev-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///goals.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    if config:
        app.config.update(config)

    db.init_app(app)
    Migrate(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    # register your routes
    with app.app_context():
        from routes import register_routes  # move your routes to a separate file
        register_routes(app)
        db.create_all()

    return app
