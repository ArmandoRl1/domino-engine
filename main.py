import time
from src.game import Game
from src.utils import *
import argparse
import random
random.seed(None)

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--simmulated",
                    help="Simmulates a game with random initial conditions",
                    action="store_true")

# Get own pieces
own_hand:Hand = None
while(not own_hand):
    own_pieces_text = input("Input your own pieces, as two digit numbers (eg. 11 = [·|·])\n")
    try:
        own_hand = text_to_hand(own_pieces_text)
    except InputError as err:
        print(err)
    except Exception:
        raise
print(own_hand)

# Get 1st player
print('''Player layout:
       P3
    P2[  ]P4
       P1

P1 is you. P3 is your teammate.
''')

initial_player:int = None # int from 1 to 4
while(not initial_player):
    initial_player_text = input("Who's the first player? ")
    initial_player_text = re.sub("[^1-4]","",initial_player_text)
    try:
        assert(len(initial_player_text)==1)
        initial_player = int(initial_player_text)
    except Exception:
        raise

current_hands = {
    'P1':own_hand,
    'P2':None,
    'P3':None,
    'P4':None,
}

g = Game(initial_hands=current_hands,
         current_player=initial_player)

while True:
    g.move(strategy='manual_input')
    g.print_hands()

    if g.is_finished:
        print(f"------> WINNER 👑: {g.winner}")
        # TODO count points
        break