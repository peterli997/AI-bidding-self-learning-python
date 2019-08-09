
# Suit = ['C', 'D', 'H', 'S']
# Rank = ['2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14']
# Position = ['N', 'E', 'S', 'W']
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
# BIDS
BID_PASS = (0,)
BID_DOUBLE = (-1,)
BID_REDOUBLE = (-2,)
BID_INVALID = (-3,)
# CONTRACTS
CONTRACT_PASS = ((0,), 0)
CONTRACT_INVALID = (BID_INVALID, -3)
# RETURN VALUES
RETURN_REJECTED_STAGE_INCORRECT = -2
RETURN_REJECTED_INVALID_BID = -1
RETURN_REJECTED_INVALID_PLAY = -1
RETURN_ACCEPTED = 0
RETURN_ACCEPTED_BIDDING_FINISHED = 1
RETURN_ACCEPTED_ROUND_FINISHED = 2
# STAGES
STAGE_BIDDING = 0
STAGE_PLAYING = 1
STAGE_FINISHED = 2
# POSITIONS
POS_N = 0
POS_E = 1
POS_S = 2
POS_W = 3
POS_INVALID = -1
# VULNERABILITY
VUL_NONE = 0
VUL_EW = 1
VUL_NS = 2
VUL_ALL = 3
# PENALTIES
PENALTY_DOUBLE = -1
PENALTY_REDOUBLE = -2
PENALTY_PASS = 0
# SCORE
SCORE_INVALID = -1
# for testing 
TOTAL_TRICKS = 13

