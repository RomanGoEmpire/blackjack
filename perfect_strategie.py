import csv
import random
import matplotlib.pyplot as plt


def create_list(name):
    with open(name, 'r') as f:
        reader = csv.reader(f)
        return list(reader)


def flatten(list):
    result = []
    for item in list:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result


hard_totals = create_list('tables/hard_totals.csv')
soft_totals = create_list('tables/soft_totals.csv')
pair_splitting = create_list('tables/pair_splitting.csv')


def create_single_deck():
    deck = []
    for number in range(2, 12):
        for _ in range(4):
            deck.append(number)
    random.shuffle(deck)
    return deck


def create_six_deck():
    deck = []
    for _ in range(7):
        deck.extend(create_single_deck())
    random.shuffle(deck)
    return deck


deck = create_six_deck()


def get_hand():
    card1 = deck.pop()
    card2 = deck.pop()
    update_count(card1)
    update_count(card2)
    return [card1, card2]


def has_two_cards(hand):
    return len(hand) == 2


def add_card(hand):
    card = deck.pop()
    hand += [card]
    update_count(card)
    return hand


def has_hand_been_split(hand):
    return any(isinstance(i, list) or i is None for i in hand)


def print_hand(hand, is_dealer=False, is_hidden=False):
    string = ""
    if is_dealer:
        string += "Dealer: "
        if is_hidden:
            string += ", ".join(str(card) for card in hand)
            string += f" -> {sum(hand)}"
        else:
            string += str(hand[0])
    else:
        if has_hand_been_split(hand):
            string += "Player: "
            for hands in hand:
                string += ", ".join(str(card) for card in hands)
                string += f" -> {sum(hands)}\n"
        else:
            string += "Player: " + ", ".join(str(card) for card in hand) + f" -> {sum(hand)}"
    # print(string)


def get_value_of_hand(hand, is_dealer=False):
    if is_dealer:
        return hand[0]
    return sum(hand)


def has_ace(hand):
    return 11 in hand


def get_correct_decision(player_hand, dealer_value):
    player_value = get_value_of_hand(player_hand)
    if has_two_cards(player_hand) and (
            player_value == 16 and dealer_value == (9 or 10 or 11) or player_value == 15 and dealer_value == 10):
        return "Surrender"
    decision = ""
    if player_hand[0] == player_hand[1] and has_two_cards(player_hand) and HANDS < 4:
        decision = get_split_decision(player_hand, dealer_value)
    if decision == "Yes" or decision == "Yes/No":
        return "Yes"
    elif has_ace(player_hand) and has_two_cards(player_hand):
        return get_soft_decision(player_hand, dealer_value)
    else:
        decision = get_hard_decision(player_hand, dealer_value)
        if decision == "Double":
            if has_two_cards(player_hand):
                global BET
                BET *= 2
                return "Double"
            else:
                return "Hit"
        else:
            return decision


def get_hard_decision(hand, dealer_value):
    your_value = get_value_of_hand(hand)
    if your_value == 16 and TRUE_COUNT > 0:
        return "Stand"
    if your_value > 17:
        return "Stand"
    if your_value < 8:
        return "Hit"

    index_you = 18 - your_value
    index_dealer = dealer_value - 1
    return hard_totals[index_you][index_dealer]


def get_soft_decision(hand, dealer_value):
    your_value = hand[0] if hand[1] == 11 else hand[1]
    index_you = 10 - your_value
    index_dealer = dealer_value - 1

    return soft_totals[index_you][index_dealer]


def get_split_decision(hand, dealer_value):
    your_value = hand[0]

    index_you = 12 - your_value
    index_dealer = dealer_value - 1

    return pair_splitting[index_you][index_dealer]


def is_correct_guess(best):
    guess = input('What is the move?\n').lower()
    return guess == 's' and best == "Stand" or \
        guess == 'h' and best == "Hit" or \
        guess == 'd' and best == "Double" or \
        guess == 'ds' and best == "Ds" or \
        guess == 'y' and best == 'Yes' or \
        guess == 'n' and best == "No" or \
        guess == 'yn' and best == "Yes/No"


def player_has_blackjack(hand):
    return get_value_of_hand(hand) == 21


