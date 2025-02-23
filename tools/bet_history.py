import sqlite3
from datetime import datetime
import numpy as np
import requests
import os
from .bookies import update_bookie

def adapt_datetime(date):
    return date.isoformat()

sqlite3.register_adapter(datetime, adapt_datetime)


def create_tables():
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS bets (
                bet_id VARCHAR(35) PRIMARY KEY,
                sport VARCHAR(50),
                team VARCHAR(50),
                bet_type VARCHAR(50),
                bookie VARCHAR(50),
                odds INT,
                bet_amount INT,
                bet_EV INT,
                this_EV INT,
                outcome VARCHAR(10),
                net INT,
                date VARCHAR(10)
                );""")
    
    conn.commit()
    conn.close()


def enter_bet(bet_id, sport, team, bet_type, bookie, odds, bet_amount, bet_EV, date):
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO bets (bet_id, sport, team, bet_type, bookie, odds, bet_amount, bet_EV, this_EV, outcome, net, date) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)      
                ''', (bet_id,sport, team, bet_type, bookie, odds, bet_amount, bet_EV, round(bet_EV*(bet_amount/100), 2), 'Pending', 0, date))

    conn.commit()
    conn.close()

    update_bookie(bookie, bet_amount, -bet_amount)


def enter_bonus_bet(bet_id, sport, team, bookie, odds, bet_amount, bet_EV, date):
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO bets (bet_id, sport, team, bet_type, bookie, odds, bet_amount, bet_EV, this_EV, outcome, net, date) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)      
                ''', (bet_id,sport, team, 'Bonus', bookie, odds, bet_amount, bet_EV, round(bet_EV*(bet_amount/100), 2), 'Pending', 0, date))

    conn.commit()
    conn.close()


def bet_exists(bet_id):
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT 1 FROM bets WHERE bet_id = ?", (bet_id,))
    exists = cursor.fetchone() is not None
    
    conn.close()
    return exists
    

def update_bet(bet_id, outcome):
    db_path = get_path()
    conn = sqlite3.connect(db_path)

    cursor = conn.cursor()
    cursor.execute('''SELECT odds, bet_amount, bookie FROM bets WHERE bet_id = ?''', (bet_id,))
    response = cursor.fetchall()
    odds = response[0][0]
    bet_amount = response[0][1]
    bookie = response[0][2]
    net = 0

    if outcome == 'win':
        if odds < 0:
            net = (100/abs(odds)) * bet_amount
        else:
            net = (odds/100) * bet_amount
    elif outcome == 'loss':
        net = -bet_amount
    else:
        net = 0


    cursor.execute('''UPDATE bets SET outcome = ?, net = ? WHERE bet_id = ?''', (outcome, net, bet_id))


    conn.commit()
    conn.close()

    if outcome == 'win':
        update_bookie(bookie, -bet_amount, net)
    elif outcome == 'loss':
        update_bookie(bookie, -bet_amount, 0)
    else:
        update_bookie(bookie, -bet_amount, bet_amount)

def delete_bet(bet_id):
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''SELECT odds, bet_amount, bookie FROM bets WHERE bet_id = ?''', (bet_id,))
    response = cursor.fetchall()
    bet_amount = response[0][1]
    bookie = response[0][2]

    
    cursor.execute('''DELETE FROM bets WHERE bet_id=?''', (bet_id,))

    conn.commit()
    conn.close()

    #update_bookie(bookie, -bet_amount, bet_amount)

def display_all_bets():
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM bets")
    bets = cursor.fetchall()

    conn.close()

    if not bets:
        print("No bets to display.")
        return

    print()
    print(f"{'Bet ID':<34}{'Sport':<37}{'Team':<49}{'Bet_Type':<12}{'Bookie':<13}{'Odds':<6}{'Bet Amount':<12}{'EV (/100)':<10}{'This EV':<10}{'Outcome':<10}{'Net':<5}{'Date':<12}")
    print("-" * 207)

    counter = 1

    for bet in bets:
        bet_id, sport, team, bet_type, bookie, odds, bet_amount, bet_EV, this_EV, outcome, net, date = bet
        if counter%4==0:
            print("- " * 104)
            counter=1
        print(f"{bet_id:<34}{sport:<37}{team:<49}{bet_type:<12}{bookie:<13}{odds:<6}{bet_amount:<12}{bet_EV:<10}{this_EV:<10}{outcome:<10}{net:<5}{date:<12}")
        counter+=1
        

def get_pending_ids():
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''SELECT bet_id FROM bets WHERE outcome = "Pending"''')

    bet_ids = cursor.fetchall()
    conn.close()

    clean_bet_ids = []
    for x in bet_ids:
        clean_bet_ids.append(x[0])

    return clean_bet_ids

def display_pending_bets():
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""SELECT * FROM bets WHERE outcome = 'Pending'""")
    bets = cursor.fetchall()

    conn.close()

    if not bets:
        print("No bets to display.")
        return

    print()
    print(f"{'Bet ID':<34}{'Sport':<37}{'Team':<49}{'Bet_Type':<12}{'Bookie':<13}{'Odds':<6}{'Bet Amount':<12}{'EV (/100)':<10}{'This EV':<10}{'Outcome':<10}{'Net':<5}{'Date':<12}")
    print("-" * 207)

    counter = 1

    for bet in bets:
        bet_id, sport, team, bet_type, bookie, odds, bet_amount, bet_EV, this_EV, outcome, net, date = bet
        if counter%4==0:
            print("- " * 104)
            counter=1
        print(f"{bet_id:<34}{sport:<37}{team:<49}{bet_type:<12}{bookie:<13}{odds:<6}{bet_amount:<12}{bet_EV:<10}{this_EV:<10}{outcome:<10}{net:<5}{date:<12}")
        counter+=1



