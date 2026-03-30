"""
One-time script: copies all bets from local SQLite → Turso.
Run from the EVBetting root:  python migrate_bets.py
"""
import os, sys, sqlite3
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import libsql
from dotenv import load_dotenv

load_dotenv()

local = sqlite3.connect('database/bet_history.db')
rows = local.execute('SELECT * FROM bets').fetchall()
local.close()

turso = libsql.connect(os.getenv('TURSO_URL'), auth_token=os.getenv('TURSO_AUTH_TOKEN'))

for row in rows:
    turso.execute("""
        INSERT OR IGNORE INTO bets
            (bet_id, sport, team, bet_type, bookie, odds, bet_amount,
             bet_EV, this_EV, outcome, net, date)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """, row)

turso.commit()
turso.close()
print(f"Migrated {len(rows)} bets.")
