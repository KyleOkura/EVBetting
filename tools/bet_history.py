import sqlite3
from datetime import datetime
import numpy as np
import requests
import os

from .odds_calculator import american_to_decimal
from .odds_calculator import american_payout
'''
FUNCTION LIST
adapt_time(date)
takes date type and returns iso format

create_tables()
creates bets and bookies tables

enter_bet(bet_id, sport, team, bet_type, odds, bet_amount, bet_ev, date)
enters the bet into the bets table. Then calls update_bookie(bookie, bet_amount, -bet_amount)

enter_bonus_bet(bet_id, sport, team, bookie, odds, bet_amount, bet_EV, date)
enters bet as type bonus, and does not call update_bookie <- should call to increase wagered? and not decrease wagerable

update_bookie(name, wagered_change, wagerable_change)








add_bookmaker(name, deposit, wagered, wagerable, withdrawl)
adds bookmaker



'''






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
    """
    cursor.execute('''CREATE TABLE IF NOT EXISTS bookies(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   bookmaker VARCHAR(20),
                   deposit_total float,
                   withdrawl_total float,
                   total_bankroll float,
                   currently_wagered float,
                   wagerable float,
                   current_net float
                   );''')
    """
    
    
    conn.commit()
    conn.close()

def create_bookie_table():
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''DROP TABLE bookies''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS bookies(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   bookmaker VARCHAR(20),
                   deposit_total float,
                   withdrawl_total float,
                   total_bankroll float,
                   currently_wagered float,
                   wagerable float,
                   current_net float,
                   bets_placed int,
                   bets_settled int,
                   bets_won int,
                   bets_lost int
                   );''')
    
    
    conn.commit()
    conn.close()


def transfer_bets():
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''SELECT * FROM bookies''')
    bookies_data = cursor.fetchall()

    cursor.execute('''DROP TABLE bookies''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS bookies(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   bookmaker VARCHAR(20),
                   deposit_total float,
                   withdrawal_total float,
                   total_bankroll float,
                   currently_wagered float,
                   wagerable float,
                   current_net float,
                   bets_placed int,
                   bets_settled int,
                   bets_won int,
                   bets_lost int
                   );''')
    

    for x in bookies_data:
        name = x['bookmaker']
        deposit = x['deposit_total']
        withdrawn = x['withdrawl_total']
        bankroll = x['total_bankroll']
        wagered = x['currently_wagered']
        wagerable = x['wagerable']
        net = x['current_net']
        cursor.execute('''INSERT INTO bookies (bookmaker, deposit_total, withdrawal_total, total_bankroll, currently_wagered, wagerable, current_net, bets_placed, bets_settled, bets_won, bets_lost)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?)''', (name, deposit, withdrawn, bankroll, wagered, wagerable, net, 0, 0, 0, 0))
        
    conn.commit()
    conn.close()

    

def get_bookies_table():
    print("Open db in get_bookies_table")
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''SELECT * FROM bookies''')
    bookies_data = cursor.fetchall()

    conn.close()
    print("Close db in get_bookies_table")
    return bookies_data



def enter_bet(bet_id, sport, team, bet_type, bookie, odds, bet_amount, bet_EV, date):
    print("Open db enter_bet")
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    #print(f"bet_id: {bet_id}")
    bet_amount = int(bet_amount)
    cursor.execute('''
    INSERT INTO bets (bet_id, sport, team, bet_type, bookie, odds, bet_amount, bet_EV, this_EV, outcome, net, date) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)      
                ''', (bet_id,sport, team, bet_type, bookie, odds, bet_amount, bet_EV, round(bet_EV*(bet_amount/100), 2), 'Pending', 0, date))

    conn.commit()
    conn.close()
    print("Close db enter_bet")

    #update_bookie(bookie, bet_amount, -bet_amount)


def enter_bonus_bet(bet_id, sport, team, bookie, odds, bet_amount, bet_EV, date):
    print("Open db enter_bonus_bet")
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO bets (bet_id, sport, team, bet_type, bookie, odds, bet_amount, bet_EV, this_EV, outcome, net, date) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)      
                ''', (bet_id,sport, team, 'Bonus', bookie, odds, bet_amount, bet_EV, round(bet_EV*(bet_amount/100), 2), 'Pending', 0, date))

    conn.commit()
    conn.close()
    print("Close db enter_bonus_bet")

    #update_bookie(bookie, bet_amount, 0)



