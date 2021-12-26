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

    def take_any(self):
        if self.is_empty():
            return None
        return self.pieces.pop()
    
    def take(self, piece):
        for i,p in enumerate(self.pieces):
            if(p==piece):
                return self.pieces.pop(i)
        raise RuntimeError("Tried to take non-existing piece from Deck")
    
    def shuffle(self, random_state:int=None):
        if random_state is not None:
            random.seed(random_state)
        random.shuffle(self.pieces)
        return
