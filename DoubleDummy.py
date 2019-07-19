import numpy as np
import time
import math

INPUT_METHOD = 0  # 0 for console, 1 for file
INPUT_FILE_NAME = ""  # file name for input

Suit = ['S', 'H', 'D', 'C']
Card = ['2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14']
"""
Card code ranges from 0 to 51,
Order: Higher suits are assigned higher codes. Clubs are assigned 0-12, diamonds 13-25, hearts 26-38, and spades 39-51.
Higher ranks are assigned higher codes. 2 of Club is assigned 0. 
"""
remaining_cards = [0] * 13


def MAX_VALUE(state, trump, alpha=0, beta=13, NS=0, EW=13):  # trump: C = 1, D = 2, H = 3, S = 4, NT = 5
    # print(state, trump, alpha, beta, NS, EW, "max")
    global play
    global card_holder_dict
    global remaining_cards
    a = NS
    b = EW
    m = len(state[0]) + len(state[1]) + len(state[2]) + len(state[3])
    l = ((52 - m) // 4) * 4
    if m == 4:
        winning_card = state[0][0]
        for i in range(1, 4):
            if (state[i][0] // 13 == winning_card // 13 and state[i][0] > winning_card) or (state[i][0] // 13 == trump - 1 and winning_card // 13 != trump - 1):
                winning_card = state[i][0]
            # print(state[i][0], winning_card)
        # print(winning_card, card_holder_dict[winning_card])
        if not card_holder_dict[winning_card] % 2:
            NS = a + 1
        # print(state, trump, alpha, beta, NS, EW, "=", NS, "1")
        return NS
    else:
        if not m % 4:
            playable_cards = set(state[0])
            remaining_cards[math.ceil(m/4) - 1] = state[0] + state[1] + state[2] + state[3]
            remaining_cards[math.ceil(m/4) - 1].sort()
        else:
            first_card = play[l]
            if not set(filter(lambda element: element // 13 == first_card // 13, state[0])):
                playable_cards = set(state[0])
            else:
                playable_cards = set(filter(lambda element: element // 13 == first_card // 13, state[0]))
            # print(first_card, playable_cards, state[0])
        # print(m, state[0], playable_cards, remaining_cards[math.ceil(m/4) - 1])
        for k in playable_cards:
            if l:
                if remaining_cards[math.ceil(m/4) - 1].index(k):
                    bool_consecutive_card = k // 13 != remaining_cards[math.ceil(m/4) - 1][remaining_cards[math.ceil(m/4) - 1].index(k) - 1] // 13 or remaining_cards[math.ceil(m/4) - 1][remaining_cards[math.ceil(m/4) - 1].index(k) - 1] not in playable_cards
                    # print(k, remaining_cards[math.ceil(m/4) - 1][remaining_cards[math.ceil(m/4) - 1].index(k) - 1])
                else:
                    bool_consecutive_card = True
            else:
                bool_consecutive_card = not k % 13 or k - 1 not in playable_cards
            # print(k, bool_consecutive_card)
            if bool_consecutive_card:
                # print(state[0], k)
                s = state.copy()
                t = s[0].copy()
                play[52 - m] = k
                t.remove(k)
                flag = False
                if m % 4 != 1:
                    s = [s[1], s[2], s[3], t]
                else:
                    winning_card = play[l]
                    winner = 0
                    for i in range(l + 1, l + 4):
                        if (play[i] // 13 == winning_card // 13 and play[i] > winning_card) or (play[i] // 13 == trump - 1 and winning_card // 13 != trump - 1):
                            winning_card = play[i]
                            winner = i - l
                    if not card_holder_dict[winning_card] % 2:
                        flag = True
                        NS = a + 1
                    else:
                        EW = b - 1
                    if NS > alpha:
                        alpha = NS
                        # print("alpha = NS, ", alpha)
                        if alpha >= beta:
                            return alpha
                    if EW < beta:
                        beta = EW
                        if alpha >= beta:
                            return alpha
                    if not winner:
                        s = [s[1], s[2], s[3], t]
                    elif winner == 1:
                        s = [s[2], s[3], t, s[1]]
                    elif winner == 2:
                        s = [s[3], t, s[1], s[2]]
                    else:
                        s = [t, s[1], s[2], s[3]]
                if flag:
                    alpha = max(alpha, MAX_VALUE(s, trump, alpha, beta, NS, EW))
                    # print("alpha = max(max), ", alpha, s, trump, alpha, beta, NS, EW)
                else:
                    # print("alpha is about to = max(min)", alpha, s, trump, alpha, beta, NS, EW)
                    alpha = max(alpha, MIN_VALUE(s, trump, alpha, beta, NS, EW))
                    # print("alpha = max(min), ", alpha, s, trump, alpha, beta, NS, EW)
                if l <= 8:
                    finish = time.time()
                    print(finish - start)
                    quit()
                if alpha >= beta:
                    # print(state, trump, alpha, beta, NS, EW, "=", beta, "2")
                    return beta
    # print(state, trump, alpha, beta, NS, EW, "=", alpha, "3")
    return alpha


def MIN_VALUE(state, trump, alpha=0, beta=13, NS=0, EW=13):
    # print(state, trump, alpha, beta, NS, EW, "min")
    global play
    global card_holder_dict
    global remaining_cards
    a = NS
    b = EW
    m = len(state[0]) + len(state[1]) + len(state[2]) + len(state[3])
    l = ((52 - m) // 4) * 4
    if m == 4:
        winning_card = state[0][0]
        for i in range(1, 4):
            if (state[i][0] // 13 == winning_card // 13 and state[i][0] > winning_card) or (state[i][0] // 13 == trump - 1 and winning_card // 13 != trump - 1):
                winning_card = state[i][0]
        if card_holder_dict[winning_card] % 2:
            EW = b - 1
        # print(state, trump, alpha, beta, NS, EW, "=", EW, "4")
        return EW
    else:
        if not m % 4:
            playable_cards = set(state[0])
            remaining_cards[math.ceil(m/4) - 1] = state[0] + state[1] + state[2] + state[3]
            remaining_cards[math.ceil(m/4) - 1].sort()
        else:
            first_card = play[l]
            if not set(filter(lambda element: element // 13 == first_card // 13, state[0])):
                playable_cards = set(state[0])
            else:
                playable_cards = set(filter(lambda element: element // 13 == first_card // 13, state[0]))
            # print(first_card, playable_cards, state[0])
        # print(state[0], playable_cards, remaining_cards[math.ceil(m/4) - 1])
        for k in playable_cards:
            if l:
                if remaining_cards[math.ceil(m/4) - 1].index(k):
                    bool_consecutive_card = k // 13 != remaining_cards[math.ceil(m/4) - 1][remaining_cards[math.ceil(m/4) - 1].index(k) - 1] // 13 or remaining_cards[math.ceil(m/4) - 1][remaining_cards[math.ceil(m/4) - 1].index(k) - 1] not in playable_cards
                    # print(k, remaining_cards[math.ceil(m/4) - 1][remaining_cards[math.ceil(m/4) - 1].index(k) - 1])
                else:
                    bool_consecutive_card = True
            else:
                bool_consecutive_card = k - 1 not in playable_cards or not k % 13
            # print(k, bool_consecutive_card)
            if bool_consecutive_card:
                # print(state[0], k)
                s = state.copy()
                t = s[0].copy()
                play[52 - m] = k
                t.remove(k)
                flag = True
                if m % 4 != 1:
                    s = [s[1], s[2], s[3], t]
                else:
                    winning_card = play[l]
                    winner = 0
                    for i in range(l + 1, l + 4):
                        if (play[i] // 13 == winning_card // 13 and play[i] > winning_card) or (play[i] // 13 == trump - 1 and winning_card // 13 != trump - 1):
                            winning_card = play[i]
                            winner = i - l
                    if not card_holder_dict[winning_card] % 2:
                        NS = a + 1
                    else:
                        flag = False
                        EW = b - 1
                    if NS > alpha:
                        alpha = NS
                        if alpha >= beta:
                            return beta
                    if EW < beta:
                        beta = EW
                        if alpha >= beta:
                            return beta
                    if not winner:
                        s = [s[1], s[2], s[3], t]
                    elif winner == 1:
                        s = [s[2], s[3], t, s[1]]
                    elif winner == 2:
                        s = [s[3], t, s[1], s[2]]
                    else:
                        s = [t, s[1], s[2], s[3]]
                if flag:
                    beta = min(beta, MAX_VALUE(s, trump, alpha, beta, NS, EW))
                else:
                    beta = min(beta, MIN_VALUE(s, trump, alpha, beta, NS, EW))
                if l <= 8:
                    finish = time.time()
                    print(finish - start)
                    quit()
                if alpha >= beta:
                    # print(state, trump, alpha, beta, NS, EW, "=", alpha, "5")
                    return alpha
    # print(state, trump, alpha, beta, NS, EW, "=", beta, "6")
    return beta
"""
Above is the minimax algorithm, showing that on NS perspective, North and South (dummy controlled by North) aims to
maximize NS tricks, where East and West aims to minimize EW tricks. Both MAX_VALUE and MIN_VALUE returns the number of
NS tricks. MAX_VALUE returns at this state, given EW's best effort to minimize NS tricks, how many tricks can NS get.
MIN_VALUE returns at this state, at most how many tricks can NS get with all possible plays (potentially not with any
effort towards the bridge game's goals).
Alpha-beta algorithm is an algorithm that skips unnecessary nodes in a bridge game that aims to optimize the algorithm.
The effectiveness of the optimization from the alpha-beta algorithm depends on how the tree is approached with the
algorithm, which in turn depends on the actual distribution of hands. Nevertheless, alpha-beta will skip nodes and
should be faster than minimax algorithm itself.
"""


def get_suit(card):
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
    output = []
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
            output.append(int(card) - 2)
        if suit == 'D':
            output.append(int(card) + 11)
        if suit == 'H':
            output.append(int(card) + 24)
        if suit == 'S':
            output.append(int(card) + 37)
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
    if 0 <= string <= 8:
        return str(string + 2)


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
            curr_hand = []
            suit_offset = 0
            separated_line = line_of_hand.split(" ")
            for suit in separated_line:
                for rank in suit:
                    curr_hand.append(string_to_rank(rank) + suit_offset)
                suit_offset += 13
            hands.append(curr_hand)
            hand_count += 1
    return hands

play = [-1] * 52
card_holder = [-1] * 52
card_rank = list(range(52))
n = [0, 11, 15, 22, 25, 27, 33, 35, 38, 40, 41, 45, 47]
w = [1, 7, 9, 12, 21, 24, 30, 31, 36, 39, 43, 44, 48]
s = [3, 6, 8, 13, 17, 18, 19, 23, 32, 34, 37, 50, 51]
e = [2, 4, 5, 10, 14, 16, 20, 26, 28, 29, 33, 42, 46]
for j in s:
    card_holder[j] = 0
for j in w:
    card_holder[j] = 1
for j in n:
    card_holder[j] = 2
for j in e:
    card_holder[j] = 3
card_holder_dict = dict(zip(card_rank, card_holder))
start = time.time()
c = MAX_VALUE(state=[n, w, s, e], trump=5, alpha=0, beta=len(n), NS=0, EW=len(n))
finish = time.time()
print(c, "NT")
print(finish - start)
start = time.time()
c = MAX_VALUE(state=[n, w, s, e], trump=1, alpha=0, beta=len(n), NS=0, EW=len(n))
finish = time.time()
print(c, "C")
print(finish - start)
start = time.time()
c = MAX_VALUE(state=[n, w, s, e], trump=2, alpha=0, beta=len(n), NS=0, EW=len(n))
finish = time.time()
print(c, "D")
print(finish - start)
start = time.time()
c = MAX_VALUE(state=[n, w, s, e], trump=3, alpha=0, beta=len(n), NS=0, EW=len(n))
finish = time.time()
print(c, "H")
print(finish - start)
start = time.time()
c = MAX_VALUE(state=[n, w, s, e], trump=4, alpha=0, beta=len(n), NS=0, EW=len(n))
finish = time.time()
print(c, "S")
print(finish - start)
quit()

RC = set(range(52))  # RC for remaining cards
if INPUT_METHOD == 0:
    Nindex = input_hand_from_console("North")
    Sindex = input_hand_from_console("South")
elif INPUT_METHOD == 1:
    hands = input_hands_from_file(INPUT_FILE_NAME, 2)
    Nindex = np.array(hands[0])
    Sindex = np.array(hands[1])
    Nindex = Nindex.tolist()
    Sindex = Sindex.tolist()
else:
    Nindex = []
    Sindex = []
RC = RC - set(Nindex)
RC = RC - set(Sindex)
RC = list(RC)
RC2 = RC.copy()

print("N")
print(hand_to_string(Nindex))
print("S")
print(hand_to_string(Sindex))


for count in range(5):
    RC = RC2
    print(count + 1)
    Windex = list(np.random.choice(a=RC, size=13, replace=False))
    Windex.sort()
    print("W")
    print(hand_to_string(Windex))
    RC = set(RC) - set(Windex)
    RC = list(RC)
    Eindex = RC

    print()
    print("E")
    print(hand_to_string(Eindex))
    card_holder = [-1] * 52
    card_rank = list(range(52))
    for j in Sindex:
        card_holder[j] = 0
    for j in Windex:
        card_holder[j] = 1
    for j in Nindex:
        card_holder[j] = 2
    for j in Eindex:
        card_holder[j] = 3
    card_holder_dict = dict(zip(card_rank, card_holder))
    # card_holder_dict is a dictionary that sends every card to the player that holds it in the beginning
    play = [-1] * 52
    # play stores card codes of cards that have been played in order, and -1 represents haven't reached that turn yet

    # Case 1: Trump = NT
    # print(type(Windex), type(Sindex), type(Eindex), type(Nindex))
    current_state = [Windex, Nindex, Eindex, Sindex]
    start = time.time()
    print(MAX_VALUE(state=current_state, trump=5, alpha=0, beta=13, NS=0, EW=13), "NT")
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