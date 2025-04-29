from flask import render_template
from app import app
from app.forms import LoginForm, Sign_upForm

@app.route('/login')
def login():
    form = LoginForm()
    return render_template('login.html', form=form)

@app.route('/sign_up')
def sign_up():
    form = Sign_upForm()
    return render_template('sign_up.html', form=form)