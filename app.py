
from flask import Flask, request, jsonify, render_template
from models import db, Goal

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///goals.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/')
def home():
    return render_template('mainpage.html')

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
      
      
@app.route('/calculator')
def home():
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

    return render_template('resulttest.html', gpa=gpa, wam=wam)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

