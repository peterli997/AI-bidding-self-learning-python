import gym
from gym import error, spaces, utils
from gym.utils import seeding
from contract_bridge.bridge_game import *
HOST_BOARD = 0
AWAY_BOARD = 1

class BridgeEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, hands=None, dealer=None, vulnerability=None):
        import random
        if hands is None:
            hands = BridgeGame.random_board()
        if dealer is None:
            dealer = random.randint(0, 4)
        if vulnerability is None:
            vulnerability = random.randint(0, 3)
        # duplicate bridge needs two games, play host_board first
        self.host_board = BridgeGame(hands, dealer, vulnerability)
        self.away_board = BridgeGame(hands, dealer, vulnerability)
        self.board_no = HOST_BOARD
        self.current_player = dealer % 2

        pass

    def step(self, action):
        ...

    def reset(self):
        ...

    def render(self, mode='human'):
        ...

    def close(self):
        ...

    def update_board(self, new_board):
        self.board = new_board

