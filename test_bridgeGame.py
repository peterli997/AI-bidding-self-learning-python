from unittest import TestCase
from bridge_game import *
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

class TestBridgeGame(TestCase):
    def test_create_random_board(self):
        pass

    def test_calculate_score(self):
        self.fail()

    def test_is_greater_bid(self):
        # 1C, 2C
        self.assertTrue(BridgeGame.is_greater_bid(BID_2C, BID_1C))
        self.assertFalse(BridgeGame.is_greater_bid(BID_1C, BID_2C))
        self.assertFalse(BridgeGame.is_greater_bid(BID_1C, BID_1C))

        # 1D, 2C
        self.assertTrue(BridgeGame.is_greater_bid(BID_2C, BID_1D))

        # 1D, 1H
        self.assertTrue(BridgeGame.is_greater_bid(BID_1H, BID_1D))

        # 2NT, 1C
        self.assertTrue(BridgeGame.is_greater_bid(BID_2NT, BID_1C))

        # Do not fail
        # self.fail()

    def test_bid_sequence(self, bids, returns):
        for pos in range(4):
            working_list = []
            test_game = BridgeGame([], VUL_NONE, pos)
            for idx, bid in enumerate(bids):
                result = test_game.bid(bid)
                self.assertEqual(returns[idx], result,
                                 "prev bids: " + str(working_list) +
                                 " curr_bid: " + str(bid))
                working_list.append(bid)

    def test_validate_bid(self):
        # 1C P 1D P 2C P 3D P 4D P P P P
        bid_list = [BID_1C, BID_1D, BID_PASS, BID_2C, BID_PASS, BID_PASS, BID_3D, BID_4D,
                    BID_PASS, BID_PASS, BID_PASS, BID_PASS]
        return_list = [RETURN_ACCEPTED] * 10 + [RETURN_ACCEPTED_BIDDING_FINISHED, RETURN_REJECTED_STAGE_INCORRECT]
        self.test_bid_sequence(bid_list, return_list)

        # 7NT 1C
        bid_list = [BID_7NT, BID_1C]
        return_list = [RETURN_ACCEPTED, RETURN_REJECTED_INVALID_BID]
        self.test_bid_sequence(bid_list, return_list)

        # P P P P
        bid_list = [BID_PASS, BID_PASS, BID_PASS, BID_PASS]
        return_list = [RETURN_ACCEPTED] * 3 + [RETURN_ACCEPTED_ROUND_FINISHED]
        self.test_bid_sequence(bid_list, return_list)

        # P P P 7NT
        bid_list = [BID_PASS, BID_PASS, BID_PASS, BID_7NT]
        return_list = [RETURN_ACCEPTED] * 4
        self.test_bid_sequence(bid_list, return_list)

        # P X
        bid_list = [BID_PASS, BID_DOUBLE]
        return_list = [RETURN_ACCEPTED] + [RETURN_REJECTED_INVALID_BID]
        self.test_bid_sequence(bid_list, return_list)

        # P XX
        bid_list = [BID_PASS, BID_REDOUBLE]
        return_list = [RETURN_ACCEPTED] + [RETURN_REJECTED_INVALID_BID]
        self.test_bid_sequence(bid_list, return_list)

        # X
        bid_list = [BID_DOUBLE]
        return_list = [RETURN_REJECTED_INVALID_BID]
        self.test_bid_sequence(bid_list, return_list)

        # XX
        bid_list = [BID_REDOUBLE]
        return_list = [RETURN_REJECTED_INVALID_BID]
        self.test_bid_sequence(bid_list, return_list)

        # P 7NT XX
        bid_list = [BID_PASS, BID_7NT, BID_REDOUBLE]
        return_list = [RETURN_ACCEPTED] * 2 + [RETURN_REJECTED_INVALID_BID]
        self.test_bid_sequence(bid_list, return_list)

        # P 7NT P X
        bid_list = [BID_PASS, BID_7NT, BID_PASS, BID_DOUBLE]
        return_list = [RETURN_ACCEPTED] * 3 + [RETURN_REJECTED_INVALID_BID]
        self.test_bid_sequence(bid_list, return_list)

        # P 7NT P P XX
        bid_list = [BID_PASS, BID_7NT, BID_PASS, BID_PASS, BID_REDOUBLE]
        return_list = [RETURN_ACCEPTED] * 4 + [RETURN_REJECTED_INVALID_BID]
        self.test_bid_sequence(bid_list, return_list)

        # P P 7NT X XX XX
        bid_list = [BID_PASS, BID_PASS, BID_7NT, BID_DOUBLE, BID_REDOUBLE, BID_REDOUBLE]
        return_list = [RETURN_ACCEPTED] * 5 + [RETURN_REJECTED_INVALID_BID]
        self.test_bid_sequence(bid_list, return_list)

        # P 1C X P P XX P P 2C P P X P XX
        bid_list = [BID_PASS, BID_1C, BID_DOUBLE, BID_PASS, BID_PASS, BID_REDOUBLE, BID_PASS, BID_PASS,
                    BID_2C, BID_PASS, BID_PASS, BID_DOUBLE, BID_PASS, BID_REDOUBLE]
        return_list = [RETURN_ACCEPTED] * 13 + [RETURN_REJECTED_INVALID_BID]
        self.test_bid_sequence(bid_list, return_list)

        # Don't fail
        # self.fail()

    def test_is_done_playing(self):
        self.fail()

    def test_get_contract(self):
        # 1C P 1D P 2C P 3D P 4D P P P P
        bid_list = [BID_1C, BID_1D, BID_PASS, BID_2C, BID_PASS, BID_PASS, BID_3D, BID_4D,
                    BID_PASS, BID_PASS, BID_PASS, BID_PASS]


        # 7NT 1C
        bid_list = [BID_7NT, BID_1C]
        self.test_bid_sequence(bid_list)

        # P P P P
        bid_list = [BID_PASS, BID_PASS, BID_PASS, BID_PASS]
        self.test_bid_sequence(bid_list)

        # P P P 7NT
        bid_list = [BID_PASS, BID_PASS, BID_PASS, BID_7NT]
        self.test_bid_sequence(bid_list)

        # P X
        bid_list = [BID_PASS, BID_DOUBLE]
        self.test_bid_sequence(bid_list)

        # P XX
        bid_list = [BID_PASS, BID_REDOUBLE]
        self.test_bid_sequence(bid_list)

        # X
        bid_list = [BID_DOUBLE]
        self.test_bid_sequence(bid_list)

        # XX
        bid_list = [BID_REDOUBLE]
        self.test_bid_sequence(bid_list)

        # P 7NT XX
        bid_list = [BID_PASS, BID_7NT, BID_REDOUBLE]
        self.test_bid_sequence(bid_list)

        # P 7NT P X
        bid_list = [BID_PASS, BID_7NT, BID_PASS, BID_DOUBLE]
        self.test_bid_sequence(bid_list)

        # P 7NT P P XX
        bid_list = [BID_PASS, BID_7NT, BID_PASS, BID_PASS, BID_REDOUBLE]
        self.test_bid_sequence(bid_list)

        # P P 7NT X XX XX
        bid_list = [BID_PASS, BID_PASS, BID_7NT, BID_DOUBLE, BID_REDOUBLE, BID_REDOUBLE]
        self.test_bid_sequence(bid_list)

        # P 1C X P P XX P P 2C P P X P XX
        bid_list = [BID_PASS, BID_1C, BID_DOUBLE, BID_PASS, BID_PASS, BID_REDOUBLE, BID_PASS, BID_PASS,
                    BID_2C, BID_PASS, BID_PASS, BID_DOUBLE, BID_PASS, BID_REDOUBLE]
        self.test_bid_sequence(bid_list)

        # Don't fail
        # self.fail()

    def test_card_value_key(self):
        self.fail()

    def test_get_trick_winner(self):
        self.fail()
