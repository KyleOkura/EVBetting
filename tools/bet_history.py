import sqlite3
from datetime import datetime
import numpy as np

def adapt_datetime(date):
    return date.isoformat()

sqlite3.register_adapter(datetime, adapt_datetime)


def create_table():
    conn = sqlite3.connect('bet_history.db')
    cursor = conn.cursor()
    #cursor.execute('DROP TABLE IF EXISTS bets;')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bets (
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
                );
                ''')
    
    conn.commit()
    conn.close()


def enter_bet(bet_id, sport, team, bet_type, bookie, odds, bet_amount, bet_EV):
    date = datetime.now().date()
    conn = sqlite3.connect('bet_history.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO bets (bet_id, sport, team, bet_type, bookie, odds, bet_amount, bet_EV, this_EV, outcome, net, date) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)      
                ''', (bet_id,sport, team, bet_type, bookie, odds, bet_amount, bet_EV, round(bet_EV*(bet_amount/100), 2), 'Pending', 0, date))
    conn.commit()
    conn.close()

def bet_exists(bet_id):
    conn = sqlite3.connect("bet_history.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT 1 FROM bets WHERE bet_id = ?", (bet_id,))
    exists = cursor.fetchone() is not None
    
    conn.close()
    return exists
    

def update_bet(bet_id, net, outcome):
    conn = sqlite3.connect('bet_history.db')
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE bets
    SET outcome = ?, net = ?
    WHERE bet_id = ?
    ''', (outcome, net, bet_id))

    conn.commit()
    conn.close()

def delete_bet(bet_id):
    conn = sqlite3.connect('bet_history.db')
    cursor = conn.cursor()
    cursor.execute('''
    DELETE FROM bets WHERE bet_id=?
    ''', (bet_id,))

    conn.commit()
    conn.close()

def display_bets():
    conn = sqlite3.connect('bet_history.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM bets")
    bets = cursor.fetchall()

    conn.close()

    if not bets:
        print("No bets to display.")
        return

    print()
    print(f"{'Bet ID':<34}{'Sport':<35}{'Team':<50}{'Bet_Type':<12}{'Bookie':<13}{'Odds':<6}{'Bet Amount':<12}{'EV (/100)':<10}{'This EV':<10}{'Outcome':<10}{'Net':<5}{'Date':<12}")
    print("-" * 205)

    for bet in bets:
        bet_id, sport, team, bet_type, bookie, odds, bet_amount, bet_EV, this_EV, outcome, net, date = bet
        '''
        odds = odds.decode('utf-8') if isinstance(odds, bytes) else odds
        print(f"{bet_id:<34}{sport:<30}{team:<50}{bet_type:<12}{bookie:<13}"
        f"{int(odds) if isinstance(odds, np.integer) else float(odds) if isinstance(odds, np.floating) else odds:<7}"
        f"{bet_amount:<12}{bet_EV:<12}{this_EV:<10}{outcome:<10}{net:<6}{date:<12}")

        '''
        print(f"{bet_id:<34}{sport:<35}{team:<50}{bet_type:<12}{bookie:<13}{odds:<6}{bet_amount:<12}{bet_EV:<10}{this_EV:<10}{outcome:<10}{net:<5}{date:<12}")
        
#create_table()

"""
enter_bet('2fb7ce1eb6a7a1be2780ebdeeb591f52', 'icehockey_liiga', 'SaiPa', 'Moneyline', 'draftkings', -210, 25, 0.38)
enter_bet('316e7c961f4f1c5ac8b37b203e10438b', 'soccer_england_league2', 'Harrogate Town', 'Moneyline', 'betrivers', 310, 5, 4.59)
enter_bet('5e07b98039bcfb67dfc55e9b42438945', 'boxing_boxing', 'Floyd Scholfield', 'Moneyline', 'betrivers', 1050, 5, 33.05)
enter_bet('8cc36d0751e0fa140487483066b95255', 'soccer_belgium_first_div', 'Draw (Genk v Gent)', 'Moneyline', 'betrivers', 335, 5, 4.79)
enter_bet('8ce8f60eb86df244b23f571dff7b9ef3', 'soccer_china_superleague', 'Wuhan Three Towns', 'Moneyline', 'fanduel', 900, 5, 19.9)
enter_bet('a724ca6ac5d0780170f9f77c5d1f6857', 'soccer_china_superleague', 'Yunnan Yukun', 'Moneyline', 'fanduel', 330, 5, 9.05)
enter_bet('c9ab1019ab4de271fa95394ac65e9d74', 'soccer_chile_campeonato', 'draw (Universidad de Chile v Union La Calera)', 'Moneyline', 'betrivers', 510, 5, 10.04)
enter_bet('f4556d715ed72f9d5831c5944aee4508', 'soccer_france_ligue_one', 'Lille', 'Moneyline', 'ballybet', 575, 5, 11.24)
enter_bet('1ee16fc6c64a9fbcaceac0d84c153fd8', 'soccer_italy_serie_a', 'draw (Bologna v Cagliari)', 'Moneyline', 'betrivers', 340, 5, 8.02)
"""

#display_bets()

