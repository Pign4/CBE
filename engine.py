from itertools import product, permutations
from copy import deepcopy
from decimal import Decimal

from actions import TurnFinisher, Placement, Movement, Activation
from printfs import show
import pdb


class Engine:

    def __init__(self):
        ''' Stores all the actions at each phase of the turn and the best play '''

        self.actions = []
        self.bestPlay = ()

    def updateActions(self, pl, board):
        ''' Updates the actions and sorts them by piece
        (so that  it is easier to print them later)
        '''

        self.actions = sorted(allActions(pl, board), key = lambda action: action.piece)

    def worstCase(self, pl, board, depth):
        # problems:
        # 1. what if checkmate is not inevitable ...?
        # 2. doesn't perform shortest play
        worstSoFar = ("", 1000001)
        for n, newBoard in enumerate(allCases(pl, board)):
            cont, val = self.best(pl, board, depth, -1000000, 1000000)
            if val < worstSoFar[1]:
                worstSoFar = (cont, val)
        self.bestPlay = worstSoFar

    def best(self, pl, board, depth, alpha, beta):
        if board.winner == pl: return "", 1000
        if board.winner == 1 - pl: return "", max(-1000, alpha)
        if depth == 0: return "", evaluate(pl, board)
        bestSoFar = None
        for action in allActions(pl, board):
            action.execute(board)
            cont, val = self.best(pl, board, depth, alpha, beta)
            if val >= beta:
                action.goBack(board)
                return action.string + " " + cont, beta
            if val > alpha:
                alpha = val
            if bestSoFar is None or bestSoFar[1] < val:
                bestSoFar = (action.string + " " + cont, val)
            if bestSoFar[1] == 1000:
                action.goBack(board)
                break
            finish = TurnFinisher(pl)
            finish.execute(board)
            cont, val = self.best(1 - pl, board, depth - 1, -beta, -alpha)
            finish.goBack(board)
            action.goBack(board)
            val = -val
            if val >= beta:
                return action.string + " " + cont, beta
            if val > alpha:
                alpha = val
            if bestSoFar is None or bestSoFar[1] < val:
                bestSoFar = (action.string + " ; " + cont, val)
            if bestSoFar[1] == 1000:
                break
        return bestSoFar or ("", max(-1000, alpha))


def opposite(direction):
    ''' Returns the the opposite direction: right-left and up-down '''

    if direction in 'rl': return 'rl'.replace(direction, '')
    else: return 'ud'.replace(direction, '')


def allActions(pl, board):
    ''' Returns all possible placements, movements and activations in one list.
    Each element is an Action object
    '''

    if board.players[pl].canPlace:
        yield from allPlacements(pl, board)
    for piece in board.players[pl].placed:
        if piece not in board.players[pl].played:
            # sometimes gives error: not in list --> it's in .placed but it was not removed or it should be on the board but it wasn't added
            index = board.pos.index((pl, piece))
            yield from allMovements(pl, piece, index, board)
            yield from filter(None, allActivations(pl, piece, index, board, 'ruld'))
                       # ^^^ needs filter due to H and M


def allPlacements(pl, board):
    ''' Yields all legal placements (each piece in hand in each free starting square) '''

    squares = filter(board.free, board.startSquares[pl])
    for piece, square in product(board.players[pl].hand, squares):
        yield Placement(pl, piece, square, piece + board.index2coords(square))


def allMovements(pl, piece, index, board):
    ''' Yields all legal movements (each piece on the board moving right and upwards) '''

    for direction in 'ru':
        newIndex = board.dir2index(pl, index, direction)
        if newIndex < 0 or board.free(newIndex):
            yield Movement(pl, piece, index, newIndex, piece + direction)


def allActivations(pl, piece, index, board, ruld):
    ''' Auxiliary function to redirect to the correct letter-search-function. '''

    if piece == 'D': return allD(pl, index, board)
    elif piece == 'J': return allJ(pl, index, board)
    elif piece == 'P': return allP(pl, index, board)
    elif piece == 'T': return allT(pl, index, board)
    elif piece == 'S': return allS(pl, index, board)
    elif piece == 'M': return allM(pl, index, board, ruld)
    elif piece == 'H': return allH(pl, index, board, ruld)
    else: return allA(pl, index, board)


def allD(pl, index, board):
    ''' Yields all legal activations of D
    (if the arriving square is not occupied or is out of the board)
    '''

    for direction in ['ru', 'rd', 'lu', 'ld']:
        newIndex = board.dir2index(pl, index, direction[0])
        if newIndex >= 0:
            newIndex = board.dir2index(pl, newIndex, direction[1])
        if newIndex < 0 or board.free(newIndex):
            yield Activation(pl, 'D', index, newIndex, 'D' + direction)


def allJ(pl, index, board):
    ''' Yields all legal activations of J
    (if the arriving square is not occupied or is out of the board, and the adjacent square is occupied)
    '''

    for direction in 'ruld':
        adjIndex = board.dir2index(pl, index, direction)
        if adjIndex >= 0 and not(board.free(adjIndex)):
            newIndex = board.dir2index(pl, adjIndex, direction)
            if newIndex < 0 or board.free(newIndex):
                yield Activation(pl, 'J', index, newIndex, 'J' + direction)


def allS(pl, index, board):
    ''' Yields all legal activations of S (if the arriving square is occupied) '''

    for direction in 'ruld':
        newIndex = board.dir2index(pl, index, direction)
        if newIndex >= 0 and not(board.free(newIndex)):
            yield Activation(pl, 'S', index, newIndex, 'S' + direction)