class BridgeGame:
    """
    Class that simulates a game of bridge
    """

    def __init__(self, hands, vulnerability, starting_pos):
        # meta data
        global TOTAL_TRICKS
        TOTAL_TRICKS = len(hands[0]) if len(hands[0]) != 0 else 13
        # initialize a round of bridge
        self.vulnerability = vulnerability
        self.hands = hands
        self.dealer = starting_pos
        self.current_player = self.dealer
        # Round stage, can be STAGE_BIDDING, STAGE_PLAYING, STAGE_FINISHED
        self.stage = STAGE_BIDDING
        # Bidding
        self.bid_history = []
        self.last_normal_bid = BID_PASS  #
        self.last_normal_bidder = -1  # index of last normal bid
        self.last_penalty = PENALTY_PASS  #
        # Playing
        self.contract = CONTRACT_INVALID  #
        self.declarer = POS_INVALID  #
        self.play_history = []
        self.declarer_tricks = 0  #
        # Result
        self.declarer_score = SCORE_INVALID

    def reset_round(self):
        self.hands = self.hands_bac
        self.stage = STAGE_BIDDING
        self.bid_history = []
        self.last_normal_bid = BID_PASS
        self.last_normal_bidder = -1
        self.last_penalty = PENALTY_PASS
        self.contract = CONTRACT_INVALID
        self.declarer = POS_INVALID
        self.play_history = []
        self.declarer_tricks = 0
        self.declarer_score = SCORE_INVALID

    @property
    def hands(self):
        return self._hands

    @hands.setter
    def hands(self, hands):
        global TOTAL_TRICKS
        self._hands = [[c for c in d] for d in hands]
        self.hands_bac = [[c for c in d] for d in hands]
        TOTAL_TRICKS = len(hands[0]) if len(hands[0]) != 0 else 13

    def create_random_board(self):
        self.hands = BridgeGame.random_board()

    def player_inc(self):
        self.current_player = (self.current_player + 1) % 4

    def bid(self, new_bid):
        """
        Place a new bid during bidding stage. Skips invalid bids.
        :param new_bid: the new bid to be bid
        :return: RETURN_REJECTED_STAGE_INCORRECT if not in the correct stage,
                 RETURN_REJECTED_INVALID_BID if bid is not valid
                 RETURN_ACCEPTED if bid is accepted
                 RETURN_ACCEPTED_BIDDING_FINISHED if bid is accepted and bidding stage is finished
                 RETURN_ACCEPTED_ROUND_FINISHED if bid is accepted and this round is finished,
                                      i.e. bidding stage finished with CONTRACT_PASS
        """
        # check if bid is valid
        if self.stage != STAGE_BIDDING:
            return RETURN_REJECTED_STAGE_INCORRECT
        if not self.is_valid_bid(new_bid):
            return RETURN_REJECTED_INVALID_BID
        # check bid type
        if new_bid == BID_DOUBLE or new_bid == BID_REDOUBLE:
            self.last_penalty = new_bid[0]
        elif new_bid != BID_PASS:
            self.last_normal_bid = new_bid
            self.last_normal_bidder = self.current_player
            self.last_penalty = PENALTY_PASS
        self.bid_history.append(new_bid)
        # if is done bidding, prepare for playing stage
        if self.is_done_bidding():
            self.stage = STAGE_PLAYING
            self.contract = self.last_normal_bid, self.last_penalty
            if self.contract != CONTRACT_PASS:
                self.declarer = self.calc_declarer()
                self.current_player = (self.declarer - 1) % 4
                return RETURN_ACCEPTED_BIDDING_FINISHED
            else:
                self.stage = STAGE_FINISHED
                self.declarer_score = 0
                return RETURN_ACCEPTED_ROUND_FINISHED
        self.player_inc()
        return RETURN_ACCEPTED

    def play(self, new_play):
        """
        Play a new card during playing stage. Skips invalid plays.
        :param new_play: the new card to be played
        :return: RETURN_REJECTED_STAGE_INCORRECT if play not in the correct stage
                 RETURN_REJECTED_INVALID_BID if play is not valid,
                 RETURN_ACCEPTED if bid is accepted
                 RETURN_ACCEPTED_ROUND_FINISHED if bid is accepted and playing stage is finished
        """
        # check if bid is valid
        if self.stage != STAGE_PLAYING:
            return RETURN_REJECTED_STAGE_INCORRECT
        if not self.is_valid_play(new_play):
            return RETURN_REJECTED_INVALID_BID
        # update everything related
        self.hands[self.current_player].remove(new_play)
        self.play_history.append(new_play)
        if len(self.play_history) % 4 == 0:
            self.current_player = self.last_trick_winner()
            if (self.current_player + self.declarer) % 2 == 0:
                self.declarer_tricks += 1
        else:
            self.player_inc()
        if len(self.play_history) == TOTAL_TRICKS*4:
            self.stage = STAGE_FINISHED
            self.declarer_score = self.calculate_score(self.contract, self.declarer,
                                                       self.vulnerability, self.declarer_tricks)
            return RETURN_ACCEPTED_ROUND_FINISHED
        return RETURN_ACCEPTED

    def get_score(self, position):
        if self.stage != STAGE_FINISHED:
            return RETURN_REJECTED_STAGE_INCORRECT
        if self.declarer_score == SCORE_INVALID:
            self.declarer_score = self.calculate_score(self.contract, self.declarer,
                                                       self.vulnerability, self.declarer_tricks)
        if (position - self.declarer) % 2 == 0:
            return self.declarer_score
        else:
            return -self.declarer_score

    @staticmethod
    def calculate_score(contract, declarer, vulnerability, result):
        """
        Helper method for calculating score
        :param contract: Contract
        :param declarer: Declarer
        :param vulnerability: Vulnerability
        :param result: how many tricks the declarer made
        :return: score for declarer
        """
        doubling = contract[1]
        contract_trump = contract[0][1]
        contract_level = contract[0][0]
        vul = ((declarer == POS_N or declarer == POS_S) and (vulnerability == VUL_NS or vulnerability == VUL_ALL)) or \
              ((declarer == POS_E or declarer == POS_W) and (vulnerability == VUL_EW or vulnerability == VUL_ALL))
        if contract_level + 6 > result:
            if not vul:
                if doubling == PENALTY_REDOUBLE:
                    if contract_level - result <= -4:
                        return 200 - 400 * (contract_level + 6 - result)
                    else:
                        return 800 - 600 * (contract_level + 6 - result)
                elif doubling == PENALTY_DOUBLE:
                    if contract_level - result <= 8:
                        return 100 - 200 * (contract_level + 6 - result)
                    else:
                        return 400 - 300 * (contract_level + 6 - result)
                else:
                    return -50 * (contract_level + 6 - result)
            else:
                if doubling == PENALTY_REDOUBLE:
                    return 200 - 600 * (contract_level + 6 - result)
                elif doubling == PENALTY_DOUBLE:
                    return 100 - 300 * (contract_level + 6 - result)
                else:
                    return -100 * (contract_level + 6 - result)
        else:
            score = 0
            if contract_trump == 1 or contract_trump == 2:
                contract_score = contract_level * 20
            elif contract_trump == 3 or contract_trump == 4:
                contract_score = contract_level * 30
            else:
                contract_score = 10 + contract_level * 30
            if doubling == PENALTY_REDOUBLE:
                contract_score *= 4
                score += 100
                if vul:
                    score += 400 * (result - contract_level - 6)
                else:
                    score += 200 * (result - contract_level - 6)
            elif doubling == PENALTY_DOUBLE:
                contract_score *= 2
                score += 50
                if vul:
                    score += 200 * (result - contract_level - 6)
                else:
                    score += 100 * (result - contract_level - 6)
            else:
                if contract_trump == 1 or contract_trump == 2:
                    score += 20 * (result - contract_level - 6)
                else:
                    score += 30 * (result - contract_level - 6)
            score += contract_score
            if contract_score < 100:
                score += 50
            else:
                if vul:
                    score += 500
                else:
                    score += 300
            if contract_level == 6:
                if vul:
                    score += 750
                else:
                    score += 500
            if contract_level == 7:
                if vul:
                    score += 1500
                else:
                    score += 1000
        return score

    def calc_declarer(self):
        assert self.last_normal_bid != BID_PASS, "should not be pass contract"
        target_trump = self.last_normal_bid[1]
        for ind, bid in enumerate(self.bid_history[(self.last_normal_bidder - self.dealer) % 2::2]):
            if bid[0] > 0 and bid[1] == target_trump:
                return ((self.last_normal_bidder - self.dealer) % 2 + ind * 2 + self.dealer) % 4

    @staticmethod
    def random_board():
        import numpy as np
        RC = set(range(TOTAL_TRICKS * 4))
        Nindex = set(np.random.choice(a=RC, size=TOTAL_TRICKS, replace=False))
        N = set()
        for i in Nindex:
            N.add((i // 13, i % 13))
        RC = RC - Nindex
        Sindex = set(np.random.choice(a=RC, size=TOTAL_TRICKS, replace=False))
        S = set()
        for i in Sindex:
            S.add((i // 13, i % 13))
        RC = RC - Sindex
        Windex = set(np.random.choice(a=RC, size=TOTAL_TRICKS, replace=False))
        W = set()
        for i in Windex:
            W.add((i // 13, i % 13))
        Eindex = RC - Windex
        E = set()
        for i in Eindex:
            E.add((i // 13, i % 13))
        return N, E, S, W

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
        if self.is_done_bidding():  # Bidding should not have finished
            return False
        if new_bid == BID_PASS:  # passing bid
            return True
        if not self.bid_history:
            return True if new_bid[0] > 0 else False  # allow first normal bid
        if new_bid == BID_REDOUBLE:  # redouble
            return self.last_normal_bidder != -1 and self.last_penalty == PENALTY_DOUBLE \
                   and (self.current_player - self.last_normal_bidder) % 2 == 0
        if new_bid == BID_DOUBLE:  # double
            return self.last_normal_bidder != -1 and self.last_penalty == PENALTY_PASS \
                   and (self.current_player - self.last_normal_bidder) % 2 == 1
        return BridgeGame.is_greater_bid(new_bid, self.last_normal_bid)  # normal bid

    def is_valid_play(self, new_play):
        """
        Check if a new bid is valid
        :param new_play: the new bid to be checked
        :return: if the new bid is valid
        """
        # the player should have the card
        if new_play not in self.hands[self.current_player]:
            return False
        # first card played in the round is valid
        if len(self.play_history) % 4 == 0:
            return True
        # card following the suit is valid
        leading_suit = self.play_history[len(self.play_history) // 4 * 4][0]
        if new_play[0] == leading_suit:
            return True
        # can play other suit if leading suit is void in this hand
        return len(set(filter(lambda x: x[0] == leading_suit, self.hands[self.current_player]))) == 0

    def is_done_bidding(self):
        if self.stage == STAGE_PLAYING:
            return True
        if len(self.bid_history) <= 3:
            return False
        return self.bid_history[-1] == self.bid_history[-2] == self.bid_history[-3] == BID_PASS

    def is_done_playing(self):
        return len(self.play_history) == TOTAL_TRICKS * 4

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
    def get_trick_winner(cards, trump):
        """
        get the winner of the trick
        :param cards: list of 4 cards, first one being the lead
        :param trump: trump of the game
        :return: the index of the winner in cards
        """
        assert len(cards) == 4, "need 4 cards per round"
        lead = cards[0]
        highest_card = max(cards, key=lambda a: BridgeGame.card_value_key(a, trump, lead[0]))
        return cards.index(highest_card)

    def last_trick_winner(self):
        """
        get the winner of the last four cards
        Note: this function does not check if the last four cards are cards from the same trick in the game.
        :return: the player that wins the last four cards
        """
        return (self.get_trick_winner(self.play_history[-4:], self.contract[0][1])
                + 1 + self.current_player) % 4

    def step(self, action):
        """
        Make a move, either a play or a bid
        :param action: play or bid to be used
        """
        if self.stage == STAGE_BIDDING:
            self.bid(action)
        elif self.stage == STAGE_PLAYING:
            self.play(action)
        elif self.stage == STAGE_FINISHED:
            raise Exception('This round is over.')