def result_of_split(player_hand, dealer_hand):
    global HANDS
    # print("Split")
    hand1 = [player_hand[0], deck.pop()]
    hand2 = [player_hand[1], deck.pop()]
    HANDS += 1
    # print_hand(hand1)
    # print_hand(hand2)
    # print()
    hand1 = play_hand_player(hand1, dealer_hand)
    hand2 = play_hand_player(hand2, dealer_hand)
    return [hand1, hand2]


def update_count(card):
    global COUNT
    if card < 7:
        COUNT += 1
    elif card > 9:
        COUNT -= 1


def result_of_hit(player_hand, dealer_hand):
    dealer_value = get_value_of_hand(dealer_hand, True)
    add_card(player_hand)
    if get_value_of_hand(player_hand) > 21 and has_ace(player_hand):
        player_hand = change_aceto1(player_hand)
    elif get_value_of_hand(player_hand) > 21:
        return player_hand
    # print_hand(player_hand)
    decision = get_correct_decision(player_hand, dealer_value)
    # print(decision)
    if decision == "Stand":
        return player_hand
    elif decision == "Hit":
        return result_of_hit(player_hand, dealer_hand)
    else:
        print("Something went wrong")


def result_of_double(player_hand):
    add_card(player_hand)
    if get_value_of_hand(player_hand) > 21 and has_ace(player_hand):
        player_hand = change_aceto1(player_hand)
    return player_hand


def play_hand_player(player_hand, dealer_hand):
    # print("Player turn")
    # print_hand(dealer_hand, True)
    # print_hand(player_hand)
    dealer_value = get_value_of_hand(dealer_hand, True)
    decision = get_correct_decision(player_hand, dealer_value)
    # print(decision)
    match decision:
        case "Surrender":
            return None
        case "Stand":
            return player_hand
        case "Double":
            return result_of_double(player_hand)
        case "Ds":
            return result_of_double(player_hand)
        case "Hit":
            return result_of_hit(player_hand, dealer_hand)
        case "Yes/No":
            return result_of_split(player_hand, dealer_hand)
        case "Yes":
            return result_of_split(player_hand, dealer_hand)


def play_hand_player_2(player_hand):
    if get_value_of_hand(player_hand) == 21:
        return player_hand
    if get_value_of_hand(player_hand) > 21 and has_ace(player_hand):
        player_hand = change_aceto1(player_hand)
    elif get_value_of_hand(player_hand) > 21:
        return player_hand
    if get_value_of_hand(player_hand) == 16 and TRUE_COUNT > 0:
        return player_hand
    if get_value_of_hand(player_hand) == 11 and has_two_cards(player_hand):
        global BET
        BET *= 2
        add_card(player_hand)
        return player_hand
    while get_value_of_hand(player_hand) < 17:
        add_card(player_hand)
        # print_hand(dealer_hand, True, True)
    # print()
    return player_hand


def change_aceto1(hand):
    index = hand.index(11)
    hand[index] = 1
    return hand


def play_dealer_hand(dealer_hand):
    # print("Dealer's turn")
    if get_value_of_hand(dealer_hand) == 21:
        return dealer_hand
    if get_value_of_hand(dealer_hand) > 21 and has_ace(dealer_hand):
        dealer_hand = change_aceto1(dealer_hand)
    elif get_value_of_hand(dealer_hand) > 21:
        return dealer_hand
    while get_value_of_hand(dealer_hand) < 17:
        add_card(dealer_hand)
        # print_hand(dealer_hand, True, True)
    # print()
    return dealer_hand


