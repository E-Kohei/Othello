## Create a new record from some record by transforming it.
## This is useful when the dataset of records is small or covers only
## limited case (e.g. all records start with 5-6)

import sys
import random, csv

from othello import *


# turn right
def rotate(move, state_size=8):
    if move == "---":
        return "---"
    half = state_size // 2
    nums = move.split("-")
    # map to xy coordinates
    row = int(nums[0])
    col = int(nums[1])
    x = col - half if col < half else col - half + 1
    y = row - half if row < half else row - half + 1
    # rotate!
    x2 = -y
    y2 = x
    row2 = y2 + half if y2 < 0 else y2 + half - 1
    col2 = x2 + half if x2 < 0 else x2 + half - 1
    return f"{row2}-{col2}"

# flip right-side-left
def fliplr(move, state_size=8):
    if move == "---":
        return "---"
    nums = move.split("-")
    return f"{nums[0]}-{state_size-1-int(nums[1])}"

# flip up-side-down
def flipud(move, state_size=8):
    if move == "---":
        return "---"
    nums = move.split("-")
    return f"{state_size-1-int(nums[0])}-{nums[1]}"

# create new moves from moves
def transformMoves(moves, transformations, state_size=8):
    if type(moves)  == str:
        moves = moves.split(",")
    result = moves.copy()
    
    for t in transformations:
        for i, move in enumerate(result):
            result[i] = t(move, state_size)
    return result

# create a new moves by transforming moves randomly
def transformMovesRandomly(moves, state_size=8, num_transforms=20):
    transformations = []
    for _ in range(num_transforms):
        transformations.append(random.choice([rotate, fliplr, flipud]))
    return transformMoves(moves, transformations, state_size=state_size)

# list up all set of moves
def generateAllTransformedMoves(moves, state_size=8):
    moves_set = []
    moves_set.append(transformMoves(moves, [fliplr, fliplr], state_size=state_size))
    moves_set.append(transformMoves(moves, [rotate, rotate], state_size=state_size))
    moves_set.append(transformMoves(moves, [fliplr, rotate], state_size=state_size))
    moves_set.append(transformMoves(moves, [fliplr, rotate, rotate, rotate], state_size=state_size))
    return moves_set


if __name__ == '__main__':
    infilename = sys.argv[1]
    outfilename = sys.argv[2]
    try:
        infile = open(infilename, mode='r')
        outfile = open(outfilename, mode='w')
        reader = csv.reader(infile)

        header1 = next(reader)
        header2 = next(reader)
        outfile.writelines(",".join(header1) + "\n")
        outfile.writelines(",".join(header2) + "\n")

        for row in reader:
            moves = row[5:]
            all_moves_set = generateAllTransformedMoves(moves)
            for new_moves in all_moves_set:
                row2 = row[:5]
                row2.extend(new_moves)
                outfile.writelines(",".join(row2) + "\n")

    finally:
        infile.close()
        outfile.close()
        
