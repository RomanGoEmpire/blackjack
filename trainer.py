import csv
import random


def create_single_deck():
    deck = []
    for number in ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']:
        for suit in ['♤', '♥', '♣', '♦']:
            deck.append(f'{number}{suit}')
    random.shuffle(deck)
    return deck


def create_six_deck():
    deck = []
    for i in range(6):
        deck += create_single_deck()
    return deck


def get_hand(deck):
    return [deck.pop(), deck.pop()]


def print_hand(hand, is_dealer=False):
    if is_dealer:
        print(f"Dealer: {hand[0]}")
    else:
        print(f"You: {hand[0]}, {hand[1]}")


def get_value_of_hand(hand, is_dealer=False):
    def convert_card_into_value(card):
        number = card[0]
        if number in ['A', 'K', 'Q', 'J']:
            number = 11 if number == 'A' else 10
        else:
            number = int(number)
        return number

    opened = convert_card_into_value(hand[0])
    closed = convert_card_into_value(hand[1])

    return opened if is_dealer else opened + closed


def get_correct_decision(your_number, dealer_number, decision_list):
    if your_number > 17:
        return "Stand"
    if your_number < 8:
        return "Hit"
    index_dealer = dealer_number - 1
    index_you = 18 - your_number
    return decision_list[index_you][index_dealer]


def create_list(name):
    with open(name, 'r') as f:
        reader = csv.reader(f)
        return list(reader)


def is_correct_guess(best):
    guess = input('What is the move?\n').lower()
    return guess == 's' and best == "Stand" or guess == 'h' and best == "Hit" or guess == 'd' and best == "Double"


if __name__ == '__main__':
    decision_list = create_list('hardtotals.csv')
    deck = create_six_deck()

    statistics = {'correct': 0, 'false': 0}

    while True:
        if len(deck) < 4:
            deck = create_six_deck()

        hand = get_hand(deck)
        dealer_hand = get_hand(deck)

        your_value = get_value_of_hand(hand)
        dealer_value = get_value_of_hand(dealer_hand, True)

        best_decision = get_correct_decision(your_value, dealer_value, decision_list)

        print_hand(hand)
        print_hand(dealer_hand, True)

        if not is_correct_guess(best_decision):
            print(f'Wrong. Best move is: {best_decision}')
            statistics['false'] += 1
        print('Correct')
        statistics['correct'] += 1

        if input() == "q":
            print(statistics)
            break
