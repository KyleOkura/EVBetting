# Bonus Bet Fix Summary

## Changes Made

### 1. Fixed `update_outcome()` function in `bet_history.py`
- **Issue**: All losing bets were being set to net = -bet_amount, including bonus bets
- **Fix**: Added logic to check if bet_type is "Bonus" when outcome is "loss"
  - Bonus bets that lose: net = 0 (no money wagered from bankroll)
  - Regular bets that lose: net = -bet_amount (normal loss)

### 2. Fixed existing database records
- Found 3 bonus bets with losses that had incorrect negative nets:
  - `cfe01c5ba65d45040a0f353b58464d1e`: -5 → 0
  - `fca5f337441a5206ff9cc9cc2c65b145`: -10 → 0
  - `85b3d6c684d8c28fb5677beecff5cac5`: -25 → 0
- All have been corrected to net = 0

### 3. Verified `update_bookie_values()` logic
**The existing logic is correct and doesn't need changes:**
- For Bonus bets that lose (net = 0): No wagerable adjustment
- For Bonus bets that win (net = profit): Profit added to wagerable
- For Regular bets that lose (net = negative): Loss added to wagerable
- For Regular bets that win (net = profit): Profit added to wagerable

The formula used:
```
bookie_wagerable = sum(all_settled_bet_nets) + deposits - withdrawals
bookie_bankroll = bookie_wagerable + bookie_wagered
bookie_net = bookie_bankroll - deposits + withdrawals
```

Since bonus losses now have net = 0, they don't negatively impact the calculation, which is the correct behavior.

### 4. Total Impact
- Net adjustment: -40 (the 3 fixed bets were pulling down totals by $40)
- With `update_bookie_values()` called, the total bankroll will increase by $40
- This correctly reflects that bonus bets don't actually cost money when they lose

## How It Works

**Bonus Bet Loss Scenario:**
- Bet $100 bonus (not from bankroll)
- Lose the bet
- Net = 0 (no money lost from bankroll)
- Bankroll impact: $0

**Bonus Bet Win Scenario:**
- Bet $100 bonus
- Win $150 (3:1 odds)
- Net = +$150 (profit added to bankroll)
- Bankroll impact: +$150

**Regular Bet Loss Scenario:**
- Bet $100 from bankroll
- Lose the bet
- Net = -$100 (money lost from bankroll)
- Bankroll impact: -$100
