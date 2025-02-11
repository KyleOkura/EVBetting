import requests
import pandas as pd
import numpy as np
from warnings import simplefilter

import sys
import os
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from EVBetting.tools.odds_calculator import get_no_vig_probability
from EVBetting.tools.odds_calculator import get_no_vig_odds
from EVBetting.tools.odds_calculator import kelly_criterion
from EVBetting.tools.odds_calculator import normalize_score

simplefilter(action="ignore", category=pd.errors.PerformanceWarning)

# An api key is emailed to you when you sign up to a plan
# Get a free API key at https://api.the-odds-api.com/
#API_KEY = 'cb81bec595198c37776a7c7216aa95a5'
API_KEY = 'fa53e41dfc61191562135b54ca8dee4d'



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#
# First get a list of in-season sports
#   The sport 'key' from the response can be used to get odds in the next request
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 



def get_nba_dates_for_season(date):
    url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
    date_str = date[:10].replace("-", "")
    params = {"dates": date_str}

    response = requests.get(url, params=params)

    if(response.status_code != 200):
        print(f"Failed to get scores: {response.status_code}, {response.text}")
        return None
    
    data = response.json()
    dates = []

    for calendar in data['leagues'][0]['calendar']:
        dates.append(calendar)

    return dates







def get_historical_nba_data(games_dictionary, SPORT, REGIONS, MARKETS, ODDS_FORMAT, DATE_FORMAT, DATE):

    #THIS IS FOR GETTING ALL OF THE EVENTS IN THE SELECTED DATE - FOR TESTING JUST DOING ONE

    events_response = requests.get(f'https://api.the-odds-api.com/v4/historical/sports/{SPORT}/events', params={
            'api_key': API_KEY,
            'date': DATE,
            'commenceTimeFrom': DATE[:10] + "T00:00:00Z",
            'commenceTimeTo': DATE[:10] + "T23:59:59Z",
        })
    

    if events_response.status_code != 200:
        print(f'Failed to get events: status_code {events_response.status_code}, response body {events_response.text}')
        return []
    
    #print(events_response.text)
    
    events = events_response.json().get('data', [])
    #print(events)
    event_ids = [event['id'] for event in events]

    odds_response = requests.get(f'https://api.the-odds-api.com/v4/historical/sports/{SPORT}/odds', params={
        'api_key': API_KEY,
        'regions': REGIONS,
        'markets': MARKETS,
        'oddsFormat': ODDS_FORMAT,
        'dateFormat': DATE_FORMAT,
        'date': DATE,
        'eventIds': ",".join(event_ids)  # Pass specific event IDs
    })

    if odds_response.status_code != 200:
        print(f'Failed to get games: status_code {odds_response.status_code}, response body {odds_response.text}')
        return []

    data = odds_response.json()

    for game in data['data']:
        print(game)
        game_id = game['id']
        games_dictionary[game_id] = game

    print('Remaining credits', odds_response.headers['x-requests-remaining'])
    print('Used credits', odds_response.headers['x-requests-used'])

    return games_dictionary




