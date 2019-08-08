from unittest import TestCase
from bridge_game.bridge_constants import *

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
        self.assertFalse(board.is_valid_play((3, 5)))

        board.play((1, 0))
        self.assertTrue(board.is_valid_play((1, 12)))
        self.assertFalse(board.is_valid_play((2, 12)))
        self.assertFalse(board.is_valid_play((3, 12)))

        board.play((1, 12))
        self.assertTrue(board.is_valid_play((3, 0)))
        self.assertTrue(board.is_valid_play((4, 0)))

    def test_play_sequence(self, hands, trump, opening_leader, plays, returns, final_history, cur_players, declarer_trick):
        board = BridgeGame(hands, vulnerability=0, starting_pos=opening_leader)
        board.declarer = (opening_leader + 1) % 4
        board.stage = 1
        board.contract = ((4, trump), 0)
        for play, returned, cur_player in zip(plays, returns, cur_players):
            self.assertEqual(returned, board.play(play), board.play_history)
            if not board.is_done_playing():
                self.assertEqual(cur_player, board.current_player, board.play_history)
        self.assertEqual(final_history, board.play_history)
        self.assertEqual(declarer_trick, board.declarer_tricks)

    def test_play(self):
        N = {D2, C2}
        E = {DA, CA}
        S = {H2, S2}
        W = {SA, HA}
        hands = [N, E, S, W]
        board = BridgeGame(hands, vulnerability=0, starting_pos=0)
        board.stage = 0
        self.assertEqual(RETURN_REJECTED_STAGE_INCORRECT, board.play((2, 0)))

        # no trump (SK) D2 (CA) DA H2 HA (C2) (H2) (SA) CA (H2) S2 SA C2 (D2)
        opening_leader = 0
        trump = 5
        plays = [SK, D2, CA, DA, H2, HA, C2, H2, SA, CA, H2, S2, SA, C2, D2]
        returns = [RETURN_REJECTED_INVALID_PLAY, RETURN_ACCEPTED, RETURN_REJECTED_INVALID_BID] + \
            [RETURN_ACCEPTED] * 3 + [RETURN_REJECTED_INVALID_PLAY] * 3 + [RETURN_ACCEPTED] + \
            [RETURN_REJECTED_INVALID_PLAY] + [RETURN_ACCEPTED] * 2 + [RETURN_ACCEPTED_ROUND_FINISHED] + \
            [RETURN_REJECTED_STAGE_INCORRECT]
        final_history = [D2, DA, H2, HA, CA, S2, SA, C2]
        cur_players = [0, 1, 1, 2, 3, 1, 1, 1, 1, 2, 2, 3, 0, 1, 1]
        declarer_trick = 2
        self.test_play_sequence(hands, trump, opening_leader, plays, returns, final_history, cur_players, declarer_trick)

        # trump spade DA H2 HA D2 CA S2 SK SA
        N = {D2, SA}
        E = {DA, CA}
        S = {H2, S2}
        W = {SK, HA}
        hands = [N, E, S, W]
        opening_leader = 1
        trump = 4
        plays = [DA, H2, HA, D2, CA, S2, SK, SA]
        returns = [RETURN_ACCEPTED] * 7 + [RETURN_ACCEPTED_ROUND_FINISHED]
        final_history = [DA, H2, HA, D2, CA, S2, SK, SA]
        cur_players = [2, 3, 0, 1, 2, 3, 0, 0]
        declarer_trick = 1
        self.test_play_sequence(hands, trump, opening_leader, plays, returns, final_history, cur_players, declarer_trick)

        # trump spade CA H2 HA SA D2 DA S2 SK
        opening_leader = 1
        trump = 4
        plays = [CA, H2, HA, SA, D2, DA, S2, SK]
        returns = [RETURN_ACCEPTED] * 7 + [RETURN_ACCEPTED_ROUND_FINISHED]
        final_history = [CA, H2, HA, SA, D2, DA, S2, SK]
        cur_players = [2, 3, 0, 0, 1, 2, 3, 3]
        declarer_trick = 1
        self.test_play_sequence(hands, trump, opening_leader, plays, returns, final_history, cur_players,
                                declarer_trick)
        # Don't fail
        # self.fail()

    def test_get_score(self):
        board = BridgeGame([[]], VUL_NONE, 0)
        board.contract = CONTRACT_4D
        board.declarer = POS_N
        board.declarer_tricks = 10
        board.stage = 0
        for i in range(4):
            self.assertEqual(RETURN_REJECTED_STAGE_INCORRECT, board.get_score(i))
        board.stage = 1
        for i in range(4):
            self.assertEqual(RETURN_REJECTED_STAGE_INCORRECT, board.get_score(i))
        board.stage = 2
        self.assertEqual(130, board.get_score(POS_N))
        self.assertEqual(130, board.get_score(POS_S))
        self.assertEqual(-130, board.get_score(POS_E))
        self.assertEqual(-130, board.get_score(POS_W))
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
