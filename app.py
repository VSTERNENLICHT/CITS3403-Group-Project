from flask import Flask, request, jsonify, render_template
from models import db, Goal

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///goals.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/set-goal')
def set_goal():
    return render_template('set-goal.html')

@app.route('/save-goal', methods=['POST'])
def save_goal():
    data = request.get_json()
    try:
        wam = float(data['wam'])
        gpa = float(data['gpa'])

        # Enforce constraints
        if not (0 <= wam <= 100):
            return jsonify({"message": "WAM must be between 0 and 100"}), 400
        if not (0 <= gpa <= 7):
            return jsonify({"message": "GPA must be between 0 and 7"}), 400
        if round(gpa, 1) != gpa:
            return jsonify({"message": "GPA must be rounded to 1 decimal place"}), 400

        new_goal = Goal(wam=wam, gpa=gpa)
        db.session.add(new_goal)
        db.session.commit()

        return jsonify({"message": "Your goals have been saved!"}), 200

    except (KeyError, ValueError):
        return jsonify({"message": "Invalid input format."}), 400

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)


@app.route('/')
def home():
    return render_template('set-goal.html')  # or whatever your homepage is


@app.route('/')
def home():
    return render_template('set-goal.html')