def clean_df(input_df):
    commence_time= input_df.iloc[0]['commence_time']

    home_team = input_df.iloc[0]['home_team']
    away_team = input_df.iloc[0]['away_team']

    '''
    print(input_df['bookmakers'])
    print()
    print(f'home_team: {home_team}')
    print(f'away_team: {away_team}')
    '''
    this_game_df = pd.DataFrame()
    this_game_df["Teams"] = [f"{home_team}", f"{away_team}"]

    score = get_final_score(commence_time[:10], home_team, away_team)
    if(score[0] == 0):
        print(f'home_team: {home_team}')
        print(f'away_team: {away_team}')
        print()

    this_game_df["Score"] = score

    for x in range(len(input_df['bookmakers'])):
        book = input_df.iloc[x]['bookmakers']

        home_moneyline = 0
        away_moneyline = 0
        home_spread = 0
        away_spread = 0
        home_spread_juice = 0
        away_spread_juice = 0
        over_line = 0
        over_juice = 0
        under_juice = 0
        for market in book['markets']:
            market_key = market['key']
            #print(f'market_key: {market_key}')

            switch = market['outcomes'][0]['name'] == away_team

            if market_key == 'h2h':
                moneyline_data = [outcome['price'] for outcome in market['outcomes']]
                if(switch):
                    home_moneyline = moneyline_data[1]
                    away_moneyline = moneyline_data[0]
                else:
                    home_moneyline = moneyline_data[0]
                    away_moneyline = moneyline_data[1]
            
            if market_key == 'spreads':
                spread_data = [outcome['point'] for outcome in market['outcomes']]
                spread_juice_data = [outcome['price'] for outcome in market['outcomes']]

                if(switch):
                    home_spread = spread_data[1]
                    away_spread = spread_data[0]
                    home_spread_juice = spread_juice_data[1]
                    away_spread_juice = spread_juice_data[0]
                else:
                    home_spread = spread_data[0]
                    away_spread = spread_data[1]
                    home_spread_juice = spread_juice_data[0]
                    away_spread_juice = spread_juice_data[1]

            if market_key == 'totals':
                over_data = [outcome['point'] for outcome in market['outcomes']]
                over_line = over_data[0]
                over_juice_data = [outcome['price'] for outcome in market['outcomes']]
                over_juice = over_juice_data[0]
                under_juice = over_juice_data[1]
            
            bookie = book['key']

            #print(f'bookie: {bookie}')
            bookie_moneyline_data = [home_moneyline, away_moneyline]
            bookie_spread_data = [home_spread, away_spread]
            bookie_spread_juice_data = [home_spread_juice, away_spread_juice]
            bookie_over_data = [over_line, over_line]
            bookie_over_juice_data = [over_juice, under_juice]
            
            this_game_df[f'{bookie} moneyline'] = bookie_moneyline_data
            this_game_df[f'{bookie} spread'] = bookie_spread_data
            this_game_df[f'{bookie} spread juice'] = bookie_spread_juice_data
            this_game_df[f'{bookie} over/under'] = bookie_over_data
            this_game_df[f'{bookie} over/under juice'] = bookie_over_juice_data

            moneyline_odds = [home_moneyline, away_moneyline]
            no_vig_moneyline_odds = get_no_vig_odds(moneyline_odds)

            spread_odds = [home_spread_juice, away_spread_juice]
            no_vig_spread_odds = get_no_vig_odds(spread_odds)

            over_under_odds = [over_juice, under_juice]
            no_vig_over_under_odds = get_no_vig_odds(over_under_odds)

            this_game_df[f'{bookie}_novig moneyline'] = no_vig_moneyline_odds
            this_game_df[f'{bookie}_novig spread'] = bookie_spread_data
            this_game_df[f'{bookie}_novig spread juice'] = no_vig_spread_odds
            this_game_df[f'{bookie}_novig over/under'] = bookie_over_data
            this_game_df[f'{bookie}_novig over/under juice'] = no_vig_over_under_odds

            bookie_win_prediction = get_no_vig_probability(moneyline_odds)

            this_game_df[f'{bookie}_win percentage'] = bookie_win_prediction
            
    
    columns = list(this_game_df.columns)

    bookie_columns = [col for col in columns if not col.endswith('_novig')]
    novig_columns = [col for col in columns if col.endswith('_novig')]

    this_game_df = this_game_df[bookie_columns + novig_columns]

    return this_game_df


def get_final_score(date, home_team_input, away_team_input):
    url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
    date_str = date[:10].replace("-", "")
    params = {"dates": date_str}  

    response = requests.get(url, params=params)
    if(response.status_code != 200):
        print(f"Failed to get scores: {response.status_code}, {response.text}")
        return None
    
    games = response.json()
    home_score = 0
    away_score = 0

    
    for game in games['events']:
        home_team = game['competitions'][0]['competitors'][0]['team']['displayName']
        away_team = game['competitions'][0]['competitors'][1]['team']['displayName']

        print(f'espn_home_team: {home_team}')
        print(f'espn_away_team: {away_team}')

        if(home_team_input == home_team or away_team_input==away_team):
            home_score = game['competitions'][0]['competitors'][0]['score']
            away_score = game['competitions'][0]['competitors'][1]['score']
        else:
            continue

    return[home_score, away_score]