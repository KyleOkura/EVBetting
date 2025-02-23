from flask import Flask, render_template, request, jsonify, redirect, url_for
from ..tools.run_sports import run_all
from ..tools.get_sports import get_sports
from ..tools.bet_history import enter_bet
from ..tools.bet_history import get_pending_bets
from ..tools.bet_history import get_all_bets
from ..tools.bet_history import get_settled_bets
import os
import sqlite3



def get_path():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../database'))
    db_path = os.path.join(root_dir, 'bet_history.db')
    return db_path


def get_db():
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_all', methods = ['GET', 'POST'])
def run_all():
    if request.method == 'POST':
        sports = get_sports(active=True, has_outrights=False)
        bets = run_all(sports)
        #returns list with format - [[sport, id, team, [bookies], odds, ev, kelly %, date],
        #                            [sport, id, team, [bookies], odds, ev, kelly %, date]]
        return render_template('select_bets.html', bets=bets)
    return render_template('run_all.html')


@app.route('/take_bet', methods = ['POST'])
def take_bet():
    id = request.form['id']
    sport = request.form['sport']
    team = request.form['team']
    bookie_choice = request.form['bookie']
    bet_type = 'Moneyline'
    odds = request.form['odds']
    bet_amount = request.form['amount']
    bet_ev = round(request.form['ev'] * bet_amount, 2)
    date = request.form['date']
    enter_bet(id, sport, team, bet_type, bookie_choice, odds, bet_amount, bet_ev, date)

    return(redirect(url_for('current_bets')))

@app.route('/current_bets', methods = ['GET'])
def current_bets():
    current_bets = get_pending_bets()
    return render_template('current_bets.html', bets=current_bets)

@app.route('/all_bets', methods = ['GET'])
def all_bets():
    all_bets = get_all_bets()
    return render_template('all_bets.html', bets=all_bets)

@app.route('/settled_bets', methods = ['GET'])
def settled_bets():
    settled_bets = get_settled_bets()
    return render_template('settled_bets.html', bets=settled_bets)


if __name__ == '__main__':
    app.run(debug=True)