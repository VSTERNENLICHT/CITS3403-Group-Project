from flask import Flask, request, jsonify, render_template, abort, flash, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask_migrate import Migrate
from forms import LoginForm, Sign_upForm, CalcForm
from models import db, Goal, User, SharedGraph, GPA, WAM, Calculations
import matplotlib.pyplot as plt
import secrets
import json
import sqlalchemy as sa
import email_validator
from urllib.parse import urlparse, urljoin
import os

app = Flask(__name__)

# Use in-memory DB if running tests
if os.environ.get("FLASK_ENV") == "testing":
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
else:
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

# --- Helper to validate URLs ---
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

# --- Routes ---
# Main Page
@app.route('/')
def home():
    return render_template('mainpage.html')

# Goal Setting Page
@app.route('/set-goal')
@login_required
def set_goal():
    return render_template('set-goal.html')

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('calculator'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.email == form.email.data))
        login_user(user)
        next_page = request.args.get('next')

        if next_page and is_safe_url(next_page):   # Redirect to the next page if it exists (e.g., if the user was trying to access set-goal page without logging in)
            return redirect(next_page)
        else:
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
        return redirect(url_for('home'))
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
        
@app.route('/calculator', methods=['GET', 'POST'])
@login_required
def calculator():
    form = CalcForm()

    if request.method == 'POST':
        form = CalcForm(formdata=request.form)
        # Step 4: Validate
        if form.validate():
            # Before calculating and validating value sums, save the form data to the database
            form_input = json.dumps(form.data)
            new_user_data = Calculations(user_id=current_user.id, form_input=form_input)
            db.session.merge(new_user_data)
            db.session.commit()
            data_validation = True

            unit_scores = {('1', '1'): [], ('1', '2'): [], ('2', '1'): [], ('2', '2'): [], ('3', '1'): [], ('3', '2'): [], ('4', '1'): [], ('4', '2'): [], ('5', '1'): [], ('5', '2'): []}
            gpa_sem = {}
            wam_sem = {}
            cumulative_count = 0
            cumulative_scores = 0
            cumulative_gpa = 0
            for unit in form.previous_units_tab[0].previous_units:
                #print(f"\nUnit: {unit.unit.data}, Semester: {unit.semester.data}, Year: {unit.year.data}")
                if len(form.previous_units_tab[0].previous_units) == 1 and unit.unit.data == '' and unit.semester.data == '' and unit.year.data == '' and unit.mark.data == '':
                    # If the first unit is empty, we can skip it
                    break
                if unit.mark.data > 100 or unit.mark.data < 0:
                    data_validation = False
                    flash(f"Your mark for {unit.unit.data} needs to be between 0 to 100.")
                score = unit.mark.data
                unit_scores[(unit.year.data[-1], unit.semester.data[-1])].append(score)
                
            for unit in form.units:
                #print(f"\nUnit: {unit.unit.data}, Semester: {unit.semester.data}, Year: {unit.year.data}")
                score = 0
                weighting = 0
                for assessment in unit.assessments:
                    #print(f"  - {assessment.atype.data}: {assessment.student_mark.data}/{assessment.max_mark.data} ({assessment.weight.data}%)")
                    if assessment.student_mark.data > assessment.max_mark.data:
                        data_validation = False
                        flash(f"Your mark for {assessment.atype.data} in {unit.unit.data} exceeds the maximum mark.")
                    if assessment.max_mark.data <= 0:
                        data_validation = False
                        flash(f"The maximum mark for {assessment.atype.data} in {unit.unit.data} needs to be greater than 0.")
                    if assessment.student_mark.data < 0:
                        data_validation = False
                        flash(f"Your mark for {assessment.atype.data} in {unit.unit.data} needs to be greater than or equal to 0.")
                    if assessment.weight.data < 0 or assessment.weight.data > 100:
                        data_validation = False
                        flash(f"The weight for {assessment.atype.data} in {unit.unit.data} needs to be between 0% to 100%.")
                    score += assessment.weight.data * (assessment.student_mark.data / assessment.max_mark.data)
                    weighting += assessment.weight.data
                if weighting != 100:
                    data_validation = False
                    flash(f"The total weightings for {unit.unit.data} do not add up to 100%.")
                    
                unit_scores[(unit.year.data[-1], unit.semester.data[-1])].append(score)
                
            if not data_validation:
                return render_template('calculator.html', form=form, form_data=form.data)
            #unit_scores = dict(sorted(unit_scores.items(), key=lambda x: (x[0][1], x[0][0])))
            for sem in unit_scores:
                if len(unit_scores[sem]) == 0:
                    wam_sem[sem] = -1
                    gpa_sem[sem] = -1
                    continue
                cumulative_scores += sum(unit_scores[sem])
                cumulative_count += len(unit_scores[sem])
                cumulative_gpa += sum([7.0 if score >= 80 else 6.0 if score >= 70 else 5.0 if score >= 60 else 4.0 if score >= 50 else 0.0 for score in unit_scores[sem]])
                wam_sem[sem] = round(cumulative_scores / cumulative_count, 1)
                gpa_sem[sem] = cumulative_gpa / cumulative_count
            gpa = round(cumulative_gpa / cumulative_count, 1)
            wam = cumulative_scores / cumulative_count
            
            existing_gpa = GPA.query.filter_by(user_id=current_user.id).first()
            if existing_gpa:
                existing_gpa.final_gpa = gpa
                existing_gpa.year_1_semester_1 = gpa_sem[('1', '1')]
                existing_gpa.year_1_semester_2 = gpa_sem[('1', '2')]
                existing_gpa.year_2_semester_1 = gpa_sem[('2', '1')]
                existing_gpa.year_2_semester_2 = gpa_sem[('2', '2')]
                existing_gpa.year_3_semester_1 = gpa_sem[('3', '1')]
                existing_gpa.year_3_semester_2 = gpa_sem[('3', '2')]
                existing_gpa.year_4_semester_1 = gpa_sem[('4', '1')]
                existing_gpa.year_4_semester_2 = gpa_sem[('4', '2')]
                existing_gpa.year_5_semester_1 = gpa_sem[('5', '1')]
                existing_gpa.year_5_semester_2 = gpa_sem[('5', '2')]
            else:
                new_gpa = GPA(user_id=current_user.id, final_gpa=gpa, year_1_semester_1=gpa_sem[('1', '1')], year_1_semester_2=gpa_sem[('1', '2')], year_2_semester_1=gpa_sem[('2', '1')], year_2_semester_2=gpa_sem[('2', '2')], year_3_semester_1=gpa_sem[('3', '1')], year_3_semester_2=gpa_sem[('3', '2')], year_4_semester_1=gpa_sem[('4', '1')], year_4_semester_2=gpa_sem[('4', '2')], year_5_semester_1=gpa_sem[('5', '1')], year_5_semester_2=gpa_sem[('5', '2')])
                db.session.add(new_gpa)
            db.session.commit()

            existing_wam = WAM.query.filter_by(user_id=current_user.id).first()
            if existing_wam:
                existing_wam.final_wam = wam
                existing_wam.year_1_semester_1 = wam_sem[('1', '1')]
                existing_wam.year_1_semester_2 = wam_sem[('1', '2')]
                existing_wam.year_2_semester_1 = wam_sem[('2', '1')]
                existing_wam.year_2_semester_2 = wam_sem[('2', '2')]
                existing_wam.year_3_semester_1 = wam_sem[('3', '1')]
                existing_wam.year_3_semester_2 = wam_sem[('3', '2')]
                existing_wam.year_4_semester_1 = wam_sem[('4', '1')]
                existing_wam.year_4_semester_2 = wam_sem[('4', '2')]
                existing_wam.year_5_semester_1 = wam_sem[('5', '1')]
                existing_wam.year_5_semester_2 = wam_sem[('5', '2')]
            else:
                new_wam = WAM(user_id=current_user.id, final_wam=wam, year_1_semester_1=wam_sem[('1', '1')], year_1_semester_2=wam_sem[('1', '2')], year_2_semester_1=wam_sem[('2', '1')], year_2_semester_2=wam_sem[('2', '2')], year_3_semester_1=wam_sem[('3', '1')], year_3_semester_2=wam_sem[('3', '2')], year_4_semester_1=wam_sem[('4', '1')], year_4_semester_2=wam_sem[('4', '2')], year_5_semester_1=wam_sem[('5', '1')], year_5_semester_2=wam_sem[('5', '2')])
                db.session.add(new_wam)
            db.session.commit()
            
            #flash('Your GPA and WAM have been calculated successfully!')
            
            # Update this with the actual URL of the results page
            #return redirect(url_for('set_goal'))
            print(form.data)
            return render_template('resultspage.html', gpa=gpa, wam=wam)
        else:
            print("Validation errors:", form.errors)

    stored_data = Calculations.query.filter_by(user_id=current_user.id).first()
    if stored_data:
        form_data = json.loads(stored_data.form_input)
        # Remove the CSRF token from the data before populating the form
        form_data.pop('csrf_token', None)
        
    return render_template('calculator.html', form=form, form_data=form_data if stored_data else None)


