"""
One-time script: copies bookie stats from local SQLite → Turso.
Run from the EVBetting root:  python migrate_bookies.py
"""
import os, sys, sqlite3
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import libsql
from dotenv import load_dotenv

load_dotenv()

# Read from local db
local = sqlite3.connect('database/bet_history.db')
local.row_factory = sqlite3.Row
rows = local.execute('SELECT * FROM bookies').fetchall()
local.close()

# Write to Turso
turso = libsql.connect(os.getenv('TURSO_URL'), auth_token=os.getenv('TURSO_AUTH_TOKEN'))

for row in rows:
    turso.execute("""
        UPDATE bookies SET
            deposit_total     = ?,
            withdrawal_total  = ?,
            total_bankroll    = ?,
            currently_wagered = ?,
            wagerable         = ?,
            current_net       = ?,
            bets_placed       = ?,
            bets_settled      = ?,
            bets_won          = ?,
            bets_lost         = ?,
            bets_pending      = ?
        WHERE bookmaker = ?
    """, (
        row['deposit_total'], row['withdrawal_total'], row['total_bankroll'],
        row['currently_wagered'], row['wagerable'], row['current_net'],
        row['bets_placed'], row['bets_settled'], row['bets_won'],
        row['bets_lost'], row['bets_pending'], row['bookmaker'],
    ))
    print(f"Updated {row['bookmaker']}")

turso.commit()
turso.close()
print("Done.")
