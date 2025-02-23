#from ..tools.home import *
import requests
from ..tools.odds_calculator import *
import pandas as pd
from ..tools.get_sports import bookie_skip_list
from dotenv import load_dotenv
import os

def get_three_result_moneyline_bets(EVbetlist, sport, printdf = False):

    print(f"Running {sport} Moneyline bets")

    load_dotenv()
    API_KEY = os.getenv("API_KEY")

    #API_KEY = 'fa53e41dfc61191562135b54ca8dee4d'
    SPORT = sport # use the sport_key from the /sports endpoint below, or use 'upcoming' to see the next 8 games across all sports
    REGIONS = 'us,us2,eu' # uk | us | eu | au. Multiple can be specified if comma delimited
    MARKETS = 'h2h' # h2h | spreads | totals. Multiple can be specified if comma delimited
    ODDS_FORMAT = 'american' # decimal | american
    DATE_FORMAT = 'iso' # iso | unix
    
    odds_response = requests.get(f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds/?apiKey={API_KEY}&regions={REGIONS}&markets={MARKETS}', params={
        'api_key': API_KEY,
        'sports': SPORT,
        'regions': REGIONS,
        'markets': MARKETS,
        'oddsFormat': ODDS_FORMAT,
        'dateFormat': DATE_FORMAT,
    })

    if odds_response.status_code != 200:
        print(f'Failed to get games: status_code {odds_response.status_code}, response body {odds_response.text}')
        return []

    sportdata = odds_response.json()

    for game in sportdata:
        '''
        df = pd.DataFrame(data=game)
        if(df.empty):
            continue
        gameid = df.iloc[0]['id']
        home_team = df.iloc[0]['home_team']
        away_team = df.iloc[0]['away_team']
        '''
        if not game:
            continue

        gameid = game['id']
        home_team = game['home_team']
        away_team = game['away_team']

        commence_time = sportdata[0]['commence_time'] if sportdata else None
        commence_date = commence_time[:10]

        game_df = pd.DataFrame()
        game_df["Teams"] = [f"{home_team}", f"{away_team}", "Draw"]
        for bookmaker in game['bookmakers']:
            bookie = bookmaker['key']
            if bookie in bookie_skip_list:
                continue
            home_moneyline = 0
            away_moneyline = 0
            draw_moneyline = 0
            lines = bookmaker['markets']
            prices = lines[0]['outcomes']

            home_name = prices[0]['name']

            if home_name == home_team:
                home_moneyline = int(prices[0]['price'])
                away_moneyline = int(prices[1]['price'])
                draw_moneyline = int(prices[2]['price'])
            else:
                home_moneyline = int(prices[1]['price'])
                away_moneyline = int(prices[0]['price'])
                draw_moneyline = int(prices[2]['price'])
                
            bookie_data = [home_moneyline, away_moneyline, draw_moneyline]
            game_df[f'{bookie}'] = bookie_data

        home_team_row_list = game_df.iloc[0].to_list()[1:]

        if not home_team_row_list:
            continue

        if(printdf):
            print(game_df)

        ev_bet = find_ev_bet_three_result(game_df)

        if not ev_bet:
            continue

        else:
            for x in ev_bet:
                x.insert(0, sport)
                x.insert(1, gameid)
                x.append(commence_date)
                EVbetlist.append(x)


    print('Remaining credits', odds_response.headers['x-requests-remaining'])
    print('Used credits', odds_response.headers['x-requests-used'])

    print(f"Finished Running {sport} Moneyline bets \n")
    
def test_three_result():
    EVbetlist = []
    printdf = True
    sports = ['soccer_italy_serie_a']
    for sport in sports:
        get_three_result_moneyline_bets(EVbetlist, sport, printdf)
    print(f"EVbetlist: {EVbetlist}")

#test_three_result()









