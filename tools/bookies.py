import sqlite3
import os


def create_bookies_table():
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

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
    
    conn.commit()
    conn.close()


def add_bookmaker(name, deposit, wagered, wagerable):
    bankroll = wagered + wagerable
    net = bankroll - deposit

    db_path = get_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''INSERT INTO bookies (bookmaker, deposit_total, withdrawl_total, total_bankroll, currently_wagered, wagerable, current_net)
                    VALUES(?,?,?,?,?,?,?)''', (name, deposit, 0, bankroll, wagered, wagerable, net))
    conn.commit()
    conn.close()



def update_bookie(name, wagered_change, wagerable_change):
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''SELECT total_bankroll, currently_wagered, wagerable, current_net FROM bookies WHERE bookmaker = ?''', (name))
    data = cursor.fetchall()

    bankroll, wagered, wagerable, current_net = data

    new_wagered = wagered + wagered_change
    new_wagerable = wagerable + wagerable_change

    new_bankroll = bankroll + wagerable_change + wagered_change
    new_net = current_net + wagerable_change + wagered_change

    cursor.execute('''UPDATE bookies SET total_bankroll = ?, currently_wagered = ?, wagerable = ?, current_net = ? WHERE bookmaker = ?''', (new_bankroll, new_wagered, new_wagerable, new_net))
    conn.commit()
    conn.close()


def display_bookie_table():
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''SELECT * FROM bookies''')

    data = cursor.fetchall()

    print()
    print(f"{'id':<3}{'bookie':<15}{'deposit total':<20}{'withdrawl total':<20}{'total bankroll':<20}{'currently wagered':<20}{'wagerable amount':<20}{'current net':<20}")
    print('-' * 130)

    total_net = 0

    for bookie in data:
        id, name, deposit, withdrawl, bankroll, wagered, wagerable, net = bookie
        print(f"{id:<3}{name:<20}{deposit:<20}{withdrawl:<20}{bankroll:<20}{wagered:<20}{wagerable:<20}{net:<20}")
        total_net += net

    print()
    print(f'Net across all bookies: {total_net}')



def get_path():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    db_path = os.path.join(root_dir, 'bet_history.db')

    return db_path




#display_bookie_table()