def update_bookie(name, wagered_change, wagerable_change):
    print("Open db update_bookie")
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    """
    
    id INTEGER PRIMARY KEY AUTOINCREMENT,
                   bookmaker VARCHAR(20),
                   deposit_total float,
                   withdrawal_total float,
                   total_bankroll float,
                   currently_wagered float,
                   wagerable float,
                   current_net float,
                   bets_placed int,
                   bets_settled int,
                   bets_won int,
                   bets_lost int
    
    
    """


    cursor.execute('''SELECT * FROM bookies WHERE bookmaker = ?''', (name,))
    data = cursor.fetchone()

    id, bookmaker, deposited, withdrawn, bankroll, wagered, wagerable, net, bets_placed, bets_settled, bets_won, bets_lost, bets_pending = data

    new_wagered = wagered + wagered_change
    new_wagerable = wagerable + wagerable_change

    new_bankroll = bankroll + new_wagered + new_wagerable
    new_net = withdrawn - deposited + new_bankroll

    cursor.execute('''UPDATE bookies SET total_bankroll = ?, currently_wagered = ?, wagerable = ?, current_net = ? WHERE bookmaker = ?''', (new_bankroll, new_wagered, new_wagerable, new_net, name))
    conn.commit()
    conn.close()
    print("Close db update_bookie")

    
def get_total_bankroll():
    print("Open db get_total_bankroll")
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    ev_bookie_list = ['draftkings', 'fanduel', 'betmgm', 'betrivers', 'ballybet', 'espnbet', 'fanatics']

    total_bankroll = 0
    for bookie in ev_bookie_list:
        cursor.execute('''SELECT total_bankroll FROM bookies WHERE bookmaker = ?''', (bookie,))
        data = cursor.fetchone()
        total_bankroll+=data[0]


    conn.close()
    print("Close db get_total_bankroll")

    return round(total_bankroll, 2)



def add_bookmaker(name, deposit, withdrawn, wagered, wagerable):
    bankroll = wagered + wagerable
    net = round(bankroll - deposit + withdrawn, 2)

    db_path = get_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''INSERT INTO bookies (bookmaker, deposit_total, withdrawl_total, total_bankroll, currently_wagered, wagerable, current_net)
                    VALUES(?,?,?,?,?,?,?)''', (name, deposit, withdrawn, bankroll, wagered, wagerable, net))
    conn.commit()
    conn.close()

    

def update_outcome(bet_id, outcome):
    db_path = get_path()
    conn = sqlite3.connect(db_path)

    cursor = conn.cursor()
    cursor.execute('''SELECT odds, bet_amount, bookie FROM bets WHERE bet_id = ?''', (bet_id,))
    response = cursor.fetchall()
    odds = response[0][0]
    bet_amount = response[0][1]
    bookie = response[0][2]
    this_bet_net = 0

    if outcome == 'win':
        if odds < 0:
            this_bet_net = (100/abs(odds)) * bet_amount
        else:
            this_bet_net = (odds/100) * bet_amount
    elif outcome == 'loss':
        this_bet_net = -bet_amount
    else:
        this_bet_net = 0

    this_bet_net = round(this_bet_net, 2)

    cursor.execute('''UPDATE bets SET outcome = ?, net = ? WHERE bet_id = ?''', (outcome, this_bet_net, bet_id))


    conn.commit()
    conn.close()

    #bookie_wagerable_change = this_bet_net + bet_amount

    #update_bookie(bookie, -bet_amount, bookie_wagerable_change)


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





def get_bookie_wagerable_amount(bookie):
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''SELECT wagerable FROM bookies WHERE bookmaker = ?''', (bookie,))

    wagerable_amount = cursor.fetchone()

    conn.close()

    return wagerable_amount[0]



