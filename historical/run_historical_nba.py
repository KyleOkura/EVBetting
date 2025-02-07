from EVBetting.historical.historical_nba import get_nba_dates_for_season
from EVBetting.historical.historical_nba import get_historical_nba_data
from EVBetting.historical.historical_nba import clean_df
import pandas as pd
import pickle


SPORT = 'basketball_nba' # use the sport_key from the /sports endpoint below, or use 'upcoming' to see the next 8 games across all sports

#REGIONS = 'us,eu' # uk | us | eu | au. Multiple can be specified if comma delimited
REGIONS = 'us'

MARKETS = 'h2h,spreads,totals' # h2h | spreads | totals. Multiple can be specified if comma delimited
#MARKETS = 'h2h'

ODDS_FORMAT = 'american' # decimal | american

DATE_FORMAT = 'iso' # iso | unix

DATE = '2024-11-02T00:00:00Z'

skip = {'onexbet', 'sport888', 'betclic', 'betanysports', 'betfair_ex_eu', 'betsson', 'betvictor', 'coolbet', 'everygaame', 'gtbets', 'marathonbet', 'matchbook', 'nordicbet', 'suprabets', 'tipico_de', 'unibet_eu', 'williamhill'}

def run_historical_nba():
    nba_date_list = get_nba_dates_for_season(DATE)
    nba_date_list_modified = []
    for date in nba_date_list:
        new_date = date[:16] + ':00' + date[16:]
        nba_date_list_modified.append(new_date)

    games_dictionary = {}

    #print(f'Date: {nba_date_list_modified[0]}')

    get_historical_nba_data(games_dictionary, SPORT=SPORT, REGIONS=REGIONS, MARKETS=MARKETS, ODDS_FORMAT=ODDS_FORMAT, DATE_FORMAT=DATE_FORMAT, DATE=nba_date_list_modified[0])
    
    with open("historical_nba_data.pkl", "wb") as file:
        pickle.dump(games_dictionary, file)

def get_historical_nba():
    with open('historical_nba_data.pkl', 'rb') as file:
        all_games = pickle.load(file)

    print(all_games)
    cleaned_dictionary = {}

    for id, data in all_games.items():
        df = pd.DataFrame(data)
        print(df['commence_time'])
        print(len(df['bookmakers']))

        #cleaned_df = clean_df(df)
        #print(cleaned_df.columns)
        #print()
        #cleaned_dictionary[id] = cleaned_df


run_historical_nba()

print('\n')
print('staging \n')
print('\n')



get_historical_nba()