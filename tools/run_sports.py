from ..moneyline.threeresult import get_three_result_moneyline_bets
from ..moneyline.tworesult import get_two_result_moneyline_bets
from .get_sports import get_sports
from .odds_calculator import *
from .get_sports import two_result_sport_list
from .get_sports import three_result_sport_list
from .bet_history import enter_bet
from .bet_history import bet_exists
from .bet_history import display_pending_bets
from .bet_history import get_pending_ids
from .bet_history import update_bet
from .bet_history import display_all_bets
from .bet_history import display_pending_bets
from .bookies import get_total_bankroll
from .bookies import get_bookie_wagerable_amount

ev_cutoff = 10
odds_cutoff = 1000

def run_all(sport_list):
    EVbetslist = []
    printdf = False
    not_found_list = []

    for x in sport_list:
        if x in two_result_sport_list:
            get_two_result_moneyline_bets(EVbetslist, x, printdf)
        elif x in three_result_sport_list:
            get_three_result_moneyline_bets(EVbetslist, x, printdf)
        else:
            not_found_list.append(x)

    return(EVbetslist)


    print()
    print("Not Found: ")
    for x in not_found_list:
        print(x)

    print('\n')
    print("EVbetslist: ")
    for x in EVbetslist:
        print(x)
        
    total_bankroll = get_total_bankroll()
    print('\n\n')
    for x in EVbetslist:
        id = x[1]
        alr_exists = bet_exists(id)
        if(alr_exists):
            #print("Bet already exists")
            continue
        print(x)
        percent_wager = x[6]
        suggested_wager = percent_wager * total_bankroll
        print(f"Kelly criterion suggested wager: {round(suggested_wager, 2)}")
        bookie_list = x[3]
        for bookie in bookie_list:
            this_bookie_wagerable_amount = get_bookie_wagerable_amount(bookie)
            print(f'{bookie}: {this_bookie_wagerable_amount}')
        
        take_bet = input("Would you like to take this?(y/n): ")
        if take_bet == 'n':
            continue

        sport = x[0]
        team = x[2]
        bet_type = 'Moneyline'
        bookie_choice = None
        while not bookie_choice:
            for bookie in bookie_list:
                choice = input(f'{bookie}? (y/n): ')
                if choice == 'y':
                    bookie_choice = bookie
                    break
            if not bookie_choice:
                print("Please select a bookie")
        odds = int(x[4])
        bet_amount = int(input("Bet amount: "))
        bet_ev = int(x[5])
        date = x[7]

        enter_bet(id, sport, team, bet_type, bookie_choice, odds, bet_amount, bet_ev, date)
    
    display_pending_bets()

'''
def run_get_sports():
    active = True
    has_outrights = False

    sports_list = get_sports(active, has_outrights)
    #sports_list =['basketball_ncaab']
    return sports_list
'''

def update_bets():
    pending_bet_ids = get_pending_ids()
    display_pending_bets()
    print('\n')
    for x in pending_bet_ids:
        print(x)
        settled = input("Is the bet settled? (y/n): ")
        if settled == 'y':
            result = input("Result (win or loss): ")
            update_bet(x[0], result)

#sports = get_sports(active=True, has_outrights=False)
sports =['soccer_argentina_primera_division']

print(run_all(sports))
