import numpy as np

<<<<<<< HEAD
def suitfc(a): # suit function
    if 0 <= a and a < 13:
        return 'C'
    elif 13 <= a and a < 26:
        return 'D'
    elif 26 <= a and a < 39:
=======

def suitfc(card):  # suit function
    if card < 13:
        return 'C'
    elif card < 26:
        return 'D'
    elif card < 39:
>>>>>>> 0a9b03559c5ea69339fef19bb664c9294fae4a31
        return 'H'
    else:
        return 'S'


<<<<<<< HEAD
=======
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
            suit = input(name + ", re-enter suit (single letter, S = Spades, H = Hearts, D = Diamonds, C = Clubs). ")
        card = input(name + ", card value (J = 11, Q = 12, K = 13, A = 14). ")
        while card not in Card:
            print("Error. Card not found.")
            card = input(name + ", re-enter card (2 - 10 = value as shown on card, J = 11, Q = 12, K = 13, A = 14). ")
        if suit == 'C':
            hand[int(card) - 2] = 1
        if suit == 'D':
            hand[int(card) + 11] = 1
        if suit == 'H':
            hand[int(card) + 24] = 1
        if suit == 'S':
            hand[int(card) + 37] = 1


>>>>>>> 0a9b03559c5ea69339fef19bb664c9294fae4a31
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
    Windex = np.random.choice(a = np.nonzero(RC)[0], size = 13, replace = False)
    Windex.sort()
    j = 0
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
<<<<<<< HEAD
    print("C ", end='')
    for j in np.where(Eindex < 13)[0]:
        if 0 <= Eindex[j] and Eindex[j] < 8:
            print(Eindex[j] + 2, end='')
        if Eindex[j] == 8:
            print("T", end='')
        if Eindex[j] == 9:
            print("J", end='')
        if Eindex[j] == 10:
            print("Q", end='')
        if Eindex[j] == 11:
            print("K", end='')
        if Eindex[j] == 12:
            print("A", end='')
    print()
    print("D ", end='')
    for j in np.where(Eindex[np.where(Eindex < 26)[0]] > 12)[0]:
        if 13 <= Eindex[j] and Eindex[j] < 21:
            print(Eindex[j] - 11, end='')
        if Eindex[j] == 21:
            print("T", end='')
        if Eindex[j] == 22:
            print("J", end='')
        if Eindex[j] == 23:
            print("Q", end='')
        if Eindex[j] == 24:
            print("K", end='')
        if Eindex[j] == 25:
            print("A", end='')
    print()
    print("H ", end='')
    for j in np.where(Eindex[np.where(Eindex < 39)[0]] > 25)[0]:
        if 26 <= Eindex[j] and Eindex[j] < 34:
            print(Eindex[j] - 24, end='')
        if Eindex[j] == 34:
            print("T", end='')
        if Eindex[j] == 35:
            print("J", end='')
        if Eindex[j] == 36:
            print("Q", end='')
        if Eindex[j] == 37:
            print("K", end='')
        if Eindex[j] == 38:
            print("A", end='')
    print()
    print("S ", end='')
    for j in np.where(Eindex[np.where(Eindex < 52)[0]] > 38)[0]:
        if 39 <= Eindex[j] and Eindex[j] < 47:
            print(Eindex[j] - 37, end='')
        if Eindex[j] == 47:
            print("T", end='')
        if Eindex[j] == 48:
            print("J", end='')
        if Eindex[j] == 49:
            print("Q", end='')
        if Eindex[j] == 50:
            print("K", end='')
        if Eindex[j] == 51:
            print("A", end='')
    print()
    print()
    SD = np.array([-1, 12, 25, 38, 51])
    #suit distinguisher
    play = np.zeros(52, dtype = int)
    # alpha = np.arange(14, 15)
    # alpha = alpha.repeat((13, 4))
    # beta = np.arange(-10, -9)
=======
    print_hand(Eindex)

    play = np.zeros((13, 4))
    alpha = np.arange(10, 11)
    alpha = alpha.repeat((13, 4))
    beta = np.arange(-10, -9)
>>>>>>> 0a9b03559c5ea69339fef19bb664c9294fae4a31
    # beta = beta.repeat((13, 4))
    Nindex_image, Windex_image, Sindex_image, Eindex_image = Nindex.copy(), Windex.copy(), Sindex.copy(), Eindex.copy()
    player = np.zeros(52, dtype = int)
    turn_winner = 1
    # N = 0, W = 1, S = 2, E = 3
    count2 = 0
    PC = [0] * 52
    # Playable Cards
    it = [0] * 52
    # iterations
    trickNS, trickEW = 0, 0
    index_set = [Nindex, Windex, Sindex, Eindex]
    # Case 1: Trump = NT
    while count2 in range(52):
        print(count2)
        index_set = [Nindex, Windex, Sindex, Eindex]
        print(index_set)
        if count2 % 4 == 0:
            player[count2] = turn_winner
            PC[count2] = index_set[player[count2]]
        else:
            player[count2] = player[count2 - 1] + 1
            if player[count2] == 4:
                player[count2] = 0
<<<<<<< HEAD
            if len(np.where(SD.searchsorted(index_set[player[count2]]) == SD.searchsorted(play[count2 - count2 % 4]))[0]) == 0:
                PC[count2] = index_set[player[count2]]
            else:
                PC[count2] = index_set[player[count2]][np.where(SD.searchsorted(index_set[player[count2]]) == SD.searchsorted(play[count2 - count2 % 4]))[0]]
        it[count2] = iter(PC[count2])
        print(PC[count2], player[count2])
        try:
            play[count2] = next(it[count2])
            index_set[player[count2]] = index_set[player[count2]].tolist()
            index_set[player[count2]].remove(play[count2])
            index_set[player[count2]] = np.array(index_set[player[count2]])
            # print(index_set[player[count2]])
            print(play)
            if count2 % 4 == 3:
                turn = [play[count2 - 3]]
                i = count2 - 2
                for i in range(count2 - 2, count2 + 1):
                    if suitfc(play[count2 - 3]) == suitfc(play[i]):
                        turn.append(play[i])
                    else:
                        turn.append(0)
                turn_player = [player[count2 - 3], player[count2 - 2], player[count2 - 1], player[count2]]
                turn_winner = turn_player[np.argmax(turn)]
                # print(turn_winner)
                if turn_winner == 0 or turn_winner == 2:
                    trickNS += 1
                else:
                    trickEW += 1
            count2 += 1
            if count2 == 52:
                count2 -= 1
        except StopIteration:
            play[count2] = 0
            if count2 != 0:
                count2 -= 1
=======
        if count2 % 4 == 0:
            for play[count2] in index_set[player[count2]]:
                continue
        else:
            if len(np.where(SD.searchsorted(index_set[player[count2]]) == SD.searchsorted(play[count2 - count2%4]))[0]) == 0:
                for play[count2] in index_set[player[count2]]:
                    continue
>>>>>>> 0a9b03559c5ea69339fef19bb664c9294fae4a31
            else:
                break


    # Case 2：Trump = C
    # Case 3: Trump = D
    # Case 4: Trump = H
    # Case 5: Trump = S
    print()
