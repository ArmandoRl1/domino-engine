import re

from src.piece import Piece
from src.hand import Hand

class InputError(Exception):
    def __init__(self, message):
        self.message = 'Input Error: '+ message +'\n'
        Exception.__init__(self, self.message)


def text_to_hand(input_text):
    # Validate that hand input is valid
    input_text=re.sub("[^0-9]","",input_text)
    if(re.search("[7-9]", input_text)):
        raise InputError(message='Numbers 7-9 are invalid.')
    if(len(input_text)%2):
        raise InputError(message='Odd number of numbers: {:0f}.'.format(len(input_text)))
    if(len(input_text)!=14):
        raise InputError('Hand is not 7 pieces, but {:.0f}.'.format(len(input_text)/2))
    pieces_text = [input_text[i:i+2] for i in range(0, len(input_text), 2)]
    if(len(set(pieces_text))!=len(pieces_text)):
        raise InputError('Pieces are not unique.')
    pieces = []
    for i in range(len(input_text)):
        if(i%2==1):
            continue
        pieces.append(Piece(input_text[i], input_text[i+1]))
    return Hand(pieces)

