import sqlite3
from datetime import datetime
import os
import matplotlib.pyplot as plt
import seaborn as sns

from .odds_calculator import american_to_decimal

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

def get_path():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../database'))
    db_path = os.path.join(root_dir, 'bet_history.db')
    return db_path


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
                   current_net float,
                   bets_placed int,
                   bets_settled int,
                   bets_won int,
                   bets_lost int
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

def create_evbets_table():
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''DROP TABLE evbets''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS evbets(
                    bet_id VARCHAR(35) PRIMARY KEY,
                    sport VARCHAR(50),
                    team VARCHAR(50),
                    odds INTEGER,
                    bet_EV INT,
                    kelly_percent INT,
                    date VARCHAR(10),
                    kelly_wager INT
                   );''')
    
    cursor.execute('''DROP TABLE evbets_bookies''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS evbets_bookies(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bet_id VARCHAR(35),
                    bookie VARCHAR(20),
                    FOREIGN KEY (bet_id) REFERENCES evbets(bet_id) ON DELETE CASCADE
                   );''')
    
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

    total_bankroll = 0
    total_wagered = 0
    total_wagerable = 0
    net_total = 0

    for bookie in bookies_data:
        total_bankroll += bookie['total_bankroll']
        total_wagered += bookie['currently_wagered']
        total_wagerable += bookie['wagerable']
        net_total += bookie['current_net']

    conn.close()
    print("Close db in get_bookies_table")
    return bookies_data, (total_bankroll, total_wagered, total_wagerable, net_total)



def enter_bet(bet_id, sport, team, bet_type, bookie, odds, bet_amount, bet_EV, date):
    print("Open db enter_bet")
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    #print(f"bet_id: {bet_id}")
    bet_amount = int(bet_amount)
    cursor.execute('''
    INSERT INTO bets (bet_id, sport, team, bet_type, bookie, odds, bet_amount, bet_EV, this_EV, outcome, net, date) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)      
                ''', (bet_id, sport, team, bet_type, bookie, odds, bet_amount, bet_EV, round(bet_EV*(bet_amount/100), 2), 'Pending', 0, date))
    
    cursor.execute('''DELETE FROM evbets WHERE bet_id = ?''', (bet_id,))

    conn.commit()
    conn.close()
    print("Close db enter_bet")


def enter_bonus_bet(bet_id, sport, team, bookie, odds, bet_amount, bet_EV, date):
    print("Open db enter_bonus_bet")
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO bets (bet_id, sport, team, bet_type, bookie, odds, bet_amount, bet_EV, this_EV, outcome, net, date) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)      
                ''', (bet_id,sport, team, 'Bonus', bookie, odds, bet_amount, bet_EV, round(bet_EV*(bet_amount/100), 2), 'Pending', 0, date))
    
    cursor.execute('''DELETE FROM evbets WHERE bet_id = ?''', (bet_id,))

    conn.commit()
    conn.close()
    print("Close db enter_bonus_bet")


def get_current_evbets():
    print("Open db get_current_evbets")
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM evbets''')
    bets = cursor.fetchall()

    evbets = []
    for bet in bets:
        bet_id = bet[0]
        cursor.execute('''SELECT bookie FROM evbets_bookies WHERE bet_id=?''',(bet_id,))
        bookie_list = [bookie[0] for bookie in cursor.fetchall()]
        bet = list(bet)
        bet.insert(3, bookie_list)
        evbets.append(bet)

    conn.close()
    print("Close db get_current_evbets")
    return evbets


def get_evbet_bookies(bet_id):
    print("Open db get_evbet_bookies")
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''SELECT bookie FROM evbets_bookies WHERE bet_id = ?''', (bet_id,))
    data = cursor.fetchall()

    conn.commit()
    conn.close()

    print("Close db get_evbet_bookies")
    return data


