import numpy as np
import time
from itertools import permutations
import os
from collections import Counter
import pickle
import math
TEST_L = 16 # -1 for complete run
LINK_LEVEL = 11
from DoubleDummy import SuitLevelLinks, update_link_lookup_table, pickle_dump_link_lookup_table, start


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
        self.suit_level_links = suit_level_links
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
    def MAX_VALUE(self, state, trump, alpha=0, beta=0, NS=0, EW=0, play_number=0):  # trump: C = 1, D = 2, H = 3, S = 4, NT = 5
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
        # print(state, trump, alpha, beta, NS, EW, "max")
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
                    links = SuitLevelLinks(self.suit_level_links, trump, cur_player)
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
                        alpha_new, f_EW_new, f_NS_new = self.MAX_VALUE(s, trump, beta, alpha, EW, NS, play_number + 1)
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
                            alpha_new, f_EW_new, f_NS_new = self.MAX_VALUE(s, trump, beta, alpha, EW, NS, play_number + 1)
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
                            alpha_new, f_EW_new, f_NS_new = self.MAX_VALUE(s, trump, beta, alpha, EW, NS, play_number + 1)
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
