import os
import sys

# Add the project root (EVBetting/) to sys.path so absolute imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import libsql
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

from tools.run_sports import run_all_bets
from tools.get_sports import get_sports
from tools.bet_history import enter_bet
from tools.bet_history import get_pending_bets
from tools.bet_history import get_all_bets
from tools.bet_history import get_settled_bets
from tools.bet_history import update_outcome
from tools.bet_history import get_total_bankroll
from tools.bet_history import get_bookies_table
from tools.bet_history import update_bet_amount
from tools.bet_history import update_bet_odds
from tools.bet_history import update_date
from tools.bet_history import update_bookie_values
from tools.bet_history import update_bet_type
from tools.bet_history import get_pending_ev
from tools.bet_history import get_pending_wagered
from tools.bet_history import get_current_evbets
from tools.bet_history import update_evbets
from tools.bet_history import transfer_bookie_funds
from tools.bet_history import get_ev_bookies
from tools.bet_history import enter_bonus_bet
from tools.bet_history import update_bet_bookie

load_dotenv()

TURSO_URL = os.getenv("TURSO_URL")
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN")

FRONTEND_DIST = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'dist')

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])


def get_db():
    return libsql.connect(TURSO_URL, auth_token=TURSO_AUTH_TOKEN)


def _rows_to_dicts(cursor) -> list[dict]:
    cols = [d[0] for d in cursor.description]
    return [dict(zip(cols, row)) for row in cursor.fetchall()]


# ---------------------------------------------------------------------------
# API routes
# ---------------------------------------------------------------------------

@app.route('/api/home')
def api_home():
    update_bookie_values()
    bookie_table = get_bookies_table()

    bookie_nets = {}
    net = 0
    skip = {'cash'}

    for bookie in bookie_table[0]:
        name = bookie['bookmaker']
        if name in skip:
            continue
        current_net = bookie['current_net']
        bookie_nets[name] = current_net
        net += current_net

    return jsonify({'net': net, 'bookie_nets': bookie_nets})


@app.route('/api/select_bets', methods=['GET'])
def api_select_bets():
    evbets = get_current_evbets()
    result = []
    for bet in evbets:
        result.append({
            'bet_id': bet[0],
            'sport': bet[1],
            'team': bet[2],
            'bookies': bet[3],
            'odds': bet[4],
            'bet_EV': bet[5],
            'kelly_percent': bet[6],
            'date': bet[7],
            'kelly_wager': bet[8],
        })
    return jsonify({'bets': result})


@app.route('/api/refresh_bets', methods=['POST'])
def api_refresh_bets():
    sports = get_sports(active=True, has_outrights=False)
    evbets = run_all_bets(sports)
    total_bankroll = get_total_bankroll()

    data_ids = get_pending_bets()
    current_ids = [b['bet_id'] for b in data_ids]

    evbets = [bet for bet in evbets if bet[1] not in current_ids]

    for bet in evbets:
        kelly_percent = bet[6]
        kelly_wager = kelly_percent * total_bankroll
        bet.append(round(kelly_wager, 2))

    update_evbets(evbets)
    evbets = get_current_evbets()

    result = []
    for bet in evbets:
        result.append({
            'bet_id': bet[0],
            'sport': bet[1],
            'team': bet[2],
            'bookies': bet[3],
            'odds': bet[4],
            'bet_EV': bet[5],
            'kelly_percent': bet[6],
            'date': bet[7],
            'kelly_wager': bet[8],
        })
    return jsonify({'status': 'ok', 'count': len(result), 'bets': result})


@app.route('/api/take_bet', methods=['POST'])
def api_take_bet():
    data = request.get_json()
    bet_id = data['bet_id']
    sport = data['sport']
    team = data['team']
    bookie_choice = data['bookie']
    odds = int(data['odds'])
    bet_amount = float(data['amount'])
    bet_ev = round(float(data['ev']), 2)
    date = data['date']

    if data.get('bonus_bet'):
        enter_bonus_bet(bet_id, sport, team, bookie_choice, odds, bet_amount, bet_ev, date)
    else:
        enter_bet(bet_id, sport, team, 'Moneyline', bookie_choice, odds, bet_amount, bet_ev, date)

    return jsonify({'success': True})