@app.route('/reset_form')
@login_required
def reset_form():
    # Clear the form data from the database
    stored_data = Calculations.query.filter_by(user_id=current_user.id).first()
    if stored_data:
        db.session.delete(stored_data)
        db.session.commit()
    return redirect(url_for('calculator'))

# Route to render the HTML page
@app.route('/results')
@login_required
def results_page():
    return render_template("resultspage.html")

# Route to fetch GPA/WAM data dynamically
@app.route('/api/results')
@login_required
def get_results_data():
    gpa = GPA.query.filter_by(user_id=current_user.id).first()
    wam = WAM.query.filter_by(user_id=current_user.id).first()
    goal = Goal.query.filter_by(user_id=current_user.id).first()

    if not gpa or not wam:
        return jsonify({"error": "GPA or WAM data missing"}), 404

    # Dynamically extract semester fields from GPA and WAM models
    def extract_semesters(obj):
        semesters = {}
        for field in obj.__table__.columns.keys():
            if field.startswith("year_") and field != "user_id":
                year_sem = field.replace("year_", "").replace("_semester_", " Sem ")
                value = getattr(obj, field)
                if value != -1:
                    semesters[year_sem] = value
        return semesters

    response = {
        "gpa": round(gpa.final_gpa, 2),
        "wam": round(wam.final_wam, 2),
        "desired_gpa": round(goal.gpa, 2) if goal else None,
        "desired_wam": round(goal.wam, 2) if goal else None,
        "gpa_semesters": extract_semesters(gpa),
        "wam_semesters": extract_semesters(wam)
    }
    return jsonify(response)

