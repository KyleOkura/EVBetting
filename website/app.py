from flask import Flask, render_template, request, jsonify, redirect, url_for
from ..tools.run_sports import run_all_bets
from ..tools.get_sports import get_sports
from ..tools.bet_history import enter_bet
from ..tools.bet_history import get_pending_bets
from ..tools.bet_history import get_all_bets
from ..tools.bet_history import get_settled_bets
from ..tools.bet_history import get_bet
from ..tools.bet_history import update_bet2
from ..tools.bookies import get_total_bankroll
from ..tools.bookies import get_ev_bookies

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
        bets = run_all_bets(sports)
        #returns list with format - [[sport, id, team, [bookies], odds, ev, kelly %, date],
        #                            [sport, id, team, [bookies], odds, ev, kelly %, date]]

        total_bankroll = get_total_bankroll()

        for bet in bets:
            kelly_percent = bet[6]
            kelly_wager = kelly_percent * total_bankroll
            bet.append(round(kelly_wager, 2))

        return render_template('select_bets.html', bets=bets)
    return render_template('run_all.html')


@app.route('/take_bet', methods = ['POST'])
def take_bet():
    id = request.form['bet_id']
    sport = request.form['sport']
    team = request.form['team']
    bookie_choice = request.form['bookie']
    bet_type = 'Moneyline'
    odds = request.form['odds']
    bet_amount = request.form['amount']
    bet_ev = round(request.form['ev'] * bet_amount, 2)
    date = request.form['date']
    enter_bet(id, sport, team, bet_type, bookie_choice, odds, bet_amount, bet_ev, date)

    return(redirect(url_for('run_all')))

@app.route('/current_bets', methods = ['GET'])
def current_bets():
    current_bets = get_pending_bets()
    return render_template('current_bets.html', bets=current_bets)

@app.route('/all_bets', methods = ['GET'])
def all_bets():
    all_bets = get_all_bets()
    bookies = get_ev_bookies()
    return render_template('all_bets.html', bets=all_bets)

@app.route('/settled_bets', methods = ['GET'])
def settled_bets():
    settled_bets = get_settled_bets()
    return render_template('settled_bets.html', bets=settled_bets)

@app.route('/edit_bet', methods=['POST'])
def edit_bet():
    id = request.form['bet_id']
    bet_id = str(id)
    new_date = request.form.get('date', None)
    new_outcome = request.form.get('outcome', None) 

    odds_str = request.form.get('odds', '').strip()
    new_odds = int(odds_str) if odds_str else 0

    amount_str = request.form.get('amount', '').strip()
    new_amount = int(amount_str) if amount_str else 0 

    current_bet = get_bet(bet_id)
    if new_odds is 0:
        new_odds = current_bet['odds']
    if new_date is None:
        new_date = current_bet['date']
    if new_outcome is None:
        new_outcome = current_bet['outcome']
    if new_amount is 0:
        new_amount = int(current_bet['bet_amount'])

    update_bet2(bet_id, new_odds, new_date, new_outcome, new_amount)  

    return redirect(url_for('all_bets')) 

if __name__ == '__main__':
    app.run(debug=True)