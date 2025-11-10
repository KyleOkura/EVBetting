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
from ..tools.bet_history import update_bet_type
from ..tools.bet_history import get_pending_ev
from ..tools.bet_history import get_pending_wagered
from ..tools.bet_history import get_current_evbets
from ..tools.bet_history import update_evbets
from ..tools.bet_history import transfer_bookie_funds
from ..tools.bet_history import refresh_graphs
from ..tools.bet_history import get_ev_bookies
from ..tools.bet_history import enter_bonus_bet
from ..tools.bet_history import update_bet_bookie

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
    draftkings_net = fanduel_net = betmgm_net = betrivers_net = ballybet_net = williamhill_net = espnbet_net = fanatics_net = net = 0

    for bookie in bookie_table[0]:
        bookie_name = bookie['bookmaker']
        match bookie_name:
            case 'draftkings':
                draftkings_net = bookie['current_net']
                net += draftkings_net
            case 'fanduel':
                fanduel_net = bookie['current_net']
                net += fanduel_net
            case 'betmgm':
                betmgm_net = bookie['current_net']
                net += betmgm_net
            case 'betrivers':
                betrivers_net = bookie['current_net']
                net += betrivers_net
            case 'ballybet':
                ballybet_net = bookie['current_net']
                net += ballybet_net
            case 'williamhill_us':
                williamhill_net = bookie['current_net']
                net += williamhill_net
            case 'espnbet':
                espnbet_net = bookie['current_net']
                net += espnbet_net
            case 'fanatics':
                fanatics_net = bookie['current_net']
                net += fanatics_net
            case 'cash':
                continue
            case _:
                raise ValueError(f"{bookie_name} not found")
    


    bookie_nets = (draftkings_net, fanduel_net, betmgm_net, betrivers_net, ballybet_net, williamhill_net, espnbet_net, fanatics_net, net)

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
        evbets = get_current_evbets()


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

    odds = int(request.form['odds'])
    bet_amount = float(request.form['amount'])
    bet_ev = round(float(request.form['ev']), 2)
    date = request.form['date']

    if request.form.get('bonus_bet'):
        enter_bonus_bet(id, sport, team, bookie_choice, odds, bet_amount, bet_ev, date)
    else:
        bet_type = 'Moneyline'
        enter_bet(id, sport, team, bet_type, bookie_choice, odds, bet_amount, bet_ev, date)

    return redirect(url_for('select_bets'))

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
    settled_bets = sorted(response[0], key=lambda bet: bet["date"])
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
    new_bookie = request.form.get('bookie', None)

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
    if new_bookie is not None:
        update_bet_bookie(bet_id, new_bookie) 
    # optional: update bet_type if provided (e.g., Moneyline or Bonus)
    new_bet_type = request.form.get('bet_type', None)
    if new_bet_type is not None:
        update_bet_type(bet_id, new_bet_type)

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

    return render_template('bookie_stats.html', combined=combined, net_bankroll=totals[0], net_wagered=totals[1], net_wagerable=totals[2], net_total=totals[3], bookies=bookies)

@app.route('/transfer_funds', methods=["POST"])
def transfer_funds():
    send_bookie = request.form['sending_bookie']
    receiving_bookie = request.form['receiving_bookie']
    amount = float(request.form['amount'])

    transfer_bookie_funds(send_bookie, receiving_bookie, amount)
    update_bookie_values()

    return redirect(url_for('bookie_stats'))




@app.route('/graphs')
def graphs():
    refresh_graphs()

    return render_template('graphs.html')


