from ..sports.threeresult import get_three_result_moneyline_bets
from ..sports.tworesult import get_two_result_moneyline_bets
from .get_sports import get_sports
from .odds_calculator import *
from .get_sports import two_result_sport_list
from .get_sports import three_result_sport_list


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


def run_get_sports():
    active = True
    has_outrights = False

    sports_list = get_sports(active, has_outrights)
    run_all(sports_list)
    
run_get_sports()