#initially had the date as when i entered the bet - changed updated table entries so that the date reflects when the game is, not the enter date
def update_dates(bet_ids):
    for x in bet_ids:
        db_path = get_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute('''SELECT sport FROM bets WHERE bet_id = ?''', (x,))

        sport = cursor.fetchall()

        this_sport = sport[0][0]

        
        API_KEY = 'fa53e41dfc61191562135b54ca8dee4d'
        SPORT = this_sport # use the sport_key from the /sports endpoint below, or use 'upcoming' to see the next 8 games across all sports
        REGIONS = 'eu' # uk | us | eu | au. Multiple can be specified if comma delimited
        MARKETS = 'h2h' # h2h | spreads | totals. Multiple can be specified if comma delimited
        ODDS_FORMAT = 'american' # decimal | american
        DATE_FORMAT = 'iso' # iso | unix
        
        odds_response = requests.get(f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds/?apiKey={API_KEY}&regions={REGIONS}&markets={MARKETS}', params={
            'api_key': API_KEY,
            'sports': SPORT,
            'regions': REGIONS,
            'markets': MARKETS,
            'oddsFormat': ODDS_FORMAT,
            'dateFormat': DATE_FORMAT,
            'eventIds': x,
        })

        if odds_response.status_code != 200:
            print(f'Failed to get games: status_code {odds_response.status_code}, response body {odds_response.text}')
            return []

        data = odds_response.json()

        commence_time = data[0]['commence_time'] if data else None

        if not commence_time:
            continue

        commence_date = commence_time[:10]

        cursor.execute('''UPDATE bets SET date = ? WHERE bet_id = ?''', (commence_date, x))

        conn.commit()
        conn.close()

        display_all_bets()

def display_settled_bets():
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""SELECT * FROM bets WHERE outcome = 'loss' or outcome = 'win'""")
    bets = cursor.fetchall()

    conn.close()

    if not bets:
        print("No bets to display.")
        return

    print()
    print(f"{'Bet ID':<34}{'Sport':<37}{'Team':<49}{'Bet_Type':<12}{'Bookie':<13}{'Odds':<6}{'Bet Amount':<12}{'EV (/100)':<10}{'This EV':<10}{'Outcome':<10}{'Net':<5}{'Date':<12}")
    print("-" * 207)

    counter = 1

    total_net = 0
    expected_total = 0

    for bet in bets:
        bet_id, sport, team, bet_type, bookie, odds, bet_amount, bet_EV, this_EV, outcome, net, date = bet
        total_net += net
        expected_total += this_EV
        if counter%4==0:
            print("- " * 104)
            counter=1
        print(f"{bet_id:<34}{sport:<37}{team:<49}{bet_type:<12}{bookie:<13}{odds:<6}{bet_amount:<12}{bet_EV:<10}{this_EV:<10}{outcome:<10}{net:<5}{date:<12}")
        counter+=1
    
    print()
    print(f"Expected total: {round(expected_total,2)}")
    print(f"Net total: {total_net}")



def get_path():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    db_path = os.path.join(root_dir, 'bet_history.db')

    return db_path

def edit_odds(game_id, odds):
    db_path = get_path()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""UPDATE bets SET odds = ? WHERE bet_id = ?""", (odds, game_id))

    conn.commit()
    conn.close()

def display_bookie_bets(bookie):
    db_path = get_path()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''SELECT * FROM bets WHERE bookie = ?''', (bookie,))
    data = cursor.fetchall()

    conn.close()

    if not data:
        print("No bets to display")
        return
    
    print()
    print(f"{'Bet ID':<34}{'Sport':<37}{'Team':<49}{'Bet_Type':<12}{'Bookie':<13}{'Odds':<6}{'Bet Amount':<12}{'EV (/100)':<10}{'This EV':<10}{'Outcome':<10}{'Net':<5}{'Date':<12}")
    print("-" * 207)

    total_net = 0
    expected_total = 0

    counter = 1
    for line in data:
        bet_id, sport, team, bet_type, bookie, odds, bet_amount, bet_EV, this_EV, outcome, net, date = line
        total_net += net
        expected_total += this_EV
        if counter%4==0:
            print("- " * 104)
            counter=1
        print(f"{bet_id:<34}{sport:<37}{team:<49}{bet_type:<12}{bookie:<13}{odds:<6}{bet_amount:<12}{bet_EV:<10}{this_EV:<10}{outcome:<10}{net:<5}{date:<12}")
        counter+=1

    print()
    print(f"Expected total: {round(expected_total,2)}")
    print(f"Net total: {total_net}")



