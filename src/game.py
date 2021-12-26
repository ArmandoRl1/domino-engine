import multiprocessing as mp
import random
import re
from src.piece import Piece, UnknownPiece
from src.utils import InputError
from copy import deepcopy
from .hand import Hand
from .deck import Deck
from .piece import Piece, UnknownPiece
from .route import Route

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



class Map(object):
    def __init__(self):
        self.center = None
        self.routes = []
        self.skips_in_a_row = 0
        self.stuck = False

    def __str__(self):
        __available = self.get_available_sides()
        # __on_table = self.get_pieces_on_table()
        __routes = "\n\n".join([str(r) for r in self.routes])
        return f"MAP: available moves: {__available}\n\nRoutes:\n{__routes}" #", pieces on table: {__on_table}"

    def get_available_sides(self):
        if len(self.routes)==0:
            # All pieces are valid as 1st move
            return set((0,1,2,3,4,5,6))
        return set(r.end for r in self.routes)

    def get_pieces_on_table(self):
        return sum(len(r) for r in self.routes) + 1  # the first one

    def put(self, piece, route=1):
        self.skips_in_a_row=0

        if self.center is None:  # putting the first one on the table
            self.center = piece
            self.routes = [Route(piece, idx) for idx in range(2)]
            return
        
        if piece.route!=-1:
            if piece.a == self.routes[piece.route-1].end or piece.b == self.routes[piece.route-1].end:
                self.routes[piece.route-1].put(piece)
                return

        for route in self.routes:
            if piece.a == route.end or piece.b == route.end:
                route.put(piece)
                break
        
    def someone_skipped(self):
        self.skips_in_a_row+=1
        if self.skips_in_a_row>=4:
            self.stuck=True
            return
        return


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


    def go(self, game_map, game_deck, game_players, strategy='manual_input', piece_from_params=None):

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
                        if played_piece_input=='*-*':
                            print('Launching Analysis...')
                            analysis = Simulation(game_map, game_deck, game_players, playable_pieces).run()
                            print(analysis, '\n')
                            continue
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
            case 'from_params':
                if piece_from_params is not None:
                    return piece_from_params
                else:
                    # Fall back into first playable
                    for piece in self.hand.pieces:
                        if piece.a in open_sides or piece.b in open_sides:
                            return piece
            case _:
                # In case no pieces are playable
                return None


