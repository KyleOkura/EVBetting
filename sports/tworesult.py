from ..tools.home import *
from ..tools.odds_calculator import *
import pandas as pd

#skiplist = ['bovada', 'mybookieag', 'betonlineag', 'betus', 'lowvig', 'betanysports', 'betparx', 'fliff', 'hardrockbet', 'windcreek']

def get_tworesult_moneyline_bets(EVbetlist, sport, printdf = False):

    print(f"Running {sport} Moneyline bets")

    API_KEY = 'fa53e41dfc61191562135b54ca8dee4d'
    SPORT = sport # use the sport_key from the /sports endpoint below, or use 'upcoming' to see the next 8 games across all sports
    REGIONS = 'us,us2' # uk | us | eu | au. Multiple can be specified if comma delimited
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

        if not home_team_row_list:
            continue


        #do calculations for avg line and such to find EV even when lines arent arbitrage
        no_vig_df = pd.DataFrame()
        no_vig_df["Teams"] = return_df['Teams']

        bookies = return_df.columns
        for x in bookies[1:]:
            odds = [return_df[x][0], return_df[x][1]]
            no_vig_odds = get_no_vig_odds(odds)
            no_vig_df[f"{x}"] = no_vig_odds
        
        
        for x in bookies[1:]:
            temp_df = no_vig_df.drop(columns=[x])
            temp_df_columns = temp_df.columns
            no_vig_fair_odds_home = 0
            no_vig_fair_odds_away = 0
            #print(temp_df)
            for y in temp_df_columns[1:]:
                no_vig_fair_odds_home += temp_df[y][0]
                no_vig_fair_odds_away += temp_df[y][1]
            
            no_vig_fair_odds_home = no_vig_fair_odds_home/len(temp_df[1:])
            no_vig_fair_odds_away = no_vig_fair_odds_away/len(temp_df[1:])
            no_vig_decimal_odds = american_to_decimal([no_vig_fair_odds_home, no_vig_fair_odds_away])
            decimal_odds = american_to_decimal([return_df[x][0], return_df[x][1]])
            ev_home = (decimal_odds[0] - no_vig_decimal_odds[0])/no_vig_decimal_odds[0]
            ev_away = (decimal_odds[1] - no_vig_decimal_odds[1])/no_vig_decimal_odds[1]

            print(f'ev home: {ev_home}')
            print(f'ev away: {ev_away}')


        home_team_best_line = max(home_team_row_list)
        away_team_best_line = max(away_team_row_list)

        home_team_best_line_bookie_index_list = []
        away_team_best_line_bookie_index_list = []

        for x in range(len(home_team_row_list)):
            if home_team_row_list[x] == home_team_best_line:
                home_team_best_line_bookie_index_list.append(x+1)

        for x in range(len(away_team_row_list)):
            if away_team_row_list[x] == away_team_best_line:
                away_team_best_line_bookie_index_list.append(x+1)


        return_df['Best Lines'] = [home_team_best_line, away_team_best_line]


        
        if(home_team_best_line > 0 and home_team_best_line > abs(away_team_best_line)):
            bookie1 = list(return_df.columns[home_team_best_line_bookie_index_list])
            bookie2 = list(return_df.columns[away_team_best_line_bookie_index_list])
            bookie1_line = home_team_best_line
            bookie2_line = away_team_best_line
            EVbetlist.append([sport, home_team, away_team, bookie1, bookie1_line, bookie2, bookie2_line])

        elif(away_team_best_line > 0 and away_team_best_line > abs(home_team_best_line)):
            bookie1 = list(return_df.columns[home_team_best_line_bookie_index_list])
            bookie2 = list(return_df.columns[away_team_best_line_bookie_index_list])
            bookie1_line = home_team_best_line
            bookie2_line = away_team_best_line
            EVbetlist.append([sport, home_team, away_team, bookie1, bookie1_line, bookie2, bookie2_line])
        
            

        if(printdf):
            print(return_df)


    print('Remaining credits', odds_response.headers['x-requests-remaining'])
    print('Used credits', odds_response.headers['x-requests-used'])

    print(f"Finished Running {sport} Moneyline bets \n")
    
def test_tworesult():
    EVbetlist = []
    printdf = True
    sports = ['icehockey_mestis']
    for sport in sports:
        get_tworesult_moneyline_bets(EVbetlist, sport, printdf)
    print(f"EVbetlist: {EVbetlist}")
    
#test_tworesult()