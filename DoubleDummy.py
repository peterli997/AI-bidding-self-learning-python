import numpy as np

INPUT_METHOD = 0  # 0 for console, 1 for file
INPUT_FILE_NAME = ""  # file name for input

Suit = ['S', 'H', 'D', 'C']
Card = ['2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14']
"""
Card code ranges from 0 to 51,
Order: Higher suits are assigned higher codes. Clubs are assigned 0-12,
Higher ranks are assigned higher codes. 2 of Club is assigned 0. 
"""


def MAX_VALUE(state, alpha, beta):
    if len(state[0]) + len(state[1]) + len(state[2]) + len(state[3]) == 0:
        return 0
    else:
        for k in state[0]:
            s = state.copy()
            s[0] = s[0].tolist()
            s[0].remove(k)
            s[0] = np.array(s[0])
            alpha = max(alpha, MIN_VALUE(s, alpha, beta))
        if alpha >= beta:
            return beta
        else:
            return alpha


def MIN_VALUE(state, alpha, beta):
    if len(state[0]) + len(state[1]) + len(state[2]) + len(state[3]) == 0:
        return 0
    else:
        for k in state[0]:
            s = state.copy()
            s[0] = s[0].tolist()
            s[0].remove(k)
            s[0] = np.array(s[0])
            beta = min(beta, MAX_VALUE(s, alpha, beta))
        if alpha >= beta:
            return alpha
        else:
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
    for j in hand[hand > 38]:
        str_list.append(rank_to_string(hand[j] % 13))
    str_list.append("\nH")
    for j in hand[(hand < 39) & (hand > 25)]:
        str_list.append(rank_to_string(hand[j] % 13))
    str_list .append("\nD")
    for j in hand[(hand < 26) & (hand > 12)]:
        str_list.append(rank_to_string(hand[j] % 13))
    str_list.append("\nC")
    for j in hand[hand < 13]:
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


RC = np.arange(1, 2) # RC for Remaining Cards
RC = RC.repeat(52)


RC = set(range(52))
if INPUT_METHOD == 0:
    Nindex = input_hand_from_console("North")
    Sindex = input_hand_from_console("South")
elif INPUT_METHOD == 1:
    hands = input_hands_from_file(INPUT_FILE_NAME, 2)
    Nindex = np.array(hands[0])
    Sindex = np.array(hands[1])
else:
    Nindex = []
    Sindex = []
RC = RC - set(Nindex)
RC = RC - set(Sindex)
RC2 = RC.copy()

print("S")
print(hand_to_string(Sindex))
print("N")
print(hand_to_string(Nindex))

