from ..sports.threeresult import get_three_result_moneyline_bets
from ..sports.tworesult import get_two_result_moneyline_bets
from .get_sports import get_sports
from .odds_calculator import *
from .get_sports import two_result_sport_list
from .get_sports import three_result_sport_list
from .bet_history import enter_bet
from .bet_history import bet_exists
from .bet_history import display_bets

ev_cutoff = 10
odds_cutoff = 1000

def run_all(sport_list):
    EVbetslist = []
    printdf = False
    for x in sport_list:
        if x in two_result_sport_list:
            get_two_result_moneyline_bets(EVbetslist, x, printdf)
        elif x in three_result_sport_list:
            get_three_result_moneyline_bets(EVbetslist, x, printdf)
        else:
            print(f'Sport not found: {x}')

    print('\n')
    print("EVbetslist: ")
    for x in EVbetslist:
        print(x)
        
    print('\n\n')
    for x in EVbetslist:
        id = x[1]
        alr_exists = bet_exists(id)
        if(alr_exists):
            continue
        print(x)
        will_take = input("Would you like to take this? (y/n): ")
        if will_take == 'y':
            sport = x[0]
            team = x[2]
            bet_type = 'Moneyline'
            bookie_list = x[3]
            bookie = ""
            for bookies in bookie_list:
                bookie_bool = input(f'{bookies}? (y/n): ')
                if bookie_bool == 'y':
                    bookie = bookies
            odds = int(x[4])
            bet_amount = int(input("Bet amount: "))
            bet_ev = int(x[5])

            print(odds)
            print(bet_ev)

            enter_bet(id, sport, team, bet_type, bookie, odds, bet_amount, bet_ev)
    
    display_bets()


def run_get_sports():
    active = True
    has_outrights = False

    sports_list = get_sports(active, has_outrights)
    #sports_list =['soccer_argentina_primera_division']
    global ev_cutoff
    global odds_cutoff

    ev_cutoff = 10
    odds_cutoff = 1000
    run_all(sports_list)
    
run_get_sports()
