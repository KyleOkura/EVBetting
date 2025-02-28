from ..tools.bet_history import *


def run_display_ev_bookies():
    display_ev_bookie_table()






delete_bookie('draftkings')
delete_bookie('fanduel')
delete_bookie('betmgm')
delete_bookie('betrivers')
delete_bookie('ballybet')
delete_bookie('espnbet')
delete_bookie('fanatics')

reset_autoincrement()

add_bookmaker('draftkings', 100, 0, 0, 137.84)
add_bookmaker('fanduel', 100, 0, 45, 98)
add_bookmaker('betmgm', 150, 0, 25, 112)
add_bookmaker('betrivers', 100, 0, 125, 42.50)
add_bookmaker('ballybet', 60, 0, 30, 94.25)
add_bookmaker('espnbet', 10, 0, 10, 100.02)
add_bookmaker('fanatics', 0, 0, 0, 0)


display_bookie_table()