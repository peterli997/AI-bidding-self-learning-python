import numpy as np
import time
from itertools import permutations
import os
from collections import Counter
import pickle
import math

INPUT_METHOD = 1  # 0 for console, 1 for file
INPUT_FILE_NAME = "input.txt"  # file name for input

TRICK_LOOKUP_TABLE = False  # if using trick lookup table

LINK_LEVEL = 11  # number of remaining tricks to be stored - 1
HASH_MOD = [64,65536,536870912,8589934592,4611686018427387904,4611686018427387904,4611686018427387904,
            4611686018427387904,4611686018427387904,4611686018427387904,4611686018427387904,4611686018427387904,
            4611686018427387904,4611686018427387904,4611686018427387904,4611686018427387904,4611686018427387904]
DETAILED_LINK_OBJ = False  # if links are stored

Suit = ['S', 'H', 'D', 'C']
Card = ['2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14']
TEST_L = -1 # -1 for complete run
COLLISION_DETECTOR = dict()
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
        if self.cache_hash in COLLISION_DETECTOR:
            if self.compressed_link != COLLISION_DETECTOR[self.cache_hash]:
                print(self.cache_hash, self.compressed_link, COLLISION_DETECTOR[self.cache_hash])
                quit()
        COLLISION_DETECTOR[self.cache_hash] = self.compressed_link

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
        if DETAILED_LINK_OBJ:
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
            self.links = (links, link_trump)
            self.cache_links_hash = (sorted([x.__hash__() for x in links]), link_trump.__hash__())
            self.cache_hash = self.hashing(self.cache_links_hash)
        else:
            if leader != 0:
                links = []
                link_trump = -1
                for i, link in link_dict.items():
                    if i == trump - 1:
                        link_trump = SuitLink.hashing([(x - leader) % 4 for x in link if x != -1])
                    elif link != [-1] * 13:
                        links.append(SuitLink.hashing([(x - leader) % 4 for x in link if x != -1]))
            else:
                links = [SuitLink.hashing([z for z in y if z != -1]) for x, y in link_dict.items() if x != trump - 1 and y != [-1] * 13]
                link_trump = SuitLink.hashing([z for z in link_dict[trump-1] if z != -1]) if trump != 5 else -1
            self.cache_links_hash = (sorted(links), link_trump)
            self.cache_hash = self.hashing(self.cache_links_hash)
            if self.cache_links_hash[0][0] < 0:
                print(self.cache_links_hash[0][0], link_dict, trump)
                quit()

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


