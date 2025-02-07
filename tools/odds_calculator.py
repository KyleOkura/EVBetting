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

'''
temp_odds = [-900, 550]
print(get_no_vig_probability(temp_odds))
print(get_no_vig_odds(temp_odds))
'''


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

#print(kelly_criterion(0.5, -130))
odds = [+130, -155]

no_vig_odds = get_no_vig_odds(odds)

'''
print(get_no_vig_probability(odds))
print(get_no_vig_probability(no_vig_odds))
'''