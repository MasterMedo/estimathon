import yaml
import random
from flask import Flask, render_template, request, redirect, url_for, abort


app = Flask(__name__)


class Team:
    def __init__(self):
        self.tries = max_tries
        self.answers = [(0, 0)]*questions_count
        self.points = [0]*questions_count

    def submit(self, i, low, high):
        assert self.tries > 0, 'no more tries left :('

        self.tries -= 1
        self.answers[i] = (low, high)
        if low <= answers[i] <= high:
            self.points[i] = int(high/low)

    def score(self):
        return (10 + sum(self.points)) * 2**sum(not pts for pts in self.points)


@app.route('/')
def estimathon():
    return render_template('estimathon.html')


@app.route('/start', methods=['POST'])
def start():
    global teams, questions, answers

    names = (name.strip() for name in request.form['teams'].split())
    teams = {name: Team() for name in names}

    with open('questions.yaml') as f:
        questions = next(yaml.load_all(f, Loader=yaml.FullLoader))

    sample = random.sample(questions, questions_count)
    questions, answers = zip(*[i.values() for i in sample])
    return redirect(url_for('results'))


@app.route('/results')
def results():
    return render_template('results.html', questions=questions, teams=teams)


@app.route('/submit')
def submit():
    return render_template('submit.html', questions=questions, teams=teams)


@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    try:
        team_name = request.form['team'].strip()
        i = int(request.form['i'])
        low = float(request.form['low'].replace(' ', ''))
        high = float(request.form['high'].replace(' ', ''))
        low_exp = float(request.form['low_exp'].replace(' ', ''))
        high_exp = float(request.form['high_exp'].replace(' ', ''))

        low = low * 10**low_exp
        high = high * 10**high_exp

        assert low > 0 and high > 0, 'bounds must be greater than 0'

        teams[team_name].submit(i, low, high)

    except (AssertionError, TimeoutError) as e:
        abort(400, description=e)

    except (NameError, ValueError):
        abort(400, description='Invalid input!')

    return redirect(url_for('results'))


@app.errorhandler(400)
def bad_request(e):
    return render_template('400.html', error=str(e))


questions_count = 13
max_tries = 18

if __name__ == '__main__':
    app.run(debug=True)
