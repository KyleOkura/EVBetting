import requests
import pandas as pd
from .odds_calculator import *

# An api key is emailed to you when you sign up to a plan
# Get a free API key at https://api.the-odds-api.com/
#API_KEY = 'cb81bec595198c37776a7c7216aa95a5'
API_KEY = 'fa53e41dfc61191562135b54ca8dee4d'


SPORT = 'upcoming' # use the sport_key from the /sports endpoint below, or use 'upcoming' to see the next 8 games across all sports

REGIONS = 'us,eu' # uk | us | eu | au. Multiple can be specified if comma delimited

MARKETS = 'h2h,spreads,totals' # h2h | spreads | totals. Multiple can be specified if comma delimited

ODDS_FORMAT = 'american' # decimal | american

DATE_FORMAT = 'iso' # iso | unix

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#
# First get a list of in-season sports
#   The sport 'key' from the response can be used to get odds in the next request
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 


def get_current_sports():
    sport_arr = []
    sports_response = requests.get(
        'https://api.the-odds-api.com/v4/sports', 
        params={
            'api_key': API_KEY
        }
    )

    if sports_response.status_code != 200:
        print(f'Failed to get sports: status_code {sports_response.status_code}, response body {sports_response.text}')

    else:
        #print('List of in season sports:', sports_response.json())
        for x in sports_response.json():
            sport_arr.append(x['key'])
    
    return sport_arr



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#
# Now get a list of live & upcoming games for the sport you want, along with odds for different bookmakers
# This will deduct from the usage quota
# The usage quota cost = [number of markets specified] x [number of regions specified]
# For examples of usage quota costs, see https://the-odds-api.com/liveapi/guides/v4/#usage-quota-costs
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 




def fill_sports_df(sport_arr):
    sport_dataframes = {}
    #print(sport_arr)
    for x in sport_arr:
        SPORT = x

        odds_response = requests.get(
            f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds',
            params={
                'api_key': API_KEY,
                'regions': REGIONS,
                'markets': MARKETS,
                'oddsFormat': ODDS_FORMAT,
                'dateFormat': DATE_FORMAT,
            }
        )



        if odds_response.status_code != 200:
            print(f'Failed to get odds: status_code {odds_response.status_code}, response body {odds_response.text}')

        else:
            odds_json = odds_response.json()
            #print('Number of events:', len(odds_json))
            #print(odds_json)

            df = pd.json_normalize(odds_json)
            sport_dataframes[SPORT] = df


            # Check the usage quota
        print('Remaining requests', odds_response.headers['x-requests-remaining'])
        print('Used requests', odds_response.headers['x-requests-used'])

    return sport_dataframes


def get_specific_sport(this_sport):
    SPORT = this_sport

    odds_response = requests.get(
        f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds',
        params={
            'api_key': API_KEY,
            'regions': REGIONS,
            'markets': MARKETS,
            'oddsFormat': ODDS_FORMAT,
            'dateFormat': DATE_FORMAT,
        }
    )

    if odds_response.status_code != 200:
        print(f'Failed to get odds: status_code {odds_response.status_code}, response body {odds_response.text}')

    else:
        odds_json = odds_response.json()
        df = pd.json_normalize(odds_json)


        # Check the usage quota
    print('Remaining requests', odds_response.headers['x-requests-remaining'])
    print('Used requests', odds_response.headers['x-requests-used'])

    return df


def run_all():
    arr = get_current_sports()
    #print(arr)
    return fill_sports_df(arr)




