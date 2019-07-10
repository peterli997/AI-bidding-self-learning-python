import numpy as np

def suitfc(a): # suit function
    if a in range(13):
        return 'C'
    elif a in range(26):
        return 'D'
    elif a in range(39):
        return 'H'
    else:
        return 'S'

handN = np.zeros(52)
handW = np.zeros(52)
handS = np.zeros(52)
handE = np.zeros(52)
RC = np.arange(1, 2) # RC for Remaining Cards
RC = RC.repeat(52)

count = 0
Suit = ['S', 'H', 'D', 'C']
Card = ['2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14']
for count in range(13):
    suit = input("North, suit (single letter). ")
    while suit not in Suit:
        print("Error. Suit not found.")
        suit = input("North, re-enter suit (single letter, S = Spades, H = Hearts, D = Diamonds, C = Clubs). ")
    card = input("North, card value (J = 11, Q = 12, K = 13, A = 14). ")
    while card not in Card:
        print("Error. Card not found.")
        card = input("North, re-enter card (2 - 10 = value as shown on card, J = 11, Q = 12, K = 13, A = 14). ")
    if suit == 'C':
        handN[int(card) - 2] = 1
    if suit == 'D':
        handN[int(card) + 11] = 1
    if suit == 'H':
        handN[int(card) + 24] = 1
    if suit == 'S':
        handN[int(card) + 37] = 1

RC = RC - handN

count = 0
for count in range(13):
    suit = input("South, suit (single letter). ")
    while suit not in Suit:
        print("Error. Suit not found.")
        suit = input("South, re-enter suit (single letter, S = Spades, H = Hearts, D = Diamonds, C = Clubs). ")
    card = input("South, card value (J = 11, Q = 12, K = 13, A = 14). ")
    while card not in Card:
        print("Error. Card not found.")
        card = input("South, re-enter card (2 - 10 = value as shown on card, J = 11, Q = 12, K = 13, A = 14). ")
    if suit == 'C':
        handS[int(card) - 2] = 1
    if suit == 'D':
        handS[int(card) + 11] = 1
    if suit == 'H':
        handS[int(card) + 24] = 1
    if suit == 'S':
        handS[int(card) + 37] = 1

RC = RC - handS
RC2 = RC.copy()

count = 0
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
    print("C ", end='')
    for j in np.where(Windex < 13)[0]:
        if Windex[j] in range(0, 8):
            print(Windex[j] + 2, end='')
        if Windex[j] == 8:
            print("T", end='')
        if Windex[j] == 9:
            print("J", end='')
        if Windex[j] == 10:
            print("Q", end='')
        if Windex[j] == 11:
            print("K", end='')
        if Windex[j] == 12:
            print("A", end='')
    print()
    print("D ", end='')
    for j in np.where(Windex[np.where(Windex < 26)[0]] > 12)[0]:
        if Windex[j] in range(13, 21):
            print(Windex[j] - 11, end='')
        if Windex[j] == 21:
            print("T", end='')
        if Windex[j] == 22:
            print("J", end='')
        if Windex[j] == 23:
            print("Q", end='')
        if Windex[j] == 24:
            print("K", end='')
        if Windex[j] == 25:
            print("A", end='')
    print()
    print("H ", end='')
    for j in np.where(Windex[np.where(Windex < 39)[0]] > 25)[0]:
        if Windex[j] in range(26, 34):
            print(Windex[j] - 24, end='')
        if Windex[j] == 34:
            print("T", end='')
        if Windex[j] == 35:
            print("J", end='')
        if Windex[j] == 36:
            print("Q", end='')
        if Windex[j] == 37:
            print("K", end='')
        if Windex[j] == 38:
            print("A", end='')
    print()
    print("S ", end='')
    for j in np.where(Windex[np.where(Windex < 52)[0]] > 38)[0]:
        if Windex[j] in range(39, 47):
            print(Windex[j]- 37, end='')
        if Windex[j] == 47:
            print("T", end='')
        if Windex[j] == 48:
            print("J", end='')
        if Windex[j] == 49:
            print("Q", end='')
        if Windex[j] == 50:
            print("K", end='')
        if Windex[j] == 51:
            print("A", end='')
    print()
    RC = RC - handW
    Eindex = np.nonzero(RC)[0]
    j = 0
    for j in range(13):
        handE[Eindex[j]] = 1
    print()
    print("E")
    print("C ", end='')
    for j in np.where(Eindex < 13)[0]:
        if Eindex[j] in range(0, 8):
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
        if Eindex[j] in range(13, 21):
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
        if Eindex[j] in range(26, 34):
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
        if Eindex[j] in range(39, 47):
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
    play = np.zeros((13, 4))
    alpha = np.arange(10, 11)
    alpha = alpha.repeat((13, 4))
    beta = np.arange(-10, -9)
    beta = beta.repeat((13, 4))
    handN_image, handW_image, handS_image, handE_image = handN.copy(), handW.copy(), handS.copy(), handE.copy()
    player = 2 # N = 1, W = 2, S = 3, E = 4
    trickNS, trickEW = 0, 0
    # Case 1: Trump = NT
    if count2%4 == 0:
        
    # Case 2：Trump = C
    # Case 3: Trump = D
    # Case 4: Trump = H
    # Case 5: Trump = S
    print()
