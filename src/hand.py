from typing import List

from .piece import Piece

class Hand(object):
    def __init__(self, pieces: List[Piece] = []):
        self.pieces = pieces

    def __len__(self):
        return len(self.pieces)

    def __str__(self):
        top_row = '|'+"| |".join([str(b.a) for b in self.pieces])+'|'
        bot_row = '|'+"| |".join([str(b.b) for b in self.pieces])+'|'
        return f"""  {top_row}\n  {bot_row}"""

    def put(self, piece):
        self.pieces.append(piece)

    def does_have(self, piece):
        return piece in self.pieces