def clean_df(df):
    
    for x in range(len(df)):
        home_team = df.iloc[x]['home_team']
        away_team = df.iloc[x]['away_team']

        books = df.iloc[x]['bookmakers']
        books_list = eval(books) if isinstance(books, str) else books
        #print(books_list)
        this_game_df = pd.DataFrame()
        this_game_df["Teams"] = [f"{home_team} Moneyline", f"{away_team} Moneyline", f"{home_team} Spread", f"{away_team} Spread", f"{home_team} Spread Juice", f"{away_team} Spread Juice", "Over/Under", "Over", "Under"]
        
        for y in books_list:
            #print(y)
            home_moneyline = 0
            away_moneyline = 0
            home_spread = 0
            away_spread = 0
            home_spread_juice = 0
            away_spread_juice = 0
            over_line = 0
            over_juice = 0
            under_juice = 0
            for market in y['markets']:
                market_key = market['key']
                # y['key'] for name of sportsbook
                if(y['key'] in skip):
                    continue

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
                
                bookie = y['key']
                bookie_data = [home_moneyline, away_moneyline, home_spread, away_spread, home_spread_juice, away_spread_juice, over_line, over_juice, under_juice]
                this_game_df[f'{bookie}'] = bookie_data


                moneyline_odds = [home_moneyline, away_moneyline]
                no_vig_moneyline_odds = get_no_vig_odds(moneyline_odds)

                spread_odds = [home_spread_juice, away_spread_juice]
                no_vig_spreadodds = get_no_vig_odds(spread_odds)

                over_under_odds = [over_juice, under_juice]
                no_vig_over_under_odds = get_no_vig_odds(over_under_odds)

                no_vig_data = [no_vig_moneyline_odds[0], no_vig_moneyline_odds[1], home_spread, away_spread, no_vig_spreadodds[0], no_vig_spreadodds[1], over_line, no_vig_over_under_odds[0], no_vig_over_under_odds[1]]

                this_game_df[f'{bookie}_novig'] = no_vig_data
                
        
        columns = list(this_game_df.columns)

        bookie_columns = [col for col in columns if not col.endswith('_novig')]
        novig_columns = [col for col in columns if col.endswith('_novig')]

        this_game_df = this_game_df[bookie_columns + novig_columns]

        print(this_game_df)



def clean_historical_df(df):
    
    for x in range(len(df)):
        home_team = df.iloc[x]['home_team']
        away_team = df.iloc[x]['away_team']

        books = df.iloc[x]['bookmakers']
        books_list = eval(books) if isinstance(books, str) else books
        #print(books_list)
        this_game_df = pd.DataFrame()
        this_game_df["Teams"] = [f"{home_team} Moneyline", f"{away_team} Moneyline", f"{home_team} Spread", f"{away_team} Spread", f"{home_team} Spread Juice", f"{away_team} Spread Juice", "Over/Under", "Over", "Under"]
        
        for y in books_list:
            #print(y)
            home_moneyline = 0
            away_moneyline = 0
            home_spread = 0
            away_spread = 0
            home_spread_juice = 0
            away_spread_juice = 0
            over_line = 0
            over_juice = 0
            under_juice = 0
            for market in y['markets']:
                market_key = market['key']
                # y['key'] for name of sportsbook
                if(y['key'] in skip):
                    continue

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
                
                bookie = y['key']
                bookie_data = [home_moneyline, away_moneyline, home_spread, away_spread, home_spread_juice, away_spread_juice, over_line, over_juice, under_juice]
                this_game_df[f'{bookie}'] = bookie_data


                moneyline_odds = [home_moneyline, away_moneyline]
                no_vig_moneyline_odds = get_no_vig_odds(moneyline_odds)

                spread_odds = [home_spread_juice, away_spread_juice]
                no_vig_spreadodds = get_no_vig_odds(spread_odds)

                over_under_odds = [over_juice, under_juice]
                no_vig_over_under_odds = get_no_vig_odds(over_under_odds)

                no_vig_data = [no_vig_moneyline_odds[0], no_vig_moneyline_odds[1], home_spread, away_spread, no_vig_spreadodds[0], no_vig_spreadodds[1], over_line, no_vig_over_under_odds[0], no_vig_over_under_odds[1]]

                this_game_df[f'{bookie}_novig'] = no_vig_data
                
        
        columns = list(this_game_df.columns)

        bookie_columns = [col for col in columns if not col.endswith('_novig')]
        novig_columns = [col for col in columns if col.endswith('_novig')]

        this_game_df = this_game_df[bookie_columns + novig_columns]

        print(this_game_df)
