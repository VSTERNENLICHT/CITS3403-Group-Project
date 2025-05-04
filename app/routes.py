from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm, Sign_upForm
from flask_login import current_user, login_user
import sqlalchemy as sa
from app import db
from app.models import User

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('sign_up'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.email == form.email.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('sign_up'))
    return render_template('login.html', form=form)

@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    form = Sign_upForm()
    if form.validate_on_submit():
        flash('Sign up requested for user'.format(form.email.data))
        return redirect(url_for('sign_up'))
    return render_template('sign_up.html', form=form)