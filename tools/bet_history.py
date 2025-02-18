import sqlite3
from datetime import datetime

def adapt_datetime(date):
    return date.isoformat()

sqlite3.register_adapter(datetime, adapt_datetime)


def create_table():
    conn = sqlite3.connect('bet_history.db')
    cursor = conn.cursor()
    #cursor.execute('DROP TABLE IF EXISTS bets;')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bets (
                bet_id INTEGER PRIMARY KEY AUTOINCREMENT,
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


def enter_bet(sport, team, bet_type, bookie, odds, bet_amount, bet_EV):
    date = datetime.now().date()
    conn = sqlite3.connect('bet_history.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO bets (sport, team, bet_type, bookie, odds, bet_amount, bet_EV, this_EV, outcome, net, date) VALUES (?,?,?,?,?,?,?,?,?,?,?)      
                ''', (sport, team, bet_type, bookie, odds, bet_amount, bet_EV, round(bet_EV*(bet_amount/100), 2), 'Pending', 0, date))
    conn.commit()
    conn.close()
    

def update_bet(bet_id, outcome, net):
    conn = sqlite3.connect('bet_history.db')
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE bets
    SET outcome = ?, net = ?
    WHERE bet_id = ?
    ''', (outcome, net, bet_id))

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
    print(f"{'Bet ID':<8}{'Sport':<35}{'Team':<35}{'Bet_Type':<15}{'Bookie':<15}{'Odds':<15}{'Bet Amount':<15}{'EV (/100)':<12}{'This EV':<12}{'Outcome':<12}{'Net':<8}{'Date':<12}")
    print("-" * 200)

    for bet in bets:
        bet_id, sport, team, bet_type, bookie, odds, bet_amount, bet_EV, this_EV, outcome, net, date = bet
        print(f"{bet_id:<8}{sport:<35}{team:<35}{bet_type:<15}{bookie:<15}{odds:<15}{bet_amount:<15}{bet_EV:<12}{this_EV:<12}{outcome:<12}{net:<8}{date:<12}")



"""
enter_bet('icehockey_liiga', 'SaiPa', 'Moneyline', 'draftkings', -210, 25, 0.38)
enter_bet('soccer_england_league2', 'Harrogate Town', 'Moneyline', 'betrivers', 310, 5, 4.59)
enter_bet('boxing_boxing', 'Floyd Scholfield', 'Moneyline', 'betrivers', 1050, 5, 33.05)
enter_bet('soccer_belgium_first_div', 'Draw (Genk v Gent)', 'Moneyline', 'betrivers', 335, 5, 4.79)
enter_bet('soccer_china_superleague', 'Wuhan Three Towns', 'Moneyline', 'fanduel', 900, 5, 19.9)
enter_bet('soccer_china_superleague', 'Yunnan Yukun', 'Moneyline', 'fanduel', 330, 5, 9.05)
"""

display_bets()