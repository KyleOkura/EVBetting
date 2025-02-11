from ...tools.home import *
from ...tools.odds_calculator import *
import pandas as pd
from pandasgui import show
import os

API_KEY = 'fa53e41dfc61191562135b54ca8dee4d'

SPORT = 'upcoming' # use the sport_key from the /sports endpoint below, or use 'upcoming' to see the next 8 games across all sports

REGIONS = 'us' # uk | us | eu | au. Multiple can be specified if comma delimited

MARKETS = 'h2h' # h2h | spreads | totals. Multiple can be specified if comma delimited

ODDS_FORMAT = 'american' # decimal | american

DATE_FORMAT = 'iso' # iso | unix


def get_nba_moneyline_bets():
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
        for x in df['bookmakers']:
            print(x)

        home_team = df.iloc[0]['home_team']
        away_team = df.iloc[0]['away_team']

        books = df.iloc[0]['bookmakers']
        books_list = eval(books) if isinstance(books, str) else books
        return_df = pd.DataFrame()
        return_df["Teams"] = [f"{home_team}", f"{away_team}"]
        
        for y in books_list:
            home_moneyline = 0
            away_moneyline = 0
            moneyline_data = [outcome['price'] for outcome in df['markets']['outcomes']]
            home_moneyline = moneyline_data[0]
            away_moneyline = moneyline_data[1]
                
            bookie = y['key']
            bookie_data = [home_moneyline, away_moneyline]
            return_df[f'{bookie}'] = bookie_data

        print(this_game_df)

        print('\n\n\n')



    print('Remaining credits', odds_response.headers['x-requests-remaining'])
    print('Used credits', odds_response.headers['x-requests-used'])
    
get_nba_moneyline_bets()
    
