import numpy as np
import time
from itertools import permutations
import os
from collections import Counter
import pickle
import profile
import math

INPUT_METHOD = 1  # 0 for console, 1 for file
INPUT_FILE_NAME = "input.txt"  # file name for input

TRICK_LOOKUP_TABLE = False # if using trick lookup table

LINK_LEVEL = 9 # number of remaining tricks to be stored - 1
HASH_MOD = [64,65536,536870912,8589934592,4611686018427387904,4611686018427387904,4611686018427387904,
            4611686018427387904,4611686018427387904,4611686018427387904,4611686018427387904,4611686018427387904,
            4611686018427387904,4611686018427387904,4611686018427387904,4611686018427387904,4611686018427387904]
DETAILED_LINK_OBJ = True # if links are stored

Suit = ['S', 'H', 'D', 'C']
Card = ['2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14']
TEST_L = 8 # -1 for complete run
"""
Card code ranges from 0 to 51,
Order: Higher suits are assigned higher codes. Clubs are assigned 0-12, diamonds 13-25, hearts 26-38, and spades 39-51.
Higher ranks are assigned higher codes. 2 of Club is assigned 0. 
"""


class SuitLink:
    def __init__(self, link):
        if DETAILED_LINK_OBJ:
            self.compressed_link = list(filter(lambda x: x != -1, link))
            self.cache_hash = self.hashing(self.compressed_link)
        else:
            compressed_link = list(filter(lambda x: x != -1, link))
            self.cache_hash = self.hashing(compressed_link)

    def __str__(self):
        return str(self.compressed_link) if DETAILED_LINK_OBJ else str(self.cache_hash)

    @staticmethod
    def hashing(comp_link):
        hashed = 0
        for i in comp_link:
            hashed = hashed * 4 + i
        return hashed * 17 + len(comp_link) - 1

    def __hash__(self):  # different hash => different link
        return self.cache_hash

    def __eq__(self, other):
        return self.cache_hash == other.cache_hash

    def __bool__(self):
        return self.cache_hash != -1

    def __len__(self):
        return (self.cache_hash+1) % 17


class SuitLevelLinks:
    def __init__(self, link_dict, trump, leader=0):
        if leader != 0:
            links = []
            link_trump = SuitLink([])
            for i, link in link_dict.items():
                if i == trump - 1:
                    link_trump = SuitLink([(x - leader) % 4 for x in link if x != -1])
                elif link != [-1] * 13:
                    links.append(SuitLink([(x - leader) % 4 for x in link if x != -1]))
        else:
            links = [SuitLink(y) for x, y in link_dict.items() if x != trump - 1 and y != [-1] * 13]
            link_trump = SuitLink(link_dict[trump-1]) if trump != 5 else SuitLink([])
        if DETAILED_LINK_OBJ:
            self.links = (links, link_trump)
        self.cache_links_hash = (sorted([x.__hash__() for x in links]), link_trump.__hash__())
        self.cache_hash = self.hashing(self.cache_links_hash)
        # assert len(self) % 4 == 0

    def __str__(self):
        if DETAILED_LINK_OBJ:
            result = "{"
            for i in self.links[0]:
                result += str(i)
                result += ', '
            result += '}'
            return result + " trump:" + str(self.links[1])
        else:
            return str(self.cache_links_hash)

    @staticmethod
    def hashing(links_hash):
        hashed = links_hash[1]
        for i in links_hash[0]:
            hashed = (hashed * 1140850699 + i) % HASH_MOD[LINK_LEVEL]  # it is a prime above max hash of link
        return hashed

    def __hash__(self):
        return self.cache_hash

    def __eq__(self, other):
        if self.cache_hash != other.cache_hash:
            return False
        return self.cache_links_hash == other.cache_links_hash

    def __len__(self):
        result = 0
        for i in self.cache_links_hash[0]:
            result += (i+1) % 17
        return result + (1 + self.cache_links_hash[1]) % 17



