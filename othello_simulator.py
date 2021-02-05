import csv

from othello import *


def normalizeDisc(disc):
    if disc == BLANK:
        return 0
    elif disc == WHITE:
        return -1
    else:       # black
        return 1

# simulate game and get all states from record
def getAllStatesFromRecord(record):
    states = []
    moves = []
    for i, m in enumerate(record):
        splitted = m.split('-')
        r = int(splitted[0]) - 1
        c = int(splitted[1]) - 1
        moves.append( (r,c) )
    game = Othello(8)

    DARK_PLAYER = 0
    LIGHT_PLAYER = 1

    vfunc = np.vectorize(normalizeDisc, otypes=[np.int16])

    # simulate moves
    next_mover = DARK_PLAYER
    for i, m in enumerate(moves):
        if m == (-1,-1):
            # end of the game
            break
        
        if next_mover == DARK_PLAYER:
            if Othello.isAvailablePosition(game.state, m[0], m[1], BLACK, WHITE):
                game.takeAction(m, DARK_PLAYER)
                next_mover = LIGHT_PLAYER
            elif Othello.isAvailablePosition(game.state, m[0], m[1], WHITE, BLACK):
                # This case means that the move m is not one of dark-player
                # but one of light-player because dark-player had no choice
                # but to pass his turn.
                game.takeAction(m, LIGHT_PLAYER)
                next_mover = DARK_PLAYER
            else:
                # unexpcted behavior
                raise ActionError("This move is invalid for both players!")
        elif next_mover == LIGHT_PLAYER:
            if Othello.isAvailablePosition(game.state, m[0], m[1], WHITE, BLACK):
                game.takeAction(m, LIGHT_PLAYER)
                next_mover = DARK_PLAYER
            elif Othello.isAvailablePosition(game.state, m[0], m[1], BLACK, WHITE):
                # This case means that the move m is not one of light-player
                # but one of dark-player because light-player had no choice
                # but to pass his turn.
                game.takeAction(m, DARK_PLAYER)
                next_mover = LIGHT_PLAYER
            else:
                # unexpcted behavior
                raise ActionError("This move is invalid for both players!")
        states.append(vfunc(game.getState().flatten()))
    return states


if __name__ == "__main__":
    
    with open("othello_data\\WTH_2015.csv") as f:
        reader = csv.reader(f)
        next(reader)
        next(reader)

        skip = 881

        for _ in range(skip):
            next(reader)

        data = next(reader)
        moves = data[5:]
        score = data[3]

    for i, m in enumerate(moves):
        splitted = m.split('-')
        r = int(splitted[0]) - 1
        c = int(splitted[1]) - 1
        moves[i] = (r,c)


    game = Othello(8)

    DARK_PLAYER = 0
    LIGHT_PLAYER = 1

    # simulate moves
    next_mover = DARK_PLAYER
    for i, m in enumerate(moves):
        if m == (-1,-1):
            # end of the game
            break
        
        if next_mover == DARK_PLAYER:
            if Othello.isAvailablePosition(game.state, m[0], m[1], BLACK, WHITE):
                print(f"{i+1}th move: dark player chose {m}")
                game.takeAction(m, DARK_PLAYER)
                next_mover = LIGHT_PLAYER
            elif Othello.isAvailablePosition(game.state, m[0], m[1], WHITE, BLACK):
                # This case means that the move m is not one of dark-player
                # but one of light-player because dark-player had no choice
                # but to pass his turn.
                print("dark-player passed his turn.\n")
                print(f"{i+1}th move: light player chose {m}")
                game.takeAction(m, LIGHT_PLAYER)
                next_mover = DARK_PLAYER
            else:
                # unexpcted behavior
                raise ActionError("This move is invalid for both players!")
        elif next_mover == LIGHT_PLAYER:
            if Othello.isAvailablePosition(game.state, m[0], m[1], WHITE, BLACK):
                print(f"{i+1}th move: light player chose {m}")
                game.takeAction(m, LIGHT_PLAYER)
                next_mover = DARK_PLAYER
            elif Othello.isAvailablePosition(game.state, m[0], m[1], BLACK, WHITE):
                # This case means that the move m is not one of light-player
                # but one of dark-player because light-player had no choice
                # but to pass his turn.
                print("light-player passed his turn.\n")
                print(f"{i+1}th move: dark player chose {m}")
                game.takeAction(m, DARK_PLAYER)
                next_mover = LIGHT_PLAYER
            else:
                # unexpcted behavior
                raise ActionError("This move is invalid for both players!")

        print(game)
        print()

    print(f"score: {game.score()}")
    print(score)
