## Create a new record from some record by transforming it.
## This is useful when the dataset of records is small or covers only
## limited case (e.g. all records start with 5-6)

import sys
import random, csv
import argparse
import subprocess

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
    parser_extend.add_argument("--header-line", type=int, default=1,
                               help="line of header")
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
    parser_theo.add_argument("--header-line", type=int, default=1,
                             help="line of header")
    parser_theo.add_argument("--depth", type=int, default=10,
                             help="depth of analyze")
    parser_theo.add_argument("--use-theoscore", action="store_true",
                             help="use theoretical score provided in the file")
    
    args = parser.parse_args()
    
    if args.subparser_name == "extend":
        infilename = args.infile
        outfilename = args.outfile
        try:
            infile = open(infilename, mode='r')
            outfile = open(outfilename, mode='w', newline='')
            
            if args.use_wth_format:
                filedata = infile.readline().split(',')
                num_matches = int(filedata[2].split(':')[1]) * 4
                filedata[2] = f"number of matches : {num_matches}"
                outfile.writelines(",".join(filedata))
            else:
                if args.header_line != 1:
                    for _ in range(args.header_line-1):
                        skip = infile.readline()
                        outfile.writelines(skip)
                    
            reader = csv.DictReader(infile)
            header = reader.fieldnames
            writer = csv.DictWriter(outfile, header, lineterminator='\n')
            writer.writeheader()
            for row in reader:
                moves = [row[f"{i}"] for i in range(60)]
                all_moves_set = generateAllTransformedMoves(moves)
                for new_moves in all_moves_set:
                    row2 = row.copy()
                    for i in range(60):
                        row2[f"{i}"] = new_moves[i]
                    writer.writerow(row2)

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
            outfile = open(outfilename, mode='w', newline='')
            depth = args.depth
            
            if args.header_line != 1:
                for _ in range(args.header_line-1):
                    skip = infile.readline()
                    outfile.writelines(skip)
            
            reader = csv.DictReader(infile)
            header = reader.fieldnames
            for i in range(60):
                header.append( f"l{i}" )
            writer = csv.DictWriter(outfile, header, lineterminator='\n')
            writer.writeheader()
            
            if args.use_theoscore:
                for row in reader:
                    theo_scores = ["-" for _ in range(60)]
                    theo_score = int(row["theoretical_score"])
                    if theo_score > 32:
                        for i in range(depth):
                            theo_scores[-i-1] = 1
                    else:
                        for i in range(depth):
                            theo_scores[-i-1] = 0
                    row2 = row.copy()
                    for i in range(60):
                        row2[f"l{i}"] = theo_scores[i]
                    writer.writerow(row2)
            else:
                row_num = 1
                for row in reader:
                    theo_scores = ["-" for _ in range(60)]
                    moves = [row[f"{i}"] for i in range(60)]
                    # exclude the terminal state because theoretical score is
                    # meaningless for the terminal state
                    states = getAllStatesFromRecord(moves)
                    length = len(states)
                    for i in range(length-1):
                        if 60 - i <= depth:
                            flattened = states[i].flatten().tolist()
                            stateString = ",".join([str(d) for d in flattened])
                            order = getPlayerFromStateChange(states[i], states[i+1])
                            result = subprocess.run(["./cpp/othello", stateString,
                                                     str(order), "-2"],
                                                    capture_output=True)
                            action_score = result.stdout.decode()[:-1].split(',')
                            score = float(action_score[2])
                            if score > 0.5:
                                theo_scores[i] = 1
                            elif score < 0.5:
                                theo_scores[i] = 0
                            else:
                                theo_scores[i] = 0.5
                    row2 = row.copy()
                    for i in range(60):
                        row2[f"l{i}"] = theo_scores[i]
                    writer.writerow(row2)
                    print(f"row {row_num} analyzed")
                    row_num += 1
        
        finally:
            infile.close()
            outfile.close()
