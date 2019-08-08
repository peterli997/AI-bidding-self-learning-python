import gym
from gym import error, spaces, utils
from gym.utils import seeding
from contract_bridge.bridge_game import *


class BridgeEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
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

