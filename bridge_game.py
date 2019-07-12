import numpy as np
Suit = ['S', 'H', 'D', 'C']
Rank = ['2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14']
Position = ['N','W','S','E']
"""
Hands: set of cards
Cards: (suit, rank)
Bids: (level, trump) or (-1,) for X, (-2,) for XX, (0,) for PASS
Contract: (Bid, doubling)
doubling: -1 for X, -2 for XX, 0 for PASS
suit,trump: C:1, D:2, H:3, S:4, NT:5
rank: 2-9: 0-7, T:8, J:9, Q:10, K:11, A:12
"""
BID_PASS = (0,)
CONTRACT_PASS = ((0,),0)
BID_DOUBLE = (-1,)
BID_REDOUBLE = (-2,)


class BridgeGame:
    """
    Class that simulates a game of bridge
    """
    def __init__(self):
        self.bid_history = []
        self.play_history = []
        self.stage = "Bidding"               # or "Playing"
        self.contract = (-3,)
        self.current_round = []
        self.current_leader = -1
        self.vulnerability = -1
        self.hands = []                      # order: NWSE
        self.largest_bid = BID_PASS
        self.last_bidder = -1                # 0-3 for NWSE
        self.NSTricks = 0

    def create_random_board(self):
        self.hands = BridgeGame.create_random_board()

    def get_stage(self):
        return self.stage

    @staticmethod
    def create_random_board():
        pass

    @staticmethod
    def calculate_score(contract, vulnerability, result):  # TODO: implement this
        if contract[0][0] == 0:
            return 0
        elif result >= 0:
            pass
        else:
            pass
        return 0

    @staticmethod
    def create_random_board():  # TODO: implement this
        return 0

    @staticmethod
    def is_greater_bid(bid0, bid1):
        if bid0[0] == bid1[0]:
            return bid0[0] > bid1[0]
        return bid0[1] > bid1[1]

    @staticmethod
    def validate_bid(bid_history, new_bid, largest_bid, team_bid):
        """
        Check if a new bid is valid
        :param bid_history: history of bids
        :param new_bid: the new bid to be checked
        :param largest_bid: largest normal bid so far
        :param team_bid: if the largest normal bid is bid by a teammate
        :return: if the new bid is valid
        """
        if new_bid == BID_PASS:  # passing bid
            return True
        if not bid_history:
            return True if new_bid[0] > 0 else False
        if new_bid == BID_REDOUBLE:  # redouble
            if team_bid != 1:
                return False
            return bid_history[-1] == BID_DOUBLE or (bid_history[-1] == BID_PASS == bid_history[-2] == BID_PASS
                                                     and bid_history[-3] == BID_DOUBLE)
        if new_bid == BID_DOUBLE:  # double
            if team_bid != 0:
                return False
            return bid_history[-1][0] > 0 or (bid_history[-1] == BID_PASS == bid_history[-2] == BID_PASS
                                              and bid_history[-3][0] > 0)
        return BridgeGame.is_greater_bid(new_bid, largest_bid)  # normal bid

    @staticmethod
    def is_done_bidding(bid_history):
        if len(bid_history) < 3:
            return False
        return bid_history[-1] == bid_history[-2] == bid_history[-3] == BID_PASS

    @staticmethod
    def is_done_playing(play_history):
        return len(play_history) == 52

    @staticmethod
    def get_contract(bid_history):
        assert len(bid_history >= 3), "Need at least 3 bids"
        assert bid_history[-1] == bid_history[-2] == bid_history[-3] == BID_PASS, "Need 3 PASS at the end of bidding"

        if len(bid_history) == 3:
            return CONTRACT_PASS

        if bid_history[-4][0] > 0:
            return bid_history[-4], 0
        else:
            for bid in reversed(bid_history):
                if bid[0] > 0:
                    return bid, bid_history[-4][0]
        assert False, "Need at least one normal bid."

    # def get_result():
    #
    #     return 0

    @staticmethod
    def card_value_key(card, trump, lead_suit):
        """
        used to compare cards
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