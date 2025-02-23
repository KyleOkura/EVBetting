#from ..tools.home import *
import requests
from ..tools.odds_calculator import *
import pandas as pd
from ..tools.get_sports import bookie_skip_list
from dotenv import load_dotenv
import os


def get_two_result_moneyline_bets(EVbetlist, sport, printdf = False):

    print(f"Running {sport} Moneyline bets")

    load_dotenv()
    API_KEY = os.getenv("API_KEY")
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
        #print(f'game id: {game['id']}')
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
        game_df["Teams"] = [f"{home_team}", f"{away_team}"]
        for bookmaker in game['bookmakers']:
            bookie = bookmaker['key']
            if bookie in bookie_skip_list:
                continue
            home_moneyline = 0
            away_moneyline = 0
            lines = bookmaker['markets']
            prices = lines[0]['outcomes']

            home_name = prices[0]['name']

            if home_name == home_team:
                home_moneyline = int(prices[0]['price'])
                away_moneyline = int(prices[1]['price'])
            else:
                home_moneyline = int(prices[1]['price'])
                away_moneyline = int(prices[0]['price'])

            bookie_data = [home_moneyline, away_moneyline]
            game_df[f'{bookie}'] = bookie_data

        home_team_row_list = game_df.iloc[0].to_list()[1:]

        if not home_team_row_list:
            continue
        
        if(printdf):
            print(game_df)


        #find_ev_bet runs alg to determine if the best lines are different from pinnacles lines (EV)
        #find_ev_bet will return the ev for each of the best lines, 
        #if it is positive ev another column with the % bankroll to bet acording to the kelly criterion will be added

        #can later implement keeping track of each bookmakers bankroll and return the amount to bet accordingly


        ev_bet = find_ev_bet_two_result(game_df)

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



    
def test_tworesult():
    EVbetlist = []
    printdf = True
    sports = ['soccer_germany_bundesliga']
    for sport in sports:
        get_two_result_moneyline_bets(EVbetlist, sport, printdf)
    print(f"EVbetlist: {EVbetlist}")
    
#test_tworesult()


