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
    def test_is_valid_play(self):
        N = {(2, 0), (1, 0)}
        E = {(2, 12), (1, 12)}
        S = {(4, 0), (3, 0)}
        W = {(4, 12), (3, 12)}
        hands = [N, E, S, W]
        board = BridgeGame(hands, vulnerability=0, starting_pos=0)
        board.stage = 1
        self.assertTrue(board.is_valid_play((1, 0)))
        self.assertTrue(board.is_valid_play((2, 0)))
        self.assertFalse(board.is_valid_play((1, 12)))
        self.assertFalse(board.is_valid_play((3, 0)))

        board.play((1, 0))
        self.assertTrue(board.is_valid_play((1, 12)))
        self.assertFalse(board.is_valid_play((2, 12)))
        self.assertFalse(board.is_valid_play((3, 12)))

        board.play((1, 12))
        self.assertTrue(board.is_valid_play((3, 0)))
        self.assertTrue(board.is_valid_play((4, 0)))

    def test_play(self, hands, vulnerability, starting_pos):
        board = BridgeGame(hands, vulnerability, starting_pos)
        board.stage = 0
        assert board.play(hands[0][0]) == RETURN_REJECTED_STAGE_INCORRECT
        board.stage = 1
        for i in hands[0]:
            board.is_valid_play(i)
        i = int(len(hands[0])/2)
        board.play(i)
        for j in hands[1]:
            board.is_valid_play(j)

        # Don't fail
        # self.fail()

    # TODO: implement this, test for get_score() and calculate_score()
    def test_get_score(self, hands, vulnerability, starting_pos):
        board = BridgeGame(hands, vulnerability, starting_pos)
        board.stage = 0
        for i in range(4):
            assert board.get_score(i) == RETURN_REJECTED_STAGE_INCORRECT
        board.stage = 1
        for i in range(4):
            assert board.get_score(i) == RETURN_REJECTED_STAGE_INCORRECT
        board.stage = 2
        assert board.get_score(board.declarer) == board.calculate_score(board.contract, board.declarer, vulnerability, board.result)
        # Don't fail
        # self.fail()

    def test_calculate_score(self):
        contract = CONTRACT_4D
        vulnerability = VUL_NONE
        declarer = POS_N
        result = 10
        self.assertEqual(BridgeGame.calculate_score(contract, declarer, vulnerability, result), 130)

        result = 11
        self.assertEqual(BridgeGame.calculate_score(contract, declarer, vulnerability, result), 150)

        declarer = POS_W
        self.assertEqual(BridgeGame.calculate_score(contract, declarer, vulnerability, result), 150)
        self.assertEqual(BridgeGame.get_score(POS_N), -150)

        result = 9
        self.assertEqual(BridgeGame.calculate_score(contract, declarer, vulnerability, result), -50)

        vulnerability = VUL_EW
        self.assertEqual(BridgeGame.calculate_score(contract, declarer, vulnerability, result), -100)

        contract = CONTRACT_7C
        vulnerability = VUL_NONE
        declarer = POS_N
        result = 13
        self.assertEqual(BridgeGame.calculate_score(contract, declarer, vulnerability, result), 1440)

        vulnerability = VUL_EW
        self.assertEqual(BridgeGame.calculate_score(contract, declarer, vulnerability, result), 1440)

        vulnerability = VUL_NS
        self.assertEqual(BridgeGame.calculate_score(contract, declarer, vulnerability, result), 2140)

        vulnerability = VUL_ALL
        self.assertEqual(BridgeGame.calculate_score(contract, declarer, vulnerability, result), 2140)

        contract = CONTRACT_7NTXX
        vulnerability = VUL_ALL
        declarer = POS_N
        result = 13
        self.assertEqual(BridgeGame.calculate_score(contract, declarer, vulnerability, result), 2980)

        result = 0
        self.assertEqual(BridgeGame.calculate_score(contract, declarer, vulnerability, result), -7600)

    # TODO: implement this, test for last-trick_winner() and get_trick_winner()
    def test_last_trick_winner(self):
        cards = [(1, 0), (2, 0), (3, 0), (4, 0)]
        trump = 5
        self.test_get_trick_winner(cards, trump)

        trump = 1
        self.test_get_trick_winner(cards, trump)

        trump = 4
        self.test_get_trick_winner(cards, trump)

        cards = [(1, 5), (1, 3), (1, 7), (2, 4)]
        trump = 5
        self.test_get_trick_winner(cards, trump)

        trump = 1
        self.test_get_trick_winner(cards, trump)

        trump = 2
        self.test_get_trick_winner(cards, trump)
        # Don't fail
        # self.fail()

    def test_get_trick_winner(self, cards, trump):
        assert len(cards) == 4
        lead = cards[0]
        if len(cards, key = lambda a: a // 13 == trump - 1):
            highest_card = max(cards, key = lambda a: a // 13 == trump - 1)
        else:
            highest_card = max(cards, key = lambda a: a // 13 == lead // 13)
        winner = cards.index(highest_card)
        self.assertEqual(winner, BridgeGame.get_trick_winner(cards, trump))