@app.route('/api/current_bets', methods=['GET'])
def api_current_bets():
    bets = sorted(get_pending_bets(), key=lambda b: b['date'])
    total_ev = get_pending_ev()
    total_wagered = get_pending_wagered()
    return jsonify({
        'bets': [dict(b) for b in bets],
        'total_ev': total_ev,
        'total_wagered': total_wagered,
    })


@app.route('/api/all_bets', methods=['GET'])
def api_all_bets():
    bets = get_all_bets()
    return jsonify({'bets': [dict(b) for b in bets]})


@app.route('/api/settled_bets', methods=['GET'])
def api_settled_bets():
    response = get_settled_bets()
    bets = sorted(response[0], key=lambda b: b['date'])
    total_ev, total_net = response[1]
    bets_won, bets_lost = response[2]
    return jsonify({
        'bets': [dict(b) for b in bets],
        'totals': {
            'total_ev': total_ev,
            'total_net': total_net,
            'bets_won': bets_won,
            'bets_lost': bets_lost,
        }
    })


@app.route('/api/edit_bet', methods=['POST'])
def api_edit_bet():
    data = request.get_json()
    bet_id = str(data['bet_id'])

    new_date = data.get('date')
    new_outcome = data.get('outcome')
    new_bookie = data.get('bookie')

    odds_val = data.get('odds', '')
    new_odds = int(odds_val) if odds_val else 0

    amount_val = data.get('amount', '')
    new_amount = float(amount_val) if amount_val else 0

    if new_amount:
        update_bet_amount(bet_id, new_amount)
    if new_odds:
        update_bet_odds(bet_id, new_odds)
    if new_date:
        update_date(bet_id, new_date)
    if new_outcome:
        update_outcome(bet_id, new_outcome)
    if new_bookie:
        update_bet_bookie(bet_id, new_bookie)

    new_bet_type = data.get('bet_type')
    if new_bet_type:
        update_bet_type(bet_id, new_bet_type)

    return jsonify({'success': True})


@app.route('/api/bookie_stats', methods=['GET'])
def api_bookie_stats():
    update_bookie_values()
    bookie_data = get_bookies_table()
    bookies = [dict(b) for b in bookie_data[0]]
    totals = bookie_data[1]
    return jsonify({
        'bookies': bookies,
        'totals': {
            'net_bankroll': totals[0],
            'net_wagered': totals[1],
            'net_wagerable': totals[2],
            'net_total': totals[3],
        }
    })


@app.route('/api/transfer_funds', methods=['POST'])
def api_transfer_funds():
    data = request.get_json()
    send_bookie = data['sending_bookie']
    receiving_bookie = data['receiving_bookie']
    amount = float(data['amount'])
    transfer_bookie_funds(send_bookie, receiving_bookie, amount)
    update_bookie_values()
    return jsonify({'success': True})


