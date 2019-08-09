import gym
from gym import error, spaces, utils
from gym.utils import seeding
from contract_bridge.bridge_game import *
OPEN_TABLE = 0
CLOSED_TABLE = 1
OPEN_NS = 0
CLOSED_NS = 1


class DuplicateBridgeEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, hands=None, dealer=None, vulnerability=None, random_reset=True):
        import random
        if hands is None:
            hands = BridgeGame.random_board()
        if dealer is None:
            dealer = random.randint(0, 4)
        if vulnerability is None:
            vulnerability = random.randint(0, 3)
        # duplicate bridge needs two games, play open_board first
        self.open_table = BridgeGame(hands, dealer, vulnerability)
        self.closed_table = BridgeGame(hands, dealer, vulnerability)
        self.current_table_no = OPEN_TABLE
        self.dealer = dealer
        self.openNS_score = SCORE_INVALID
        self.closedNS_score = SCORE_INVALID
        self.random_reset = random_reset

    def reset(self):
        if self.random_reset:
            import random
            self.open_table.create_random_board()
            self.closed_table.hands = self.open_table.hands
            dealer = random.randint(0, 4)
            vulnerability = random.randint(0, 3)
            self.open_table.dealer = dealer
            self.closed_table.dealer = dealer
            self.open_table.vulnerability = vulnerability
            self.closed_table.vulnerability = vulnerability
        self.open_table.reset_round()
        self.closed_table.reset_round()
        self.current_table_no = CLOSED_TABLE
        self.openNS_score = SCORE_INVALID
        self.closedNS_score = SCORE_INVALID
        pass

    @property
    def current_team(self):
        return self.open_table.current_player % 2 if self.current_table_no == OPEN_TABLE else 1 - self.closed_table.current_player % 2

    @property
    def current_player(self):
        return self.open_table.current_player if self.current_table_no == OPEN_TABLE else self.closed_table.current_player

    def step(self, action):
        """
        Do a step. Open board first.
        :param action: the play or bid to be done.
        :return:
        observation: current_team as team
                     player_position as position,
                     declarer as position,
                     stage as stage,
                     player_card as list of cards,
                     dummy_card as list of cards, None if dummy is not available,
                     bid_history as list of bids,
                     play_history as list of cards,

                     vulnerability as vulnerability,
        reward:      the result difference of two tables for the current position at the end of the game.
                     or -1 if invalid step was given.
        done:        if it is the end of the last round
        info:        "table": the current table,
        """
        def step_finished_returning(reward=0, done=False):
            return (self.current_team, self.current_player, board.declarer,
                    board.stage, board.hands[self.current_player],
                    board.hands[(board.declarer + 2) % 4], board.bid_history,
                    board.play_history,
                    board.vulnerability), reward, done, {"table": self.current_table_no}

        if self.current_table_no == OPEN_TABLE:
            board = self.open_table
        else:
            board = self.closed_table
        if board.stage == STAGE_FINISHED:
            return RETURN_REJECTED_STAGE_INCORRECT
        elif board.stage == STAGE_PLAYING:
            returned = board.play(action)
        else:
            returned = board.bid(action)
        assert returned != RETURN_REJECTED_STAGE_INCORRECT
        if returned == RETURN_REJECTED_INVALID_PLAY:
            return step_finished_returning(-1)
        if returned == RETURN_ACCEPTED_ROUND_FINISHED:
            if self.current_table_no == CLOSED_TABLE:
                self.closedNS_score = self.closed_table.get_score(POS_N)
                score = self.openNS_score - self.closedNS_score
                if self.current_player % 2 == POS_N:
                    score = -score
                step_finished_returning(score, True)
            else:
                self.openNS_score = self.open_table.get_score(POS_N)
                self.current_table_no = CLOSED_TABLE
                step_finished_returning()
        elif returned == RETURN_ACCEPTED_BIDDING_FINISHED or returned == RETURN_ACCEPTED:
            step_finished_returning()
        else:
            assert False, "unknown return code"

    # TODO: implement this
    def render(self, mode='human'):
        ...

    def close(self):
        pass



