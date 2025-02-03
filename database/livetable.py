import sqlite3

conn = sqlite3.connect("betting_data.df")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS odds (
               id INTERGER PRIMARY KEY,
               MATCH TEXT,
               team_a TEXT,
               team_b TEXT,
               team_a_odds INT,
               team_b_odds INT,
               team_a_juice INT
               team_b_juice INT,
               team_a_moneyline INT,
               team_b_moneyline INT)"""
               )

cursor.execute("""
INSERT INTO odds (MATCH, team_a, team_b, team_a_odds, team_b_odds, team_a_juice, team_b_juice, team_a_moneyline, team_b_moneyline)
VALUES (?,?,?,?,?,?,?,?,?,?)""")

conn.commit()
conn.close()