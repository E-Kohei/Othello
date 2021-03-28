import sys
#import winsound
import time
import random

import tensorflow as tf

from othello import *
from othello_models import *
  

if __name__ == "__main__":
    
    model_files = {
        "A" : "OthelloAIModel_64_2.h5",
        "B" : "OthelloAIModel_64_16_2.h5",
        "C" : "OthelloAIModel_64_16_16_2.h5",
        "D" : "OthelloAIModel_64_16_16_16_2.h5",
        "C2" : "OthelloAIModel_64_16_16_2_dropout.h5",
        "D2" : "OthelloAIModel_64_16_16_16_2_dropout.h5",
        "EC" : "OthelloAIModel_64_16_16_2_earlyimproved.h5",
        "EC2" : "OthelloAIModel_64_16_16_2_dropout_earlyimproved.h5",
        "L" :   "OthelloAIModel_64_16_16_2_dropout_learning.h5",
        "NL":   "OthelloAIModel_64_16_16_2_dropout_learning.h5",
    }

    if len(sys.argv) < 3:
        raise SyntaxError("give two players!")

    # determine first player
    if sys.argv[1] == "CAI":
        first = CornerWeightedMinMaxOthelloAgent(None, depth=6)
        first.name = "Corner weighted AI"
    elif sys.argv[1] == "Hybrid":
        first = HybridOthelloAgent(None, depth=4,
                                   model_file="OthelloAIModel_64_16_16_2_dropout.h5")
        first.name = sys.argv[1]
    elif sys.argv[1] in model_files.keys():
        first = ModelMinMaxOthelloAgent(None, depth=4,
                                        model_file=model_files[sys.argv[1]])
        first.name = sys.argv[1]
    elif sys.argv[1][:5] == "file:":
        filename = sys.argv[1][5:]
        first = ModelMinMaxOthelloAgent(None, depth=4,
                                        model_file=filename)
        first.name = sys.argv[1]
    else:
        first = PlayerYou(name=sys.argv[1])
    if first.name == "L" or sys.argv[1][:5] == "file:":
        first.isLearning = True

    # determine second player
    if sys.argv[2] == "CAI":
        second = CornerWeightedMinMaxOthelloAgent(None, depth=4)
        second.name = "Corner weighted AI"
    elif sys.argv[2] == "Hybrid":
        second = HybridOthelloAgent(None, depth=4,
                                   model_file="OthelloAIModel_64_16_16_2_dropout.h5")
        second.name = sys.argv[2]
    elif sys.argv[2] in model_files.keys():
        second = ModelMinMaxOthelloAgent(None, depth=4,
                                        model_file=model_files[sys.argv[2]])
        second.name = sys.argv[2]
    elif sys.argv[2][:5] == "file:":
        filename = sys.argv[2][5:]
        second = ModelMinMaxOthelloAgent(None, depth=4,
                                         model_file=filename)
        second.name = sys.argv[2]
    else:
        second = PlayerYou(name=sys.argv[2])
    if second.name == "L" or sys.argv[2][:5] == "file:":
        second.isLearning = True

    # start game
    game = Othello(8, first, second)
    game.play()

    # if Learning AI losed, save trained AI model
    if first.name == "L":
        doSave = input("Save the trained model? yes(y): ")
        if doSave[0] == 'y':
            print("save the model of learning AI")
            first.saveModel("OthelloAIModel_64_16_16_2_dropout_learning.h5")
        else:
            print("don't save the model of learning AI")
    if second.name == "L":
        doSave = input("Save the trained model? yes(y): ")
        if doSave[0] == 'y':
            print("save the model of learning AI")
            second.saveModel("OthelloAIModel_64_16_16_2_dropout_learning.h5")
        else:
            print("don't save the model of learning AI")
