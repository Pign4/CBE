class TurnFinisher:

    def __init__(self, pl):
        self.pl = pl
        self.played = None
        self.discard = None
        self.canPlace = None
        self.destroyed = None

    def __repr__(self):
        return "end"

    def execute(self, board):
        # end of turn
        self.played = board.players[self.pl].played
        board.players[self.pl].played = []
        self.discard = board.players[self.pl].discard()
        # start of next turn
        board.players[1 - self.pl].draw()
        self.canPlace = board.players[1 - self.pl].canPlace
        board.players[1 - self.pl].canPlace = True if board.players[1 - self.pl].hand \
                                                   else False
        self.destroyed = board.checkSurrounded(self.pl)
        board.checkWin(1 - self.pl)

    def goBack(self, board):
        # undo start of next turn
        board.winner = None
        for (piece, index) in self.destroyed:
            board.pos[index] = (self.pl, piece)
            board.players[self.pl].append(piece)
        board.players[1 - self.pl].canPlace = self.canPlace
        board.players[1 - self.pl].undraw()
        # undo end of turn
        if self.discard:
            board.players[self.pl].hand.insert(self.discard[0], self.discard[1])
        board.players[self.pl].played = self.played


class Placement:

    def __init__(self, pl, piece, square, string):
        self.pl = pl
        self.piece = piece
        self.square = square
        self.string = string
        self.handIndex = None
        self.destroyed = []

    def __repr__(self):
        return self.string

    def execute(self, board):
        print()
        for x in range(4):
            for value in board.pos[4*x:4*x+4]:
                print(value, end = '')
            print()
        self.handIndex = board.players[self.pl].place(self.piece)
        board.pos[self.square] = (self.pl, self.piece)
        for adjIndex in board.getAdjacents(self.square):
            if board.pos[adjIndex][0] == 1 - self.pl:
                if board.isSurrounded(adjIndex, self.pl):
                    destroyed.append((board.pos[adjIndex][1], adjIndex))

    def goBack(self, board):
        # undo placement
        board.players[self.pl].hand.insert(self.handIndex, self.piece)
        board.players[self.pl].placed.remove(self.piece)
        board.players[self.pl].played.remove(self.piece)
        board.players[self.pl].canPlace = True
        board.pos[self.square] = (2,' ')
        # undo piece destructions
        for (piece, index) in self.destroyed:
            # should I care about piece position inside .placed?
            board.players[1 - self.pl].placed.append(piece)
            board.pos[index] = piece


class Movement:

    def __init__(self, pl, piece, index, newIndex, string):
        self.pl = pl
        self.piece = piece
        self.index = index
        self.newIndex = newIndex
        self.string = string
        self.destroyed = []

    def __repr__(self):
        return self.string

    def execute(self, board):
        board.players[self.pl].played.append(self.piece)
        board.pos[self.index] = (2,' ')
        if self.newIndex != -1:
            board.pos[self.newIndex] = (self.pl, self.piece)
            for adjIndex in board.getAdjacents(self.newIndex):
                if board.pos[adjIndex][0] == 1 - self.pl:
                    if board.isSurrounded(adjIndex, self.pl):
                        destroyed.append((board.pos[adjIndex][1], adjIndex))
        else:
            board.players[self.pl].destroy(self.piece)
        board.checkWin(self.pl)

    def goBack(self, board):
        board.winner = None
        board.players[self.pl].played.remove(self.piece)
        board.pos[self.index] = (self.pl, self.piece)
        if self.newIndex == -1:
            board.players[self.pl].placed.append(self.piece)
        else:
            board.pos[self.newIndex] = (2,' ')
            for (piece, index) in self.destroyed:
                board.players[1 - self.pl].placed.append(piece)
                board.pos[index] = (1 - self.pl, piece)


class Activation:

    def __init__(self, pl, piece, index, newIndex, string):
        self.pl = pl
        self.piece = piece
        self.index = index
        self.newIndex = newIndex
        self.string = string
        self.destroyed = []

    def __repr__(self):
        return self.string

    def execute(self, board):
        board.players[self.pl].played.append(self.piece)
        if self.newIndex != -1:
            board.pos[self.index], board.pos[self.newIndex] \
            = board.pos[self.newIndex], board.pos[self.index]
            self.destroyed = board.checkSurrounded(1 - self.pl)
        else:
            dPiece, board.pos[self.index] = board.pos[self.index], (2,' ')
            board.players[dPiece[0]].destroy(dPiece[1])
            self.destroyed = dPiece
        board.checkWin(self.pl)

    def goBack(self, board):
        board.winner = None
        board.players[self.pl].played.remove(self.piece)
        if self.newIndex == -1:
            board.pos[self.index] = self.destroyed
            board.players[self.destroyed[0]].placed.append(self.destroyed[1])
        else:
            board.pos[self.index], board.pos[self.newIndex] \
            = board.pos[self.newIndex], board.pos[self.index]
            for (piece, index) in self.destroyed:
                board.players[1 - self.pl].placed.append(piece)
                board.pos[index] = (1 - self.pl, piece)
