from ..sports.soccer import get_soccer_moneyline_bets
from ..sports.tworesult import get_tworesult_moneyline_bets
from .get_sports import get_sports
from .odds_calculator import *

soccer_list = ['soccer_argentina_primera_division', 'soccer_australia_aleague', 'soccer_austria_bundesliga', 'soccer_belgium_first_div', 'soccer_chile_campeonato', 'soccer_conmebol_copa_libertadores', 
 'soccer_denmark_superliga', 'soccer_efl_champ', 'soccer_england_efl_cup', 'soccer_england_league1', 'soccer_england_league2', 'soccer_epl', 'soccer_fa_cup', 'soccer_france_ligue_one', 
 'soccer_france_ligue_two', 'soccer_germany_bundesliga', 'soccer_germany_bundesliga2', 'soccer_germany_liga3', 'soccer_greece_super_league', 'soccer_italy_serie_a', 'soccer_italy_serie_b', 
 'soccer_japan_j_league', 'soccer_korea_kleague1', 'soccer_league_of_ireland', 'soccer_mexico_ligamx', 'soccer_netherlands_eredivisie', 'soccer_norway_eliteserien', 'soccer_poland_ekstraklasa', 
 'soccer_portugal_primeira_liga', 'soccer_spain_la_liga', 'soccer_spain_segunda_division', 'soccer_spl', 'soccer_sweden_allsvenskan', 'soccer_switzerland_superleague', 'soccer_turkey_super_league', 
 'soccer_uefa_champs_league', 'soccer_uefa_europa_conference_league', 'soccer_uefa_europa_league', 'soccer_usa_mls']

two_result_sport_list = ['basketball_nba', 'basketball_nbl', 'basketball_ncaab', 'basketball_wncaab', 'basketball_euroleague', 
                         'icehockey_ahl', 'icehockey_liiga', 'icehockey_mestis', 'icehockey_nhl', 'icehockey_sweden_allsvenskan',
                         'americanfootball_ncaaf', 'aussierules_afl',
                         'mma_mixed_martial_arts', 'boxing_boxing',
                         'cricket_odi',
                         'lacrosse_ncaa', 'lacrosse_pll',
                         'rugbyleague_nrl', 'rugbyunion_six_nations'
                         ]

bankrolls = {'draftkings': 100,
            'bovada': 100,
            'betonlineag': 100,
            'betmgm': 100,
            'fanduel': 100,
            'lowvig': 100,
            'betrivers': 100,
            'betus': 100,
            'williamhill_us': 100,
            'mybookieag': 100}


def run_all():
    tworesultEVbetslist = []
    soccerEVbetslist = []
    printdf = False
    for x in two_result_sport_list:
        get_tworesult_moneyline_bets(tworesultEVbetslist, x, printdf)

    for x in soccer_list:
        get_soccer_moneyline_bets(soccerEVbetslist, x, printdf)

    print('\n')
    print(f'EVbetslist: ')
    for x in tworesultEVbetslist:
        print(x)
        print(percent_bankroll_ev_bet_two_result(x, bankrolls))

    for x in soccerEVbetslist:
        print(x)
        print(percent_bankroll_ev_bet_soccer(x, bankrolls))

def run_get_sports():
    active = True
    has_outrights = False
    print(get_sports(active, has_outrights))

#run_get_sports()

run_all()