def allP(pl, index, board):
    ''' Yields all legal activations of P
    (if the adjacent square is occupied and the arriving square is not occupied or is out)
    '''

    for direction in 'ruld':
        pushedIndex = board.dir2index(pl, index, direction)
        if pushedIndex >= 0 and not(board.free(pushedIndex)):
            newIndex = board.dir2index(pl, pushedIndex, direction)
            if newIndex < 0 or board.free(newIndex):
                yield Activation(pl, 'P', pushedIndex, newIndex, 'P' + direction)


def allT(pl, index, board):
    ''' Yields all legal activations of T
    (if the adjacent square is occupied and the arriving square is not occupied or is out)
    '''

    for direction in 'ruld':
        thrownIndex = board.dir2index(pl, index, direction)
        if thrownIndex >= 0 and not(board.free(thrownIndex)):
            newIndex = board.dir2index(pl, index, opposite(direction))
            if newIndex < 0 or board.free(newIndex):
                yield Activation(pl, 'T', thrownIndex, newIndex, 'T' + direction)


def allA(pl, index, board):
    ''' Yields all legal activations of A
    (if the all the square between A and the target are empty)
    '''

    for direction in 'ruld':
        adjIndex = board.dir2index(pl, index, direction)
        if adjIndex >= 0 and board.free(adjIndex):
            attractIndex = board.dir2index(pl, adjIndex, direction)
            while attractIndex >= 0 and board.free(attractIndex):
                attractIndex = board.dir2index(pl, attractIndex, direction)
            if attractIndex >= 0:
                yield Activation(pl, 'A', attractIndex, adjIndex, \
                        'A' + board.pos[attractIndex][1] + opposite(direction))


def allM(pl, index, board, ruld):
    ''' Yields all legal activations of M
    (if the adjacent square is occupied and the additional conditions from the mimed piece are fulfilled)
    '''

    adjIndexes = board.getAdjacents(index)
    for piece in set([board.pos[aC][1] for aC in adjIndexes]):
        if piece not in [' ', 'M']:
            if piece != 'H': newRuld = 'ruld'
            else: newRuld = ruld
            activations = filter(None, allActivations(pl, piece, index, board, newRuld))
            for activation in activations:
                activation.pl = pl
                activation.piece = 'M'
                activation.string = 'M' + activation.string
                yield activation


def allH(pl, index, board, ruld):
    ''' Yields all legal activations of H
    (if the adjacent square is occupied and the additional conditions from the hacked piece are fulfilled)
    '''

    for direction in ruld:
        adjIndex = board.dir2index(pl, index, direction)
        if adjIndex >= 0:
            piece = board.pos[adjIndex]
            if piece[1] != ' ':
                if piece[1] in ['H', 'M']: newRuld = ruld.replace(opposite(direction), '')
                else: newRuld = ruld
                activations = filter(None, allActivations(pl, piece[1], adjIndex, board, newRuld))
                for activation in activations:
                    activation.pl = pl
                    activation.piece = 'H'
                    activation.string = 'H' + direction + activation.string
                    yield activation

# PROBLEM
def discardCases(pl, board):
    ''' Yields two boards.
    In each board the opponent has discarded a different card.
    The destroyed list is updated.
    '''

    board2 = deepcopy(board)
    # 1-pl because it is the opponent's turn already
    board.players[1-pl].hand.pop()
    yield board
    board2.players[1-pl].hand.pop(0)
    yield board2


def allCases(pl, board):
    ''' Yields boards for each combination of cards in hand (for the opponent) and in the pile (for both players). '''

    l = len(board.players[1 - pl].pile + board.players[1 - pl].hand)
    myPiles = list(map(list, permutations(board.players[pl].pile)))
    hisHPs = list(map(list, permutations(board.players[1 - pl].pile + board.players[1 - pl].hand, l-2 if l > 2 else l)))
    for pile in myPiles:
        for hp in hisHPs:
            newBoard = deepcopy(board)
            newBoard.players[pl].pile = pile
            if l > 2:
                newBoard.players[1 - pl].hand = list(set(board.players[1 - pl].pile + board.players[1 - pl].hand) - set(hp))
                newBoard.players[1 - pl].pile = hp + [newBoard.players[1 - pl].hand.pop()]
            else:
                newBoard.players[1 - pl].hand = hp
                newBoard.players[1 - pl].pile = [newBoard.players[1 - pl].hand.pop()] if l == 2 else []
            yield newBoard


h = sum((list(range(x,x+4)) for x in range(4,0,-1)), [])
h[3] += 999993
h[2] += 5
h[6] += 5
h[7] += 5
h[1] += 2
h[5] += 2
h[9] += 2
h[10] += 2
h[11] += 2
h[0] -= 1
h[15] -= 1
boardValues = [(h1,-h2,0) for (h1,h2) in zip(h, reversed(h))]
# for x in range(4):
#     for value in boardValues[4*x:4*x+4]:
#         print(value, end = '')
#     print()

def evaluate(pl, board):
    # only 4x4 for now.
    # must change how to calculate destroyed
    destroyed = len(board.players[1].destroyed()) - len(board.players[0].destroyed())
    position = sum(squareValue[pos[0]] for (pos, squareValue) in zip(board.pos, boardValues))
    return (1 - 2*pl) * float(destroyed * Decimal(9)/Decimal(10) \
                              + position * Decimal(1)/Decimal(10))
