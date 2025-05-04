from flask import Flask, request, jsonify, render_template, send_file, abort
from flask_login import LoginManager, login_user, logout_user, current_user, login_required, UserMixin
from models import db, Goal, User, SharedGraph
import io
import matplotlib.pyplot as plt
import secrets

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///goals.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'dev-secret-key'  # Constant key for development  # Secret key for session management

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Helper to generate a secure token ---
def generate_token():
    return secrets.token_urlsafe(32)

# --- Routes ---

@app.route('/')
def share_page():
    return render_template('SharePage.html')

# --- Temporary login route for testing only ---
@app.route('/login')
def login():
    user = User.query.filter_by(email='bob@example.com').first()
    login_user(user)
    return "Logged in as " + user.email

# --- Temporary logout route for testing only ---
@app.route('/logout')
def logout():
    logout_user()
    return "Logged out"


@app.route('/my-shared-graphs')
@login_required
def my_shared_graphs():
    received = SharedGraph.query.filter_by(shared_with_id=current_user.id, is_active=True).all()
    sent = SharedGraph.query.filter_by(user_id=current_user.id, is_active=True).all()

    received_graphs = [{
        'sharer': User.query.get(s.user_id).email,
        'token': s.token,
        'include_marks': s.include_marks
    } for s in received]

    sent_graphs = [{
        'recipient': User.query.get(s.shared_with_id).email,  # ✅ FIXED
        'token': s.token,
        'include_marks': s.include_marks,
        'is_active': s.is_active
    } for s in sent]

    return render_template("my_shared_graphs.html",
                           shared_with_me=received_graphs,
                           shared_by_me=sent_graphs)


@app.route('/share-graph', methods=['POST'])
@login_required
def share_graph():
    include_marks = request.form.get('shareMarks') == 'yes'
    recipient_username = request.form.get('sharedto')

    if not recipient_username:
        return "Recipient username is required", 400

    recipient = User.query.filter_by(email=recipient_username).first()
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


@app.route('/shared/<token>')
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

# @app.route('/my-shared-graphs')
# @login_required
# def my_shared_graphs():
#     shares = SharedGraph.query.filter_by(shared_with_id=current_user.id, is_active=True).all()
#     graphs = []
#     for s in shares:
#         sharer = User.query.get(s.user_id)
#         graphs.append({
#             'sharer': sharer.email,
#             'token': s.token,
#             'include_marks': s.include_marks
#         })
#     return render_template('my_shared_graphs.html', graphs=graphs)

# @app.route('/shared-by-me')
# @login_required
# def shared_by_me():
#     shares = SharedGraph.query.filter_by(user_id=current_user.id).all()
#     results = []
#     for s in shares:
#         recipient = User.query.get(s.shared_with_id)
#         results.append({
#             'recipient': recipient.email,
#             'token': s.token,
#             'include_marks': s.include_marks,
#             'is_active': s.is_active
#         })
#     return render_template('shared_by_me.html', shared_graphs=results)

if __name__ == '__main__':
    app.run(debug=True)
