from flask import Flask, render_template, request, jsonify, redirect, url_for
from ..tools.run_sports import run_all_bets
from ..tools.get_sports import get_sports
from ..tools.bet_history import enter_bet
from ..tools.bet_history import get_pending_bets
from ..tools.bet_history import get_all_bets
from ..tools.bet_history import get_settled_bets
from ..tools.bet_history import update_outcome
from ..tools.bet_history import get_total_bankroll
from ..tools.bet_history import get_bookies_table
from ..tools.bet_history import update_bet_amount
from ..tools.bet_history import update_bet_odds
from ..tools.bet_history import update_date
from ..tools.bet_history import update_bookie_values
from ..tools.bet_history import get_pending_ev
from ..tools.bet_history import get_pending_wagered
from ..tools.bet_history import get_current_evbets
from ..tools.bet_history import update_evbets

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
    update_bookie_values()
    bookie_table = get_bookies_table()
    draftkings_net = 0
    fanduel_net = 0
    betmgm_net = 0
    betrivers_net = 0
    ballybet_net = 0
    williamhill_net = 0
    espnbet_net = 0
    fanatics_net = 0
    cash_net = 0

    for bookie in bookie_table[0]:
        bookie_name = bookie['bookmaker']
        match bookie_name:
            case 'draftkings':
                draftkings_net = bookie['current_net']
            case 'fanduel':
                fanduel_net = bookie['current_net']
            case 'betmgm':
                betmgm_net = bookie['current_net']
            case 'betrivers':
                betrivers_net = bookie['current_net']
            case 'ballybet':
                ballybet_net = bookie['current_net']
            case 'williamhill_us':
                williamhill_net = bookie['current_net']
            case 'espnbet':
                espnbet_net = bookie['current_net']
            case 'fanatics':
                fanatics_net = bookie['current_net']
            case 'cash':
                cash_net = bookie['total_bankroll']
            case _:
                raise ValueError(f"{bookie_name} not found")
            
    bookie_nets = (draftkings_net, fanduel_net, betmgm_net, betrivers_net, ballybet_net, williamhill_net, espnbet_net, fanatics_net, cash_net)

    return render_template('index.html', bookie_nets=bookie_nets)

@app.route('/select_bets', methods = ['POST', 'GET'])
def select_bets():
    if request.method == 'POST':
        sports = get_sports(active=True, has_outrights=False)
        evbets = run_all_bets(sports)
        total_bankroll = get_total_bankroll()

        data_ids = get_pending_bets()
        current_ids = []
        for id in data_ids:
            current_ids.append(id["bet_id"])

        evbets = [bet for bet in evbets if bet[1] not in current_ids]

        for bet in evbets:
            kelly_percent = bet[6]
            kelly_wager = kelly_percent * total_bankroll
            bet.append(round(kelly_wager, 2))

        update_evbets(evbets)

        return render_template('select_bets.html', bets=evbets)
    
    else:
        evbets = get_current_evbets()
        return render_template('select_bets.html', bets=evbets)

@app.route('/take_bet', methods = ['POST'])
def take_bet():
    id = request.form['bet_id']
    print(f'id: {id}')
    sport = request.form['sport']
    team = request.form['team']
    bookie_choice = request.form['bookie']
    bet_type = 'Moneyline'
    odds = int(request.form['odds'])
    bet_amount = float(request.form['amount'])
    bet_ev = round(float(request.form['ev']), 2)
    date = request.form['date']
    enter_bet(id, sport, team, bet_type, bookie_choice, odds, bet_amount, bet_ev, date)

    evbets = get_current_evbets()
    return render_template('select_bets.html', bets=evbets)

@app.route('/current_bets', methods = ['GET'])
def current_bets():
    current_bets = sorted(get_pending_bets(), key=lambda bet: bet["date"])
    current_total_ev = get_pending_ev()
    current_total_wagered = get_pending_wagered()
    return render_template('current_bets.html', bets=current_bets, total_ev=current_total_ev, total_wagered = current_total_wagered)

@app.route('/all_bets', methods = ['GET'])
def all_bets():
    all_bets = get_all_bets()
    return render_template('all_bets.html', bets=all_bets)

@app.route('/settled_bets', methods = ['GET'])
def settled_bets():
    response = get_settled_bets()
    settled_bets = response[0]
    nums = response[1]
    results = response[2]

    total_ev = nums[0]
    total_net = nums[1]

    bets_won = results[0]
    bets_lost = results[1]
    return render_template('settled_bets.html', bets=settled_bets, bets_ev=total_ev, bets_net=total_net, bets_won=bets_won, bets_lost=bets_lost)

@app.route('/edit_bet', methods=['POST'])
def edit_bet():
    id = request.form['bet_id']
    bet_id = str(id)
    new_date = request.form.get('date', None)
    new_outcome = request.form.get('outcome', None) 

    odds_str = request.form.get('odds', '').strip()
    new_odds = int(odds_str) if odds_str else 0

    amount_str = request.form.get('amount', '').strip()
    new_amount = float(amount_str) if amount_str else 0 

    if new_amount != 0:
        update_bet_amount(bet_id, new_amount)

    if new_odds != 0:
        update_bet_odds(bet_id, new_odds)

    if new_date is not None:
        update_date(bet_id, new_date)
    
    if new_outcome is not None:
        update_outcome(bet_id, new_outcome)  

    return redirect(url_for('current_bets')) 

@app.route('/bookie_stats', methods=['GET'])
def bookie_stats():
    update_bookie_values()
    bookie_data = get_bookies_table()
    bookies = []
    bankroll = []
    wagered = []
    wagerable = []
    nets = []
    info = bookie_data[0]

    for x in info:
        bookies.append(x['bookmaker'])
        bankroll.append(x['total_bankroll'])
        wagered.append(x['currently_wagered'])
        wagerable.append(x['wagerable'])
        nets.append(x['current_net'])

    totals = bookie_data[1]

    combined = zip(bookies, bankroll, wagered, wagerable, nets)

    return render_template('bookie_stats.html', combined=combined, net_bankroll=totals[0], net_wagered=totals[1], net_wagerable=totals[2], net_total=totals[3])


"""
@app.route('/bets_graph', methods=['POST'])
def bets_graph():
    bets = get_all_bets()

    expected_value_nums = []
    net_nums = []

    for bet in bets:
        expected_value_nums.append(bet['this_EV'])
        net_nums.append(bet['net'])


    return jsonify({"actual": actual_profits, "expected": expected_profits})
"""



if __name__ == '__main__':
    app.run(debug=True)


