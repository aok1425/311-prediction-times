from __future__ import division
from flask import Flask, session, redirect, url_for, escape, request, render_template
import random
from models import get_model, make_pred

app = Flask(__name__)

# app.permanent_session_lifetime = 60 * 60 * 1.5 # seconds, so 1.5 hours

def assign_roles(database, num_mafia, num_sheriff, num_angel, columns):
    """Takes in a database result, shuffles rows, chooses roles for each player, and updates the db."""
    counters = {}
    counters['Villager'] = [len(database) - num_mafia - num_sheriff - num_angel, 0]
    counters['Mafia'] = [num_mafia, 0]
    counters['Sheriff'] = [num_sheriff, 0]
    counters['Angel'] = [num_angel, 0]

    rows_to_remove = [] # very hacky. hopefully i replace this w a more elegant solution

    random.shuffle(database)

    for num, row in enumerate(database): # assign requested roles
        for role in counters.keys():
            if counters[role][columns.index('name')] < counters[role][columns.index('date_time')]:
                if row[columns.index('preferred_role')] == role:
                    row = database[num]
                    rows_to_remove.append(row)
                    date_time, name = row[:2]
                    c.execute("update players set role = '{}' where date_time = {} and name = '{}'".format(role, date_time, name))
                    counters[role][columns.index('name')] += 1

    for row in rows_to_remove:
        database.remove(row)

    for role in counters.keys(): # randomly assign rest of roles
        for i in range(counters[role][columns.index('date_time')] - counters[role][columns.index('name')]):
            chosen_player = random.randint(0, len(database) - 1)
            row = database.pop(chosen_player)
            date_time, name = row[:2]
            c.execute("update players set role = '{}' where date_time = {} and name = '{}'".format(role, date_time, name))

    db.commit()

@app.route('/')
def start(): 
    return render_template('create_or_join_game.html')

@app.route('/create', methods=['GET', 'POST'])
def create_game():
    if request.method == 'POST':
        session['game'] = request.form['game']
        session['date_time'] = unix_time(datetime.datetime.now())
        c.execute('''INSERT INTO games(date_time, game, phone_number) VALUES(?, ?, ?)''', (session['date_time'], session['game'], request.form['phone_number']))
        db.commit()

        return redirect(url_for('host'))
    else:
        c.execute('''SELECT date_time, game FROM games WHERE date_time >= ?''', (unix_time(datetime.datetime.now()) - 5 * 60,))
        games = c.fetchall()        

        return render_template('create_game.html', current_games=games)

@app.route('/choose', methods=['GET', 'POST'])
def choose_game():
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