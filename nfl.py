from home import *

#df = get_specific_sport('basketball_nba')
#df.to_csv('temp.csv')

df = pd.read_csv('temp.csv')

for x in range(len(df)):
    home_team = df.iloc[x]['home_team']
    away_team = df.iloc[x]['away_team']

    books = df.iloc[x]['bookmakers']
    books_list = eval(books) if isinstance(books, str) else books
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

            if market_key == 'h2h':
                moneyline_data = [outcome['price'] for outcome in market['outcomes']]
                home_moneyline = moneyline_data[0]
                away_moneyline = moneyline_data[1]
            
            if market_key == 'spreads':
                spread_data = [outcome['point'] for outcome in market['outcomes']]
                spread_juice_data = [outcome['price'] for outcome in market['outcomes']]
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
            this_bookie_data = [home_moneyline, away_moneyline, home_spread, away_spread, home_spread_juice, away_spread_juice, over_line, over_juice, under_juice]
            this_game_df[f'{bookie}'] = this_bookie_data
            

    print(this_game_df)
    print()

    
#print(df)