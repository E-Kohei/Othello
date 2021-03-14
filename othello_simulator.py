import sys
import csv
import argparse

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox

from othello import *
from othello_models import ModelMinMaxOthelloAgent



def searchMove(data):
    for i, d in enumerate(data):
        if len(d) == 3 and \
           d[0].isdigit() and d[1] == '-' and d[2].isdigit():
           return data[i:i+60]
    return None

def getPlayerFromStateChange(before, after):
    num_black_before = before.flatten().tolist().count(BLACK)
    num_black_after = after.flatten().tolist().count(BLACK)
    if num_black_before < num_black_after:
        return "dark_player"
    elif num_black_before > num_black_after:
        return "light_player"
    else:  # maybe same state
        return None
        

def drawButton(box, text):
    x0 = box.x0
    x1 = box.x1
    y0 = box.y0
    y1 = box.y1
    plt.axvline(x0, ymin=y0, ymax=y1, color="black")
    plt.axvline(x1, ymin=y0, ymax=y1, color="black")
    plt.axhline(y0, xmin=x0, xmax=x1, color="black")
    plt.axhline(y1, xmin=x0, xmax=x1, color="black")
    plt.text((x0+x1)/2, (y0+y1)/2, s=text,
             horizontalalignment='center',
             verticalalignment='center')

def update_discs(index, state,
    black_scat, white_scat, move_text, score_text):
    
    bpoints = []
    wpoints = []
    bx = []; by = []
    wx = []; wy = []
    for i in range(8):
        for j in range(8):
            if state[i,j] == BLACK:
                bpoints.append( (0.15 + j*0.1, 0.9 - i*0.1) )
            elif state[i,j] == WHITE:
                wpoints.append( (0.15 + j*0.1, 0.9 - i*0.1) )
    bP = np.array(bpoints)
    wP = np.array(wpoints)
    black_scat.set_offsets(bP)
    white_scat.set_offsets(wP)
    move_text.set_text(f"move: {index}")
    score_text.set_text(f"score: {Othello.smScore(state)}")
    
    plt.draw()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Simulate othello game from record"
    )
    srcGroup = parser.add_mutually_exclusive_group(required=True)
    srcGroup.add_argument("-f", "--csvfile",
                           help="csv file with records")
    parser.add_argument("-l", "--line",
                        type=int,
                        default=2,
                        help="line of record to simulate")
    parser.add_argument("-p", "--player-columns",
                        type=int,
                        nargs=2,
                        help="column of players' name")
    srcGroup.add_argument("-s", "--string",
                          help="record string to simulate")

    parser.add_argument("-m", "--model-file",
                        help="model file to evaluate the game state")
    parser.add_argument("-g", "--show-graph",
                        action="store_true",
                        help="show a graph of evaluation by AI")
    parser.add_argument("-v", "--visualize",
                        action="store_true",
                        help="show the game in GUI mode")

    args = parser.parse_args()

    moves = None
    players = {
        "dark_player" : "dark player",
        "light_player" : "light player"
    }
    if args.csvfile:
        with open(args.csvfile) as f:
            reader = csv.reader(f)

            for _ in range(args.line-1):
                next(reader)

            data = next(reader)
            moves = searchMove(data)
            if args.player_columns:
                players["dark_player"] = data[args.player_columns[0]]
                players["light_player"] = data[args.player_columns[1]]
    elif args.string:
        moves = args.string.split(",")

    if moves is None:
        raise Exception("Invalid record!")
        
    all_states = getAllStatesFromRecord(moves)
    first = np.full((8,8), BLANK, dtype=np.int16)
    first[3,3] = first[4,4] = WHITE
    first[4,3] = first[3,4] = BLACK
    all_states.insert(0, first)
    game = Othello(8)
    
    if args.model_file:
        model = ModelMinMaxOthelloAgent(model_file=args.model_file)
        # evaluate the state in sight of the dark player
        model.setOrder(0)
    
    if args.show_graph:
        plt.figure()
        xs = np.array([i for i in range(len(all_states))])
        scores = []
        for state in all_states:
            score = Othello.smScore(state)
            scores.append(score[0] / (score[0] + score[1]))
        plt.plot(xs, scores, color="green", label="score")
        plt.title("Score")
        if args.model_file:
            evals = [model.evaluate(state) for state in all_states]
            plt.plot(xs, evals, color="red", label="AI")
            plt.title("Score and Evaluation by AI")
        plt.xlabel("moves")
        plt.ylabel("percentage of black")
        plt.legend()
        plt.ylim(0.0, 1.0)


    if args.visualize:
        # visualize othello game
        current_index = 0
        fig = plt.figure(figsize=(6,6), facecolor="white")
        ax = fig.add_axes([0, 0, 1, 1], aspect=1.0)
        ax.set_xlim(0,1)
        ax.set_xticks([])
        ax.set_ylim(0,1)
        ax.set_yticks([])
        for i in range(9):
            plt.axhline(y=0.15+0.1*i, xmin=0.1, xmax=0.9, c="black")
            plt.axvline(x=0.1+0.1*i, ymin=0.15, ymax=0.95, c="black")
        bnext = Bbox([[0.7, 0.05],[0.8, 0.125]])
        bprev = Bbox([[0.81, 0.05],[0.91, 0.125]])
        drawButton(bprev, "Prev")
        drawButton(bnext, "Next")
        bscat = plt.scatter([0.45, 0.55],[0.5, 0.6],s=500,
                            facecolors="black", edgecolors="black",
                            lw=1.0)
        wscat = plt.scatter([0.45, 0.55],[0.6, 0.5],s=500,
                            facecolors="None", edgecolors="gray",
                            lw=1.0)
        move_text = plt.text(0.1, 0.075, f"move: 0")
        score_text = plt.text(0.1, 0.025, f"score: (2,2)")
        players_text = plt.text(0.5, 0.975,
            f"{players['dark_player']} vs {players['light_player']}",
            horizontalalignment='center', verticalalignment='center')
        
        def onclick(event):
            global current_index, all_states, bscat, wscat
            global move_text, score_text
            global bprev, bnext
            px0 = bprev.x0; px1 = bprev.x1
            py0 = bprev.y0; py1 = bprev.y1
            nx0 = bnext.x0; nx1 = bnext.x1
            ny0 = bnext.y0; ny1 = bnext.y1
            x = event.xdata
            y = event.ydata
            if x is None or y is None:
                return
            elif px0 < x < px1 and py0 < y < py1:
                # change to previous state
                if current_index == 0:
                    return
                else:
                    current_index -= 1
                    state = all_states[current_index]
                    update_discs(current_index, state, bscat, wscat,
                                 move_text, score_text)
            elif nx0 < x < nx1 and ny0 < y < ny1:
                # change to next state
                if current_index == len(all_states) - 1:
                    return
                else:
                    current_index += 1
                    state = all_states[current_index]
                    update_discs(current_index, state, bscat, wscat,
                                 move_text, score_text)
        plt.connect('button_press_event', onclick)
        
    else:
        # print out all states into stdout
        for i,s in enumerate(all_states):
            game.state = s
            if i == 0:
                print("Start of the game")
                print(game)
            else:
                player = players[getPlayerFromStateChange(
                    all_states[i-1], s
                )]
                print(f"{i}th turn: {player} chose {moves[i-1]}")
                print(game)
        print(f"score: {game.score()}")


    # if you use plt, show all windows
    if args.show_graph or args.visualize:
        plt.show()
