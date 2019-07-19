import DoubleDummy
import time
from unittest import TestCase

class TestBridgeGame(TestCase):
    def test_minMax(self):
        play = [-1] * 52
        card_holder = [-1] * 52
        card_rank = list(range(52))
        s = [15, 20, 23, 24, 31, 33, 34, 36, 47]
        w = [6, 7, 9, 11, 13, 22, 28, 32, 48]
        n = [1, 3, 14, 16, 29, 43, 45, 49, 50]
        e = [8, 17, 18, 19, 21, 25, 27, 35, 44]
        for j in s:
            card_holder[j] = 0
        for j in w:
            card_holder[j] = 1
        for j in n:
            card_holder[j] = 2
        for j in e:
            card_holder[j] = 3
        card_holder_dict = dict(zip(card_rank, card_holder))
        DoubleDummy.minMax(play, card_holder_dict, [n, e, s, w], len(n))
