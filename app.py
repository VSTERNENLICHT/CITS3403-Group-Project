from flask import Flask, request, json, render_template

app = Flask(__name__)


@app.route('/calculator')
def set_goal():
    return render_template('calculator.html')


if __name__ == '__main__':
    app.run(debug=True)


@app.route('/')
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
