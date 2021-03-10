import sys
import csv
import argparse

from othello import *


def searchMove(data):
    for i, d in enumerate(data):
        if len(d) == 3 and \
           d[0].isdigit() and d[1] == '-' and d[2].isdigit():
           return data[i:i+60]
    return None

parser = argparse.ArgumentParser("Simulate othello game from record")
fileGroup = parser.add_argument_group()
strGroup = parser.add_argument_group()

fileGroup.add_argument("-f", "--csvfile",
                       help="csv file with records")
fileGroup.add_argument("-l", "--line",
                       type=int,
                       help="line of record to simulate")

strGroup.add_argument("-s", "--string",
                      help="record string to simulate")

args = parser.parse_args()

moves = None
if args.csvfile:
    with open(args.csvfile) as f:
        reader = csv.reader(f)

        for _ in range(args.line-1):
            next(reader)

        data = next(reader)
        moves = searchMove(data)
elif args.string:
    moves = args.string.split(",")

if moves is None:
    raise Exception("Invalid record!")

for i, m in enumerate(moves):
    if m == "---":
        # end of the game
        break
    else:
        splitted = m.split('-')
        r = int(splitted[0])
        c = int(splitted[1])
        moves[i] = (r,c)


game = Othello(8)

DARK_PLAYER = 0
LIGHT_PLAYER = 1

# simulate moves
next_mover = DARK_PLAYER
for i, m in enumerate(moves):
    if m == "---":
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