class DoubleDummySolver:
    def __init__(self, suit_level_links, link_lookup_table, trump, state):
        # TODO: change type(state) from set to tuple
        self.play = [-1] * 52
        self.card_rank = list(range(52))
        self.card_holder = [-1] * 52
        self.Nindex = state[0]
        self.Eindex = state[1]
        self.Sindex = state[2]
        self.Windex = state[3]
        for card in self.Nindex:
            self.card_holder[card] = 0
        for card in self.Eindex:
            self.card_holder[card] = 1
        for card in self.Sindex:
            self.card_holder[card] = 2
        for card in self.Windex:
            self.card_holder[card] = 3
        self.card_holder_dict = dict(zip(self.card_rank, self.card_holder))
        card_suit = range(4)
        self.suit_level_links = np.resize(self.card_holder, (4, 13)).tolist()
        self.suit_level_links = dict(zip(card_suit, self.suit_level_links))
        self.link_lookup_table = link_lookup_table
        self.start = time.time()
        self.trump = trump

    def decide_winner(self, trick):
        winning_card = trick[0]
        winner = 0
        for i in range(4):
            if (trick[i] // 13 == winning_card // 13 and trick[i] > winning_card) or (
                    trick[i] // 13 == self.trump - 1 and winning_card // 13 != self.trump - 1):
                winning_card = trick[i]
                winner = i
        return winner

    # TODO: remove trump
    # TODO: add N, the total number of tricks
    def MAX_VALUE(self, state, alpha=0, beta=0, NS=0, EW=0, play_number=0):  # trump: C = 1, D = 2, H = 3, S = 4, NT = 5
        """
        Main method for the Min-Max algorithm.
        It is equipped with "partial" alpha-beta pruning and memoization.
        This algorithm computes the maximum number of tricks that NS can take under optimal strategies for all players.
        The round start with North.
        :param state: the state of the current board, tuple of four lists of hands.
        :param trump: the trump of the current round.
        :param alpha: alpha in alpha-beta pruning, the maximum lower bound of the true value,
                    the minimum number of cards that the current team (team with the current player) is able to get.
        :param beta: 13 minus beta in alpha-beta pruning, 13 minus the minimum upper bound of the true value,
                    the minimum number of cards that the other team is able to get.
        :param NS: the current number of tricks that the current team has taken.
        :param EW: the current number of tricks that the other team has taken.
        :param play_number: the number of the current play.
        :return: (returned_)alpha, the maximum number of tricks the team of the first player can get,
                 f_NS, the maximum number of tricks remaining for the team of the first player,
                 f_EW, the maximum number of tricks remaining for the other team.
                 beta is not returned since it is not used.
                 It is guaranteed that f_NS, f_EW satisfy the following:
                 f_EW + f_NS = number of remaining tricks
                 or f_NS > number of total tricks - beta
                 or f_EW > number of total tricks - alpha
             f_NS^ \       |   EW + f_EW + alpha = N
                 | x \     |
                 |----\-----------  NS + f_NS + beta = N
                 |     \   |
                 |      \  |
                 |       \ |
                 |        \|
                 |         \
                 |         |\
                 |         |x\  f_NS + f_EW  = M
                 +-------------------------> f_EW
        Can be anywhere in the upper left, lower right triangles (with x in them), or on the f_NS + f_EW = m line.
        Here, N is total number of tricks, M is remaining number of tricks.
        """
        print(self.trump, alpha, beta, NS, EW)
        # alpha is used for pruning, f_NS is used for memoization
        pos_in_trick = play_number % 4
        trick_number = play_number // 4
        f_NS = 0
        f_NS2 = 0
        f_EW = 0
        f_EW2 = 0
        m = 52 - play_number
        # When it is the last trick, find the result of the trick and return the result
        if trick_number == 12:
            assert len(state[0]) == 1, "everyone should have 1 card for the last trick"
            winning_pos = self.decide_winner(
                [next(iter(state[0])), next(iter(state[1])), next(iter(state[2])), next(iter(state[3]))])
            if winning_pos % 2 == 0:
                NS += 1
                return NS, 1, 0
            else:
                return NS, 0, 1
        else:  # When it is not the last trick
            # get current player, TODO: maybe add to parameters
            cur_player = self.card_holder_dict[next(iter(state[0]))]
            # When leading the trick, the player can play any card
            if m % 4 == 0:
                # memoization process
                # use stored values if possible
                # TODO: update this memoization process, with beta being changed
                if m <= LINK_LEVEL * 4 + 4:
                    # create link
                    links = SuitLevelLinks(self.suit_level_links, self.trump, cur_player)
                    # if len(links) != m:
                    #     pass
                    assert len(links) == m, str(m) + str(links) + str(len(links))
                    # if the link has been stored before
                    if links in self.link_lookup_table:
                        # get stored value
                        stored_f_NS, stored_f_EW = self.link_lookup_table[links]
                        # if the stored value is complete, return it
                        if stored_f_EW + stored_f_NS == m // 4:
                            assert NS + stored_f_NS == EW - stored_f_EW, "NS EW should be the same if" \
                                                                           " remaining is determined" + str(
                                stored_f_NS) + str(stored_f_EW)
                            # print("max, read from lookup table, completely searched", state, stored_f_NS, stored_f_EW)
                            return NS + stored_f_NS, stored_f_NS, stored_f_EW
                        # if the stored value is not complete, update alpha beta, return if alpha + beta >= 13
                        f_NS = stored_f_NS
                        f_EW = stored_f_EW
                        if f_NS + NS > alpha:
                            alpha = f_NS + NS
                        if f_EW + EW > beta:
                            beta = f_EW + EW
                        if alpha + beta >= 13:
                            # print("max, read from lookup table, partially searched", state, stored_f_NS, stored_f_EW)
                            return alpha, f_NS, f_EW
                        f_NS2 = f_NS
                        f_EW2 = f_EW
                playable_cards = state[0].copy()
            # When not leading the trick, decide the possible playing cards
            else:
                first_card = self.play[(trick_number * 4)]
                playable_cards = set(filter(lambda element: element // 13 == first_card // 13, state[0]))
                if not playable_cards:
                    playable_cards = state[0].copy()
                # print(first_card, playable_cards, state[0])
            # print(m, state[0], playable_cards, remaining_cards[math.ceil(m/4) - 1])
            # Iterate through all playable cards
            for current_card in playable_cards:
                # Play the smallest card in a series of consecutive cards.
                # E.g. If AKQT9 are in the hand, play QT9 and skip over AK.
                # If J is played before, play only T9 and skip over AKQ
                # TODO: refine this
                smallest_in_consecutive = True
                # print(current_card, current_card // 13)
                temp_link = self.suit_level_links[current_card // 13]
                for i in range(current_card % 13 - 1, -1, -1):
                    if temp_link[i] != -1:
                        if temp_link[i] == cur_player:
                            smallest_in_consecutive = False
                        break
                if smallest_in_consecutive:
                    # play the card
                    self.play[52 - m] = current_card
                    state[0].remove(current_card)                    # remove from state
                    # print("max-in", state, current_card)
                    # assert suit_level_links[current_card//13][current_card % 13] == cur_player

                    # if not the end of a trick, recurse
                    if m % 4 != 1:   # not end of trick
                        s = state[1:] + state[:1]
                        alpha_new, f_EW_new, f_NS_new = self.MAX_VALUE(s, beta, alpha, EW, NS, play_number + 1)
                        alpha = max(alpha, alpha_new)
                        # f_NS and f_EW both change in favour of the current player
                        f_NS = max(f_NS, f_NS_new)
                        f_EW = min(f_EW, f_EW_new)
                        # print("max-out", state, current_card)
                    # if end of a trick, determine trick winner and recurse
                    else:
                        winner = self.decide_winner(self.play[trick_number * 4:trick_number * 4 + 4])
                        # If the winner is on the current team
                        if winner % 2 == 1:
                            NS += 1
                            if NS > alpha:
                                alpha = NS
                                if alpha + beta >= 13:
                                    state[0].add(current_card)
                                    return alpha, max(f_NS, 1), f_EW
                            if winner == 3:
                                s = state[:]
                            else:
                                s = state[2:] + state[:2]
                            for l in self.play[trick_number * 4:trick_number * 4 + 4]:
                                self.suit_level_links[l // 13][l % 13] = -1  # remove from suit_level_links
                            alpha_new, f_EW_new, f_NS_new = self.MAX_VALUE(s, beta, alpha, EW, NS, play_number + 1)
                            alpha = max(alpha, alpha_new)
                            f_NS = max(f_NS, f_NS_new + 1)
                            f_EW = min(f_EW, f_EW_new)
                            temp_player = (cur_player + 1) % 4
                            for l in self.play[trick_number * 4:trick_number * 4 + 4]:
                                self.suit_level_links[l // 13][l % 13] = temp_player  # return back to suit_level_links
                                temp_player = (temp_player + 1) % 4
                            # print("alpha = max(max), ", alpha, s, trump, alpha, beta, NS, EW)
                            # print("max-out", state, current_card)
                            NS -= 1
                        # when the winner is on the current team
                        else:
                            EW += 1
                            if EW > beta:
                                beta = EW
                                if alpha + beta >= 13:
                                    state[0].add(current_card)
                                    return alpha, f_NS, min(f_EW, 1)
                            s = state[winner + 1:] + state[:winner + 1]
                            # print("alpha is about to = max(min)", alpha, s, trump, alpha, beta, NS, EW)
                            for l in self.play[trick_number * 4:trick_number * 4 + 4]:
                                self.suit_level_links[l // 13][l % 13] = -1  # remove from suit_level_links
                            alpha_new, f_EW_new, f_NS_new = self.MAX_VALUE(s, beta, alpha, EW, NS, play_number + 1)
                            alpha = max(alpha, alpha_new)
                            f_NS = max(f_NS, f_NS_new + 1)
                            f_EW = min(f_EW, f_EW_new)
                            temp_player = (cur_player + 1) % 4
                            for l in self.play[trick_number * 4:trick_number * 4 + 4]:
                                self.suit_level_links[l // 13][l % 13] = temp_player  # return back to suit_level_links
                                temp_player = (temp_player + 1) % 4
                            # print("alpha = max(min), ", alpha, s, trump, alpha, beta, NS, EW)
                            # print("max-out", state, current_card)
                            EW -= 1
                    if trick_number * 4 <= TEST_L:
                        finish = time.time()
                        print(finish - start)
                        pickle_dump_link_lookup_table()
                        quit()
                    state[0].add(current_card)                                      # give back to state
                    # if the other team had equal or better play, return
                    if alpha + beta >= 13:
                        # print(state, trump, alpha, beta, NS, EW, "=", beta, "2")
                        # memoization
                        if m % 4 == 0 and m <= LINK_LEVEL * 4 + 4:
                            if f_NS > f_NS2 or f_EW > f_EW2:
                                update_link_lookup_table(links, f_NS, f_EW)
                        return alpha, f_NS, f_EW
        # memoization
        if m % 4 == 0 and m <= LINK_LEVEL * 4 + 4:
            if f_NS > f_NS2 or f_EW > f_EW2:
                update_link_lookup_table(links, f_NS, f_EW)
        return alpha, f_NS, f_EW


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

    # Case 1: Trump = NT
    # print(type(Windex), type(Sindex), type(Eindex), type(Nindex))
    current_state = [Nindex, Eindex, Sindex, Windex]
    solveNT = DoubleDummySolver(suit_level_links, link_lookup_table, 5, current_state)
    start = time.time()
    a, b, c = solveNT.MAX_VALUE(current_state)
    end = time.time()
    print(a, "NT")
    print(end-start)
    # Case 2：Trump = C
    solveC = DoubleDummySolver(suit_level_links, link_lookup_table, 1, current_state)
    start = time.time()
    a, b, c = solveC.MAX_VALUE(current_state)
    end = time.time()
    print(a, "C")
    print(end - start)
    # Case 3: Trump = D
    solveD = DoubleDummySolver(suit_level_links, link_lookup_table, 2, current_state)
    start = time.time()
    a, b, c = solveD.MAX_VALUE(current_state)
    end = time.time()
    print(a, "D")
    print(end - start)
    # Case 4: Trump = H
    solveH = DoubleDummySolver(suit_level_links, link_lookup_table, 3, current_state)
    start = time.time()
    a, b, c = solveH.MAX_VALUE(current_state)
    end = time.time()
    print(a, "H")
    print(end - start)
    # Case 5: Trump = S
    solveS = DoubleDummySolver(suit_level_links, link_lookup_table, 4, current_state)
    start = time.time()
    a, b, c = solveS.MAX_VALUE(current_state)
    end = time.time()
    print(a, "S")
    print(end - start)
    print()
    pickle_dump_link_lookup_table()


if __name__ == '__main__':
    main()
    # import cProfile
    # cProfile.run('main()',filename="profile.out")
    import pstats
    p = pstats.Stats("profile1.out")
    p.sort_stats("time").print_stats()
    p.print_callers("__hash__")


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
