class Route(object):
    def __init__(self, piece):
        assert piece.a == piece.b  # start only from tuple
         
        self.start = None
        self.end = piece.a

        self.pieces = [piece]

    def __str__(self):
        first_piece = self.pieces[0]
        s = f"{first_piece.a}{first_piece.b}"
        prev_val = first_piece.b
        for b in self.pieces[1:]:
            if b.a == prev_val:
                s += f"|{b.a}{b.b}"
                prev_val = b.b
            else:
                s += f"|{b.b}{b.a}"
                prev_val = b.a

        return s
            
        # top_row = "|".join([str(b.a) for b in self.pieces])
        # bot_row = "|".join([str(b.b) for b in self.pieces])
        # return f"""  {top_row}\n  {bot_row}"""
        # return f"Route [ends on {self.end}]"

    def __len__(self):
        return len(self.pieces) - 1

    def put(self, piece):
        if piece.a != self.end and piece.b != self.end:
            raise ValueError(f"Can't Put this {piece} to this {self}.")

        self.pieces.append(piece)
        
        self.start = self.end
        self.end = piece.a if piece.a != self.end else piece.b
