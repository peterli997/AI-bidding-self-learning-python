import numpy as np


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

def suitfc(card):  # suit function
    if card < 13:
        return 'C'
    elif card < 26:
        return 'D'
    elif card < 39:
        return 'H'
    else:
        return 'S'

def print_hand(hand):  # print hand, index list
    print("C ", end='')
    for j in np.where(hand < 13)[0]:
        if hand[j] in range(0, 8):
            print(hand[j] + 2, end='')
        if hand[j] == 8:
            print("T", end='')
        if hand[j] == 9:
            print("J", end='')
        if hand[j] == 10:
            print("Q", end='')
        if hand[j] == 11:
            print("K", end='')
        if hand[j] == 12:
            print("A", end='')
    print()
    print("D ", end='')
    for j in np.where(hand[np.where(hand < 26)[0]] > 12)[0]:
        if hand[j] in range(13, 21):
            print(hand[j] - 11, end='')
        if hand[j] == 21:
            print("T", end='')
        if hand[j] == 22:
            print("J", end='')
        if hand[j] == 23:
            print("Q", end='')
        if hand[j] == 24:
            print("K", end='')
        if hand[j] == 25:
            print("A", end='')
    print()
    print("H ", end='')
    for j in np.where(hand[np.where(hand < 39)[0]] > 25)[0]:
        if hand[j] in range(26, 34):
            print(hand[j] - 24, end='')
        if hand[j] == 34:
            print("T", end='')
        if hand[j] == 35:
            print("J", end='')
        if hand[j] == 36:
            print("Q", end='')
        if hand[j] == 37:
            print("K", end='')
        if hand[j] == 38:
            print("A", end='')
    print()
    print("S ", end='')
    for j in np.where(hand[np.where(hand < 52)[0]] > 38)[0]:
        if hand[j] in range(39, 47):
            print(hand[j] - 37, end='')
        if hand[j] == 47:
            print("T", end='')
        if hand[j] == 48:
            print("J", end='')
        if hand[j] == 49:
            print("Q", end='')
        if hand[j] == 50:
            print("K", end='')
        if hand[j] == 51:
            print("A", end='')
    print()


def input_hand(name, hand):  # name: name of hand, hand: place to put the hand
    for count in range(13):
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
            hand[int(card) - 2] = 1
        if suit == 'D':
            hand[int(card) + 11] = 1
        if suit == 'H':
            hand[int(card) + 24] = 1
        if suit == 'S':
            hand[int(card) + 37] = 1




handN = np.zeros(52)
handW = np.zeros(52)
handS = np.zeros(52)
handE = np.zeros(52)
RC = np.arange(1, 2) # RC for Remaining Cards
RC = RC.repeat(52)

Suit = ['S', 'H', 'D', 'C']
Card = ['2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14']

input_hand("North", handN)
RC = RC - handN
input_hand("South", handS)
RC = RC - handS
RC2 = RC.copy()

Nindex = np.where(handN == 1)[0]
Sindex = np.where(handS == 1)[0]

print("S")
print_hand(Sindex)
print("N")
print_hand(Nindex)

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
    print_hand(Windex)
    RC = RC - handW
    Eindex = np.nonzero(RC)[0]
    for j in range(13):
        handE[Eindex[j]] = 1
    print()
    print("E")
    print_hand(Eindex)
    SD = np.array([-1, 12, 25, 38, 51])
    #suit distinguisher
    play = np.zeros(52, dtype = int)
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