@app.route('/api/graphs/data')
def api_graphs_data():
    """Return JSON for Chart.js charts on the graphs page."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""SELECT date, bookie, net, odds, this_EV, bet_EV, bet_amount, outcome FROM bets
                      WHERE outcome IN ('win','loss') ORDER BY date(date) ASC""")
    rows = _rows_to_dicts(cursor)

    labels = []
    running_net = []
    running_ev = []
    constant_bet_arr = []
    constant_bet_ev_arr = []

    bet_num = 0
    r_net = 0
    r_ev = 0
    r_const_net = 0
    r_const_ev = 0

    bookies = get_ev_bookies()
    per_bookie = {b: [] for b in bookies}
    cum_bookie = {b: 0 for b in bookies}
    per_bookie_individual = {b: [] for b in bookies}
    per_bookie_individual_ev = {b: [] for b in bookies}
    cum_bookie_ev = {b: 0 for b in bookies}

    cats = ['<0', '100-200', '200-300', '300-400', '400-500', '500-600', '600-700', '700-800', '800+']
    win_counts = [0] * len(cats)
    loss_counts = [0] * len(cats)
    net_by_cat = [0] * len(cats)

    def cat_index(odds):
        try:
            if odds < 0:
                return 0
            if odds < 200:
                return 1
            if odds < 300:
                return 2
            if odds < 400:
                return 3
            if odds < 500:
                return 4
            if odds < 600:
                return 5
            if odds < 700:
                return 6
            if odds < 800:
                return 7
            return 8
        except Exception:
            return 8

    for row in rows:
        date = row['date']
        bookie = row['bookie']
        net = row['net'] or 0
        odds = row['odds'] or 0
        this_ev = row['this_EV'] or 0
        bet_ev_100 = row['bet_EV']
        bet_amount = row['bet_amount']
        outcome = row['outcome']

        labels.append(date)
        r_net += net
        r_ev += this_ev
        bet_num += 1
        running_net.append(r_net)
        running_ev.append(r_ev)

        if outcome == 'win':
            const = (100 / abs(odds)) * 5 if odds < 0 else (odds / 100) * 5
            const_ev = bet_ev_100 / 20 if bet_ev_100 else (this_ev * (5.0 / bet_amount) if bet_amount else this_ev)
            r_const_net += const
            r_const_ev += const_ev
        else:
            const = -5
            const_ev = bet_ev_100 / 20 if bet_ev_100 else (this_ev * (5.0 / bet_amount) if bet_amount else this_ev)
            r_const_net += const
            r_const_ev += const_ev

        constant_bet_arr.append(r_const_net)
        constant_bet_ev_arr.append(r_const_ev)

        if bookie not in cum_bookie:
            cum_bookie[bookie] = 0
            per_bookie[bookie] = [0] * (len(labels) - 1)
            per_bookie_individual[bookie] = []
            bookies.append(bookie)

        cum_bookie[bookie] += net
        for b in bookies:
            per_bookie[b].append(cum_bookie.get(b, 0))

        if bookie not in per_bookie_individual:
            per_bookie_individual[bookie] = []
            per_bookie_individual_ev[bookie] = []
            cum_bookie_ev[bookie] = 0
        per_bookie_individual[bookie].append(cum_bookie[bookie])
        cum_bookie_ev[bookie] += this_ev
        per_bookie_individual_ev[bookie].append(cum_bookie_ev[bookie])

        idx = cat_index(odds)
        if outcome == 'win':
            win_counts[idx] += 1
        else:
            loss_counts[idx] += 1
        net_by_cat[idx] += net

    win_percentages = [
        (w / (w + l)) if (w + l) > 0 else 0
        for w, l in zip(win_counts, loss_counts)
    ]

    conn.close()

    return jsonify({
        'labels': labels,
        'running_net': running_net,
        'running_ev': running_ev,
        'constant_bet_net': constant_bet_arr,
        'constant_bet_ev': constant_bet_ev_arr,
        'per_bookie': per_bookie,
        'per_bookie_individual': per_bookie_individual,
        'per_bookie_individual_ev': per_bookie_individual_ev,
        'bookies': bookies,
        'odds_categories': cats,
        'odds_win_percentages': win_percentages,
        'odds_nets': net_by_cat,
    })


# ---------------------------------------------------------------------------
# Production: serve React build
# ---------------------------------------------------------------------------

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    if path and os.path.exists(os.path.join(FRONTEND_DIST, path)):
        return send_from_directory(FRONTEND_DIST, path)
    return send_from_directory(FRONTEND_DIST, 'index.html')


if __name__ == '__main__':
    app.run(debug=True)
