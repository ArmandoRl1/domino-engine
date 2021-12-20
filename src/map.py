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
        if len(self.routes)==0:
            # All pieces are valid as 1st move
            return set((0,1,2,3,4,5,6))
        return set(r.end for r in self.routes)

    def get_pieces_on_table(self):
        return sum(len(r) for r in self.routes) + 1  # the first one

    def put(self, piece, route=1):
        if self.center is None:  # putting the first one on the table
            self.center = piece
            self.routes = [Route(piece) for _ in range(2)]  # init 4 routes
            # TODO: what if the game started not from Tuple and there are already one Route?
            return

        if len(self.routes) == 0:
            pass  # TODO: start map not from Tuple
        
        if piece.route!=-1:
            if piece.a == self.routes[piece.route-1].end or piece.b == self.routes[piece.route-1].end:
                self.routes[piece.route-1].put(piece)
                return

        for route in self.routes:
            if piece.a == route.end or piece.b == route.end:
                route.put(piece)
                break
            
    