for count in range(5):
    RC = RC2
    handW = np.zeros(52)
    handE = np.zeros(52)
    print(count + 1)
    # Windex = np.random.choice(a=np.nonzero(RC)[0], size=13, replace=False)
    # Windex.sort()
    Windex = [26, 30, 32, 36, 37, 38, 39, 40, 43, 45, 48, 49, 51]
    Windex = np.array(Windex)
    for j in range(13):
        handW[Windex[j]] = 1
    print("W")
    print(hand_to_string(Windex))
    RC = RC - handW
    Eindex = np.nonzero(RC)[0]

    for j in range(13):
        handE[Eindex[j]] = 1
    print()
    print("E")
    print(hand_to_string(Eindex))
    # suit distinguisher
    play = np.zeros(52, dtype=int)
    # alpha = np.arange(14, 15)
    # alpha = alpha.repeat((13, 4))
    # beta = np.arange(-10, -9)
    # beta = beta.repeat((13, 4))

    Nindex_image, Windex_image, Sindex_image, Eindex_image = Nindex.copy(), Windex.copy(), Sindex.copy(), Eindex.copy()
    player = np.zeros(52, dtype=int)
    turn_winner = np.zeros(14, dtype=int)
    turn_winner[0] = 1
    # N = 0, W = 1, S = 2, E = 3
    count2 = 0
    PC = [0] * 52
    # Playable Cards
    trickNS, trickEW = 0, 0
    index_set = [Nindex, Windex, Sindex, Eindex]
    j = np.zeros(52, dtype=int)
    # Case 1: Trump = NT
    print(MAX_VALUE(state=[Nindex, Windex, Sindex, Eindex], alpha=-np.infty, beta=np.infty))
    while count2 in range(52):
        while j[count2] in range(53):
            # print(count2, j[count2], play[count2])
            index_set = [Nindex, Windex, Sindex, Eindex]
            # print(index_set)
            # print(Nindex, Windex, Sindex, Eindex)
            if count2 % 4 == 0:
                player[count2] = turn_winner[count2//4]
                PC[count2] = index_set[player[count2]]
            else:
                player[count2] = player[count2 - 1] + 1
                player[count2] = player[count2] % 4
                if len(np.where(SD.searchsorted(index_set[player[count2]]) == SD.searchsorted(play[count2 - count2 % 4]))[0]) == 0:
                    PC[count2] = index_set[player[count2]]
                else:
                    PC[count2] = index_set[player[count2]][np.where(SD.searchsorted(index_set[player[count2]]) == SD.searchsorted(play[count2 - count2 % 4]))[0]]

            if j[count2] == 52:
                if count2 == 0:
                    j[count2] = 53
                else:
                    # print(play[count2], bool(play[count2]))
                    if play[count2] != -1:
                        # print(player[count2], 1)
                        if player[count2] == 0:
                            Nindex = Nindex.tolist()
                            Nindex.append(play[count2])
                            Nindex = np.array(Nindex)
                            Nindex.sort()
                        elif player[count2] == 1:
                            Windex = Windex.tolist()
                            Windex.append(play[count2])
                            Windex = np.array(Windex)
                            Windex.sort()
                        elif player[count2] == 2:
                            Sindex = Sindex.tolist()
                            Sindex.append(play[count2])
                            Sindex = np.array(Sindex)
                            Sindex.sort()
                        else:
                            Eindex = Eindex.tolist()
                            Eindex.append(play[count2])
                            Eindex = np.array(Eindex)
                            Eindex.sort()
                        # print(Nindex, Windex, Sindex, Eindex, 1)
                        play[count2] = -1
                    j[count2] = 0
                    count2 -= 1
            elif j[count2] not in PC[count2]:
                j[count2] += 1
            else:
                if play[count2] and play[count2] != -1:
                    # print(player[count2], 2)
                    if player[count2] == 0:
                        Nindex = Nindex.tolist()
                        Nindex.append(play[count2])
                        Nindex = np.array(Nindex)
                        Nindex.sort()
                    elif player[count2] == 1:
                        Windex = Windex.tolist()
                        Windex.append(play[count2])
                        Windex = np.array(Windex)
                        Windex.sort()
                    elif player[count2] == 2:
                        Sindex = Sindex.tolist()
                        Sindex.append(play[count2])
                        Sindex = np.array(Sindex)
                        Sindex.sort()
                    else:
                        Eindex = Eindex.tolist()
                        Eindex.append(play[count2])
                        Eindex = np.array(Eindex)
                        Eindex.sort()
                    # print(Nindex, Windex, Sindex, Eindex, 2)
                play[count2] = j[count2]
                # print(player[count2], 3)
                if player[count2] == 0:
                    Nindex = Nindex.tolist()
                    Nindex.remove(play[count2])
                    Nindex = np.array(Nindex, dtype=int)
                elif player[count2] == 1:
                    Windex = Windex.tolist()
                    Windex.remove(play[count2])
                    Windex = np.array(Windex, dtype=int)
                elif player[count2] == 2:
                    Sindex = Sindex.tolist()
                    Sindex.remove(play[count2])
                    Sindex = np.array(Sindex, dtype=int)
                else:
                    Eindex = Eindex.tolist()
                    Eindex.remove(play[count2])
                    Eindex = np.array(Eindex, dtype=int)
                # print(Nindex, Windex, Sindex, Eindex, 3)
                if count2 % 4 == 3:
                    turn = [play[count2 - 3]]
                    i = count2 - 2
                    for i in range(count2 - 2, count2 + 1):
                        if suitfc(play[count2 - 3]) == suitfc(play[i]):
                            turn.append(play[i])
                        else:
                            turn.append(0)
                    turn_player = [player[count2 - 3], player[count2 - 2], player[count2 - 1], player[count2]]
                    turn_winner[count2//4 + 1] = turn_player[np.argmax(turn)]
                    # print(turn_winner)
                    if turn_winner[count2//4] == 0 or turn_winner[count2//4] == 2:
                        trickNS += 1
                    else:
                        trickEW += 1
                count2 += 1
                if count2 == 52:
                    print(play)
                    count2 -= 1
                    # print(player[count2], 4)
                    if player[count2] == 0:
                        Nindex = Nindex.tolist()
                        Nindex.append(play[count2])
                        Nindex = np.array(Nindex, dtype=int)
                        Nindex.sort()
                    elif player[count2] == 1:
                        Windex = Windex.tolist()
                        Windex.append(play[count2])
                        Windex = np.array(Windex, dtype=int)
                        Windex.sort()
                    elif player[count2] == 2:
                        Sindex = Sindex.tolist()
                        Sindex.append(play[count2])
                        Sindex = np.array(Sindex, dtype=int)
                        Sindex.sort()
                    else:
                        Eindex = Eindex.tolist()
                        Eindex.append(play[count2])
                        Eindex = np.array(Eindex, dtype=int)
                        Eindex.sort()
                    # print(Nindex, Windex, Sindex, Eindex, 4)
                    play[count2] = -1
                    j[count2] += 1
        break
    # Case 2：Trump = C
    # Case 3: Trump = D
    # Case 4: Trump = H
    # Case 5: Trump = S
    print()
