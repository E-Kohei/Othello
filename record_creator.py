## Create a new record from some record by transforming it.
## This is useful when the dataset of records is small or covers only
## limited case (e.g. all records start with 5-6)

import sys
import random, csv
import argparse

from othello import *
from othello_models import NumDiscMinMaxOthelloAgent
from othello_simulator import searchMove, getPlayerFromStateChange


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
    parser = argparse.ArgumentParser(
        description="Modify and create record file"
    )
    subparsers = parser.add_subparsers(
        dest="subparser_name",
        required=True,
        help="sub-command help"
    )
    
    # extend csv file
    parser_extend = subparsers.add_parser("extend",
        help="Create new records from others by transforming them")
    parser_extend.add_argument("infile", help="record file to extend")
    parser_extend.add_argument("outfile", help="output file")
    parser_extend.add_argument("--use-wth-format", action="store_true",
        help="use WTH csv file, which includes some additional data")
    
    # change csv file to WTH format
    parser_wth = subparsers.add_parser("towth",
        help="Change csv file to WTH format")
    parser_wth.add_argument("infile", help="record file to alter")
    parser_wth.add_argument("outfile", help="output file")
    
    # analyze records and add theorical score
    parser_theo = subparsers.add_parser("analyze",
        help="Analyze each record and add theorical score field")
    parser_theo.add_argument("infile", help="record file to analyze")
    parser_theo.add_argument("outfile", help="output file")
    parser_theo.add_argument("--header", type=int, default=1,
        help="line of header")
    parser_theo.add_argument("--depth", type=int, default=10,
            help="depth of analyze")
    
    args = parser.parse_args()
    
    if args.subparser_name == "extend":
        infilename = args.infile
        outfilename = args.outfile
        try:
            infile = open(infilename, mode='r')
            outfile = open(outfilename, mode='w')
            reader = csv.reader(infile)
            
            if args.use_wth_format:
                filedata = next(reader)
                header = next(reader)

                num_matches = int(filedata[2].split(':')[1]) * 4
                filedata[2] = f"number of matches : {num_matches}"
                outfile.writelines(",".join(filedata) + "\n")
                outfile.writelines(",".join(header) + "\n")

                for row in reader:
                    moves = row[7:]
                    all_moves_set = generateAllTransformedMoves(moves)
                    for new_moves in all_moves_set:
                        row2 = row[:7]
                        row2.extend(new_moves)
                        outfile.writelines(",".join(row2) + "\n")
            else:
                header = next(reader)
                outfile.writelines(",".join(header) + "\n")
                for row in reader:
                    moves = searchMove(row)
                    all_moves_set = generateAllTransformedMoves(moves)
                    for new_moves in all_moves_set:
                        row2 = row[:-60]
                        row2.extend(new_moves)
                        outfile.writelines(",".join(row2) + "\n")

        finally:
            infile.close()
            outfile.close()
            
    elif args.subparser_name == "towth":
        pass
    
    elif args.subparser_name == "analyze":
        infilename = args.infile
        outfilename = args.outfile
        try:
            infile = open(infilename, mode='r')
            outfile = open(outfilename, mode='w')
            reader = csv.reader(infile)
            
            for _ in range(args.header-1):
                next(reader)
            header = next(reader)
            dscore = header.index("dark_score")
            lscore = header.index("light_score")
            first_move = header.index("moves")
            header.insert(first_move, "light_theo_score")
            header.insert(first_move, "dark_theo_score")
            outfile.writelines(",".join(header) + "\n")
            
            depth = args.depth
            ai = NumDiscMinMaxOthelloAgent(depth=args.depth+1)
            game = Othello(8)
            for row in reader:
                moves = searchMove(row)
                all_states = getAllStatesFromRecord(moves)
                if len(all_states) <= 60 - args.depth:
                    dtheo_score = row[dscore]
                    ltheo_score = row[lscore]
                else:
                    game.state = all_states[60-depth]
                    player = getPlayerFromStateChange(
                        all_states[60-depth-1], all_states[60-depth]
                    )
                    if player == "dark_player":
                        ai.setOrder(LIGHT_PLAYER)
                        action, score = ai.findMaxInMins(game.state,
                                                         args.depth+1)
                        dtheo_score = int(64*(1-score))
                        ltheo_score = int(64*score)
                    else:
                        ai.setOrder(DARK_PLAYER)
                        action, score = ai.findMaxInMins(game.state,
                                                         args.depth+1)
                        dtheo_score = int(64*score)
                        ltheo_score = int(64*(1-score))
                row2 = row[:first_move]
                row2.extend([str(dtheo_score), str(ltheo_score)])
                row2.extend(moves)
                print(",".join(row2))
                outfile.writelines(",".join(row2) + "\n")
        
        finally:
            infile.close()
            outfile.close()
