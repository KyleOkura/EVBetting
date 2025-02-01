from home import *

#df = get_specific_sport('basketball_nba')
#df.to_csv('temp.csv')

df = pd.read_csv('temp.csv')

for x in range(len(df)):
    home_team = df.iloc[x]['home_team']
    away_team = df.iloc[x]['away_team']

    books = df.iloc[x]['bookmakers']
    books_list = eval(books) if isinstance(books, str) else books

    row_list = ["Home Team", "Away Team", "Moneyline", "Spread", "Spread Juice", "Over/Under Line", "Over Juice", "Under Juice"]

    moneyline_data = []
    spread_data = []
    spread_juice_data = []
    over_line_data = []
    over_juice_data = []
    under_juice_data = []
    
    for y in books_list:
        for market in y['markets']:
            market_key = market['key']

            if market_key == 'h2h':
                moneyline_data.append([outcome['price'] for outcome in market['outcomes']])
            
            if market_key == 'spreads':
                spread_data.append([outcome['point'] for outcome in market['outcomes']])
                spread_juice_data.append([outcome['price'] for outcome in market['outcomes']])

            if market_key == 'totals':
                over_data = [outcome['price'] for outcome in market['outcomes']]
                over_line_data.append([outcome['point'] for outcome in market['outcomes']])
                over_juice_data.append(over_data[0])
                over_juice_data.append(over_data[1])


    sportsbook_data = {
        "Home Team": [home_team],
        "Away Team": [away_team],
        "Moneyline": moneyline_data,
        "Spread": spread_data,
        "Spread Juice": spread_juice_data,
        "Over/Under Line": over_line_data,
        "Over Juice": over_juice_data,
        "Under Juice": under_juice_data
    }

    this_game_df = pd.DataFrame(sportsbook_data)

    print(this_game_df)

    
#print(df)