def decide_winner(hand, final_hand_dealer):
    global BANKROLL
    global WINS
    global TOTAL_HANDS
    # player busts
    if get_value_of_hand(hand) > 21:
        # print("Player busts")
        BANKROLL -= BET
        TOTAL_HANDS += 1
        BANKROLL_HISTORY.append(BANKROLL)
        return "Dealer"
    # if both have the same value then no one wins
    if get_value_of_hand(hand) == get_value_of_hand(final_hand_dealer):
        TOTAL_HANDS += 1
        # print("Push")
        return "Push"
    # player has higher value than dealer or dealer busts
    if get_value_of_hand(hand) > get_value_of_hand(final_hand_dealer) or get_value_of_hand(final_hand_dealer) > 21:
        # Larger payout for blackjack
        if player_has_blackjack(hand) and has_two_cards(hand):
            # print("Player has blackjack")
            BANKROLL += BET * 1.5
            WINS += 1
            TOTAL_HANDS += 1
            BANKROLL_HISTORY.append(BANKROLL)
        # Normal payout
        else:
            # print("Player wins")
            BANKROLL += BET
            WINS += 1
            TOTAL_HANDS += 1
            BANKROLL_HISTORY.append(BANKROLL)
        return "Player"
    # dealer has higher value than player
    else:
        # print("Dealer wins")
        BANKROLL -= BET
        TOTAL_HANDS += 1
        BANKROLL_HISTORY.append(BANKROLL)
        return "Dealer"


INITIAL_BANKROLL = 100000
BANKROLL = 100000
BANKROLL_HISTORY = []
ROUNDS = 0
BET = 1
HANDS = 1
COUNT = 0
TRUE_COUNT = 0
WINS = 0
TOTAL_HANDS = 0


def get_splitted_winner(hand, final_hand_dealer):
    global BANKROLL
    global TOTAL_HANDS
    if hand is None:
        BANKROLL -= BET / 2
        TOTAL_HANDS += 1
        BANKROLL_HISTORY.append(BANKROLL)
        # print("Surrender")
        return
    if type(hand[0]) is int and type(hand[1]) is int:
        # print_hand(hand)
        # print_hand(final_hand_dealer, True, True)
        decide_winner(hand, final_hand_dealer)
    else:
        for h in hand:
            get_splitted_winner(h, final_hand_dealer)


def play_round(amount):
    global BANKROLL
    global deck
    global BET
    global ROUNDS
    global HANDS
    global COUNT
    global TRUE_COUNT
    global TOTAL_HANDS

    for i in range(amount):
        # print(f'bet: {bet}')
        if BANKROLL <= 0:
            # print("You lost all your money")
            break
        if len(deck) < 25:
            deck = create_six_deck()
            COUNT = 0
        player_hand = get_hand()
        dealer_hand = get_hand()

        # if dealer_hand[0] == 11 and TRUE_COUNT >= 5:
        #     # print("Insurance")
        #     BANKROLL -= BET / 2
        #     if dealer_hand[1] == 10:
        #         BANKROLL += BET
        #         # print("Insurance won")
        #     else:
        #         # print("Insurance lost")
        #         pass
        final_hand_player = play_hand_player(player_hand, dealer_hand)
        # final_hand_player = play_hand_player_2(player_hand)

        if final_hand_player is None:
            BANKROLL -= BET / 2
            TOTAL_HANDS += 1
            BANKROLL_HISTORY.append(BANKROLL)
            # print("Surrender")
            continue

        final_hand_dealer = play_dealer_hand(dealer_hand)

        if has_hand_been_split(final_hand_player):
            get_splitted_winner(final_hand_player, final_hand_dealer)
        else:
            # print_hand(final_hand_player)
            # print_hand(final_hand_dealer, True, True)
            decide_winner(final_hand_player, final_hand_dealer)

        # print("Bankroll: " + str(bankroll))
        print("--------------------")
        print('Statistics')
        HANDS = 1
        ROUNDS += 1
        deck_left = (len(deck) / 52)
        TRUE_COUNT = COUNT / deck_left
        print(f'count: {COUNT}')
        print(f'deck_left: {deck_left}')
        print(f'True count: {TRUE_COUNT}')
        BET = 1
        # if TRUE_COUNT > 1:
        #     BET = int(TRUE_COUNT) * 10
        #     if BET > 100:
        #         BET = 100
        print("--------------------")


def plot_history(backroll_history):
    plt.plot(backroll_history)
    plt.show()


if __name__ == '__main__':
    play_round(1000000000)
    plot_history(BANKROLL_HISTORY)
    print(f"rounds: {ROUNDS}")
    print(f"average loss per round: {INITIAL_BANKROLL / ROUNDS}")
    print(f"win rate: {WINS / TOTAL_HANDS}")
