from unittest import TestCase
from bridge_game import *


class TestBridgeGame(TestCase):

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

    def test_bid_sequence(self, bids, returns, contract, declarer):
        for dealer in range(4):
            working_list = []
            test_game = BridgeGame([], VUL_NONE, dealer)
            for idx, bid in enumerate(bids):
                result = test_game.bid(bid)
                self.assertEqual(returns[idx], result,
                                 "prev bids: " + str(working_list) +
                                 " curr_bid: " + str(bid))
                working_list.append(bid)
            self.assertEqual(contract, test_game.contract)
            if test_game.contract != CONTRACT_PASS:
                self.assertEqual((declarer + dealer) % 4, test_game.declarer,
                                 "wrong declarer, dealer:" + str(dealer))

    def test_bidding(self):
        # 1C P 1D P 2C P 3D P 4D P P P (P)
        bid_list = [BID_1C, BID_PASS, BID_1D, BID_PASS, BID_2C, BID_PASS, BID_3D, BID_PASS, BID_4D,
                    BID_PASS, BID_PASS, BID_PASS, BID_PASS]
        return_list = [RETURN_ACCEPTED] * 11 + [RETURN_ACCEPTED_BIDDING_FINISHED, RETURN_REJECTED_STAGE_INCORRECT]
        contract = CONTRACT_4D
        declarer = 2
        self.test_bid_sequence(bid_list, return_list, contract, declarer)

        # 7NT (1C) X P (X) (XX) P P
        bid_list = [BID_7NT, BID_1C, BID_DOUBLE, BID_PASS, BID_DOUBLE, BID_REDOUBLE, BID_PASS,
                    BID_PASS]
        return_list = [RETURN_ACCEPTED, RETURN_REJECTED_INVALID_BID] + \
                      [RETURN_ACCEPTED] * 2 + [RETURN_REJECTED_INVALID_BID] * 2 + [RETURN_ACCEPTED] + \
                      [RETURN_ACCEPTED_BIDDING_FINISHED]
        contract = CONTRACT_7NTX
        declarer = 0
        self.test_bid_sequence(bid_list, return_list, contract, declarer)

        # P P P P
        bid_list = [BID_PASS, BID_PASS, BID_PASS, BID_PASS]
        return_list = [RETURN_ACCEPTED] * 3 + [RETURN_ACCEPTED_ROUND_FINISHED]
        contract = CONTRACT_PASS
        declarer = 0
        self.test_bid_sequence(bid_list, return_list, contract, declarer)

        # P P P 7NT X XX (XX) P P P
        bid_list = [BID_PASS, BID_PASS, BID_PASS, BID_7NT, BID_DOUBLE, BID_REDOUBLE, BID_REDOUBLE,
                    BID_PASS, BID_PASS, BID_PASS]
        return_list = [RETURN_ACCEPTED] * 6 + [RETURN_REJECTED_INVALID_BID] + \
                      [RETURN_ACCEPTED] * 2 + [RETURN_ACCEPTED_BIDDING_FINISHED]
        contract = CONTRACT_7NTXX
        declarer = 3
        self.test_bid_sequence(bid_list, return_list, contract, declarer)

        # (X) P (X) (XX) P P (XX) P
        bid_list = [BID_DOUBLE, BID_PASS, BID_DOUBLE, BID_REDOUBLE, BID_PASS, BID_PASS, BID_REDOUBLE, BID_PASS]
        return_list = [RETURN_REJECTED_INVALID_BID, RETURN_ACCEPTED, RETURN_REJECTED_INVALID_BID,
                       RETURN_REJECTED_INVALID_BID, RETURN_ACCEPTED, RETURN_ACCEPTED,
                       RETURN_REJECTED_INVALID_BID, RETURN_ACCEPTED_ROUND_FINISHED]
        contract = CONTRACT_PASS
        declarer = 0
        self.test_bid_sequence(bid_list, return_list, contract, declarer)

        # P 1C 2C 3C 4C P 6C 7C P P P
        bid_list = [BID_PASS, BID_1C, BID_2C, BID_3C, BID_4C, BID_PASS, BID_6C, BID_7C, BID_PASS, BID_PASS, BID_PASS]
        return_list = [RETURN_ACCEPTED] * 10 + [RETURN_ACCEPTED_BIDDING_FINISHED]
        contract = CONTRACT_7C
        declarer = 1
        self.test_bid_sequence(bid_list, return_list, contract, declarer)

        # P 1C X P P XX P P 2C P P X P P P
        bid_list = [BID_PASS, BID_1C, BID_DOUBLE, BID_PASS, BID_PASS, BID_REDOUBLE, BID_PASS, BID_PASS,
                    BID_2C, BID_PASS, BID_PASS, BID_DOUBLE, BID_PASS, BID_PASS, BID_PASS]
        return_list = [RETURN_ACCEPTED] * 14 + [RETURN_ACCEPTED_BIDDING_FINISHED]
        contract = CONTRACT_2CX
        declarer = 0
        self.test_bid_sequence(bid_list, return_list, contract, declarer)

        # Don't fail
        # self.fail()

    # TODO: implement this, test for play() and is_valid_play()
    def test_play(self):
        self.fail()

    # TODO: implement this, test for get_score() and calculate_score()
    def test_get_score(self):
        self.fail()

    # TODO: implement this, test for last-trick_winner() and get_trick_winner()
    def test_last_trick_winner(self):
        self.fail()
