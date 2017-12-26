from os import system

from bsboard import Board
from engine import Engine
from actions import TurnFinisher
import printfs as p

class Game:

    def __init__(self, pieces, size, pc):
        ''' Creates the board and the engine '''

        self.board = Board(size, pieces)
        self.engine = Engine()
        self.pc = pc
        # to go backwards
        self.history = []
        self.back = False


    def startGame(self):
        ''' Makes both players draw a card and makes the first player start its turn '''

        self.board.players[0].draw()
        self.board.players[0].draw()
        self.board.players[1].draw()
        self.history.append([])
        self.Turn(0)


    def Turn(self, pl):
        ''' The turn is divided in three parts for clarity '''

        self.startTurn(pl)
        while self.board.winner is None and self.engine.actions:
            if not self.playTurn(pl): break
        self.endTurn(pl)


    def startTurn(self, pl):
        ''' The player starts, checks if the enemy has committed suicide or
        if he has suicided a piece by letting it surrounded. After caching all the legal actions,
        if there are no legal actions the opponent is proclaimed victorious,
        otherwise the engine searches for the best play
        '''

        self.engine.updateActions(pl, self.board)
        if not self.engine.actions:
            self.board.winner = 1 - pl
        else:
            if self.pc == 2 or pl == self.pc:
                self.engine.worstCase(pl, self.board, 2)


    def playTurn(self, pl):
        ''' The game current status according to player pl is printed,
        as well as all the possible first actions that can be performed by the player.
        While the player doesn't abandon, doesn't end the turn and still has moves to do,
        the program waits for the input.
        If the player wants to end the turn without making any action or
        if the input doesn't correspond to any legal action, a warning message is sent.
        '''

        p.printGame(pl, self.board)
        print(self.history)
        if self.pc == 2 or pl == self.pc:
            print(self.engine.bestPlay)
        p.printAllActions(pl, self.engine.actions)
        while True:
            action = input('\nInput action: ')
            if action:
                if action == 'end':
                    if self.board.players[pl].played: return False
                    else: print('Warning, you must perform at least an action to end the turn!')
                elif action == 'abandon':
                    self.board.winner = 1 - pl
                    return False
                elif action.isdigit() and 0 <= int(action) < len(self.engine.actions):
                    self.engine.actions[int(action)].execute(self.board)
                    self.history[-1].append(self.engine.actions[int(action)])
                    self.engine.updateActions(pl, self.board)
                    return True
                elif action.upper() == "B":
                    if len(self.history) > 1:
                        if self.history[-1]:
                            self.history[-1].pop().goBack(self.board)
                            self.engine.updateActions(pl, self.board)
                            return True
                        else:
                            del self.history[-1]
                            # 1st time undoes the FinishTurner
                            # 2nd time undoes the Action
                            self.history[-1].pop().goBack(self.board)
                            self.history[-1].pop().goBack(self.board)
                            self.back = True
                            return False
                    else:
                        print('Warning, you can\'t go backwards anymore!')
                else:
                    print('Warning, that action doesn\'t exist!')

    def endTurn(self, pl):
        ''' if there is a winner, the game is ended,
        otherwise, after cleaning the played list of the pl player and
        discarding if necessary, the opponent player's turn is started.
        '''

        if self.board.winner is not None:
            system('clear')
            print('\nThe ' + self.board.winnerString() + ' player wins the game!\n')
            p.show(pl, self.board)
        else:
            if self.back:
                self.back = False
            else:
                self.history[-1].append(TurnFinisher(pl))
                self.history[-1][-1].execute(self.board)
                self.history.append([])
            self.Turn(1-pl)

if __name__ == '__main__':
    # Ask for input: # of pieces, which pieces, which board.
    pieces, size, pc = p.type_of_game()

    # Create game and make it start
    game = Game(pieces, size, pc)
    game.startGame()
