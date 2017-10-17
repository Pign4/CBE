from player import Player

class Board:

    def __init__(self, size, pieces):
        ''' Store the size of the board, create the board,
        define the starting squares for each player,
        create the players, create winner string
        '''

        self.size = size
        # self.pos = [(2, ' '),(2, ' '),(0, 'A'),(2, ' '),
        #             (2, ' '),(1, 'T'),(2, ' '),(2, ' '),
        #             (2, ' '),(2, ' '),(2, ' '),(2, ' '),
        #             (2, ' '),(2, ' '),(2, ' '),(2, ' ')]
        self.pos = [(2, ' ')] * size**2
        self.startSquares = ([8,13],[2,7]) if size == 4 else ([10,16,22], [2,8,14])
        self.players = [Player(0, pieces), Player(1, pieces)]
        self.winner = None

    def __eq__(self, other):
        ''' If the board position and the players are the same, returns True '''

        if self.pos == other.pos and self.players == other.players:
            return True
        return False


    def checkSurrounded(self, pl):
        ''' Destroy all surrounded enemy pieces by updating position and players '''

        destroyed = []
        for piece in self.players[pl].placed:
            index = self.pos.index((pl, piece))
            adjIndexes = self.getAdjacents(index)
            if all(self.pos[ai][0] == 1-pl for ai in adjIndexes):
                self.pos[index] = (2,' ')
                # dangerous, since it destroys from the list it iterates through
                self.players[pl].destroy(piece)
                destroyed.append((piece, index))
        return destroyed


    def isSurrounded(self, index, pl, piece):
        ''' Returns True if surrounded by pl pieces, else False '''

        aIndexes = self.getAdjacents(index)
        if all(self.pos[aIndex][0] == pl for aIndex in aIndexes):
            self.players[1 - pl].destroy(piece)
            self.pos[index] = (2,' ')
            return True
        return False


    def checkWin(self, pl):
        ''' Set pl as the winner if a pl piece is occupying the enemy's base '''

        if self.pos[3*(1+3*pl)][0] == pl:
            self.winner = pl
            return True
        return False


    def free(self, index):
        ''' Returns True if the square is empty '''

        return self.pos[index] == (2,' ')


    def getAdjacents(self, index):
        ''' Yields all the valid adjacent squares indexes.
        It checks them in anti-clockwise direction starting from the square to the right.
        '''

        if index % self.size != self.size - 1: yield index + 1
        if index >= self.size: yield index - self.size
        if index % self.size != 0: yield index - 1
        if index < self.size * (self.size - 1): yield index + self.size


    def index2coords(self, index):
        ''' Returns the corrispondent square coordinates to the given index '''

        return 'abcde'[index % self.size] + str(self.size - index // self.size)


    def dir2index(self, pl, index, direction):
        ''' Returns the index of the adjacent square according to direction '''

        if direction == ['r', 'l'][pl]:
            if index % self.size != self.size - 1:
                return index + 1
        elif direction == ['u', 'd'][pl]:
            if index > self.size - 1:
                return index - self.size
        elif direction == ['l', 'r'][pl]:
            if index %  self.size != 0:
                return index - 1
        else:
            if index < self.size * (self.size - 1):
                return index + self.size
        return -1

    def winnerString(self):
        return self.players[self.winner].strcolor
