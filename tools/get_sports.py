import requests


bookie_skip_list = ['onexbet', 'sport888', 'betclic', 'betanysports', 'betfair_ex_eu', 
                    'betonlineag','betsson','betvictor','coolbet','everygame','gtbets',
                    'marathonbet','matchbook','mybookieag','nordicbet', 'suprabets',
                    'tipico_de','unibet_eu', 'williamhill',
                    'mybookieag', 'betonlineag', 'betus', 'lowvig', 'betanysports',
                    'betparx', 'fliff', 'hardrockbet', 'windcreek']

three_result_sport_list = ['soccer_argentina_primera_division', 'soccer_australia_aleague', 'soccer_austria_bundesliga',
                            'soccer_belgium_first_div', 'soccer_brazil_campeonato', 'soccer_chile_campeonato',
                            'soccer_china_superleague', 'soccer_conmebol_copa_libertadores', 'soccer_denmark_superliga', 
                            'soccer_efl_champ', 'soccer_england_efl_cup', 'soccer_england_league1', 'soccer_england_league2', 
                            'soccer_epl', 'soccer_fa_cup', 'soccer_france_ligue_one', 'soccer_france_ligue_two', 
                            'soccer_germany_bundesliga2', 'soccer_germany_liga3', 'soccer_greece_super_league', 
                            'soccer_italy_serie_a', 'soccer_italy_serie_b', 'soccer_japan_j_league', 'soccer_korea_kleague1', 
                            'soccer_league_of_ireland', 'soccer_mexico_ligamx', 'soccer_netherlands_eredivisie', 'soccer_norway_eliteserien', 
                            'soccer_poland_ekstraklasa', 'soccer_portugal_primeira_liga', 'soccer_spain_la_liga', 
                            'soccer_spain_segunda_division', 'soccer_spl', 'soccer_sweden_allsvenskan', 'soccer_switzerland_superleague', 
                            'soccer_turkey_super_league', 'soccer_uefa_champs_league', 'soccer_uefa_europa_conference_league', 
                            'soccer_uefa_europa_league', 'soccer_usa_mls']

two_result_sport_list = ['americanfootball_ncaaf', 'aussierules_afl', 'baseball_ncaa', 'basketball_euroleague', 
                         'basketball_nba', 'basketball_nbl', 'basketball_ncaab', 'boxing_boxing', 'cricket_odi', 
                         'icehockey_ahl', 'icehockey_liiga', 'icehockey_mestis', 'icehockey_nhl', 'icehockey_sweden_allsvenskan', 
                         'icehockey_sweden_hockey_league', 'lacrosse_ncaa', 'mma_mixed_martial_arts', 'rugbyleague_nrl', 'rugbyunion_six_nations']

sport_skip_list = ['tennis_atp_qatar_open', 'tennis_wta_dubai', 'soccer_germany_bundesliga']

bankrolls = {'draftkings': 100,
            'betmgm': 100,
            'fanduel': 100,
            'betrivers': 100,
            'fanatics': 100,
            'bet365': 100,
            'williamhill_us': 100,
            'ballybet': 100,
            'espnbet': 100}



def get_sports(active, has_outrights):
    API_KEY = 'fa53e41dfc61191562135b54ca8dee4d'
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