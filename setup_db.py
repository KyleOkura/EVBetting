"""
Run this once to create all tables in Turso and seed the bookies table.

Usage:
    cd /path/to/EVBetting
    python setup_db.py
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import libsql
from dotenv import load_dotenv

load_dotenv()
TURSO_URL = os.getenv("TURSO_URL")
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN")

conn = libsql.connect(TURSO_URL, auth_token=TURSO_AUTH_TOKEN)
cursor = conn.cursor()

# ── bets ──────────────────────────────────────────────────────────────────────
cursor.execute("""CREATE TABLE IF NOT EXISTS bets (
    bet_id      VARCHAR(35) PRIMARY KEY,
    sport       VARCHAR(50),
    team        VARCHAR(50),
    bet_type    VARCHAR(50),
    bookie      VARCHAR(50),
    odds        INT,
    bet_amount  INT,
    bet_EV      INT,
    this_EV     INT,
    outcome     VARCHAR(10),
    net         INT,
    date        VARCHAR(10)
)""")

# ── bookies ───────────────────────────────────────────────────────────────────
cursor.execute("""CREATE TABLE IF NOT EXISTS bookies (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    bookmaker           VARCHAR(20),
    deposit_total       FLOAT,
    withdrawal_total    FLOAT,
    total_bankroll      FLOAT,
    currently_wagered   FLOAT,
    wagerable           FLOAT,
    current_net         FLOAT,
    bets_placed         INT,
    bets_settled        INT,
    bets_won            INT,
    bets_lost           INT,
    bets_pending        INT
)""")

# ── evbets ────────────────────────────────────────────────────────────────────
cursor.execute("""CREATE TABLE IF NOT EXISTS evbets (
    bet_id          VARCHAR(35) PRIMARY KEY,
    sport           VARCHAR(50),
    team            VARCHAR(50),
    odds            INTEGER,
    bet_EV          INT,
    kelly_percent   INT,
    date            VARCHAR(10),
    kelly_wager     INT
)""")

# ── evbets_bookies ────────────────────────────────────────────────────────────
cursor.execute("""CREATE TABLE IF NOT EXISTS evbets_bookies (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    bet_id  VARCHAR(35),
    bookie  VARCHAR(20),
    FOREIGN KEY (bet_id) REFERENCES evbets(bet_id) ON DELETE CASCADE
)""")

conn.commit()
print("Tables created.")

# ── seed bookies ──────────────────────────────────────────────────────────────
# Check if bookies are already seeded
cursor.execute("SELECT COUNT(*) FROM bookies")
count = cursor.fetchone()[0]

if count == 0:
    # Full state exported from local bet_history.db on 2026-03-29
    bookies = [
        # (bookmaker, deposit_total, withdrawal_total, total_bankroll, currently_wagered, wagerable, current_net, bets_placed, bets_settled, bets_won, bets_lost, bets_pending)
        ('draftkings',     1035.0,   836.84,   163.45,   0.0,   163.45,  -34.71,   84,   78,  15,  63,   0),
        ('fanduel',        3720.0,  1651.25,  1144.6,  770.0,   374.6,  -924.15,  724,  695, 126, 569,  22),
        ('betmgm',         1570.5,  1037.16,   115.13,  30.0,    85.13, -418.21,  145,  144,  31, 113,   1),
        ('betrivers',       350.0,   413.14,     0.0,    0.0,     0.0,    63.14,   93,   93,  17,  76,   0),
        ('ballybet',        710.0,  1331.87,     0.0,    0.0,     0.0,   621.87,   50,   50,  14,  36,   0),
        ('espnbet',         595.0,   395.0,     98.8,    0.0,    98.8,  -101.2,  114,  113,  19,  94,   0),
        ('fanatics',        100.0,     0.0,      0.0,    0.0,     0.0,  -100.0,    7,    7,   0,   7,   0),
        ('williamhill_us',  400.0,   613.5,    246.75,  15.0,   231.75,  460.25,  55,   54,  12,  42,   1),
        ('cash',           6650.5,  6650.5,      0.0,    0.0,     0.0,     0.0,    0,    0,   0,   0,   0),
    ]
    for row in bookies:
        cursor.execute("""INSERT INTO bookies
            (bookmaker, deposit_total, withdrawal_total, total_bankroll,
             currently_wagered, wagerable, current_net,
             bets_placed, bets_settled, bets_won, bets_lost, bets_pending)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""", row)
    conn.commit()
    print(f"Seeded {len(bookies)} bookies.")
else:
    print(f"Bookies table already has {count} rows — skipping seed.")

conn.close()
print("Done.")
