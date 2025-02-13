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
    bookie_list1 = odds[3]
    bookie1_line = odds[4]
    bookie_list2 = odds[5]
    bookie2_line = odds[6]

    max_bookie_list1_bankroll = 0
    max_bookie1 = ""
    for x in bookie_list1:
        if bankrolls[x] > max_bookie_list1_bankroll:
            max_bookie_list1_bankroll = bankrolls[x]
            max_bookie1 = x

    max_bookie_list2_bankroll = 0
    max_bookie2 = ""
    for x in bookie_list2:
        if bankrolls[x] > max_bookie_list2_bankroll:
            max_bookie_list2_bankroll = bankrolls[x]
            max_bookie2 = x

    #bookie2_bankroll = bankrolls[bookie2]

    max_bankroll = max(max_bookie_list1_bankroll, max_bookie_list2_bankroll)

    decimal_odds = american_to_decimal([bookie1_line, bookie2_line])
    stakes = []
    total_implied_probability = 0

    for x in decimal_odds:
        temp_implied_probability = 1/x
        total_implied_probability += temp_implied_probability

    stake1 = round(((max_bankroll * (1/decimal_odds[0]))/total_implied_probability),2)
    stake2 = round(((max_bankroll * (1/decimal_odds[1]))/total_implied_probability),2)

    ev1 = round((stake1 * decimal_odds[0]) - 100, 2)
    ev2 = round((stake2 * decimal_odds[1]) - 100, 2)

    #print(ev1, ev2)

    if(ev1 >= 105):
        stakes.append(f'Sport: {odds[0]}, Home Team: {odds[1]}, Odds: {odds[4]}, Bookie: {max_bookie1}, Amount: {stake1}, EV: {round(ev1, 0)}')
        stakes.append(f'Sport: {odds[0]}, Away Team: {odds[2]}, Odds: {odds[6]}, Bookie: {max_bookie2}, Amount: {stake2}, EV: {round(ev2, 0)}')

        return stakes
    
    else:
        return []


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


'''
odds = ['basketball_nba', 'wizards', 'pacers', ['draftkings'], 380, ['betmgm'], -400]

bankrolls = {'draftkings': 100,
            'betmgm': 100,
            'fanduel': 100,
            'betrivers': 100,
            'fanatics': 100,
            'bet365': 100,
            'williamhill_us': 100,
            'ballybet': 100,
            'espnbet': 100}


stakes = percent_bankroll_ev_bet_two_result(odds, bankrolls)

print(stakes)
'''