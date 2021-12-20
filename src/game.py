import time

from .player import Player
from .deck import Deck
from .piece import Piece, UnknownPiece
from .map import Map

class Game(object):
    def __init__(
        self, 
        nplayers=4,
        npieces_per_player=7,
        initial_hands:dict=None,
        initial_map:Map=None,
        initial_player:int = None,
        simulated:bool = None,
        default_first_piece = Piece(6,6)
    ):
        assert nplayers * npieces_per_player <= 28

        self._current_move_idx = 1
        self.is_finished = False
        self.winner = None

        self.deck = Deck()
        
        if initial_map is None:
            self.map = Map()
        else:
            self.map = initial_map

        # init players
        self.players = []
        for i in range(nplayers):
            p = Player(name="P"+str(i+1))
            self.players.append(p)

        #time.sleep(2)

        # give pieces to players
        for p in self.players:
            if(initial_hands[p.name] is not None):
                p.hand=initial_hands[p.name]
                # remove given pieces from deck
                for pi in p.hand.pieces:
                    self.deck.pieces.remove(pi)
                continue
            elif(simulated):
                # Give random hand
                for nb in range(npieces_per_player):
                    p.give(self.deck.take_any())
            else:
                # For human players, we fill their hands with UnknownPieces (placeholders)
                for nb in range(npieces_per_player):
                    p.give(UnknownPiece())

        if(simulated):
            # check who has {self.first_piece}
            for i, p in enumerate(self.players):
                if self.first_piece in p.hand.pieces:  # player who has first piece
                    self.current_player_idx = i
                    print(f"MOVE: {p} goes first with {self.first_piece}!")
                    p.take(self.first_piece)
                    self.map.put(self.first_piece)
                    self._prepare_for_next_move()
                    return 
            raise Exception(f"Noone has {self.first_piece}")
        else:
            self.current_player_idx = initial_player-1
            self.move(strategy = 'manual_input')


    def print_hands(self):
        print("\nHands:")
        for p in self.players:
            print(f"""{p.name}\n{p.hand}""")


    def _prepare_for_next_move(self):
        self._current_move_idx += 1
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)


    def move(self, strategy='first_playable'):
        if self.is_finished:
            return 

        player = self.players[self.current_player_idx]

        print(f"\nMove #{self._current_move_idx} by {player}:")

        open_sides = self.map.get_available_sides()
        valid_move = False
        while(not valid_move):
            piece = player.go(self.map, strategy=strategy)
            if piece is not None:
                print(f" ---> {piece}")
                if player.take(piece):
                    # If player played an UnknownPiece, 
                    # we remove it from the Deck, which has all unknown pieces
                    # if it's not on the Deck, it's on another player's hand, and we have to request input again
                    if ((piece.a in open_sides) or (piece.b in open_sides)):
                        try:
                            self.deck.pieces.remove(piece)
                            self.map.put(piece)
                            valid_move=True
                        except ValueError as err:
                            print('ERROR: That piece has been played or is on another player\'s hand. Try another piece.')
                            player.give(UnknownPiece())
                        except Exception as owo_exception:
                            raise owo_exception
                    else:
                        print('That\'s not a valid move.')
                        player.give(UnknownPiece())
                else:
                    self.map.put(piece)
                    valid_move=True
            else:
                # The player doesnt have any playable piece. We add the ends to their info
                print(" ---> Skipping ")
                valid_move=True
                player.passes.append(self.map.get_available_sides())
        # Check if the player won
        if len(player.hand) == 0:
            valid_move=True
            self.is_finished = True
            self.winner = player
            return

        print(self.map)

        self._prepare_for_next_move()