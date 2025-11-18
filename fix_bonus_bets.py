import sqlite3
import os

def get_path():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'database'))
    db_path = os.path.join(root_dir, 'bet_history.db')
    return db_path

def fix_bonus_bet_losses():
    """Fix bonus bets that lost but show a negative net - they should all be 0"""
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Find all bonus bets that lost with non-zero net
    cursor.execute("""
        SELECT bet_id, bet_type, outcome, bet_amount, net 
        FROM bets 
        WHERE bet_type = 'Bonus' AND outcome = 'loss' AND net != 0
    """)
    bets_to_fix = cursor.fetchall()
    
    if not bets_to_fix:
        print("No bonus loss bets with non-zero net found. All are correct!")
        conn.close()
        return
    
    print(f"Found {len(bets_to_fix)} bonus bets that lost with non-zero net:")
    print(f"{'Bet ID':<35} {'Current Net':<12} {'New Net':<10}")
    print("-" * 60)
    
    total_adjustment = 0
    for bet in bets_to_fix:
        print(f"{bet['bet_id']:<35} {bet['net']:<12} 0")
        total_adjustment += bet['net']  # This will be negative, so we're tracking the total adjustment
        
        # Update the bet net to 0
        cursor.execute("""UPDATE bets SET net = 0 WHERE bet_id = ?""", (bet['bet_id'],))
    
    conn.commit()
    
    print()
    print(f"Total adjustment: {total_adjustment} (this is how much the net calculation will change)")
    print("All bonus loss bets have been set to net = 0")
    
    # Show the updated values
    cursor.execute("""
        SELECT bet_id, bet_type, outcome, bet_amount, net 
        FROM bets 
        WHERE bet_type = 'Bonus' AND (outcome = 'loss' OR outcome = 'win')
    """)
    updated_bets = cursor.fetchall()
    
    print()
    print("All settled bonus bets after fix:")
    print(f"{'Bet ID':<35} {'Outcome':<8} {'Amount':<8} {'Net':<8}")
    print("-" * 60)
    for bet in updated_bets:
        print(f"{bet['bet_id']:<35} {bet['outcome']:<8} {bet['bet_amount']:<8} {bet['net']:<8}")
    
    conn.close()

if __name__ == "__main__":
    fix_bonus_bet_losses()
