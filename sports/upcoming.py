from ..tools.home import *
from ..tools.odds_calculator import *
import pandas as pd


def get_upcoming_bets(EVbetlist):
    API_KEY = 'fa53e41dfc61191562135b54ca8dee4d'
    SPORT = 'upcoming' # use the sport_key from the /sports endpoint below, or use 'upcoming' to see the next 8 games across all sports
    REGIONS = 'us' # uk | us | eu | au. Multiple can be specified if comma delimited
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
        home_team = df.iloc[0]['home_team']
        away_team = df.iloc[0]['away_team']
        return_df = pd.DataFrame()
        return_df["Teams"] = [f"{home_team}", f"{away_team}"]
        for x in df['bookmakers']:
            home_moneyline = 0
            away_moneyline = 0
            lines = x['markets']
            prices = lines[0]['outcomes']

            home_name = prices[0]['name']
            away_name = prices[1]['name']

            if home_name == home_team:
                home_moneyline = int(prices[0]['price'])
                away_moneyline = int(prices[1]['price'])
            else:
                home_moneyline = int(prices[1]['price'])
                away_moneyline = int(prices[0]['price'])
                
            bookie = x['key']
            bookie_data = [home_moneyline, away_moneyline]
            return_df[f'{bookie}'] = bookie_data

        home_team_row_list = return_df.iloc[0].to_list()[1:]
        away_team_row_list = return_df.iloc[1].to_list()[1:]

        home_team_best_line = max(home_team_row_list)
        away_team_best_line = max(away_team_row_list)
        home_team_best_line_index = home_team_row_list.index(home_team_best_line) + 1
        away_team_best_line_index = away_team_row_list.index(away_team_best_line) + 1

        return_df['Best Lines'] = [home_team_best_line, away_team_best_line]

        #print(f"df: {return_df}")

        if(home_team_best_line > 0 and home_team_best_line > abs(away_team_best_line)):
            bookie1 = return_df.columns[home_team_best_line_index]
            bookie2 = return_df.columns[away_team_best_line_index]
            bookie1_line = home_team_best_line
            bookie2_line = away_team_best_line
            EVbetlist.append([home_team, away_team, bookie1, bookie1_line, bookie2, bookie2_line])

        elif(away_team_best_line > 0 and away_team_best_line > abs(home_team_best_line)):
            bookie1 = return_df.columns[home_team_best_line_index]
            bookie2 = return_df.columns[away_team_best_line_index]
            bookie1_line = home_team_best_line
            bookie2_line = away_team_best_line
            EVbetlist.append([home_team, away_team, bookie1, bookie1_line, bookie2, bookie2_line])


    print('Remaining credits', odds_response.headers['x-requests-remaining'])
    print('Used credits', odds_response.headers['x-requests-used'])
    
EVbetlist = []
get_upcoming_bets(EVbetlist)
    