@app.route('/graphs/data')
def graphs_data():
    """Return JSON used by interactive charts on the graphs page.
    Computes:
      - labels: list of dates (one per settled bet in chronological order)
      - running_net: cumulative net over bets
      - running_ev: cumulative EV over bets
      - constant_bet_net / ev: constant $5 bet equivalent arrays
      - per_bookie: dict mapping bookie -> cumulative net array (aligned with labels)
      - odds_categories: list of category labels
      - odds_win_percentages, odds_nets: arrays per category
    """
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""SELECT date, bookie, net, odds, this_EV, bet_EV, bet_amount, outcome FROM bets
                      WHERE outcome IN ('win','loss') ORDER BY date(date) ASC""")
    rows = cursor.fetchall()

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

    # bookies list and per-bookie cumulative
    bookies = get_ev_bookies()
    per_bookie = {b: [] for b in bookies}
    cum_bookie = {b: 0 for b in bookies}
    # per-bookie individual series: cumulative net only when that bookie had a bet
    per_bookie_individual = {b: [] for b in bookies}
    per_bookie_individual_ev = {b: [] for b in bookies}
    cum_bookie_ev = {b: 0 for b in bookies}

    # odds category counters (same buckets as refresh_graphs)
    cats = ['<0', '100-200', '200-300', '300-400', '400-500', '500-600', '600-700', '700-800', '800+']
    win_counts = [0]*len(cats)
    loss_counts = [0]*len(cats)
    net_by_cat = [0]*len(cats)

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
        bet_ev_100 = row['bet_EV'] if 'bet_EV' in row.keys() else None
        bet_amount = row['bet_amount'] if 'bet_amount' in row.keys() else None
        outcome = row['outcome']

        # labels: use date per bet (keeps same length as original image plots)
        labels.append(date)

        # running totals
        r_net += net
        r_ev += this_ev
        bet_num += 1
        running_net.append(r_net)
        running_ev.append(r_ev)

        # constant $5 bet approx (same logic as refresh_graphs)
        if outcome == 'win':
            if odds < 0:
                const = (100/abs(odds)) * 5
            else:
                const = (odds/100) * 5
            # Compute EV for a $5 stake. Prefer bet_EV (EV per 100 units) if available, else scale this_EV by stake ratio.
            if bet_ev_100:
                const_ev = bet_ev_100 / 20
            elif bet_amount and bet_amount != 0:
                const_ev = this_ev * (5.0 / bet_amount)
            else:
                const_ev = this_ev
            r_const_net += const
            r_const_ev += const_ev
        else:  # loss
            const = -5
            if bet_ev_100:
                const_ev = bet_ev_100 / 20
            elif bet_amount and bet_amount != 0:
                const_ev = this_ev * (5.0 / bet_amount)
            else:
                const_ev = this_ev
            r_const_net += const
            r_const_ev += const_ev

        constant_bet_arr.append(r_const_net)
        constant_bet_ev_arr.append(r_const_ev)

        # per-bookie cumulative (aligned with overall labels)
        if bookie not in cum_bookie:
            # if an unexpected bookie appears, add it dynamically
            cum_bookie[bookie] = 0
            per_bookie[bookie] = [0] * (len(labels) - 1)
            per_bookie_individual[bookie] = []
            bookies.append(bookie)

        cum_bookie[bookie] += net
        for b in bookies:
            per_bookie[b].append(cum_bookie.get(b, 0))

        # per-bookie individual cumulative: append only when this row is for that bookie
        if bookie not in per_bookie_individual:
            per_bookie_individual[bookie] = []
            per_bookie_individual_ev[bookie] = []
            cum_bookie_ev[bookie] = 0
        per_bookie_individual[bookie].append(cum_bookie[bookie])
        # track per-bookie EV (cumulative for that bookie only)
        cum_bookie_ev[bookie] += this_ev
        per_bookie_individual_ev[bookie].append(cum_bookie_ev[bookie])

        # odds buckets
        idx = cat_index(odds)
        if outcome == 'win':
            win_counts[idx] += 1
        else:
            loss_counts[idx] += 1
        net_by_cat[idx] += net

    # compute win percentages safely
    win_percentages = []
    for w, l in zip(win_counts, loss_counts):
        denom = w + l
        win_percentages.append((w / denom) if denom > 0 else 0)

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
        'odds_nets': net_by_cat
    })



if __name__ == '__main__':
    app.run(debug=True)