def update_evbets(bets):
    print("Open db update_evbets")
    create_evbets_table()
    
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    for bet in bets:
        sport, bet_id, team, bookie_list, odds, bet_ev, kelly_percent, date, kelly_wager = bet
        cursor.execute('''INSERT OR REPLACE INTO evbets (bet_id, sport, team, odds, bet_EV, kelly_percent, date, kelly_wager) VALUES (?,?,?,?,?,?,?,?)''', 
                        (bet_id, sport, team, int(odds), bet_ev, kelly_percent, date, kelly_wager))
        for bookie in bookie_list:
            cursor.execute('''INSERT OR REPLACE INTO evbets_bookies (bet_id, bookie) VALUES (?,?)''', (bet_id, bookie))
    
    conn.commit()
    conn.close()

    print("Close db update_evbets")


def print_evbets():
    print("Open db print_evbets")
    
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM evbets''')
    data = cursor.fetchall()
    conn.close()

    for bet in data:
        sport, bet_id, team, bookie_list, odds, bet_ev, kelly_percent, date, kelly_wager = bet
        print(f"{bet_id:<34}{sport:<37}{team:<49}{bookie_list:<20}{odds:<6}{bet_ev:<10}{kelly_percent<10}{date:<12}{kelly_wager<10}")
        print()


    print("Close db print_evbets")


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


def update_bet_type(bet_id, new_type):
    """Update the bet_type for an existing bet."""
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''UPDATE bets SET bet_type = ? WHERE bet_id = ?''', (new_type, bet_id))

    conn.commit()
    conn.close()
    print("Close db update_bet_type")

    
def get_total_bankroll():
    print("Open db get_total_bankroll")
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    ev_bookie_list = ['draftkings', 'fanduel', 'betmgm', 'betrivers', 'ballybet', 'espnbet', 'fanatics', 'williamhill_us', 'cash']

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

    cursor.execute('''INSERT INTO bookies (bookmaker, deposit_total, withdrawal_total, total_bankroll, currently_wagered, wagerable, current_net)
                    VALUES(?,?,?,?,?,?,?)''', (name, deposit, withdrawn, bankroll, wagered, wagerable, net))
    conn.commit()
    conn.close()

    

def update_outcome(bet_id, outcome):
    db_path = get_path()
    conn = sqlite3.connect(db_path)

    cursor = conn.cursor()
    cursor.execute('''SELECT odds, bet_amount, bookie, bet_type FROM bets WHERE bet_id = ?''', (bet_id,))
    response = cursor.fetchall()
    odds = response[0][0]
    bet_amount = response[0][1]
    bookie = response[0][2]
    bet_type = response[0][3]
    this_bet_net = 0

    if outcome == 'win':
        if odds < 0:
            this_bet_net = (100/abs(odds)) * bet_amount
        else:
            this_bet_net = (odds/100) * bet_amount
    elif outcome == 'loss':
        # For bonus bets, net is 0 when lost (no money wagered from bankroll)
        if bet_type == 'Bonus':
            this_bet_net = 0
        else:
            this_bet_net = -bet_amount
    else:
        this_bet_net = 0

    this_bet_net = round(this_bet_net, 2)

    cursor.execute('''UPDATE bets SET outcome = ?, net = ? WHERE bet_id = ?''', (outcome, this_bet_net, bet_id))


    conn.commit()
    conn.close()



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
    print(f"{'Bet ID':<34}{'Sport':<37}{'Team':<55}{'Bet_Type':<12}{'Bookie':<13}{'Odds':<6}{'Bet Amount':<12}{'EV (/100)':<10}{'This EV':<10}{'Outcome':<10}{'Net':<7}{'Date':<12}")
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
        print(f"{bet_id:<34}{sport:<37}{team:<55}{bet_type:<12}{bookie:<13}{odds:<6}{bet_amount:<12}{bet_EV:<10}{this_EV:<10}{outcome:<10}{net:<7}{date:<12}")
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