def pickle_dump_link_lookup_table():
    if DETAILED_LINK_OBJ:
        f = open("detailed_link_lookup_table.pkl", 'wb+')
    else:
        f = open("compressed_link_lookup_table.pkl", 'wb+')
    pickle.dump(link_lookup_table, f, pickle.HIGHEST_PROTOCOL)
    f.close()


def update_link_lookup_table(suit_level_links, NS_min, EW_min):
    global link_lookup_table
    if suit_level_links in link_lookup_table:
        NS_min1, EW_min1 = link_lookup_table[suit_level_links]
        # assert NS_min > NS_min1, "stored NS value should change"
        # assert EW_min > EW_min1, "stored EW value should change"
        NS_min1 = NS_min1 if NS_min1 > NS_min else NS_min
        EW_min1 = EW_min1 if EW_min1 > EW_min else EW_min
        link_lookup_table[suit_level_links] = (NS_min1, EW_min1)
    else:
        link_lookup_table[suit_level_links] = (NS_min, EW_min)


def MAX_VALUE(state, trump, alpha=0, beta=13, NS=0, EW=13):  # trump: C = 1, D = 2, H = 3, S = 4, NT = 5
    # print(state, trump, alpha, beta, NS, EW, "max")
    global play
    global card_holder_dict
    global suit_level_links
    global link_lookup_table
    global start
    alpha2 = alpha

    m = len(state[0]) + len(state[1]) + len(state[2]) + len(state[3])
    l = ((52 - m) // 4) * 4
    if m == 4:
        assert len(state[0]) == 1, "everyone should have 1 card for the last trick"
        if TRICK_LOOKUP_TABLE:
            winning_pos = int(trick_lookup_table[trump-1][next(iter(state[0]))][next(iter(state[1]))][next(iter(state[2]))][next(iter(state[3]))])
        else:
            winning_pos = decide_winner([next(iter(state[0])), next(iter(state[1])), next(iter(state[2])), next(iter(state[3]))], trump - 1)
        if winning_pos % 2 == 0:
            NS += 1
        return NS
    else:
        cur_player = card_holder_dict[next(iter(state[0]))]
        if m % 4 == 0:
            if m <= LINK_LEVEL * 4 + 4:
                links = SuitLevelLinks(suit_level_links, trump, cur_player)
                if len(links) != m:
                    pass
                assert len(links) == m, str(m)+ str(links)
                if links in link_lookup_table:
                    remaining_NS, remaining_EW = link_lookup_table[links]
                    if remaining_EW + remaining_NS == m // 4:
                        assert NS + remaining_NS == EW - remaining_EW, "NS EW should be the same if" \
                            " remaining is determined" + str(remaining_NS) + str(remaining_EW)
                        # print("max, read from lookup table, completely searched", state, remaining_NS, remaining_EW)
                        return NS + remaining_NS
                    if remaining_NS + NS > alpha:
                        alpha = remaining_NS + NS
                        alpha2 = alpha
                        if alpha >= beta:      # remaining_NS + NS = alpha
                            # print("max, read from lookup table, partially searched", state, remaining_NS, remaining_EW)
                            return remaining_NS + NS
                    # EW -= m // 4 - remaining_tricks
                    if EW - remaining_EW < beta:
                        beta = EW - remaining_EW
                        if beta <= alpha:  # EW - m % 4 + remaining_EW = beta
                            # print("max, read from lookup table, partially searched", state, remaining_NS, remaining_EW)
                            return alpha
            playable_cards = state[0].copy()
            # remaining_cards[math.ceil(m / 4) - 1] = state[0] | state[1] | state[2] | state[3]
            # # remaining_cards[math.ceil(m / 4) - 1].sort()  ########################################
        else:
            first_card = play[l]
            playable_cards = set(filter(lambda element: element // 13 == first_card // 13, state[0]))
            if not playable_cards:
                playable_cards = state[0].copy()
            # print(first_card, playable_cards, state[0])
        # print(m, state[0], playable_cards, remaining_cards[math.ceil(m/4) - 1])
        for k in playable_cards:
            bool_consecutive_card = True
            temp_link = suit_level_links[k//13]
            for i in range(k % 13 - 1, -1, -1):
                if temp_link[i] != -1:
                    if temp_link[i] == cur_player:
                        bool_consecutive_card = False
                    break
            # if l:
            #     if remaining_cards[math.ceil(m/4) - 1].index(k):
            #         bool_consecutive_card = k // 13 != remaining_cards[math.ceil(m/4) - 1][remaining_cards[math.ceil(m/4) - 1].index(k) - 1] // 13 or remaining_cards[math.ceil(m/4) - 1][remaining_cards[math.ceil(m/4) - 1].index(k) - 1] not in playable_cards
            #         # print(k, remaining_cards[math.ceil(m/4) - 1][remaining_cards[math.ceil(m/4) - 1].index(k) - 1])
            #     else:
            #         bool_consecutive_card = True
            # else:
            #     bool_consecutive_card = not k % 13 or k - 1 not in playable_cards
            # # print(k, bool_consecutive_card)
            #
            if bool_consecutive_card:
                play[52 - m] = k
                state[0].remove(k)                    # remove from state
                # print("max-in", state, k)
                assert suit_level_links[k//13][k % 13] == cur_player
                if m % 4 != 1:   # not end of trick
                    s = [state[1], state[2], state[3], state[0]]
                    alpha = max(alpha, MIN_VALUE(s, trump, alpha, beta, NS, EW))
                    # print("max-out", state, k)
                else:     # end of trick
                    if TRICK_LOOKUP_TABLE:
                        winner = int(trick_lookup_table[trump-1][play[l]][play[l+1]][play[l+2]][play[l+3]])
                    else:
                        winner = decide_winner(play[l:l+4], trump - 1)
                    if winner % 2 == 1:
                        NS += 1
                        if NS > alpha:
                            alpha = NS
                            if alpha >= beta:
                                state[0].add(k)
                                return alpha
                        if winner == 3:
                            s = state[:]
                        else:
                            s = state[2:] + state[:2]
                        for k in play[l:l+4]:
                            suit_level_links[k // 13][k % 13] = -1  # remove from suit_level_links
                        alpha = max(alpha, MAX_VALUE(s, trump, alpha, beta, NS, EW))
                        temp_player = (cur_player + 1) % 4
                        for k in play[l:l+4]:
                            suit_level_links[k // 13][k % 13] = temp_player  # return back to suit_level_links
                            temp_player = (temp_player + 1) % 4
                        # print("alpha = max(max), ", alpha, s, trump, alpha, beta, NS, EW)
                        # print("max-out", state, k)
                        NS -= 1
                    else:
                        EW -= 1
                        if EW < beta:
                            beta = EW
                            if alpha >= beta:
                                state[0].add(k)
                                return alpha
                        s = state[winner + 1:] + state[:winner + 1]
                        # print("alpha is about to = max(min)", alpha, s, trump, alpha, beta, NS, EW)
                        for k in play[l:l+4]:
                            suit_level_links[k // 13][k % 13] = -1  # remove from suit_level_links
                        alpha = max(alpha, MIN_VALUE(s, trump, alpha, beta, NS, EW))
                        temp_player = (cur_player + 1) % 4
                        for k in play[l:l+4]:
                            suit_level_links[k // 13][k % 13] = temp_player  # return back to suit_level_links
                            temp_player = (temp_player + 1) % 4
                        # print("alpha = max(min), ", alpha, s, trump, alpha, beta, NS, EW)
                        # print("max-out", state, k)
                        EW += 1
                if l <= TEST_L:
                    finish = time.time()
                    print(finish - start)
                    pickle_dump_link_lookup_table()
                    quit()
                state[0].add(k)                                      # give back to state
                if alpha >= beta:
                    # print(state, trump, alpha, beta, NS, EW, "=", beta, "2")
                    if m % 4 == 0 and m <= LINK_LEVEL * 4 + 4:
                        if alpha - alpha2 > 0:
                            update_link_lookup_table(links, alpha - NS, 0)
                    return alpha
    if m % 4 == 0 and m <= LINK_LEVEL * 4 + 4:
        if alpha - alpha2 > 0:
            update_link_lookup_table(links, alpha - NS, 0)
    # print(state, trump, alpha, beta, NS, EW, "=", alpha, "3")
    return alpha


def MIN_VALUE(state, trump, alpha=0, beta=13, NS=0, EW=13):
    # print(state, trump, alpha, beta, NS, EW, "min")
    global play
    global card_holder_dict
    global suit_level_links
    global link_lookup_table
    global start
    beta2 = beta
    m = len(state[0]) + len(state[1]) + len(state[2]) + len(state[3])
    l = ((52 - m) // 4) * 4
    if m == 4:
        assert len(state[0]) == 1, "everyone should have 1 card for the last trick"
        if TRICK_LOOKUP_TABLE:
            winning_pos = int(trick_lookup_table[trump-1][next(iter(state[0]))][next(iter(state[1]))][next(iter(state[2]))][next(iter(state[3]))])
        else:
            winning_pos = decide_winner(
                [next(iter(state[0])), next(iter(state[1])), next(iter(state[2])), next(iter(state[3]))], trump - 1)
        if winning_pos % 2 == 1:
            NS += 1
        return NS
    else:
        cur_player = card_holder_dict[next(iter(state[0]))]
        if m % 4 == 0:
            if m <= LINK_LEVEL * 4 + 4:
                links = SuitLevelLinks(suit_level_links, trump, cur_player)
                if links in link_lookup_table:
                    remaining_EW, remaining_NS = link_lookup_table[links]
                    if remaining_EW + remaining_NS == m // 4:
                        assert NS + remaining_NS == EW - remaining_EW, "NS EW should be the same if" \
                                                                                  " remaining is determined"
                        # print("min, read from lookup table, completely searched", state, remaining_EW, remaining_NS)
                        return NS + remaining_NS
                    if remaining_NS + NS > alpha:
                        alpha = remaining_NS + NS
                        if alpha >= beta:  # remaining_NS + NS = alpha
                            # print("min, read from lookup table, partially searched", state, remaining_EW, remaining_NS)
                            return beta
                    # EW -= m // 4 - remaining_tricks
                    if EW - remaining_EW < beta:
                        beta = EW - remaining_EW
                        beta2 = beta
                        if beta <= alpha:  # EW - m % 4 + remaining_EW = beta
                            # print("min, read from lookup table, partially searched", state, remaining_EW, remaining_NS)
                            return EW - remaining_EW
            playable_cards = state[0].copy()
        else:
            first_card = play[l]
            playable_cards = set(filter(lambda element: element//13 == first_card//13, state[0]))
            if not playable_cards:
                playable_cards = state[0].copy()
        for k in playable_cards:
            # if l:
            #     if remaining_cards[math.ceil(m/4) - 1].index(k):
            #         bool_consecutive_card = k // 13 != remaining_cards[math.ceil(m/4) - 1][remaining_cards[math.ceil(m/4) - 1].index(k) - 1] // 13 or remaining_cards[math.ceil(m/4) - 1][remaining_cards[math.ceil(m/4) - 1].index(k) - 1] not in playable_cards
            #         # print(k, remaining_cards[math.ceil(m/4) - 1][remaining_cards[math.ceil(m/4) - 1].index(k) - 1])
            #     else:
            #         bool_consecutive_card = True
            # else:
            #     bool_consecutive_card = k - 1 not in playable_cards or not k % 13
            # # print(k, bool_consecutive_card)
            bool_consecutive_card = True
            temp_link = suit_level_links[k // 13]
            for i in range(k % 13 - 1, -1, -1):
                if temp_link[i] != -1:
                    if temp_link[i] == cur_player:
                        bool_consecutive_card = False
                    break
            if bool_consecutive_card:
                play[52 - m] = k
                state[0].remove(k)
                # print("min-out", state, k)

                if m % 4 != 1:
                    s = [state[1], state[2], state[3], state[0]]
                    beta = min(beta, MAX_VALUE(s, trump, alpha, beta, NS, EW))
                    # print("min-out", state, k)
                else:
                    if TRICK_LOOKUP_TABLE:
                        winner = int(trick_lookup_table[trump-1][play[l]][play[l+1]][play[l+2]][play[l+3]])
                    else:
                        winner = decide_winner(play[l:l + 4], trump - 1)
                    if winner % 2 != 0:
                        EW -= 1
                        if EW < beta:
                            beta = EW
                            if alpha >= beta:
                                state[0].add(k)
                                return beta
                        s = state[winner + 1:] + state[:winner + 1]
                        for k in play[l:l+4]:
                            suit_level_links[k // 13][k % 13] = -1  # remove from suit_level_links
                        beta = min(beta, MIN_VALUE(s, trump, alpha, beta, NS, EW))
                        temp_player = (cur_player + 1) % 4
                        for k in play[l:l+4]:
                            suit_level_links[k // 13][k % 13] = temp_player  # return back to suit_level_links
                            temp_player = (temp_player + 1) % 4
                        # print("min-out", state, k)
                        EW += 1
                    else:
                        NS += 1
                        if NS > alpha:
                            alpha = NS
                            if alpha >= beta:
                                state[0].add(k)
                                return beta
                        if winner != 3:
                            s = state[winner + 1:] + state[:winner + 1]
                        else:
                            s = state[:]
                        for k in play[l:l+4]:
                            suit_level_links[k // 13][k % 13] = -1  # remove from suit_level_links
                        beta = min(beta, MAX_VALUE(s, trump, alpha, beta, NS, EW))
                        temp_player = (cur_player + 1) % 4
                        for k in play[l:l + 4]:
                            suit_level_links[k // 13][k % 13] = temp_player  # return back to suit_level_links
                            temp_player = (temp_player + 1) % 4
                        # print("min-in", state, k)
                        NS -= 1
                if l <= TEST_L:
                    finish = time.time()
                    print(finish - start)
                    pickle_dump_link_lookup_table()
                    quit()
                state[0].add(k)

                if alpha >= beta:
                    # print(state, trump, alpha, beta, NS, EW, "=", alpha, "5")
                    if m % 4 == 0 and m <= LINK_LEVEL * 4 + 4:
                        if beta2 - beta > 0:
                            update_link_lookup_table(links, EW - beta, 0)
                    return beta
    if m % 4 == 0 and m <= LINK_LEVEL * 4 + 4:
        if beta2-beta > 0:
            update_link_lookup_table(links, EW - beta, 0)
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

def decide_winner(trick, trump):
    winning_card = trick[0]
    winner = 0
    for i in range(4):
        if (trick[i] // 13 == winning_card // 13 and trick[i] > winning_card) or (
                trick[i] // 13 == trump and winning_card // 13 != trump):
            winning_card = trick[i]
            winner = i
    return winner


def create_lookup_table():
    global trick_lookup_table
    trick_lookup_table = np.zeros(shape=(5, 52, 52, 52, 52))
    for trick in permutations(range(52), 4):
        for trump in range(5):
            winning_card = trick[0]
            winner = 0
            for i in range(4):
                if (trick[i] // 13 == winning_card // 13 and trick[i] > winning_card) or (
                        trick[i] // 13 == trump and winning_card // 13 != trump):
                    winning_card = trick[i]
                    winner = i
            trick_lookup_table[trump][trick[0]][trick[1]][trick[2]][trick[3]] = winner
    # start = time.time()
    np.save("trick_lookup_table", trick_lookup_table)
    # finish = time.time()
    # print("save using np.save() time:", finish - start)


suit_level_links = []
start = 0


def main():
    global play
    global card_holder_dict
    global suit_level_links
    global link_lookup_table
    global start

    RC = set(range(52))  # RC for remaining cards
    if INPUT_METHOD == 0:
        Nindex = input_hand_from_console("North")
        Sindex = input_hand_from_console("South")

    elif INPUT_METHOD == 1:
        hands = input_hands_from_file(INPUT_FILE_NAME, 4)
        Nindex = hands[0]
        Eindex = hands[1]
        Sindex = hands[2]
        Windex = hands[3]
    else:
        Nindex = set(range(13))
        Sindex = set(range(14, 26))

    print("S")
    print(hand_to_string(Sindex))
    print("N")
    print(hand_to_string(Nindex))

    if INPUT_METHOD != 1:
        RC = RC - Nindex
        RC = RC - Sindex
        RC = RC
        RC2 = RC.copy()
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
    if TRICK_LOOKUP_TABLE:
        if os.path.exists("trick_lookup_table.npy"):
            trick_lookup_table = np.load("trick_lookup_table.npy")
        else:
            create_lookup_table()

    if DETAILED_LINK_OBJ:
        if os.path.exists("detailed_link_lookup_table.pkl"):
            f = open("detailed_link_lookup_table.pkl", 'rb')
            link_lookup_table = pickle.load(f)
            f.close()
        else:
            link_lookup_table = dict()
    else:
        if os.path.exists("compressed_link_lookup_table.pkl"):
            f = open("compressed_link_lookup_table.pkl", 'rb')
            link_lookup_table = pickle.load(f)
            f.close()
        else:
            link_lookup_table = dict()

    card_holder = np.empty(52, dtype=int)
    card_holder.fill(-1)
    card_rank = np.arange(52).tolist()
    card_suit = np.arange(4).tolist()
    for j in Nindex:
        card_holder[j] = 0
    for j in Eindex:
        card_holder[j] = 1
    for j in Sindex:
        card_holder[j] = 2
    for j in Windex:
        card_holder[j] = 3
    suit_level_links = np.resize(card_holder, (4, 13)).tolist()
    suit_level_links = dict(zip(card_suit, suit_level_links))
    card_holder_dict = dict(zip(card_rank, card_holder.tolist()))
    # card_holder_dict is a dictionary that sends every card to the player that holds it in the beginning
    play = [-1] * 52
    # play stores card codes of cards that have been played in order, and -1 represents haven't reached that turn yet
    play_len = len(Windex)
    # Case 1: Trump = NT
    # print(type(Windex), type(Sindex), type(Eindex), type(Nindex))
    current_state = [Nindex, Eindex, Sindex, Windex]
    start = time.time()
    print(MAX_VALUE(state=current_state, trump=5, alpha=0, beta=play_len, NS=0, EW= play_len), "NT")
    end = time.time()
    print(end-start)
    # Case 2：Trump = C
    start = time.time()
    print(MAX_VALUE(state=current_state, trump=1, alpha=0, beta=play_len, NS=0, EW= play_len), "C")
    end = time.time()
    print(end-start)
    # Case 3: Trump = D
    start = time.time()
    print(MAX_VALUE(state=current_state, trump=2, alpha=0, beta=play_len, NS=0, EW=play_len), "D")
    end = time.time()
    print(end-start)
    # Case 4: Trump = H
    start = time.time()
    print(MAX_VALUE(state=current_state, trump=3, alpha=0, beta=play_len, NS=0, EW= play_len), "H")
    end = time.time()
    print(end-start)
    # Case 5: Trump = S
    start = time.time()
    print(MAX_VALUE(state=current_state, trump=4, alpha=0, beta=play_len, NS=0, EW= play_len), "S")
    print(end-start)
    print()
    pickle_dump_link_lookup_table()


if __name__ == '__main__':
    main()
    # profile.run('main()')


def minMax(play1, card_holder_dict1, state1, length):
    global play
    global card_holder_dict
    global start
    play = play1
    card_holder_dict = card_holder_dict1

    start = time.time()
    c = MAX_VALUE(state=state1, trump=5, alpha=0, beta=length, NS=0, EW=length)
    finish = time.time()
    print(c)
    print(finish - start)