def display_ev_bookie_table():
    #refresh_bookie_table()
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''SELECT * FROM bookies''')

    data = cursor.fetchall()

    print()
    print(f"{'id':<3}{'bookie':<15}{'deposit total':<20}{'withdrawl total':<20}{'total bankroll':<20}{'currently wagered':<20}{'wagerable amount':<20}{'current net':<20}{'bets placed':<20}{'bets settled':<20}{'bets pending':<20}{'bets won':<20}{'bets lost':<20}")
    print('-' * 130)

    total_net = 0

    for bookie in data:
        id, name, deposit, withdrawl, bankroll, wagered, wagerable, net, bets_placed, bets_settled, bets_won, bets_lost, bets_pending = bookie
        print(f"{id:<3}{name:<20}{deposit:<20}{withdrawl:<20}{bankroll:<20}{wagered:<20}{wagerable:<20}{net:<20}{bets_placed:<20}{bets_settled:<20}{bets_pending:<20}{bets_won:<20}{bets_lost:<20}")
        total_net += net

    print()
    print(f'Net winnings across EV bookies: {round(total_net, 2)}')



def get_ev_bookies():
    ev_bookie_list = ['draftkings', 'fanduel', 'betmgm', 'betrivers', 'ballybet', 'espnbet', 'fanatics']
    return ev_bookie_list




def delete_bookie(name):
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''DELETE FROM bookies WHERE bookmaker = ?''', (name,))

    conn.commit()
    conn.close()

def reset_autoincrement():
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''DELETE FROM sqlite_sequence WHERE name='bookies';''')

    conn.commit()
    conn.close()

def update_bookie_net(name, new_net):
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''UPDATE bookies SET current_net = ? WHERE bookmaker = ?''', (new_net, name))

    conn.commit()
    conn.close()


