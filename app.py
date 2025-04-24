from flask import Flask, request, jsonify, render_template

app = Flask(__name__)


@app.route('/calculator')
def set_goal():
    return render_template('calculator.html')


if __name__ == '__main__':
    app.run(debug=True)


@app.route('/')
def home():
    return render_template('calculator.html')  # or whatever your homepage is

