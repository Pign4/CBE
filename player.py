from random import choice, sample

class Player:

    def __init__(self, color, pieces):
        ''' Store the color and the state of the player's pile and hand.
        It also takes note of the placed and played pieces,
        and if the player can place a piece
        '''

        self.type = pieces
        self.color = '\x1b[37;41m' if color == 0 else '\x1b[31;40m'
        self.strcolor = self.paint('red') if color == 0 else self.paint('black')
        self.pile = sample(pieces,len(pieces))
        self.hand = []
        self.placed = []
        self.played = []
        self.canPlace = True


    def __eq__(self, other):
        ''' Returns True if the last 6 attributes have the same elements.
        The pile is the only attribute that also needs the elements to be ordered.
        '''

        if self.pile == other.pile \
        and set(self.hand) == set(other.hand) \
        and set(self.placed) == set(other.placed) \
        and set(self.played) == set(other.played) \
        and self.canPlace == other.canPlace:
            return True
        return False


    def draw(self):
        ''' If there are any cards to draw, one card is drawn.
        The last element of the self.pile list is moved to self.hand.
        '''

        if self.pile:
            self.hand.append(self.pile.pop())

    def undraw(self):

        self.pile.append(self.hand.pop())


    def discard(self):
        ''' If the player has two cards in hand (at the end of the turn),
        one piece is randomly discarded.
        The discarded piece and its index are returned.
        '''

        if len(self.hand) == 2:
            index = choice([0,1])
            return (index, self.hand.pop(index))


    def place(self, piece):
        ''' The piece is moved from the hand (self.hand) to the board (self.placed).
        The piece is also marked as played (added to self.played),
        so that it cannot perform other actions.
        '''

        index = self.hand.index(piece)
        self.hand.remove(piece)
        self.placed.append(piece)
        self.played.append(piece)
        self.canPlace = False
        return index


    def destroy(self, piece):
        ''' The piece is removed from the board (self.board) '''

        self.placed.remove(piece)


    def show(self, obj):
        ''' Method to show the elements of one list without the brackets '''

        return ', '.join(self.paint(piece) for piece in obj)

    def destroyed(self):
        return self.type - set(self.placed) - set(self.hand) - set(self.pile)


    def paint(self,obj):
        ''' Returns a "colored" string according to the player's color '''

        return self.color + obj + '\x1b[0m'
