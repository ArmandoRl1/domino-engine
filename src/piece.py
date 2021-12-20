
class Piece(object):
    def __init__(self, a: int, b: int, route:int=-1):
        self.a = min(int(a), int(b))
        self.b = max(int(a), int(b))
        self.route = route


    def __str__(self):
        # if self.a == self.b == 1:
        #     __name = "🀹"
        # elif self.a == self.b == 6:
        #     __name = "🁡"
        # else:
        __name = f"[{self.a}|{self.b}]"
        return f"Piece {__name}"

    def __eq__(self, b):
        return self.a == b.a and self.b == b.b  # always sorted

    def is_double(self):
        return self.a == self.b

class UnknownPiece(Piece):
    # Placeholder to fill their hands
    def __init__(self):
        super().__init__(-1, -1)