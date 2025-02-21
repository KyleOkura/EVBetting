import pandas as pd
#from .run_sports import ev_cutoff
#from .run_sports import odds_cutoff
from .bookies import get_bookie_wagerable_amount
#input a list
def get_no_vig_probability(odds):
    total_implied_probability = 0
    implied_probabilities = []

    for x in odds:
        if(x > 0):
            implied_probability = 100 / (x+100)
        elif (x < 0):
            implied_probability = abs(x) / (abs(x)+100)
        else:
            return [0,0]

        implied_probabilities.append(implied_probability)
        total_implied_probability += implied_probability

    return [round((p / total_implied_probability) * 100, 2) for p in implied_probabilities]


def get_no_vig_odds(odds):
    probabilities = get_no_vig_probability(odds)

    decimal_odds = []
    for x in probabilities:
        if x != 0:
            decimal_odds.append((1/(x/100)))
        else:
            return[0,0]

    return_odds = []
    for x in decimal_odds:
        if (x > 2):
            return_odds.append(round((x-1)*100, 2))
        else:
            return_odds.append(round(-100/(x-1),2))

    return return_odds


def kelly_criterion(win_probability, given_odds):
    #win_probability in the format of 0.5
    #given odds in the format of +185
    #return fraction of bankroll to wager

    lose_probability = 1-win_probability

    if given_odds > 0:
        win_proportion = given_odds/100
    else:
        win_proportion = 100/abs(given_odds)

    fraction = win_probability - (lose_probability/win_proportion)
    return fraction


def normalize_score(scores):
    total = scores[0] + scores[1]
    normalized_first = scores[0]/total
    normalized_second = scores[1]/total

    return [normalized_first, normalized_second]



def american_to_decimal(odds):
    return_odds = []
    for odd in odds:
        if odd < 0:
            temp = (100/abs(odd)) + 1
            return_odds.append(temp)
        else:
            temp = (odd/100) + 1
            return_odds.append(temp)

    return return_odds


def find_ev_bet_two_result(game_df):
    home_team = game_df['Teams'][0]
    away_team = game_df['Teams'][1]

    home_team_row_list = game_df.iloc[0].to_list()[1:]
    away_team_row_list = game_df.iloc[1].to_list()[1:]

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


    game_df['Best Lines'] = [home_team_best_line, away_team_best_line]

    best_line_decimal_odds = american_to_decimal([home_team_best_line, away_team_best_line])
    home_best_decimal = best_line_decimal_odds[0]
    away_best_decimal = best_line_decimal_odds[1]

    bookies = game_df.columns
    ret_list = []

    if 'pinnacle' in bookies:
        true_pinnacle_odds = get_no_vig_odds(game_df['pinnacle'])
        true_pinnacle_prob = get_no_vig_probability(true_pinnacle_odds)

        home_true_pinnacle_prob = true_pinnacle_prob[0]/100
        away_true_pinnacle_prob = true_pinnacle_prob[1]/100

        home_ev = 0
        away_ev = 0

        home_ev = (home_true_pinnacle_prob * (home_best_decimal-1) * 100) + (away_true_pinnacle_prob * -100)
        away_ev = (away_true_pinnacle_prob * (away_best_decimal-1) * 100) + (home_true_pinnacle_prob * -100)

        home_ev = round(home_ev, 2)
        away_ev = round(away_ev, 2)

        ev_cutoff = 5
        odds_cutoff = 1000

        if home_ev > ev_cutoff:
            if home_team_best_line < odds_cutoff:
                bookie_list = list(game_df.columns[home_team_best_line_bookie_index_list])

                percent_wager = kelly_criterion(home_true_pinnacle_prob, home_team_best_line)

                ret_list.append([home_team, bookie_list, home_team_best_line, home_ev, percent_wager])


        if away_ev > ev_cutoff:
            if away_team_best_line < odds_cutoff:
                bookie_list = list(game_df.columns[away_team_best_line_bookie_index_list])

                percent_wager = kelly_criterion(away_true_pinnacle_prob, away_team_best_line)

                ret_list.append([away_team, bookie_list, away_team_best_line, away_ev, percent_wager])

        return ret_list

    else:
        return([])
    
    '''
    else:
        if(home_team_best_line > 0 and home_team_best_line > abs(away_team_best_line)):
            bookie1 = list(game_df.columns[home_team_best_line_bookie_index_list])
            bookie2 = list(game_df.columns[away_team_best_line_bookie_index_list])
            bookie1_line = home_team_best_line
            bookie2_line = away_team_best_line
            

            ret_list.append([home_team, bookie1, bookie1_line, ])
            ret_list.append([away_team, bookie2, bookie2_line, ])

        elif(away_team_best_line > 0 and away_team_best_line > abs(home_team_best_line)):
            bookie1 = list(game_df.columns[home_team_best_line_bookie_index_list])
            bookie2 = list(game_df.columns[away_team_best_line_bookie_index_list])
            bookie1_line = home_team_best_line
            bookie2_line = away_team_best_line
            ret_list.append([home_team, away_team, bookie1, bookie1_line, bookie2, bookie2_line])
        
        return ret_list
        
    '''

