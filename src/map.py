from .route import Route

class Map(object):
    def __init__(self):
        self.center = None
        self.routes = []

    def __str__(self):
        __available = self.get_available_sides()
        # __on_table = self.get_pieces_on_table()
        __routes = "\n\n".join([str(r) for r in self.routes])
        return f"MAP: available moves: {__available}\n\nRoutes:\n{__routes}" #", pieces on table: {__on_table}"

    def get_available_sides(self):
        return set(r.end for r in self.routes)

    def get_pieces_on_table(self):
        return sum(len(r) for r in self.routes) + 1  # the first one

    def put(self, piece):
        if self.center is None:  # putting the first one on the table
            self.center = piece
            self.routes = [Route(piece) for _ in range(4)]  # init 4 routes
            # TODO: what if the game started not from Tuple and there are already one Route?
            return

        if len(self.routes) == 0:
            pass  # TODO: start map not from Tuple

        for route in self.routes:
            if piece.a == route.end or piece.b == route.end:
                route.put(piece)
                break
            
    