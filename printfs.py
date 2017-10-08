from os import system
from random import sample

def checkNumber(string):

    number = input(string)
    if number.isdigit(): return eval(number)
    else: print('This is not a valid number!')


def type_of_game():
    ''' First it asks for the size of the board,
    then for the number of pieces for each player
    and finally for which pieces to exclude.
    It is possible exclude random pieces by not typing anything.
    '''

#    size = 0
#    while size not in [4,5]:
#        check = checkNumber('On which board are we going to play, 4 or 5? ')
#        if check: size = check
    size = 4

    n = 0
    letters = set('JDHPTAMS')
    while not(4 <= n <= 8):
        check = checkNumber('With how many pieces are we going to play (min 4, max 8)? ')
        if check: n  = check

    if n == 8: return letters, size

    exclude = '0'
    while len(exclude) > 8-n or any(l not in letters for l in exclude):
        exclude = set(input('Which {} piece(s) to exclude? '.format(8-n)).upper())
    exclude |= set(sample(letters - exclude, 8-n-len(exclude)))

    # pc = None
    # while pc is None:
    #     check = input("Which player should the computer help? (1, 2 or BOTH) ")
    #     if check == "1":
    #         pc = 0
    #     elif check == "2":
    #         pc = 1
    #     elif check == "BOTH":
    #         pc = 2
    #     else:
    #         print("The answer must be 1, 2 or BOTH!")

    return letters - exclude, size, 2 # pc


def printGame(pl, board):
    ''' First it prints information regarding the opponent,
    then it prints the board and finally it prints information about the player
    '''

    system('clear')
    print("It's the turn of the {} player!\n".format(board.players[pl].strcolor))
    print('The {} player has {} pieces in his hand, {} on the pile, {} on the board.'.format(board.players[1-pl].strcolor,len(board.players[1-pl].hand),len(board.players[1-pl].pile), len(board.players[1-pl].placed)))
    print("{} pieces destroyed: {}\n".format(board.players[1-pl].strcolor, board.players[1-pl].show(board.players[1-pl].destroyed())))
    show(pl, board)
    print('\nYour hand: ',board.players[pl].show(board.players[pl].hand))
    print('You have {} pieces in your pile.'.format(len(board.players[pl].pile)))
    print('Your destroyed pieces: ', board.players[pl].show(board.players[pl].destroyed()))
    print('You have already performed an action with: ', board.players[pl].show(board.players[pl].played))


def show(pl, board):
    ''' Prints the board line by line, including extra space, coordinates and 7x3-area squares. '''

    #must improve
    bg2 = paint(3,'  ')
    bg9 = paint(3,'         ')
    bgline = paint(3,' '*(56-9*(5-board.size)))
    rPosition = board.pos[::1-2*pl]
    rPosition = [rPosition[x:y] for (x,y) in [(0,4),(4,8),(8,12),(12,16)]]
    rNumbers = list(map(lambda number: paint(3, '    '+str(number)+'    '),range(1,board.size+1)))[::2*pl-1]
    rLetters = list(map(lambda x: paint(3,'   '+x+'   '), 'abcde'[:board.size]))[::1-2*pl]
    print(bgline + '\n' + bgline)
    for (number, line) in zip(rNumbers, rPosition):
        print(bg9 + printLine(line, False, bg2))
        print(number + printLine(line, True, bg2))
        print(bg9 + printLine(line, False, bg2))
        print(bgline)
    print(bg9 + bg2.join(rLetters) + bg2*2)
    print(bgline)


def printLine(line, letter, bg2):
    ''' Returns a colored string, component of the board.
    If it belongs to the central line of the board-line, it adds the piece
    '''

    if letter: return bg2.join([paint(color,'   '+square+'   ') for (color,square) in line]) + 2*bg2
    else: return bg2.join([paint(color,'       ') for (color,square) in line]) + 2*bg2


def paint(color, obj):
    ''' Paints the object according with the color-number:
    - 3 is the color of the board (purpleish)
    - 2 is the color of the squares when empty (white)
    - 1 is the color of the second player (black)
    - 0 is the color of first player (red)
    '''

    if color == 3: return '\x1b[37;45m' + obj + '\x1b[0m'
    elif color == 2: return '\x1b[30;47m' + obj + '\x1b[0m'
    elif color == 0: return '\x1b[37;41m' + obj + '\x1b[0m'
    else: return '\x1b[31;40m' + obj + '\x1b[0m'


def printAllActions(pl, actions):
    ''' Prints all the actions assigning to each of them a number '''

    print('Possible actions:', end = '')
    letters = []
    for number, action in enumerate(actions):
        if action.piece in letters:
            print(',', paint(pl, str(number)), action, end = '')
        else:
            print()
            letters.append(action.piece)
            print(letters[-1], ':', paint(pl, str(number)), action, end = '')