def find_ev_bet_three_result(game_df):
    home_team = game_df['Teams'][0]
    away_team = game_df['Teams'][1]

    home_team_row_list = game_df.iloc[0].to_list()[1:]
    away_team_row_list = game_df.iloc[1].to_list()[1:]
    draw_row_list = game_df.iloc[2].to_list()[1:]

    home_team_best_line = max(home_team_row_list)
    away_team_best_line = max(away_team_row_list)
    draw_best_line = max(draw_row_list)

    home_team_best_line_bookie_index_list = []
    away_team_best_line_bookie_index_list = []
    draw_best_line_bookie_index_list = []

    for x in range(len(home_team_row_list)):
        if home_team_row_list[x] == home_team_best_line:
            home_team_best_line_bookie_index_list.append(x+1)

    for x in range(len(away_team_row_list)):
        if away_team_row_list[x] == away_team_best_line:
            away_team_best_line_bookie_index_list.append(x+1)

    for x in range(len(draw_row_list)):
        if draw_row_list[x] == draw_best_line:
            draw_best_line_bookie_index_list.append(x+1)


    game_df['Best Lines'] = [home_team_best_line, away_team_best_line, draw_best_line]

    best_line_decimal_odds = american_to_decimal([home_team_best_line, away_team_best_line, draw_best_line])
    home_best_decimal = best_line_decimal_odds[0]
    away_best_decimal = best_line_decimal_odds[1]
    draw_best_decimal = best_line_decimal_odds[2]

    bookies = game_df.columns
    ret_list = []

    if 'pinnacle' in bookies:
        true_pinnacle_odds = get_no_vig_odds(game_df['pinnacle'])
        true_pinnacle_prob = get_no_vig_probability(true_pinnacle_odds)

        home_true_pinnacle_prob = true_pinnacle_prob[0]/100
        away_true_pinnacle_prob = true_pinnacle_prob[1]/100
        draw_true_pinnacle_prob = true_pinnacle_prob[2]/100

        home_ev = 0
        away_ev = 0
        draw_ev = 0

        home_ev = (home_true_pinnacle_prob * (home_best_decimal-1) * 100) + (away_true_pinnacle_prob * -100) + (draw_true_pinnacle_prob * -100)
        away_ev = (away_true_pinnacle_prob * (away_best_decimal-1) * 100) + (home_true_pinnacle_prob * -100) + (draw_true_pinnacle_prob * -100)
        draw_ev = (draw_true_pinnacle_prob * (draw_best_decimal-1) * 100) + (away_true_pinnacle_prob * -100) + (home_true_pinnacle_prob * -100)

        home_ev = round(home_ev, 2)
        away_ev = round(away_ev, 2)
        draw_ev = round(draw_ev, 2)

        ev_cutoff = 5
        odds_cutoff = 1000


        if home_ev > ev_cutoff:
            if home_team_best_line < odds_cutoff:
                bookie_list = list(game_df.columns[home_team_best_line_bookie_index_list])

                percent_wager = kelly_criterion(home_true_pinnacle_prob, home_team_best_line)
                ret_list.append([home_team, bookie_list, home_team_best_line, home_ev, percent_wager])
        if away_ev > ev_cutoff:
            if away_team_best_line < odds_cutoff:
                bookie_list = list(game_df.columns[away_team_best_line_bookie_index_list])
                percent_wager = kelly_criterion(away_true_pinnacle_prob, away_team_best_line)

                ret_list.append([away_team, bookie_list, away_team_best_line, away_ev, percent_wager])
        if draw_ev > ev_cutoff:
            if draw_best_line < odds_cutoff:
                bookie_list = list(game_df.columns[draw_best_line_bookie_index_list])
                percent_wager = kelly_criterion(draw_true_pinnacle_prob, draw_best_line)

                draw_game = "draw (" + home_team + " v " + away_team + ")"
                ret_list.append([draw_game, bookie_list, draw_best_line, draw_ev, percent_wager])


        
        return ret_list

    else:
        return([])