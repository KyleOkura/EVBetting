import requests
from dotenv import load_dotenv
import os

bookie_skip_list = ['onexbet', 'sport888', 'betclic', 'betanysports', 'betfair_ex_eu', 
                    'betonlineag','betsson','betvictor','coolbet','everygame','gtbets',
                    'marathonbet','matchbook','mybookieag','nordicbet', 'suprabets', 'winamax_fr', 'winamax_de',
                    'tipico_de','unibet_eu', 'williamhill', 
                    'betonlineag', 'betus', 'lowvig', 'betanysports',
                    'betparx', 'fliff', 'hardrockbet', 'windcreek', 'bovada',
                    'betrivers', 'ballybet', 'unibet_fr', 'unibet_it', 'unibet_nl', 'betclic_fr',
                    'parionssport_fr', 'unibet_se', 'leovegas_se', 'codere_it']

three_result_sport_list = ['soccer_argentina_primera_division', 'soccer_australia_aleague', 'soccer_austria_bundesliga',
                            'soccer_belgium_first_div', 'soccer_brazil_campeonato', 'soccer_chile_campeonato',
                            'soccer_china_superleague', 'soccer_conmebol_copa_libertadores', 'soccer_denmark_superliga', 
                            'soccer_efl_champ', 'soccer_england_efl_cup', 'soccer_england_league1', 'soccer_england_league2', 
                            'soccer_epl', 'soccer_fa_cup', 'soccer_germany_liga3', 'soccer_greece_super_league', 
                            'soccer_italy_serie_a', 'soccer_japan_j_league', 'soccer_korea_kleague1', 
                            'soccer_league_of_ireland', 'soccer_mexico_ligamx', 'soccer_netherlands_eredivisie', 'soccer_norway_eliteserien', 
                            'soccer_poland_ekstraklasa', 'soccer_portugal_primeira_liga', 'soccer_spain_la_liga', 
                            'soccer_spain_segunda_division', 'soccer_spl', 'soccer_sweden_allsvenskan', 
                            'soccer_turkey_super_league', 'soccer_uefa_champs_league', 'soccer_uefa_europa_conference_league', 
                            'soccer_uefa_europa_league', 'soccer_usa_mls', 'soccer_germany_bundesliga', 'soccer_brazil_serie_b', 
                            'soccer_conmebol_copa_sudamericana', 'soccer_finland_veikkausliiga', 'soccer_sweden_superettan', 
                            'soccer_switzerland_superleague', 'soccer_uefa_champs_league_women', 'soccer_uefa_nations_league',
                            'soccer_fifa_world_cup_qualifiers_europe', 'soccer_concacaf_leagues_cup', 'soccer_fifa_world_cup_qualifiers_south_america',
                            'soccer_uefa_champs_league_qualification']

two_result_sport_list = ['americanfootball_ncaaf', 'aussierules_afl', 'baseball_ncaa', 'basketball_euroleague', 
                         'basketball_nba', 'basketball_nbl', 'basketball_ncaab', 'boxing_boxing', 'cricket_odi', 
                         'icehockey_ahl', 'icehockey_liiga', 'icehockey_mestis', 'icehockey_nhl', 'icehockey_sweden_allsvenskan', 
                         'icehockey_sweden_hockey_league', 'lacrosse_ncaa', 'mma_mixed_martial_arts', 'rugbyleague_nrl', 'rugbyunion_six_nations',
                         'baseball_mlb_preseason', 'basketball_wncaab', 'cricket_international_t20', 'baseball_mlb', 'cricket_icc_trophy', 'cricket_ipl',
                         'americanfootball_ufl', 'baseball_kbo', 'baseball_milb', 'baseball_npb', 'cricket_psl', 'americanfootball_cfl', 'americanfootball_nfl',
                         'americanfootball_nfl_preseason', 'basketball_wnba', 'cricket_caribbean_premier_league', 'cricket_the_hundred', 'lacrosse_pll']

sport_skip_list = ['tennis_atp_qatar_open', 'tennis_wta_dubai', 'soccer_switzerland_superleague', 'tennis_atp_us_open', 'tennis_wta_us_open', 'soccer_france_ligue_one',
                   'soccer_france_ligue_two', 'soccer_germany_bundesliga2', 'soccer_italy_serie_b']


def get_sports(active, has_outrights):
    load_dotenv()
    API_KEY = os.getenv("API_KEY")
    print(API_KEY)
    response = requests.get(f'https://api.the-odds-api.com/v4/sports/?apiKey={API_KEY}', params={
        'api_key': API_KEY,
    })

    if response.status_code != 200:
        print(f'Failed to get sports: status_code {response.status_code}, response body {response.text}')
        return []
    
    sports = response.json()

    sports_list = []

    for sport in sports:
        if(sport['active'] == active and sport['has_outrights'] == has_outrights):
            sports_list.append(sport['key'])

    return sports_list


#print(get_sports(True, False))