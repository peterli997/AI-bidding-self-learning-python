import numpy as np
# Suit = ['C', 'D', 'H', 'S']
# Rank = ['2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14']
# Position = ['N', 'W', 'S', 'E']
"""
Hands: set of cards
Cards: (suit, rank)
Bids: (level, trump) or (-1,) for X, (-2,) for XX, (0,) for PASS
Contract: (Bid, doubling)
Penalty: 0:Pass, -1:X, -2:XX
Suit,Trump: C:1, D:2, H:3, S:4, NT:5
Rank: 2-9: 0-7, T:8, J:9, Q:10, K:11, A:12
Positions: N:0, W:1, S:2, E:3
"""
BID_1C = (1, 1)
BID_2C = (2, 1)
BID_1D = (1, 2)
BID_1H = (1, 3)
BID_2NT = (2, 5)
BID_3D = (3, 2)
BID_4D = (4, 2)
BID_7NT = (7, 5)
BID_PASS = (0,)
BID_DOUBLE = (-1,)
BID_REDOUBLE = (-2,)
BID_INVALID = (-3,)
CONTRACT_PASS = ((0,), 0)
CONTRACT_INVALID = (BID_INVALID, -3)
PENALTY_DOUBLE = -1
PENALTY_REDOUBLE = -2
PENALTY_PASS = 0
STAGE_BIDDING = 0
STAGE_PLAYING = 1
POS_N = 0
POS_W = 1
POS_S = 2
POS_E = 3
VUL_NONE = 0
VUL_EW = 1
VUL_NS = 2
VUL_ALL = 3

