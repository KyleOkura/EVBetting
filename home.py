import requests
import pandas as pd

# An api key is emailed to you when you sign up to a plan
# Get a free API key at https://api.the-odds-api.com/
API_KEY = 'cb81bec595198c37776a7c7216aa95a5'

SPORT = 'upcoming' # use the sport_key from the /sports endpoint below, or use 'upcoming' to see the next 8 games across all sports

REGIONS = 'us' # uk | us | eu | au. Multiple can be specified if comma delimited

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
    return fill_sports_df(arr)