"""

def get_three_result_moneyline_bets(EVbetlist, sport, printdf = False):

    print(f"Running {sport} Moneyline bets")

    API_KEY = 'fa53e41dfc61191562135b54ca8dee4d'
    SPORT = sport # use the sport_key from the /sports endpoint below, or use 'upcoming' to see the next 8 games across all sports
    REGIONS = 'us,us2,eu' # uk | us | eu | au. Multiple can be specified if comma delimited
    MARKETS = 'h2h' # h2h | spreads | totals. Multiple can be specified if comma delimited
    ODDS_FORMAT = 'american' # decimal | american
    DATE_FORMAT = 'iso' # iso | unix
    
    odds_response = requests.get(f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds/?apiKey={API_KEY}&regions={REGIONS}&markets={MARKETS}', params={
        'api_key': API_KEY,
        'sports': SPORT,
        'regions': REGIONS,
        'markets': MARKETS,
        'oddsFormat': ODDS_FORMAT,
        'dateFormat': DATE_FORMAT,
    })

    if odds_response.status_code != 200:
        print(f'Failed to get games: status_code {odds_response.status_code}, response body {odds_response.text}')
        return []

    data = odds_response.json()

    for game in data:
        df = pd.DataFrame(data=game)
        if(df.empty):
            continue
        home_team = df.iloc[0]['home_team']
        away_team = df.iloc[0]['away_team']
        return_df = pd.DataFrame()
        return_df["Teams"] = [f"{home_team}", f"{away_team}", "Draw"]
        for x in df['bookmakers']:
            bookie = x['key']
            if bookie in bookie_skip_list:
                continue
            home_moneyline = 0
            away_moneyline = 0
            draw_moneyline = 0
            lines = x['markets']
            prices = lines[0]['outcomes']

            home_name = prices[0]['name']
            away_name = prices[1]['name']

            if home_name == home_team:
                home_moneyline = int(prices[0]['price'])
                away_moneyline = int(prices[1]['price'])
                draw_moneyline = int(prices[2]['price'])
            else:
                home_moneyline = int(prices[1]['price'])
                away_moneyline = int(prices[0]['price'])
                draw_moneyline = int(prices[2]['price'])
                
            bookie_data = [home_moneyline, away_moneyline, draw_moneyline]
            return_df[f'{bookie}'] = bookie_data

        home_team_row_list = return_df.iloc[0].to_list()[1:]
        away_team_row_list = return_df.iloc[1].to_list()[1:]
        draw_row_list = return_df.iloc[2].to_list()[1:]

        home_team_best_line = max(home_team_row_list)
        away_team_best_line = max(away_team_row_list)
        draw_best_line = max(draw_row_list)

        home_team_best_line_index = home_team_row_list.index(home_team_best_line) + 1
        away_team_best_line_index = away_team_row_list.index(away_team_best_line) + 1
        draw_best_line_index = draw_row_list.index(draw_best_line) + 1

        return_df['Best Lines'] = [home_team_best_line, away_team_best_line, draw_best_line]

        decimal_odds = american_to_decimal(return_df['Best Lines'].to_list())

        #return_df['Decimal Best Lines'] = decimal_odds

        total_implied_prob = 0
        for x in decimal_odds:
            temp_implied_prob = 1/x
            total_implied_prob += temp_implied_prob

        if(total_implied_prob < 0):
            bookie1 = return_df.columns[home_team_best_line_index]
            bookie2 = return_df.columns[away_team_best_line_index]
            bookie3 = return_df.columns[draw_best_line_index]
            bookie1_line = home_team_best_line
            bookie2_line = away_team_best_line
            bookie3_line = draw_best_line
            EVbetlist.append([sport, home_team, away_team, 'draw', bookie1, bookie1_line, bookie2, bookie2_line, bookie3, bookie3_line])

        if printdf:
            print(return_df)


    print('Remaining credits', odds_response.headers['x-requests-remaining'])
    print('Used credits', odds_response.headers['x-requests-used'])

    print(f"Finished Running {sport} Moneyline bets \n")

"""