def get_ev_bookies():
    ev_bookie_list = ['cash', 'draftkings', 'fanduel', 'betmgm', 'betrivers', 'ballybet', 'espnbet', 'fanatics', 'williamhill_us']
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
    print(f"{'id':<3}{'bookie':<15}{'deposit total':<20}{'withdrawal total':<20}{'total bankroll':<20}{'currently wagered':<20}{'wagerable amount':<20}{'current net':<15}{'bets placed':<15}{'bets settled':<15}{'bets pending':<15}{'bets won':<15}{'bets lost':<15}")
    print('-' * 200)

    total_net = 0

    for bookie in data:
        id, name, deposit, withdrawals, bankroll, wagered, wagerable, net, bets_placed, bets_settled, bets_won, bets_lost, bets_pending = bookie
        
        deposit = round(deposit, 2)
        withdrawals = round(withdrawals, 2)
        wagered = round(wagered, 2)
        wagerable = round(wagerable, 2)
        net = round(net, 2)
        
        print(f"{id:<3}{name:<20}{deposit:<20}{withdrawals:<20}{bankroll:<20}{wagered:<20}{wagerable:<20}{net:<15}{bets_placed:<15}{bets_settled:<15}{bets_pending:<15}{bets_won:<15}{bets_lost:<15}")
        total_net += net

    print()
    print(f'Net winnings across EV bookies: {round(total_net, 2)}')



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

def get_pending_ev():
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    #conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""SELECT this_EV FROM bets WHERE outcome = 'Pending'""")
    evs = cursor.fetchall()

    conn.close()

    total_ev = 0
    for ev in evs:
        total_ev += ev[0]

    return total_ev

def get_pending_wagered():
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    #conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""SELECT bet_amount FROM bets WHERE outcome = 'Pending'""")
    amounts = cursor.fetchall()

    conn.close()

    total_amount = 0
    for amount in amounts:
        total_amount += amount[0]

    return total_amount



