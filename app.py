from flask import Flask, request, jsonify, render_template
from models import db, Goal
import io
import matplotlib.pyplot as plt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///goals.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/')
def home():
    return render_template('SharePage.html')

@app.route('/generate-graph', methods=['POST'])
def generate_graph():
    data = request.get_json()
    include_marks = data.get('shareMarks') == 'yes'
    export_format = data.get('exportFormat')

    # Retrieve data from DB (replace with your logic)
    goals = Goal.query.all()
    semesters = list(range(1, len(goals) + 1))
    wam_values = [g.wam for g in goals]

    # Create graph
    fig, ax = plt.subplots()
    ax.plot(semesters, wam_values, marker='o', label='WAM')

    if include_marks:
        for i, v in enumerate(wam_values):
            ax.text(semesters[i], wam_values[i], str(v), ha='center', va='bottom')

    ax.set_title('Semester WAM Progress')
    ax.set_xlabel('Semester')
    ax.set_ylabel('WAM')
    ax.grid(True)

    buf = io.BytesIO()
    if export_format == 'jpeg':
        plt.savefig(buf, format='jpeg')
        buf.seek(0)
        return send_file(buf, mimetype='image/jpeg', download_name='calcmywam_graph.jpeg', as_attachment=True)
    else:  # pdf
        plt.savefig(buf, format='pdf')
        buf.seek(0)
        return send_file(buf, mimetype='application/pdf', download_name='calcmywam_graph.pdf', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

