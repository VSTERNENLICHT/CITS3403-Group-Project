from flask import Flask, request, jsonify, render_template, send_file, abort, flash, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, current_user, login_required, UserMixin
from flask_migrate import Migrate
from forms import LoginForm, Sign_upForm
from models import db, Goal, User, SharedGraph, GPA, WAM
import matplotlib.pyplot as plt
import secrets
import json
import sqlalchemy as sa
import email_validator

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///goals.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'dev-secret-key'  # Constant key for development  # Secret key for session management

# --- Initialize extensions ---
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

migrate = Migrate(app, db)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# --- Helper to generate a secure token ---
def generate_token():
    return secrets.token_urlsafe(32)

# --- Routes ---
# Main Page
@app.route('/')
def home():
    return render_template('mainpage.html')

# Goal Setting Page
@app.route('/set-goal')
def set_goal():
    return render_template('set-goal.html')

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('calculate'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.email == form.email.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('calculator'))
    return render_template('login.html', form=form)

# Logout
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

# Sign Up Page
@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if current_user.is_authenticated:
        return redirect(url_for('calculator'))
    form = Sign_upForm()
    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('sign_up.html', form=form)

# Goal Setting Page
@app.route('/save-goal', methods=['POST'])
@login_required
def save_goal():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid request"}), 400
    try:
        wam = float(data['wam'])
        gpa = float(data['gpa'])
        user_id = data.get("user_id")

        # Ensure the user_id matches the logged-in user
        if int(user_id) != current_user.id:
            return jsonify({"message": "Unauthorized access"}), 403

        # Enforce constraints
        if not (0 <= wam <= 100):
            return jsonify({"message": "WAM must be between 0 and 100"}), 400
        if not (0 <= gpa <= 7):
            return jsonify({"message": "GPA must be between 0 and 7"}), 400
        if round(gpa, 1) != gpa:
            return jsonify({"message": "GPA must be rounded to 1 decimal place"}), 400

        # Check if goal already exists for current user
        existing_goal = Goal.query.filter_by(user_id=current_user.id).first()

        if existing_goal:
            # Update existing goal
            wam = data.get('wam')
            gpa = data.get('gpa')
            existing_goal.wam = wam
            existing_goal.gpa = gpa
            db.session.commit()
            return jsonify({"message": "Your goals have been updated!"}), 200
        else:
            # Create new goal
            new_goal = Goal(user_id=current_user.id, wam=wam, gpa=gpa)
            db.session.add(new_goal)
            db.session.commit()
            return jsonify({"message": "Your goals have been saved!"}), 200

    except (KeyError, ValueError):
        return jsonify({"message": "Invalid input format."}), 400
        
@app.route('/calculator')
def calculator():
    return render_template('test.html')  # or whatever your homepage is

@app.route('/calculate', methods=['POST'])
def calculate():
    raw_data = request.form['data']
    data = json.loads(raw_data)

    unit_scores = []
    for unit in data['Previous Units']:
        unit_scores.append(unit[2])

    for unit in data:
        if unit != 'Previous Units':
            score = 0
            for assessment in data[unit]["assessments"]:
                # weighting = [1], max = [2], marks = [3]
                score += assessment[1] * (assessment[3] / assessment[2])
            unit_scores.append(score)

    unit_count = len(unit_scores)
    total_scores = sum(unit_scores)
    total_gpa = 0
    for score in unit_scores:
        if score >= 80:
            total_gpa += 7.0
        elif score >= 70:
            total_gpa += 6.0
        elif score >= 60:
            total_gpa += 5.0
        elif score >= 50:
            total_gpa += 4.0
        else:
            total_gpa += 0.0

    gpa = total_gpa / unit_count
    wam = total_scores / unit_count

    return render_template('resultspage.html', gpa=gpa, wam=wam)

