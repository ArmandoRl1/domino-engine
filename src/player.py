import random

from .hand import Hand

def get_random_name():
    NAMES = ["Anya", "Dan", "Prosolkin", "Dan's Papa", "Ivan Potylitcyn", "Lera Muravya", "Random dude"]
    return random.choice(NAMES)

class Player(object):
    def __init__(self, name: str=None, team = None):
        self.name = name or get_random_name()
        self.hand = Hand([])
        self.team = team

    def __str__(self):
        return f"Player '{self.name}'"  # \n{self.hand}"

    def give(self, piece):
        self.hand.put(piece)

    def take(self, piece):
        self.hand.pieces.remove(piece)

    def go(self, game_map, strategy='first_playable'):
        open_sides = game_map.get_available_sides()
        match strategy:
            case 'first_playable':
                # Loops through the pieces and plays the first playable piece found
                for piece in self.hand.pieces:
                    if piece.a in open_sides or piece.b in open_sides:
                        return piece
            case _:
                # In case no pieces are playable
                return None
        
        