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


def percent_bankroll_ev_bet_two_result(odds, bankrolls):
    bookie1 = odds[3]
    bookie1_line = odds[4]
    bookie2 = odds[5]
    bookie2_line = odds[6]

    bookie1_bankroll = bankrolls[bookie1]
    bookie2_bankroll = bankrolls[bookie2]

    max_bankroll = max(bookie1_bankroll, bookie2_bankroll)

    decimal_odds = american_to_decimal([bookie1_line, bookie2_line])
    stakes = []
    total_implied_probability = 0

    for x in decimal_odds:
        temp_implied_probability = 1/x
        total_implied_probability += temp_implied_probability

    for x in decimal_odds:
        temp_stake = (max_bankroll * (1/x))/total_implied_probability
        stakes.append(temp_stake)

    return stakes


def percent_bankroll_ev_bet_soccer(odds, bankrolls):
    bookie1 = odds[4]
    bookie1_line = odds[5]
    bookie2 = odds[6]
    bookie2_line = odds[7]
    bookie3 = odds[8]
    bookie3_line = odds[9]

    bookie1_bankroll = bankrolls[bookie1]
    bookie2_bankroll = bankrolls[bookie2]
    bookie3_bankroll = bankrolls[bookie3]

    max_bankroll = max(bookie1_bankroll, bookie2_bankroll, bookie3_bankroll)

    decimal_odds = american_to_decimal([bookie1_line, bookie2_line, bookie3_line])
    stakes = []
    total_implied_probability = 0

    for x in decimal_odds:
        temp_implied_probability = 1/x
        total_implied_probability += temp_implied_probability

    for x in decimal_odds:
        temp_stake = (max_bankroll * (1/x))/total_implied_probability
        stakes.append(temp_stake)

    return stakes