import random

from .piece import Piece

class Deck(object):
    def __init__(self):
        self.pieces = []

        for i in range(7):
            for j in range(7):
                if i <= j:
                    self.pieces.append(Piece(i,j))

        random.shuffle(self.pieces)

    def is_empty(self):
        return len(self.pieces) == 0

    def __len__(self):
        return len(self.pieces)

    def take(self):
        if self.is_empty():
            return None
        return self.pieces.pop()
