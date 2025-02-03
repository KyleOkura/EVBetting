from home import *
from odds_calculator import *
from pandasgui import show

'''
df = get_specific_sport('basketball_nba')
df.to_csv('basketball_nba.csv')
'''

skip = {'onexbet', 'sport888', 'betclic', 'betanysports', 'betfair_ex_eu', 'betsson', 'betvictor', 'coolbet', 'everygaame', 'gtbets', 'marathonbet', 'matchbook', 'nordicbet', 'suprabets', 'tipico_de', 'unibet_eu', 'williamhill'}

df = pd.read_csv('basketball_nba.csv')
#print(df.columns.to_list())
# print(df)

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

    
#print(df)