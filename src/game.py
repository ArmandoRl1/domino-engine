import time

from .player import Player
from .deck import Deck
from .piece import Piece
from .map import Map


class Game(object):
    def __init__(
        self, 
        nplayers=4,
        npieces_per_player=7,
        game_number=1,
    ):
        assert nplayers * npieces_per_player <= 28

        self._current_move_idx = 1
        self.is_finished = False
        self.winner = None

        self.deck = Deck()
        self.map = Map()

        # init players
        self.players = []
        for i in range(nplayers):
            p = Player(name="P"+str(i+1))
            self.players.append(p)

        __players_names = ", ".join([p.name for p in self.players])
        print(f"NEW GAME. Players: {__players_names}")
        #time.sleep(2)

        # give pieces to users
        for p in self.players:
            for nb in range(npieces_per_player):
                p.give(self.deck.take())

        self.first_piece = Piece(game_number, game_number)

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


    def print_hands(self):
        print("\nHands:")
        for p in self.players:
            print(f"""{p.name}\n{p.hand}""")


    def _prepare_for_next_move(self):
        self._current_move_idx += 1
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)


    def move(self):
        if self.is_finished:
            return 

        player = self.players[self.current_player_idx]

        print(f"\nMove #{self._current_move_idx} by {player}:")

        piece = player.go(self.map)
        if piece is not None:
            print(f" ---> {piece}")
            player.take(piece)
            self.map.put(piece)

            if len(player.hand) == 0:
                self.is_finished = True
                self.winner = player
                return

        else:
            print(" ---> Skipping ")

        print(self.map)

        self._prepare_for_next_move()