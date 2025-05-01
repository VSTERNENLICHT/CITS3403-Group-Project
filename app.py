from flask import Flask, request, jsonify, render_template, send_file, abort
from flask_login import login_required, current_user
from models import db, Goal, User, SharedGraph
import io
import matplotlib.pyplot as plt
import secrets

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///goals.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# --- Helper to generate a secure token ---
def generate_token():
    return secrets.token_urlsafe(32)

# --- Root (for testing only) ---
@app.route('/')
def home():
    return render_template('SharePage.html')

# --- Route to share a graph with another user ---
@app.route('/share-graph', methods=['POST'])
@login_required
def share_graph():
    data = request.get_json()
    include_marks = data.get('shareMarks') == 'yes'
    recipient_username = data.get('sharedWithUsername')

    if not recipient_username:
        return jsonify({'error': 'Recipient username is required'}), 400

    recipient = User.query.filter_by(username=recipient_username).first()
    if not recipient:
        return jsonify({'error': 'Recipient user not found'}), 404

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
    return jsonify({'link': share_link})


# --- Route to view a shared graph ---
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

    sharer = User.query.get(shared.user_id)

    return render_template('view_shared_graph.html', 
                           semesters=semesters,
                           wam_values=wam_values,
                           include_marks=shared.include_marks,
                           sharer_username=sharer.username)


# --- (Optional) Route to revoke shared graph ---
@app.route('/revoke/<token>', methods=['POST'])
@login_required
def revoke_graph(token):
    shared = SharedGraph.query.filter_by(token=token, user_id=current_user.id).first()
    if shared:
        shared.is_active = False
        db.session.commit()
        return jsonify({'status': 'revoked'})
    return jsonify({'status': 'not found'}), 404


# --- Run the app ---
if __name__ == '__main__':
    app.run(debug=True)
