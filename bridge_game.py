import numpy as np
Suit = ['C', 'D', 'H', 'S']
Rank = ['2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14']
Position = ['N', 'W', 'S', 'E']
"""
Hands: set of cards
Cards: (suit, rank)
Bids: (level, trump) or (-1,) for X, (-2,) for XX, (0,) for PASS
Contract: (Bid, doubling)
doubling: -1 for X, -2 for XX, 0 for PASS
suit,trump: C:1, D:2, H:3, S:4, NT:5
rank: 2-9: 0-7, T:8, J:9, Q:10, K:11, A:12
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
CONTRACT_PASS = ((0,), 0)
BID_DOUBLE = (-1,)
BID_REDOUBLE = (-2,)
BID_INVALID = (-3,)
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
        self.bid_history = []
        self.play_history = []
        self.stage = STAGE_BIDDING               # or STAGE_PLAYING
        self.contract = CONTRACT_INVALID
        self.contractor = POS_N
        self.current_round = []
        self.current_leader = -1
        self.vulnerability = VUL_NONE
        self.hands = []                      # order: NWSE
        self.last_normal_bid = BID_PASS
        self.last_normal_bidder = -1                # index of last normal bid
        self.last_penalty = PENALTY_PASS
        self.NSTricks = 0

    def create_random_board(self):
        self.hands = BridgeGame.create_random_board()

    def get_stage(self):
        return self.stage

    def bid(self, new_bid):
        assert self.stage == STAGE_BIDDING, "should not have finished bidding"
        if not self.is_valid_bid(new_bid):
            return BID_INVALID
        if new_bid == BID_DOUBLE or new_bid == BID_REDOUBLE:
            self.last_penalty = new_bid
        if new_bid != BID_PASS:
            self.last_normal_bid = new_bid
            self.last_normal_bidder = len(self.bid_history)
        self.bid_history.append(new_bid)
        if self.is_done_bidding():
            self.stage = STAGE_PLAYING
            self.contract = self.last_normal_bid, self.last_penalty
            if self.contract != CONTRACT_PASS:
                self.contractor = self.calc_contractor()

    @staticmethod
    def calculate_score(contract, vulnerability, result):  # TODO: implement this
        if contract[0][0] == 0:
            return 0
        elif result >= 0:
            pass
        else:
            pass
        return 0

    def calc_contractor(self):
        assert self.last_normal_bid != BID_PASS, "should be pass contract"
        target_trump = self.last_normal_bid[1]
        for ind, bid in enumerate(self.play_history[self.last_normal_bidder%2::2]):
            if bid[0] > 0 and bid[1] == target_trump:
                return ind % 2 * 2 + self.last_normal_bidder % 2


    @staticmethod
    def create_random_board():  # TODO: implement this
        return 0

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
            return self.last_penalty == PENALTY_DOUBLE and (len(self.bid_history) - self.last_normal_bidder) % 2 == 0
            # if (len(self.bid_history) - self.last_normal_bidder) % 2 != 0:
            #     return False
            # return self.bid_history[-1] == BID_DOUBLE or (len(self.bid_history) >= 4
            #                                   and self.bid_history[-1] == BID_PASS == self.bid_history[-2] == BID_PASS
            #                                          and self.bid_history[-3] == BID_DOUBLE)
        if new_bid == BID_DOUBLE:  # double
            return self.last_penalty == PENALTY_PASS and (len(self.bid_history) - self.last_normal_bidder) % 2 == 1
            # if (len(self.bid_history) - self.last_normal_bidder) % 2 != 1:
            #     return False
            # return self.bid_history[-1][0] > 0 or
            #                                    (self.bid_history[-1] == BID_PASS == self.bid_history[-2] == BID_PASS
            #                                   and self.bid_history[-3][0] > 0)
        return BridgeGame.is_greater_bid(new_bid, self.last_normal_bid)  # normal bid

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
        return self.contract

    # def get_result():
    #
    #     return 0

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
