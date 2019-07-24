import numpy as np
import time
from itertools import permutations
import os
from collections import Counter
import pickle
import math
TEST_L = 16 # -1 for complete run
LINK_LEVEL = 11
from DoubleDummy import SuitLevelLinks
class DoubleDummySolver:
    play = ...
    card_holder_dict = ...
    suit_level_links = ...
    link_lookup_table = ...
    start = ...
    trump = ...
    def decide_winner(self, trick):
        winning_card = trick[0]
        winner = 0
        for i in range(4):
            if (trick[i] // 13 == winning_card // 13 and trick[i] > winning_card) or (
                    trick[i] // 13 == self.trump - 1 and winning_card // 13 != self.trump - 1):
                winning_card = trick[i]
                winner = i
        return winner

    def MAX_VALUE(self, state, trump, alpha=0, beta=13, NS=0, EW=13, pos_in_trick=0, trick_number=0):  # trump: C = 1, D = 2, H = 3, S = 4, NT = 5
        """
        Main method for the Min-Max algorithm.
        It is equipped with "partial" alpha-beta pruning and memoization.
        This algorithm computes the maximum number of tricks that NS can take under optimal strategies for all players.
        The round start with North.
        :param state: the state of the current board, tuple of four lists of hands.
        :param trump: the trump of the current round.
        :param alpha: alpha in alpha-beta pruning, the maximum lower bound of the true value.
        :param beta: beta in alpha-beta pruning, the minimum upper bound of the true value.
        :param NS: the current number of tricks that NS has taken.
        :param EW: the current number of tricks that EW has taken.
        :param pos_in_trick: the position of the current player in the current trick. (0-3)
        :param trick_number: the number of the current trick. (0-12)
        :return: (returned_)alpha, the maximum number of tricks the team of the first player can get,
                 f_NS, the maximum number of tricks remaining for the team of the first player,
                 f_EW, the maximum number of tricks remaining for the other team.
                 beta is not returned since it is not used.
                 It is guaranteed that f_NS, f_EW satisfy the following:
                 f_EW + f_NS = number of remaining tricks
                 or f_NS > number of total tricks - beta
                 or f_EW > number of total tricks - alpha
             f_NS^ \       |   EW + f_EW + alpha = n
                 | x \     |
                 |----\-----------  NS + f_NS + beta = n
                 |     \   |
                 |      \  |
                 |       \ |
                 |        \|
                 |         \
                 |         |\
                 |         |x\  f_NS + f_EW + NS + EW = m
                 +-------------------------> f_EW
        Can be anywhere in the upper left, lower right triangles (with x in them), or on the f_NS + f_EW = m line.
        Here, n is total number of tricks, m is remaining number of tricks.
        """
        # print(state, trump, alpha, beta, NS, EW, "max")
        # alpha is used for pruning, f_NS is used for memoization

        f_NS = NS
        f_NS2 = NS
        f_EW = 0
        f_EW2 = 0
        m = 52 - trick_number * 4 + pos_in_trick
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
            # get current player
            cur_player = self.card_holder_dict[next(iter(state[0]))]
            # When leading the trick, the player can play any card
            if m % 4 == 0:
                # memoization process
                # use stored values if possible
                if m <= LINK_LEVEL * 4 + 4:
                    # create link
                    links = SuitLevelLinks(self.suit_level_links, trump, cur_player)
                    # if len(links) != m:
                    #     pass
                    assert len(links) == m, str(m) + str(links) + str(len(links))
                    # if the link has been stored before
                    if links in self.link_lookup_table:
                        # get stored value
                        remaining_NS, remaining_EW = self.link_lookup_table[links]
                        # if the stored value is complete, return it
                        if remaining_EW + remaining_NS == m // 4:
                            assert NS + remaining_NS == EW - remaining_EW, "NS EW should be the same if" \
                                                                           " remaining is determined" + str(
                                remaining_NS) + str(remaining_EW)
                            # print("max, read from lookup table, completely searched", state, remaining_NS, remaining_EW)
                            return NS + remaining_NS, remaining_NS, remaining_EW
                        # if the stored value is not complete, update alpha beta, return if alpha >= beta
                        f_NS = remaining_NS + NS
                        f_NS2 = f_NS
                        if f_NS > alpha:
                            alpha = f_NS
                            if alpha >= beta:  # remaining_NS + NS = alpha
                                # print("max, read from lookup table, partially searched", state, remaining_NS, remaining_EW)
                                return alpha, f_NS, f_EW
                        # EW -= m // 4 - remaining_tricks
                        f_EW2 = EW - remaining_EW
                        if f_EW2 < beta:
                            beta = f_EW2
                            if beta <= alpha:  # EW - remaining_EW = beta
                                # print("max, read from lookup table, partially searched", state, remaining_NS, remaining_EW)
                                return alpha, f_NS, f_EW2
                playable_cards = state[0].copy()
            # When not leading the trick, first check if the player if
            else:
                first_card = play[(trick_number * 4)]
                playable_cards = set(filter(lambda element: element // 13 == first_card // 13, state[0]))
                if not playable_cards:
                    playable_cards = state[0].copy()
                # print(first_card, playable_cards, state[0])
            # print(m, state[0], playable_cards, remaining_cards[math.ceil(m/4) - 1])
            for k in playable_cards:
                bool_consecutive_card = True
                temp_link = self.suit_level_links[k // 13]
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
                    # assert suit_level_links[k//13][k % 13] == cur_player
                    if m % 4 != 1:   # not end of trick
                        s = state[1:] + state[:1]
                        alpha_new, f_alpha_new, f_beta_new = MIN_VALUE(s, trump, alpha, beta, NS, EW)
                        alpha = max(alpha, alpha_new)
                        f_NS = max(f_NS, f_alpha_new)
                        f_EW = max(f_EW, f_beta_new)
                        # print("max-out", state, k)
                    else:     # end of trick
                        if TRICK_LOOKUP_TABLE:
                            winner = int(trick_lookup_table[trump - 1][play[(trick_number * 4)]][play[
                                trick_number * 4 + 1]][play[trick_number * 4 + 2]][play[trick_number * 4 + 3]])
                        else:
                            winner = self.decide_winner(play[trick_number * 4:trick_number * 4 + 4], trump - 1)
                        if winner % 2:
                            NS += 1
                            if NS > f_NS:
                                f_NS = NS
                                if NS > alpha:
                                    alpha = NS
                                    if alpha >= beta:
                                        state[0].add(k)
                                        return alpha, f_NS, f_EW
                            if winner == 3:
                                s = state[:]
                            else:
                                s = state[2:] + state[:2]
                            for k in play[trick_number * 4:trick_number * 4 + 4]:
                                self.suit_level_links[k // 13][k % 13] = -1  # remove from suit_level_links
                            alpha_new, f_alpha_new, f_beta_new = MAX_VALUE(s, trump, alpha, beta, NS, EW)
                            alpha = max(alpha, alpha_new)
                            f_NS = max(f_NS, f_alpha_new)
                            f_EW = max(f_EW, f_beta_new)
                            temp_player = (cur_player + 1) % 4
                            for k in play[trick_number * 4:trick_number * 4 + 4]:
                                self.suit_level_links[k // 13][k % 13] = temp_player  # return back to suit_level_links
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
                                    return alpha, f_NS, f_EW
                            s = state[winner + 1:] + state[:winner + 1]
                            # print("alpha is about to = max(min)", alpha, s, trump, alpha, beta, NS, EW)
                            for k in play[trick_number * 4:trick_number * 4 + 4]:
                                self.suit_level_links[k // 13][k % 13] = -1  # remove from suit_level_links
                            alpha_new, f_alpha_new = MIN_VALUE(s, trump, alpha, beta, NS, EW)
                            alpha = max(alpha, alpha_new)
                            f_NS = max(f_NS, f_alpha_new)
                            temp_player = (cur_player + 1) % 4
                            for k in play[trick_number * 4:trick_number * 4 + 4]:
                                self.suit_level_links[k // 13][k % 13] = temp_player  # return back to suit_level_links
                                temp_player = (temp_player + 1) % 4
                            # print("alpha = max(min), ", alpha, s, trump, alpha, beta, NS, EW)
                            # print("max-out", state, k)
                            EW += 1
                    if trick_number * 4 <= TEST_L:
                        finish = time.time()
                        print(finish - start)
                        pickle_dump_link_lookup_table()
                        quit()
                    state[0].add(k)                                      # give back to state
                    if alpha >= beta:
                        # print(state, trump, alpha, beta, NS, EW, "=", beta, "2")
                        if m % 4 == 0 and m <= LINK_LEVEL * 4 + 4:
                            if f_NS > f_NS2 or beta < beta2:
                                update_link_lookup_table(links, f_NS - NS if f_NS > f_NS2 else 0
                                                         , EW - beta if beta < beta2 else 0)
                        return alpha, f_NS, f_EW
        if m % 4 == 0 and m <= LINK_LEVEL * 4 + 4:
            if f_NS > f_NS2 or beta < beta2:
                update_link_lookup_table(links, f_NS - NS if f_NS > f_NS2 else 0
                                         , EW - beta if beta < beta2 else 0)
        return alpha, f_NS, f_EW