class BridgeGame:
    """
    Class that simulates a game of bridge
    """
    def __init__(self):
        # initial board
        self.vulnerability = VUL_NONE
        self.hands = []                   #          # order: NWSE
        # Round stage
        self.stage = STAGE_BIDDING                   # or STAGE_PLAYING
        # Bidding
        self.bid_history = []
        self._last_normal_bid = BID_PASS  #
        self._last_normal_bidder = -1     #          # index of last normal bid
        self._last_penalty = PENALTY_PASS #
        # Playing
        self._contract = CONTRACT_INVALID #
        self.contractor = POS_N           #
        self.play_history = []
        self._current_trick = []          #
        self._current_player = -1         #
        self._NSTricks = 0                #

    def create_random_board(self):
        self.hands = BridgeGame.create_random_board()

    def get_stage(self):
        return self.stage

    def bid(self, new_bid):
        assert self.stage == STAGE_BIDDING, "should not have finished bidding"
        if not self.is_valid_bid(new_bid):
            return BID_INVALID
        if new_bid == BID_DOUBLE or new_bid == BID_REDOUBLE:
            self._last_penalty = new_bid
        if new_bid != BID_PASS:
            self._last_normal_bid = new_bid
            self._last_normal_bidder = len(self.bid_history)
        self.bid_history.append(new_bid)
        if self.is_done_bidding():
            self.stage = STAGE_PLAYING
            self._contract = self._last_normal_bid, self._last_penalty
            if self._contract != CONTRACT_PASS:
                self.contractor = self.calc_contractor()

    def get_score(self, result):
        return self.calculate_score(self._contract, self.contractor, self)
    @staticmethod
    def calculate_score(contract, contractor, doubling, vulnerability, result):
        vul = ((contractor == POS_N or contractor == POS_S) and (vulnerability == VUL_NS or vulnerability == VUL_ALL)) or ((contractor == POS_E and contractor == POS_W) and (vulnerability == VUL_EW or vulnerability == VUL_ALL))
        if contract[0][0] + 6 > result:
            if not vul:
                if doubling == BID_REDOUBLE:
                    if contract[0][0] - result <= -4:
                        return 200 - 400 * (contract[0][0] + 6 - result)
                    else:
                        return 800 - 600 * (contract[0][0] + 6 - result)
                elif doubling == BID_DOUBLE:
                    if contract[0][0] - result <= 8:
                        return 100 - 200 * (contract[0][0] + 6 - result)
                    else:
                        return 400 - 300 * (contract[0][0] + 6 - result)
                else:
                    return -50 * (contract[0][0] + 6 - result)
            else:
                if doubling == BID_REDOUBLE:
                    return 200 - 600 * (contract[0][0] + 6 - result)
                elif doubling == BID_DOUBLE:
                    return 100 - 300 * (contract[0][0] + 6 - result)
                else:
                    return -100 * (contract[0][0] + 6 - result)
        else:
            score = 0
            if contract[1] == 1 or contract[1] == 2:
                contract_score = contract[0][0] * 20
            elif contract[1] == 3 or contract[1] == 4:
                contract_score = contract[0][0] * 30
            else:
                contract_score = 10 + contract[0][0] * 30
            if doubling == BID_REDOUBLE:
                contract_score *= 4
                score += 100
                if vul:
                    score += 400 * (result - contract[0][0] - 6)
                else:
                    score += 200 * (result - contract[0][0] - 6)
            elif doubling == BID_DOUBLE:
                contract_score *= 2
                score += 50
                if vul:
                    score += 200 * (result - contract[0][0] - 6)
                else:
                    score += 100 * (result - contract[0][0] - 6)
            else:
                if contract[1] == 1 or contract[1] == 2:
                    score += 20 * (result - contract[0][0] - 6)
                else:
                    score += 30 * (result - contract[0][0] - 6)
            score += contract_score
            if contract_score < 100:
                score += 50
            else:
                if vul:
                    score += 500
                else:
                    score += 300
            if contract[0][0] == 6:
                if vul:
                    score += 750
                else:
                    score += 500
            if contract[0][0] == 7:
                if vul:
                    score += 1500
                else:
                    score += 1000
        return score

    def calc_contractor(self):
        assert self._last_normal_bid != BID_PASS, "should be pass contract"
        target_trump = self._last_normal_bid[1]
        for ind, bid in enumerate(self.play_history[self._last_normal_bidder % 2::2]):
            if bid[0] > 0 and bid[1] == target_trump:
                return ind % 2 * 2 + self._last_normal_bidder % 2


    @staticmethod
    def create_random_board():
        RC = list(range(52))
        Nindex = list(np.random.choice(a=RC, size=13, replace=False))
        RC = list(set(RC) - set(Nindex))
        Sindex = list(np.random.choice(a=RC, size=13, replace=False))
        RC = list(set(RC) - set(Sindex))
        Windex = list(np.random.choice(a=RC, size=13, replace=False))
        Eindex = list(set(RC) - set(Windex))
        return Sindex, Windex, Nindex, Eindex

    @staticmethod
    def is_greater_bid(bid0, bid1):
        assert bid0 != BID_DOUBLE and bid0 != BID_REDOUBLE, "Can not compare doubles or redoubles"
        assert bid1 != BID_DOUBLE and bid1 != BID_REDOUBLE, "Can not compare doubles or redoubles."

        if bid0[0] == bid1[0]:
            return bid0[1] > bid1[1]
        return bid0[0] > bid1[0]

    def is_valid_bid(self, new_bid):
        """
        Check if a new bid is valid
        :param new_bid: the new bid to be checked
        :return: if the new bid is valid
        """
        if self.is_done_bidding():
            return False
        if new_bid == BID_PASS:  # passing bid
            return True
        if not self.bid_history:
            return True if new_bid[0] > 0 else False  # allow first normal bid
        if new_bid == BID_REDOUBLE:  # redouble
            return self._last_penalty == PENALTY_DOUBLE and (len(self.bid_history) - self._last_normal_bidder) % 2 == 0
            # if (len(self.bid_history) - self.last_normal_bidder) % 2 != 0:
            #     return False
            # return self.bid_history[-1] == BID_DOUBLE or (len(self.bid_history) >= 4
            #                                   and self.bid_history[-1] == BID_PASS == self.bid_history[-2] == BID_PASS
            #                                          and self.bid_history[-3] == BID_DOUBLE)
        if new_bid == BID_DOUBLE:  # double
            return self._last_penalty == PENALTY_PASS and (len(self.bid_history) - self._last_normal_bidder) % 2 == 1
            # if (len(self.bid_history) - self.last_normal_bidder) % 2 != 1:
            #     return False
            # return self.bid_history[-1][0] > 0 or
            #                                    (self.bid_history[-1] == BID_PASS == self.bid_history[-2] == BID_PASS
            #                                   and self.bid_history[-3][0] > 0)
        return BridgeGame.is_greater_bid(new_bid, self._last_normal_bid)  # normal bid

    def is_done_bidding(self):
        if self.stage == STAGE_PLAYING:
            return True
        if len(self.bid_history) < 3:
            return False
        return self.bid_history[-1] == self.bid_history[-2] == self.bid_history[-3] == BID_PASS

    def is_done_playing(self):
        return len(self.play_history) == 52

    def get_contract(self):
        assert self.is_done_bidding(), "Need to be done bidding"
        return self._contract

    def get_result(self):
        return 0

    @staticmethod
    def card_value_key(card, trump, lead_suit):
        """
        key function used to compare cards while playing
        :param card: card to be compared
        :param trump: trump of the trick
        :param lead_suit: leading suit of the trick
        :return: a number used to compare against other cards
        """
        value = card[1]
        if card[0] == trump:
            value += 26
        elif card[0] == lead_suit:
            value += 13
        return value

    @staticmethod
    def get_trick_winner(cards, trump, lead):
        """
        get the winner of the trick
        :param cards: list of 4 cards, first one being the lead
        :param trump: trump of the game
        :param lead: index of the lead for this trick
        :return: the index of the winner
        """
        assert len(cards) == 4, "need 4 cards per round"
        assert 0 <= lead <= 3, "lead can only be of position 0-3"
        highest_card = max(cards, key=lambda a: BridgeGame.card_value_key(a, trump, cards[lead][0]))
        return cards.index(highest_card)
