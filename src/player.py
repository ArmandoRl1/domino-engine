import random
import re

from src.utils import InputError
from src.piece import Piece, UnknownPiece

from .hand import Hand

def text_to_piece(input_text):
    # Validate that piece input is valid
    input_text=re.sub("[^0-9]","",input_text)
    if(re.search("[7-9]", input_text)):
        raise InputError(message='Numbers 7-9 are invalid.')
    if(len(input_text)%2):
        raise InputError(message='Odd number of numbers: {:0f}.'.format(len(input_text)))
    return Piece(input_text[0], input_text[1])

def get_random_name():
    NAMES = ["Anya", "Dan", "Prosolkin", "Dan's Papa", "Ivan Potylitcyn", "Lera Muravya", "Random dude"]
    return random.choice(NAMES)

class Player(object):
    def __init__(self, name: str=None, passes=None):
        self.name = name or get_random_name()
        self.hand = Hand([])
        self.passes = []

    def __str__(self):
        return f"Player '{self.name}'"  # \n{self.hand}"

    def give(self, piece):
        self.hand.put(piece)

    def take(self, piece, revealed_unkown=False):
        if piece in self.hand.pieces:
            self.hand.pieces.remove(piece)
        elif any([x.__class__ is UnknownPiece for x in self.hand.pieces]):
            self.hand.pieces.remove(UnknownPiece())
            revealed_unkown=True
        return revealed_unkown


    def go(self, game_map, strategy='manual_input'):

        open_sides = game_map.get_available_sides()
        
        playable_pieces = []
        for p in self.hand.pieces:
            if p.a in open_sides or p.b in open_sides:
                playable_pieces.append(p)
        
        player_has_unknown_pieces = any([p.__class__ is UnknownPiece for p in self.hand.pieces])

        if (not player_has_unknown_pieces) and len(playable_pieces)==0:
            # No playable pieces bruh
            return None

        match strategy:
            case 'manual_input':
                # Requests the played piece to user
                played_piece=None
                while(played_piece is None):
                    try:
                        if not player_has_unknown_pieces:
                            print("Playable pieces:{}".format(str(list(map(str,playable_pieces)))))
                        played_piece_input=input("What is {}'s move? (\"--\" to skip) ".format(self.name))
                        if played_piece_input=='--':
                            # Player cant skip turn if it can play pieces
                            assert len(playable_pieces)==0, "Player has playable pieces:{}".format(str(map(str,playable_pieces)))
                            return None
                        played_piece_input=text_to_piece(played_piece_input)
                        assert (played_piece_input in playable_pieces or player_has_unknown_pieces), "That\'s not a valid move."
                        assert (played_piece_input in self.hand.pieces or player_has_unknown_pieces), "Player doesn\'t have that piece."
                        played_piece=played_piece_input
                    except InputError as ir:
                        print(ir)
                    except Exception as err:
                        print(err)
                
                # Check if selected piece can be put in multiple routes:
                if game_map.center is not None \
                    and (((played_piece.a in open_sides) and (played_piece.b in open_sides)) or ({played_piece.a}==open_sides) or ({played_piece.b}==open_sides))\
                    and not (played_piece.is_double() and len(open_sides)>1):
                    chosen_route = False
                    while not chosen_route:
                        try:
                            chosen_route = int(input("On which route? (1/2): "))
                        except Exception as err:
                            print(err)
                    played_piece.route=chosen_route

                return played_piece
            case 'first_playable':
                # Loops through the pieces and plays the first playable piece found
                for piece in self.hand.pieces:
                    if piece.a in open_sides or piece.b in open_sides:
                        return piece
            case _:
                # In case no pieces are playable
                return None
        
        