def get_settled_bets():
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""SELECT * FROM bets WHERE outcome = 'loss' or outcome = 'win'""")
    bets = cursor.fetchall()

    total_ev = 0
    total_net = 0
    bets_won = 0
    bets_lost = 0

    for bet in bets:
        this_ev = bet['this_ev']
        this_net = bet['net']
        total_ev += this_ev
        total_net += this_net

        if bet['outcome'] == 'win':
            bets_won += 1
        elif bet['outcome'] == 'loss':
            bets_lost += 1
        else:
            print('result not found')
            continue


    conn.close()

    return (bets, (total_ev, total_net), (bets_won, bets_lost))



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


def update_bookie_values():
    ev_bookie_list = ['draftkings', 'fanduel', 'betmgm', 'betrivers', 'ballybet', 'espnbet', 'fanatics', 'cash', 'williamhill_us']
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



def get_bookie_withdrawal(bookie):
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''SELECT withdrawal_total FROM bookies WHERE bookmaker=?''',(bookie,)) 
    num = cursor.fetchone()
    conn.close()

    return num[0]

def deposit(bookie, amount):
    curr_deposit = get_bookie_deposit(bookie)
    new_deposit = curr_deposit + amount

    db_path = get_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''UPDATE bookies SET deposit_total = ? WHERE bookmaker = ?''', (new_deposit, bookie))

    conn.commit()
    conn.close()
    


def get_bookie_deposit(bookie):
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''SELECT deposit_total FROM bookies WHERE bookmaker=?''',(bookie,)) 
    num = cursor.fetchone()
    conn.close()

    return num[0]



def transfer_bookie_funds(sending_bookie, receive_bookie, amount):
    if amount < 0:
        print("Not a valid amount")
        return

    sending_bookie_wagerable = get_bookie_wagerable_amount(sending_bookie)
    receive_bookie_wagerable = get_bookie_wagerable_amount(receive_bookie)

    if sending_bookie_wagerable < amount:
        print("Not enough funds")
        return
    
    sending_bookie_new_wagerable = sending_bookie_wagerable - amount
    receive_bookie_new_wagerable = receive_bookie_wagerable + amount

    sending_bookie_withdrawal = get_bookie_withdrawal(sending_bookie)
    sending_bookie_new_withdrawal = sending_bookie_withdrawal + amount

    receive_bookie_deposit = get_bookie_deposit(receive_bookie)
    receive_booke_new_deposit = receive_bookie_deposit + amount

    db_path = get_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''UPDATE bookies SET withdrawal_total = ?, wagerable = ? WHERE bookmaker = ?''',(sending_bookie_new_withdrawal, sending_bookie_new_wagerable, sending_bookie))
    cursor.execute('''UPDATE bookies SET deposit_total = ?, wagerable = ? WHERE bookmaker = ?''',(receive_booke_new_deposit, receive_bookie_new_wagerable, receive_bookie))    

    conn.commit()
    conn.close()





def refresh_graphs():
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''SELECT * FROM bets ORDER BY date(date) ASC''')
    data = cursor.fetchall()
    conn.close()

    bet_num = 0

    running_net = 0
    running_ev = 0
    running_constant_bet_net = 0
    running_constant_bet_ev = 0
    bets_won_negative = 0
    bets_lost_negative = 0
    bets_won_100_200 = 0
    bets_lost_100_200 = 0
    bets_won_200_300 = 0
    bets_lost_200_300 = 0
    bets_won_300_400 = 0
    bets_lost_300_400 = 0
    bets_won_400_500 = 0
    bets_lost_400_500 = 0
    bets_won_500_600 = 0
    bets_lost_500_600 = 0
    bets_won_600_700 = 0
    bets_lost_600_700 = 0
    bets_won_700_800 = 0
    bets_lost_700_800 = 0
    bets_won_800_plus = 0
    bets_lost_800_plus = 0

    net_negative = 0
    net_100_200 = 0
    net_200_300 = 0
    net_300_400 = 0
    net_400_500 = 0
    net_500_600 = 0
    net_600_700 = 0
    net_700_800 = 0
    net_800_plus = 0

    net_arr = []
    ev_net_arr = []
    constant_bet_arr = []
    constant_bet_ev_arr = []


    for bet in data:
        if bet['outcome'] == 'win':
            running_net += bet['net']
            running_ev += bet['this_EV']
            bet_num += 1
            net_arr.append(running_net)
            ev_net_arr.append(running_ev)


            odds = bet['odds']
            if odds < 0:
                constant_bet = (100/abs(odds)) * 5
                bets_won_negative += 1
            else:
                constant_bet = (odds/100) * 5
                
                match odds:
                    case x if odds<0:
                        bets_won_negative += 1
                        net_negative += bet['net']
                    case x if odds<200:
                        bets_won_100_200 += 1
                        net_100_200 += bet['net']
                    case x if odds<300:
                        bets_won_200_300 += 1
                        net_200_300 += bet['net']
                    case x if odds<400:
                        bets_won_300_400 += 1
                        net_300_400 += bet['net']
                    case x if odds<500:
                        bets_won_400_500 += 1
                        net_400_500 += bet['net']
                    case x if odds<600:
                        bets_won_500_600 += 1
                        net_500_600 += bet['net']
                    case x if odds<700:
                        bets_won_600_700 += 1
                        net_600_700 += bet['net']
                    case x if odds<800:
                        bets_won_700_800 += 1
                        net_700_800 += bet['net']
                    case x if odds>=800:
                        bets_won_800_plus += 1
                        net_800_plus += bet['net']
                    case _:
                        print("not found")

            constant_bet_ev = bet['bet_EV']/20

            running_constant_bet_net += constant_bet
            running_constant_bet_ev += constant_bet_ev

            constant_bet_arr.append(running_constant_bet_net)
            constant_bet_ev_arr.append(running_constant_bet_ev)

            
        elif bet['outcome'] == 'loss':
            running_net += bet['net']
            running_ev += bet['this_EV']
            bet_num += 1
            net_arr.append(running_net)
            ev_net_arr.append(running_ev)

            constant_bet_ev = bet['bet_EV']/20

            running_constant_bet_net -= 5
            running_constant_bet_ev += constant_bet_ev

            constant_bet_arr.append(running_constant_bet_net)
            constant_bet_ev_arr.append(running_constant_bet_ev)

            this_bet_odds = bet['odds']

            match this_bet_odds:
                case x if this_bet_odds<0:
                    bets_lost_negative += 1
                    net_negative += bet['net']
                case x if this_bet_odds<200:
                    bets_lost_100_200 += 1
                    net_100_200 += bet['net']
                case x if this_bet_odds<300:
                    bets_lost_200_300 += 1
                    net_200_300 += bet['net']
                case x if this_bet_odds<400:
                    bets_lost_300_400 += 1
                    net_300_400 += bet['net']
                case x if this_bet_odds<500:
                    bets_lost_400_500 += 1
                    net_400_500 += bet['net']
                case x if this_bet_odds<600:
                    bets_lost_500_600 += 1
                    net_500_600 += bet['net']
                case x if this_bet_odds<700:
                    bets_lost_600_700 += 1
                    net_600_700 += bet['net']
                case x if this_bet_odds<800:
                    bets_lost_700_800 += 1
                    net_700_800 += bet['net']
                case x if this_bet_odds>=800:
                    bets_lost_800_plus += 1
                    net_800_plus += bet['net']
                case _:
                    print("not found")
        else:
            continue


    SCRIPT_DIR = os.path.dirname(__file__)
    STATIC_PATH = os.path.join(SCRIPT_DIR, '..', 'website', 'static')
    os.makedirs(STATIC_PATH, exist_ok=True)



    plt.plot(range(len(net_arr)), net_arr)
    plt.plot(range(len(ev_net_arr)), ev_net_arr)
    plt.title("Running Net")
    plt.xlabel("Bet Number")
    plt.ylabel("Net Value")
    plt.legend(["running net", "running EV"])
    plt.savefig(os.path.join(STATIC_PATH, "graph1.png"))
    plt.clf()


    plt.plot(range(len(constant_bet_arr)), constant_bet_arr)
    plt.plot(range(len(constant_bet_ev_arr)), constant_bet_ev_arr)
    plt.title("Bet Size $5")
    plt.xlabel("Bet Number")
    plt.ylabel("Net Value")
    plt.legend(["running net", "running EV"])
    #plt.savefig("website/static/graph2.png")
    plt.savefig(os.path.join(STATIC_PATH, "graph2.png"))
    plt.clf()


    negative_win_percentage = bets_won_negative/(bets_won_negative+bets_lost_negative) if (bets_won_negative+bets_lost_negative)>0 else 0
    odds_100_200_win_percentage = bets_won_100_200/(bets_won_100_200+bets_lost_100_200)
    odds_200_300_win_percentage = bets_won_200_300/(bets_won_200_300+bets_lost_200_300)
    odds_300_400_win_percentage = bets_won_300_400/(bets_won_300_400+bets_lost_300_400)
    odds_400_500_win_percentage = bets_won_400_500/(bets_won_400_500+bets_lost_400_500)
    odds_500_600_win_percentage = bets_won_500_600/(bets_won_500_600+bets_lost_500_600)
    odds_600_700_win_percentage = bets_won_600_700/(bets_won_600_700+bets_lost_600_700)
    odds_700_800_win_percentage = bets_won_700_800/(bets_won_700_800+bets_lost_700_800)
    odds_800_plus_win_percentage = bets_won_800_plus/(bets_won_800_plus+bets_lost_800_plus)
    odds_categories = ['<0', '100-200', '200-300', '300-400', '400-500', '500-600', '600-700', '700-800', '800+']

    sns.barplot(x=odds_categories, y=[negative_win_percentage, odds_100_200_win_percentage, odds_200_300_win_percentage, odds_300_400_win_percentage, odds_400_500_win_percentage, odds_500_600_win_percentage, odds_600_700_win_percentage, odds_700_800_win_percentage, odds_800_plus_win_percentage], 
                width=0.5)
    plt.title("Win Percentage across Odds Ranges")
    plt.xlabel("Odds Ranges")
    plt.xticks(rotation=35)
    plt.ylabel("Win Percentage")
    plt.savefig(os.path.join(STATIC_PATH, "graph3.png"))
    plt.clf()




    sns.barplot(x=odds_categories, y=[net_negative, net_100_200, net_200_300, net_300_400, net_400_500, net_500_600, net_600_700, net_700_800, net_800_plus],
                width=0.5)
    plt.title("Net across Odds Ranges")
    plt.xlabel("Odds Ranges")
    plt.xticks(rotation=35)
    plt.ylabel("Net Amount")
    plt.savefig(os.path.join(STATIC_PATH, "graph4.png"))
    plt.clf()




#display_all_bets()