class Game(object):
    def __init__(
        self, 
        nplayers=4,
        npieces_per_player=7,
        initial_hands:dict=None,
        initial_map:Map=None,
        initial_deck:Deck=None,
        initial_players:list[Player]=None,
        current_player:int = None,
        next_move:Piece = None,
        simulated:bool = False,
        random_state:int = None,
        default_first_piece = Piece(6,6)
    ):
        assert nplayers * npieces_per_player <= 28

        self._current_move_idx = 1
        self.is_finished = False
        self.winner = None
        self.simulated = simulated
        self.next_move = next_move
        self.random_state = random_state

        if initial_deck is None:
            self.deck = Deck()
        else:
            self.deck = initial_deck
            self.deck.shuffle(random_state=self.random_state)
        
        if initial_map is None:
            self.map = Map()
        else:
            self.map = initial_map

        # init players
        if initial_players is None:
            self.players = []
            for i in range(nplayers):
                p = Player(name="P"+str(i+1))
                self.players.append(p)
            # give pieces to players
            for p in self.players:
                if(initial_hands[p.name] is not None):
                    p.hand=initial_hands[p.name]
                    # remove given pieces from deck
                    for pi in p.hand.pieces:
                        self.deck.pieces.remove(pi)
                    continue
                elif(self.simulated):
                    # Give random hand
                    for nb in range(npieces_per_player):
                        p.give(self.deck.take_any())
                else:
                    # For human players, we fill their hands with UnknownPieces (placeholders)
                    for nb in range(npieces_per_player):
                        p.give(UnknownPiece())
        else:
            self.players = initial_players
            if(self.simulated):
                # replace all Unknown Pieces for random pieces
                for p in self.players:
                    no_pieces_to_give = sum([pi.__class__ is UnknownPiece for pi in p.hand.pieces])
                    for i in range(no_pieces_to_give):
                        p.hand.pieces.remove(UnknownPiece())
                        p.give(self.deck.take_any())

        if(self.simulated & (self.map.center is None)):
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
        elif(self.simulated):
            self.current_player_idx = current_player-1
            self.move(strategy = 'from_params')
        else:
            self.current_player_idx = current_player-1
            self.move(strategy = 'manual_input')


    def print_hands(self):
        print("\nHands:")
        for p in self.players:
            print(f"""{p.name}\n{p.hand}""")


    def _prepare_for_next_move(self):
        self._current_move_idx += 1
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)

    def count_points_in_hand(self, hand:Hand):
        assert self.simulated
        s = 0
        for p in hand.pieces:
            s+=p.a
            s+=p.b
        return s

    def move(self, strategy='first_playable'):
        
        if self.is_finished:
            return 

        if self.map.stuck:
            prev_player_idx = (self.current_player_idx + 3) % len(self.players)
            prev_player_count = self.count_points_in_hand(self.players[prev_player_idx].hand)
            own_count = self.count_points_in_hand(self.players[self.current_player_idx].hand)
            if(own_count<prev_player_count):
                self.winner = self.players[self.current_player_idx]
            elif(own_count>=prev_player_count):
                self.winner = self.players[prev_player_idx]
            self.is_finished=True
            return

        player = self.players[self.current_player_idx]

        print(f"\nMove #{self._current_move_idx} by {player}:")

        open_sides = self.map.get_available_sides()
        valid_move = False
        while(not valid_move):
            piece = player.go(self.map, self.deck, self.players, strategy=strategy, piece_from_params=self.next_move)
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
                self.map.skips_in_a_row=0
            else:
                # The player doesnt have any playable piece. We add the ends to their info
                print(" ---> Skipping ")
                valid_move=True
                self.map.someone_skipped()
                player.passes.append(self.map.get_available_sides())
        # Check if the player won
        if len(player.hand) == 0:
            valid_move=True
            self.is_finished = True
            self.winner = player
            return

        print(self.map)

        self._prepare_for_next_move()
    
    def get_winner(self):
        assert self.simulated
        while True:
            self.move(strategy='first_playable')
            if self.is_finished:
                return self.winner.name


class Simulation(object):
    def __init__(self, init_map:Map, init_deck:Deck, init_players:list[Player], playable_pieces:list[Piece], current_player:int=1) -> None:
        self.map=init_map
        self.deck=init_deck
        self.players = init_players
        self.playable_pieces = playable_pieces
        self.current_player = current_player
        return
        
    def run(self, max_simulations = 100) -> dict:
        sims_per_option = int(max_simulations/len(self.playable_pieces))
        results = dict()
        for p in self.playable_pieces:
            results[str(p)]={}
            for i in range(sims_per_option):
                simulation_winner = Game(initial_map = deepcopy(self.map), 
                                         initial_deck = deepcopy(self.deck), 
                                         initial_players = deepcopy(self.players),
                                         current_player = deepcopy(self.current_player), 
                                         next_move = deepcopy(p), 
                                         simulated = True,
                                         random_state = random.randint(-2147483648, 2147483647)
                                         ).get_winner()
                if simulation_winner in results[str(p)]:
                    results[str(p)][simulation_winner]+=1
                else:
                    results[str(p)][simulation_winner]=1
        # Calculate the individual player's probabilities
        win_probabilities = results
        for k in win_probabilities:
            win_probabilities[k] = dict(zip(results[k].keys(), [x/sum(results[k].values()) for x in results[k].values()]))
        return win_probabilities