# Share Graph Page
@app.route('/share')
@login_required
def share_page():
    return render_template('SharePage.html')

@app.route('/my-shared-graphs') # Inbox
@login_required
def my_shared_graphs():
    received = SharedGraph.query.filter_by(shared_with_id=current_user.id, is_active=True).all()
    sent = SharedGraph.query.filter_by(user_id=current_user.id, is_active=True).all()

    received_graphs = [{
        'sharer': User.query.get(s.user_id).email,
        'token': s.token,
        'include_marks': s.include_marks,
        'timestamp': s.timestamp.strftime('%Y-%m-%d %H:%M')
    } for s in received]

    sent_graphs = [{
        'recipient': User.query.get(s.shared_with_id).email,
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

    recipient = User.query.filter_by(email=recipient_username).first()
    if not recipient:
        return render_template('SharePage.html', error="User not found.")
    
    if recipient.id == current_user.id:
        return render_template('SharePage.html', error="You cannot share with yourself.")

    token = generate_token()

    shared = SharedGraph(
        token=token,
        include_marks=include_marks,
        is_active=True,
        user_id=current_user.id,
        shared_with_id=recipient.id)
    db.session.add(shared)
    db.session.commit()

    share_link = request.host_url.rstrip('/') + '/shared/' + token
    return render_template('SharePage.html', share_link=share_link)

@app.route('/shared/<token>')   # View shared graph
@login_required
def view_shared_graph(token):
    shared = SharedGraph.query.filter_by(token=token, is_active=True).first()

    if not shared:
        print(f"[DEBUG] No SharedGraph found with token: {token}")
        abort(403, description="This shared link is invalid or has been revoked.")

    if int(shared.shared_with_id) != int(current_user.id):
        print(f"[DEBUG] Token matched but user is not authorized. Expected {shared.shared_with_id}, got {current_user.id}")
        abort(403, description="You are not authorized to view this shared graph.")

    gpa = GPA.query.filter_by(user_id=shared.user_id).first()
    wam = WAM.query.filter_by(user_id=shared.user_id).first()

    if not gpa or not wam:
        return "No GPA/WAM data available for this user.", 404

    def extract_semesters(data):
        semesters = []
        values = []
        for i in range(1, 6):
            for j in range(1, 3):
                field_name = f'year_{i}_semester_{j}'
                val = getattr(data, field_name)
                if val != -1:
                    semesters.append(f"Y{i} S{j}")
                    values.append(val)
        return semesters, values

    gpa_labels, gpa_values = extract_semesters(gpa)
    wam_labels, wam_values = extract_semesters(wam)

    # Ensure both GPA and WAM use the same semester labels
    semesters = gpa_labels  # Assuming GPA and WAM are populated identically

    sharer = User.query.get(shared.user_id)
    return render_template('view_shared_graph.html', 
                        semesters=semesters,
                        wam_values=wam_values,
                        gpa_values=gpa_values,
                        include_marks=shared.include_marks,
                        sharer_username=sharer.email)


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