@app.route('/results')
@login_required
def get_results_data():
    gpa = GPA.query.filter_by(user_id=current_user.id).first()
    wam = WAM.query.filter_by(user_id=current_user.id).first()
    goal = Goal.query.filter_by(user_id=current_user.id).first()

    if not gpa or not wam:
        return jsonify({"error": "GPA or WAM data missing"}), 404

    response = {
        "gpa": round(gpa.final_gpa, 2),
        "wam": round(wam.final_wam, 2),
        "desired_gpa": round(goal.gpa, 2) if goal else None,
        "desired_wam": round(goal.wam, 2) if goal else None,
        "gpa_semesters": {
            "sem1_yr1": gpa.year_1_semester_1,
            "sem2_yr1": gpa.year_1_semester_2,
            "sem1_yr2": gpa.year_2_semester_1,
            "sem2_yr2": gpa.year_2_semester_2
        },
        "wam_semesters": {
            "sem1_yr1": wam.year_1_semester_1,
            "sem2_yr1": wam.year_1_semester_2,
            "sem1_yr2": wam.year_2_semester_1,
            "sem2_yr2": wam.year_2_semester_2
        }
    }

    return jsonify(response)

# Share Graph Page
@app.route('/share')
def share_page():
    return render_template('SharePage.html')

@app.route('/my-shared-graphs') # Inbox
@login_required
def my_shared_graphs():
    received = SharedGraph.query.filter_by(shared_with_id=current_user.id, is_active=True).all()
    sent = SharedGraph.query.filter_by(user_id=current_user.id, is_active=True).all()

    received_graphs = [{
        'sharer': User.query.get(s.user_id).id,
        'token': s.token,
        'include_marks': s.include_marks,
        'timestamp': s.timestamp.strftime('%Y-%m-%d %H:%M')
    } for s in received]

    sent_graphs = [{
        'recipient': User.query.get(s.shared_with_id).id,
        'token': s.token,
        'include_marks': s.include_marks,
        'is_active': s.is_active,
        'timestamp': s.timestamp.strftime('%Y-%m-%d %H:%M')
    } for s in sent]

    return render_template("my_shared_graphs.html",
                           shared_with_me=received_graphs,
                           shared_by_me=sent_graphs)


@app.route('/share-graph', methods=['POST'])    # Share graph
@login_required
def share_graph():
    include_marks = request.form.get('shareMarks') == 'yes'
    recipient_username = request.form.get('sharedto')

    if not recipient_username:
        return "Recipient username is required", 400

    recipient = User.query.filter_by(id=recipient_username).first()
    if not recipient:
        return "Recipient user not found", 404
    
    if recipient.id == current_user.id:
        return render_template('SharePage.html', error="You cannot share with yourself.")

    token = generate_token()

    shared = SharedGraph(
        token=token,
        include_marks=include_marks,
        is_active=True,
        user_id=current_user.id,
        shared_with_id=recipient.id
    )
    db.session.add(shared)
    db.session.commit()

    share_link = request.host_url.rstrip('/') + '/shared/' + token
    return render_template('SharePage.html', share_link=share_link)

@app.route('/shared/<token>')   # View shared graph
@login_required
def view_shared_graph(token):
    shared = SharedGraph.query.filter_by(token=token, is_active=True).first()

    if not shared or shared.shared_with_id != current_user.id:
        abort(403, description="You are not authorized to view this shared graph.")

    goals = Goal.query.filter_by(user_id=shared.user_id).all()
    if not goals:
        return "No data available for this user.", 404

    semesters = list(range(1, len(goals) + 1))
    wam_values = [g.wam for g in goals]
    gpa_values = [g.gpa for g in goals]

    sharer = User.query.get(shared.user_id)

    return render_template('view_shared_graph.html', 
                           semesters=semesters,
                           wam_values=wam_values,
                           gpa_values=gpa_values, 
                           include_marks=shared.include_marks,
                           sharer_username=sharer.id)

@app.route('/revoke/<token>', methods=['POST'])
@login_required
def revoke_graph(token):
    shared = SharedGraph.query.filter_by(token=token, user_id=current_user.id).first()
    if shared:
        shared.is_active = False
        db.session.commit()
        return jsonify({'status': 'revoked'})
    return jsonify({'status': 'not found'}), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