def display_bookie_table():
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''SELECT * FROM bookies''')

    data = cursor.fetchall()

    print()
    print(f"{'id':<3}{'bookie':<15}{'deposit total':<20}{'withdrawl total':<20}{'total bankroll':<20}{'currently wagered':<20}{'wagerable amount':<20}{'current net':<20}{'bets placed':<20}{'bets settled':<20}{'bets won':<20}{'bets lost':<20}")
    print('-' * 130)

    total_net = 0

    for bookie in data:
        id, name, deposit, withdrawl, bankroll, wagered, wagerable, net, bets_placed, bets_settled, bets_won, bets_lost = bookie
        print(f"{id:<3}{name:<20}{deposit:<20}{withdrawl:<20}{bankroll:<20}{wagered:<20}{wagerable:<20}{net:<20}{bets_placed:<20}{bets_settled:<20}{bets_won:<20}{bets_lost:<20}")
        total_net += net

    print()
    print(f'Net winnings across all bookies: {round(total_net, 2)}')



def bet_exists(bet_id):
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT 1 FROM bets WHERE bet_id = ?", (bet_id,))
    exists = cursor.fetchone() is not None

    if exists:
        cursor.execute("SELECT * FROM bets WHERE bet_id = ?", (bet_id,))
        print(f'exists: {exists}')
        print(cursor.fetchall())
    
    conn.close()
    return exists


def delete_bet(bet_id):
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    
    cursor.execute('''DELETE FROM bets WHERE bet_id=?''', (bet_id,))

    conn.commit()
    conn.close()



def get_all_bets():
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM bets")
    bets = cursor.fetchall()

    conn.close()
    return bets
        

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




def get_pending_bets():
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""SELECT * FROM bets WHERE outcome = 'Pending'""")
    bets = cursor.fetchall()

    conn.close()

    return bets



def get_settled_bets():
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""SELECT * FROM bets WHERE outcome = 'loss' or outcome = 'win'""")
    bets = cursor.fetchall()

    conn.close()

    return bets



def get_path():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../database'))
    db_path = os.path.join(root_dir, 'bet_history.db')
    return db_path



def get_bet(bet_id):
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bets WHERE bet_id = ?", (bet_id,))
    bet = cursor.fetchone()
    if not bet:
        print("error")
    
    conn.close()
    return bet


#updates the odds and the EVs (/100 and for this bet)
def update_bet_odds(bet_id, new_odds):
    db_path = get_path()
    conn = sqlite3.connect(db_path)

    cursor = conn.cursor()
    cursor.execute('''SELECT bet_EV, bet_amount, odds FROM bets WHERE bet_id = ?''', (bet_id,))
    response = cursor.fetchone()
    ev = response[0]
    bet_amount = response[1]
    old_odds = response[2]

    old_decimal = american_to_decimal([old_odds])
    true_prob = (ev + 100)/(100*old_decimal[0])
    new_decimal = american_to_decimal([new_odds])
    new_ev = 100*true_prob*new_decimal[0] - 100
    new_ev = round(new_ev, 2)
    
    this_new_ev = new_ev * bet_amount
    this_new_ev = round(this_new_ev/100, 2)

    cursor.execute('''UPDATE bets SET bet_EV = ?, this_EV = ?, odds = ? WHERE bet_id = ?''', (new_ev, this_new_ev, new_odds, bet_id))
    conn.commit()
    conn.close()

    
def update_date(bet_id, new_date):
    db_path = get_path()
    conn = sqlite3.connect(db_path)

    cursor = conn.cursor()
    cursor.execute('''UPDATE bets SET date = ?  WHERE bet_id = ?''', (new_date, bet_id))
    conn.commit()
    conn.close()

def update_bet_bookie(bet_id, new_bookie):
    db_path = get_path()
    conn = sqlite3.connect(db_path)

    cursor = conn.cursor()
    cursor.execute('''UPDATE bets SET bookie = ?  WHERE bet_id = ?''', (new_bookie, bet_id))
    conn.commit()
    conn.close()

#used to initially change bonus bets with negative nets
def update_bet_net(bet_id, new_net):
    db_path = get_path()
    conn = sqlite3.connect(db_path)

    cursor = conn.cursor()
    cursor.execute('''UPDATE bets SET net = ?  WHERE bet_id = ?''', (new_net, bet_id))
    conn.commit()
    conn.close()



def update_bet_amount(bet_id, new_amount):
    db_path = get_path()
    conn = sqlite3.connect(db_path)

    cursor = conn.cursor()
    cursor.execute('''SELECT bet_EV, bet_amount, bookie FROM bets WHERE bet_id = ?''', (bet_id,))
    response = cursor.fetchone()
    ev = response[0]
    old_amount = response[1]
    bookie = response[2]
    
    this_new_ev = ev * new_amount
    this_new_ev = round(this_new_ev/100, 2)

    cursor.execute('''UPDATE bets SET bet_EV = ?, this_EV = ?, bet_amount=? WHERE bet_id = ?''', (ev, this_new_ev, new_amount, bet_id))
    conn.commit()
    conn.close()

    wagered_change = new_amount - old_amount

    #update_bookie(bookie, wagered_change, 0)




def reset_bookie():
    bankroll = 126.27
    wagered = 15
    wagerable = 111.27
    net = 116.27
    bookmaker = 'espnbet'

    db_path = get_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''UPDATE bookies SET total_bankroll = ?, currently_wagered = ?, wagerable = ?, current_net = ? WHERE bookmaker = ?''', (bankroll, wagered, wagerable, net, bookmaker))
    conn.commit()
    conn.close()




