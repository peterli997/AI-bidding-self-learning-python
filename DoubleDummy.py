import numpy as np
import time

INPUT_METHOD = 1  # 0 for console, 1 for file
INPUT_FILE_NAME = "input.txt"  # file name for input

Suit = ['S', 'H', 'D', 'C']
Card = ['2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14']
"""
Card code ranges from 0 to 51,
Order: Higher suits are assigned higher codes. Clubs are assigned 0-12, diamonds 13-25, hearts 26-38, and spades 39-51.
Higher ranks are assigned higher codes. 2 of Club is assigned 0. 
"""


def comp(a, b):
    return a//13 == b//13


def MAX_VALUE(state, trump, alpha=0, beta=13, NS=0, EW=13):  # trump: C = 1, D = 2, H = 3, S = 4, NT = 5
    global play
    global card_holder_dict
    m = len(state[0]) + len(state[1]) + len(state[2]) + len(state[3])
    l = ((52 - m) // 4) * 4
    if m == 4:
        assert len(state[0]) == 1, "everyone should have 1 card for the last trick"
        winning_card = list(state[0])[0]
        for i in range(1, 4):
            assert len(state[i]) == 1, "everyone should have 1 card for the last trick"
            next_card = list(state[0])[0]
            if trump == 5:
                if comp(next_card, winning_card) and next_card > winning_card:
                    winning_card = next_card
            else:
                if (comp(next_card, winning_card) and next_card > winning_card) or (next_card // 13 == trump - 1 and winning_card // 13 != trump - 1):
                    winning_card = next_card
        if card_holder_dict[winning_card] % 2 == 0:
            NS += 1
        return NS
    else:
        if m % 4 == 0:
            playable_cards = state[0].copy()
        else:
            first_card = play[l]
            try:
                filter(lambda element: comp(element, first_card), state[0]).__next__()
                playable_cards = set(filter(lambda element: comp(element, first_card), state[0]))
            except StopIteration:
                playable_cards = state[0].copy()
        for k in playable_cards:
            if k % 13 == 0 or k - 1 not in playable_cards:
                s = state.copy()
                play[52 - m] = k
                s[0].remove(k)
                flag = False
                if m % 4 != 1:
                    s = [s[1], s[2], s[3], s[0]]
                else:
                    winning_card = play[l]
                    winner = 0
                    for i in range(l + 1, l + 4):
                        if (comp(play[i], winning_card) and play[i] > winning_card) or (play[i] // 13 == trump - 1 and winning_card // 13 != trump - 1):
                            winning_card = play[i]
                            winner = i - l
                    if card_holder_dict[winning_card] % 2 == 0:
                        flag = True
                        NS += 1
                    else:
                        EW += 1
                    if NS > alpha:
                        alpha = NS
                        if alpha >= beta:
                            s[0].add(k)
                            return alpha
                    if EW < beta:
                        beta = EW
                        if alpha >= beta:
                            s[0].add(k)
                            return alpha
                    if winner == 0:
                        s = [s[1], s[2], s[3], s[0]]
                    elif winner == 1:
                        s = [s[2], s[3], s[0], s[1]]
                    elif winner == 2:
                        s = [s[3], s[0], s[1], s[2]]
                    else:
                        s = [s[0], s[1], s[2], s[3]]
                if flag:
                    alpha = max(alpha, MAX_VALUE(s, trump, alpha, beta, NS, EW))
                else:
                    alpha = max(alpha, MIN_VALUE(s, trump, alpha, beta, NS, EW))
                # if l <= 8:
                #     finish = time.time()
                #     print(finish - start)
                #     quit()
                s[0].add(k)
                if alpha >= beta:
                    return beta
    return alpha


def MIN_VALUE(state, trump, alpha=0, beta=13, NS=0, EW=13):
    global play
    global card_holder_dict
    m = len(state[0]) + len(state[1]) + len(state[2]) + len(state[3])
    l = ((52 - m) // 4) * 4
    if m == 4:
        assert len(state[0]) == 1, "everyone should have 1 card for the last trick"
        winning_card = list(state[0])[0]
        for i in range(1, 4):
            assert len(state[i]) == 1, "everyone should have 1 card for the last trick"
            next_card = list(state[0])[0]
            if trump == 5:
                if comp(next_card, winning_card) and next_card > winning_card:
                    winning_card = next_card
            else:
                if (comp(next_card, winning_card) and next_card > winning_card) or (next_card // 13 == trump - 1 and winning_card // 13 != trump - 1):
                    winning_card = next_card
        if card_holder_dict[winning_card] % 2 == 0:
            NS += 1
        return NS
    else:
        if m % 4 == 0:
            playable_cards = state[0].copy()
        else:
            first_card = play[l]
            try:
                filter(lambda element: comp(element, first_card), state[0]).__next__()
                playable_cards = set(filter(lambda element: comp(element, first_card), state[0]))
            except StopIteration:
                playable_cards = state[0].copy()
        for k in playable_cards:
            if k % 13 == 0 or k - 1 not in playable_cards:
                play[52 - m] = k
                state[0].remove(k)
                flag = False
                if m % 4 != 1:
                    s = [state[1], state[2], state[3], state[0]]
                else:
                    winning_card = play[l]
                    winner = 0
                    for i in range(l + 1, l + 4):
                        if (comp(play[i], winning_card) and play[i] > winning_card) or (play[i] // 13 == trump - 1 and winning_card // 13 != trump - 1):
                            winning_card = play[i]
                            winner = i - l
                    if card_holder_dict[winning_card] % 2 == 0:
                        flag = True
                        NS += 1
                    else:
                        EW += 1
                    if NS > alpha:
                        alpha = NS
                        if alpha >= beta:
                            state[0].add(k)
                            return beta
                    if EW < beta:
                        beta = EW
                        if alpha >= beta:
                            state[0].add(k)
                            return beta
                    if winner == 0:
                        s = [state[1], state[2], state[3], state[0]]
                    elif winner == 1:
                        s = [state[2], state[3], state[0], state[1]]
                    elif winner == 2:
                        s = [state[3], state[0], state[1], state[2]]
                    else:
                        s = [state[0], state[1], state[2], state[3]]
                if flag:
                    beta = min(beta, MAX_VALUE(s, trump, alpha, beta, NS, EW))
                else:
                    beta = min(beta, MIN_VALUE(s, trump, alpha, beta, NS, EW))
                # if l <= 8:
                #     finish = time.time()
                #     print(finish - start)
                #     quit()
                state[0].add(k)
                if alpha >= beta:
                    return alpha
    return beta


def get_suit(card):  # suit function
    """
    Get suit from card code
    :param card: card code
    :return: suit of the card, as string
    """
    if card < 13:
        return 'C'
    elif card < 26:
        return 'D'
    elif card < 39:
        return 'H'
    else:
        return 'S'


def rank_to_string(rank):
    """
    Get the corresponding string of card ranks.
    0 -> "2", ..., 7 -> "9", 8 -> "T", 9 -> "J", 10 -> "Q", 11 -> "K", 12 -> "A"
    :param rank: an integer representing a card rank, range 0-12, 12 the highest rank.
    :return: the corresponding string, as shown on real cards
    """
    if 0 <= rank <= 8:
        return str(rank + 2)
    if rank == 8:
        return "T"
    if rank == 9:
        return "J"
    if rank == 10:
        return "Q"
    if rank == 11:
        return "K"
    if rank == 12:
        return "A"


def hand_to_string(hand):
    """
    Print a hand. Order: S H D C. One suit per line.
    :param hand: list of card index.
    """
    str_list = ["S "]
    for j in [k for k in hand if k > 38]:
        str_list.append(rank_to_string(j % 13))
    str_list.append("\nH ")
    for j in [k for k in hand if 25 < k < 39]:
        str_list.append(rank_to_string(j % 13))
    str_list .append("\nD ")
    for j in [k for k in hand if 12 < k < 26]:
        str_list.append(rank_to_string(j % 13))
    str_list.append("\nC ")
    for j in [k for k in hand if k < 13]:
        str_list.append(rank_to_string(j))
    str_list.append("\n")
    return ''.join(str_list)


def input_hand_from_console(name):  # name: name of hand, hand: list of card code
    output = set()
    for _ in range(13):
        suit = input(name + ", suit (single letter). ")
        while suit not in Suit:
            print("Error. Suit not found.")
            suit = input(
                name + ", re-enter suit (single letter, S = Spades, H = Hearts, D = Diamonds, C = Clubs). ")
        card = input(name + ", card value (J = 11, Q = 12, K = 13, A = 14). ")
        while card not in Card:
            print("Error. Card not found.")
            card = input(
                name + ", re-enter card (2 - 10 = value as shown on card, J = 11, Q = 12, K = 13, A = 14). ")
        if suit == 'C':
            output.add(int(card) - 2)
        if suit == 'D':
            output.add(int(card) + 11)
        if suit == 'H':
            output.add(int(card) + 24)
        if suit == 'S':
            output.add(int(card) + 37)
    return output


def string_to_rank(string):
    """
    Inverse of rank_to_string()
    :param string: string to be parsed
    :return: an integer in range 0-12
    """
    if string == "T":
        return 8
    if string == "J":
        return 9
    if string == "Q":
        return 10
    if string == "K":
        return 11
    if string == "A":
        return 12
    if 2 <= int(string) <= 9:
        return int(string) - 2

def input_hands_from_file(filename, number_of_hands):
    """
    Read hands from file. File format: One line per hand, separate suit by space, suit order: S H D C
    Characters other than 2-9,AKQJT, are ignored
    Example hand with no Diamonds: AKT76 KQ87 X J543
    Ranks are not necessarily ordered.
    Does not check number of cards and suits.
    :param filename: Name of file containing hands
    :param number_of_hands: number of hands to be read
    :return: a list of hands represented by lists of card index.
    """
    hands = []
    with open(filename) as file:
        hand_count = 0
        for line_of_hand in file:
            if hand_count >= number_of_hands:
                break
            curr_hand = set()
            suit_offset = 0
            separated_line = line_of_hand.split()
            for suit in separated_line:
                for rank in suit:
                    if rank in "23456789TJQKA":
                        curr_hand.add(string_to_rank(rank) + suit_offset)
                suit_offset += 13
            hands.append(curr_hand)
            hand_count += 1
    return hands


RC = set(range(52))  # RC for remaining cards
if INPUT_METHOD == 0:
    Nindex = input_hand_from_console("North")
    Sindex = input_hand_from_console("South")
    RC = RC - Nindex
    RC = RC - Sindex
    RC = RC
    RC2 = RC.copy()
elif INPUT_METHOD == 1:
    hands = input_hands_from_file(INPUT_FILE_NAME, 4)
    Nindex = hands[0]
    Sindex = hands[1]
    Windex = hands[1]
    Eindex = hands[1]
else:
    Nindex = set(range(13))
    Sindex = set(range(14, 26))


print("S")
print(hand_to_string(Sindex))
print("N")
print(hand_to_string(Nindex))


if INPUT_METHOD != 1:
    RC = np.array(list(RC2))
    Windex = np.random.choice(a=RC, size=13, replace=False)
    Windex.sort()
    Windex = Windex.tolist()
    Windex = set(Windex)
    RC = set(RC) - Windex
    Eindex = RC


print("W")
print(hand_to_string(Windex))
print("E")
print(hand_to_string(Eindex))
card_holder = np.zeros(52, dtype=int)
card_rank = np.arange(52)
for j in Nindex:
    card_holder[j] = 0
for j in Windex:
    card_holder[j] = 1
for j in Sindex:
    card_holder[j] = 2
for j in Eindex:
    card_holder[j] = 3
card_holder_dict = dict(zip(card_rank, card_holder))
play = [-1] * 52

# Case 1: Trump = NT
# print(type(Windex), type(Sindex), type(Eindex), type(Nindex))
current_state = [Windex, Sindex, Eindex, Nindex]
start = time.time()
print(MAX_VALUE(state=current_state, trump=5), "NT")
# Case 2：Trump = C
start = time.time()
print(MAX_VALUE(state=current_state, trump=1), "C")
# Case 3: Trump = D
start = time.time()
print(MAX_VALUE(state=current_state, trump=2), "D")
# Case 4: Trump = H
start = time.time()
print(MAX_VALUE(state=current_state, trump=3), "H")
# Case 5: Trump = S
start = time.time()
print(MAX_VALUE(state=current_state, trump=4), "S")
print()
