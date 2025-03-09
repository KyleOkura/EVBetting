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