def update_bookie_values():
    ev_bookie_list = ['draftkings', 'fanduel', 'betmgm', 'betrivers', 'ballybet', 'espnbet', 'fanatics']
    deposits = []
    withdraws = []

    db_path = get_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for bookie in ev_bookie_list:
        cursor.execute('''SELECT deposit_total, withdrawal_total FROM bookies WHERE bookmaker = ?''',(bookie,))
        response = cursor.fetchone()
        if response:
            deposits.append(response[0])
            withdraws.append(response[1])
        else:
            print("error")

    counter = 0

    for bookie in ev_bookie_list:
        cursor.execute('''SELECT * FROM bets WHERE bookie = ?''',(bookie,))
        response = cursor.fetchall()

        print(f'response length: {len(response)}')
        bookie_wagerable = 0
        bookie_wagered = 0
        bets_placed = 0
        bets_settled = 0
        bets_won = 0
        bets_lost = 0
        pending_bets = 0

        for x in response:
            bet_type = x[3]
            bet_amount = x[6]
            outcome = x[9]
            net = x[10]
            bets_placed += 1

            if bet_type == "Bonus":
                if outcome == "win":
                    bookie_wagerable += net
                    bets_won += 1
                    bets_settled += 1
                elif outcome == "loss":
                    bets_lost += 1
                    bets_settled += 1
                elif outcome == "Pending":
                    pending_bets += 1
                else:
                    print("status not found")
                    continue
            else:
                if outcome == "win":
                    bookie_wagerable += net
                    #bookie_wagerable += bet_amount
                    bets_won += 1
                    bets_settled += 1
                elif outcome == "loss":
                    bookie_wagerable += net
                    bets_lost += 1
                    bets_settled += 1
                elif outcome == "Pending":
                    bookie_wagered += bet_amount
                    bookie_wagerable -= bet_amount
                    pending_bets += 1
                elif outcome == "offset":
                    bookie_wagerable += net
                    bets_placed -= 1
                else:
                    print("status not found")
                    continue
        
        bookie_wagerable += deposits[counter] - withdraws[counter]
        bookie_bankroll = bookie_wagerable + bookie_wagered
        bookie_net = bookie_bankroll - deposits[counter] + withdraws[counter]

        counter += 1

        bookie_wagerable = round(bookie_wagerable, 2)
        bookie_bankroll = round(bookie_bankroll, 2)
        bookie_net = round(bookie_net, 2)

        cursor.execute('''UPDATE bookies SET total_bankroll = ?, currently_wagered = ?, wagerable = ?, current_net = ?, bets_placed = ?, bets_settled = ?, bets_won = ?, bets_lost = ?, bets_pending = ? WHERE bookmaker = ?''', (bookie_bankroll, bookie_wagered, bookie_wagerable, bookie_net, bets_placed, bets_settled, bets_won, bets_lost, pending_bets, bookie))



    conn.commit()
    conn.close()



#update_bookie_values()
#display_ev_bookie_table()





"""
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




    id INTEGER PRIMARY KEY AUTOINCREMENT,
                   bookmaker VARCHAR(20),
                   deposit_total float,
                   withdrawal_total float,
                   total_bankroll float,
                   currently_wagered float,
                   wagerable float,
                   current_net float,
                   bets_placed int,
                   bets_settled int,
                   bets_won int,
                   bets_lost int
    

                   

    cursor.execute('''DROP TABLE bookies;''')

    cursor.execute('''
                   CREATE TABLE bookies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bookmaker TEXT UNIQUE,
    deposit_total REAL DEFAULT 0.0,
    withdrawal_total REAL DEFAULT 0.0,
    total_bankroll REAL DEFAULT 0.0,
    currently_wagered REAL DEFAULT 0.0,
    wagerable REAL DEFAULT 0.0,
    current_net REAL DEFAULT 0.0,
    bets_placed INTEGER DEFAULT 0,
    bets_settled INTEGER DEFAULT 0,
    bets_won INTEGER DEFAULT 0,
    bets_lost INTEGER DEFAULT 0,
    bets_pending INTEGER DEFAULT 0
);
                   ''')
    
    cursor.execute('''
                    INSERT INTO bookies (bookmaker, deposit_total, withdrawal_total, total_bankroll, currently_wagered, wagerable, current_net, bets_placed, bets_settled, bets_won, bets_lost, bets_pending) VALUES
('draftkings', 100.0, 0.0, 20.0, 20.0, 0.0, -80.0, 8, 7, 2, 5, 0),
('fanduel', 100.0, 0.0, 6.65, 10.0, -3.35, -93.35, 30, 29, 5, 24, 0),
('betmgm', 150.0, 0.0, -18.0, 20.0, -38.0, -168.0, 9, 7, 1, 6, 0),
('betrivers', 100.0, 0.0, 143.63, 112.63, 31.0, 43.63, 60, 44, 9, 35, 0),
('ballybet', 60.0, 0.0, 64.25, 35.0, 29.25, 4.25, 14, 11, 5, 6, 0),
('espnbet', 10.0, 0.0, 40.0, 15.0, 25.0, 30.0, 13, 12, 3, 9, 0),
('fanatics', 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0, 0, 0);
''')





"""