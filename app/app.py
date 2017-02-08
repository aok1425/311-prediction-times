from __future__ import division
from flask import Flask, session, redirect, url_for, escape, request, render_template
import random
from models import get_model, make_pred, sample_row

app = Flask(__name__)
# app.permanent_session_lifetime = 60 * 60 * 1.5 # seconds, so 1.5 hours
model = get_model()


@app.route('/')
def start(): 
    return render_template('home.html')


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    return render_template('predict.html')


@app.route('/predict-results', methods=['POST'])
def predict_results():
    pred = make_pred(request.form, model)
    return str(pred)[:4]


@app.route('/explore', methods=['GET', 'POST'])
def explore():
    if request.method == 'POST':
        session['game'] = request.form.keys()[0] # revise HTML form to get value, not key 
        return redirect(url_for('login'))
    else:
        c.execute('''SELECT date_time, game FROM games WHERE date_time >= ?''', (unix_time(datetime.datetime.now()) - 5 * 60,))
        games = c.fetchall()

        return render_template('choose_game.html', games=games)    

@app.route('/signin')
def signin():
    if 'username' in session:
        c.execute('''SELECT * FROM players WHERE date_time >= ? AND game = ?''', (unix_time(datetime.datetime.now()) - 5 * 60, session['game']))
        players = c.fetchall()

        return render_template('player_waiting.html', players=players, name=session['username'], num=len(players))
    return redirect(url_for('login'))

@app.route('/role', methods=['GET', 'POST'])
def role():
    if request.method == 'POST':
        session['date_time'] = unix_time(datetime.datetime.now())
        c.execute('''INSERT INTO players(date_time, name) VALUES(?, ?)''', (session['date_time'], session['username']))
        db.commit()
        return redirect(url_for('index'))
    if 'username' in session:
        c.execute('''SELECT role FROM players WHERE date_time = ? AND name = ?''', (session['date_time'], session['username']))
        session['role'] = c.fetchone()[0]

        c.execute('''SELECT phone_number FROM games WHERE game = ? ORDER BY date_time DESC''', (session['game'],))
        phone_number = c.fetchone()[0]

        if phone_number:
            phone_number = str(phone_number)
            phone_number = "{}-{}-{}".format(phone_number[:3],phone_number[3:6],phone_number[6:])

        return render_template('player_role.html', name=session['username'], role=session['role'], phone_number=phone_number)
    return redirect(url_for('login'))

@app.route('/host', methods=['GET', 'POST'])
def host():
    if request.method == 'POST':
        c.execute('''SELECT * FROM players WHERE {} ORDER BY role'''.format('date_time = "' + '" OR date_time = "'.join(request.form.keys()) + '"'))
        players = c.fetchall()    
        columns = [i[0] for i in c.description]

        assign_roles(players, int(request.form['mafia']), int(request.form['sheriff']), int(request.form['angel']), columns=columns)

        c.execute('''SELECT * FROM players WHERE {} ORDER BY role'''.format('date_time = "' + '" OR date_time = "'.join([i for i in request.form.keys() if i[0] == "1"]) + '"')) # i[0] == 1 lasts until 2033
        players = c.fetchall()

        players = [[num]+list(values) for num, values in list(enumerate(players, 1))]
        
        return render_template('host_after.html', players=players)
    else:
        c.execute('''SELECT * FROM players WHERE date_time >= ? AND game = ?''', (unix_time(datetime.datetime.now()) - 5 * 60, session['game']))
        players = c.fetchall()

        num_players = len(players)
        num_mafia = [int(num_players/3.), int(ceil(num_players/3.))]

        if num_mafia[0] == num_mafia[1]:
            num_mafia[0] -= 1

        if num_players > 6 and num_players < 12:
            num_sheriff = [0,1]
            num_angel = [0,1]
        elif num_players >= 12:
            num_sheriff = [1,2]
            num_angel = [1,2]
        else:
            num_sheriff = [0,1]
            num_angel = [0,1]

        return render_template('host_before.html', players=players, num_mafia=num_mafia, num_sheriff=num_sheriff, num_angel=num_angel, num_players=num_players)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        session['date_time'] = unix_time(datetime.datetime.now())
        c.execute('''INSERT INTO players(date_time, name, preferred_role, game) VALUES(?,?,?,?)''', (session['date_time'], session['username'], request.form['preferred_role'], session['game']))
        db.commit()

        return redirect(url_for('signin'))
    return render_template('login.html')

@app.route('/test_login/<name>/<preferred_role>/<game>')
def test_login(name, preferred_role, game):
    c.execute('''INSERT INTO players(date_time, name, preferred_role, game) VALUES(?,?,?,?)''', (unix_time(datetime.datetime.now()), name, preferred_role, game))
    db.commit()

    return "Added {}, requesting {} role, into game {}".format(name, preferred_role, game)

@app.route('/logout')
def logout():
    """remove the username from the session if it's there"""
    session.pop('username', None)
    return redirect(url_for('index'))

# set the secret key.  keep this really secret:
app.secret_key = 'alex'

if __name__ == '__main__':
    app.run(debug=True)