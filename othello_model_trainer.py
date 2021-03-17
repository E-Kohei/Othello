import sys
import re
import csv
import argparse

import tensorflow as tf

from othello import *



def searchMove(data):
    for i, d in enumerate(data):
        if len(d) == 3 and \
           d[0].isdigit() and d[1] == '-' and d[2].isdigit():
           return data[i:i+60]
    return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Train neural network model by records"
    )
    parser.add_argument("-s", "--data-source", required=True,
                        help="csv file of records used for training")
    parser.add_argument("-m", "--model-file", required=True,
                        help="model file to train")
    parser.add_argument("-o", "--out-file",
                        help="output model file")
    
    parser.add_argument("--header", type=int, default=1,
                        help="line of header")
    parser.add_argument("--depth", type=int, default=24,
                        help="depth of theoretical score")
    parser.add_argument("--use-wth-format", action="store_true",
                        help="use WTH csv file, which includes some additional data")
    args = parser.parse_args()

    csvfilename = None
    inh5filename = None
    outh5filename = None
    
    if args.data_source:
        csvfilename = args.data_source
    if args.model_file:
        inh5filename = args.model_file
    if args.out_file:
        outh5filename = args.out_file
    else:
        # save the trained model to the same file
        outh5filename = args.model_file


    ## train model ##

    if inh5filename is not None:
        print(f"load model from infile: {inh5filename}")
        model = tf.keras.models.load_model(inh5filename)
    ##    # create new model
    ##    print("create new model")
    ##    model = tf.keras.models.Sequential([
    ##
    ##        tf.keras.layers.Dense(16, input_shape=(64,), activation="relu"),
    ##
    ##        #tf.keras.layers.Dropout(0.5),
    ##
    ##        tf.keras.layers.Dense(16, activation="relu"),
    ##
    ##        #tf.keras.layers.Dropout(0.5),
    ##
    ##        tf.keras.layers.Dense(2, activation="softmax")])
    ##
    ##    model.compile(
    ##        optimizer="adam",
    ##        loss="categorical_crossentropy",
    ##        metrics=["accuracy"]
    ##    )


    # read all data in from csv file
    print(f"read all data in from csv file: {csvfilename}")
    with open(csvfilename) as f:
        reader = csv.reader(f)
        
        data = []
        if args.use_wth_format:
            filedata = next(reader)
            depth = int(filedata[7].split(':')[1])
            print("depth of theorical score: ", depth)
            next(reader)

            for row in reader:
                try:
                    end_index = row.index("---")
                except ValueError:
                    end_index = 60
                dark_score = int(row[5])
                light_score = int(row[6])
                theo_score = int(row[4])
                num_disc = end_index + 4
                if num_disc <= 64 - depth:
                    # use real score
                    data.append({
                        "moves": row[7:],
                        # 1 if dark player won, else 0
                        "label": 1 if dark_score > light_score else 0
                    })
                else:
                    # use theorical score
                    data.append({
                        "moves": row[7:],
                        # 1 if dark player would win, else 0
                        "label": 1 if theo_score > 32 else 0
                    })
        else:
            depth = args.depth
            dscore = 4
            lscore = 5
            dtheoscore = None
            ltheoscore = None
            if args.header != 0:
                for _ in range(args.header-1):
                    next(reader)
                header = next(reader)
                try:
                    dscore = header.index("dark_score")
                    lscore = header.index("light_score")
                except ValueError:
                    pass
                try:
                    dtheoscore = header.index("dark_theo_score")
                    ltheoscore = header.index("light_theo_score")
                except:
                    pass
            
            if dtheoscore is not None:
                # use theoretical score for learning
                for row in reader:
                    dark_score = int(row[dscore])
                    light_score = int(row[lscore])
                    dark_theo_score = int(row[dtheoscore])
                    light_theo_score = int(row[ltheoscore])
                    moves = searchMove(row)
                    try:
                        end_index = moves.index("---")
                    except ValueError:
                        end_index = 60
                    num_disc = end_index + 4
                    if num_disc <= 64 - depth:
                        # use actual score
                        data.append({
                            "moves": moves,
                            # 1 if dark player won, else 0
                            "label": 1 if dark_score > light_score else 0
                        })
                    else:
                        # use theorical score
                        data.append({
                            "moves": moves,
                            # 1 if dark player would win, else 0
                            "label": 1 if dark_theo_score > light_theo_score else 0
                        })
            else:
                # use actual score for learning
                for row in reader:
                    dark_score = int(row[dscore])
                    light_score = int(row[lscore])
                    moves = searchMove(row)
                    data.append({
                        "moves": moves,
                        "label": 1 if dark_score > light_score else 0
                    })
        num_matches = len(data)


    # train neural network
    print("train neural network")

    x_train_early = []
    y_train_early = []
    x_train_late = []
    y_train_late = []
    # all states extracted by the records will be too large,
    # so separate data into some groups and train the model
    batch_size = 1000
    for i in range(num_matches//batch_size + 1):
        print(f"training with {i}th group")
        for j in range(batch_size*i, min(num_matches, batch_size*(i+1))):
            states = getAllStatesFromRecord(data[j]["moves"], False, True, True)
            num_blank = states[-1].tolist().count(0)
            label = data[j]["label"]
            
            if -depth + num_blank > 0:
                # the game was over before depth
                print("the game was over before depth")
                x_train_late.extend(states)
                for _ in range(len(states)):
                    y_train_late.append( (label, 1-label) )
            else:
                # otherwise, separate training data
                x_train_early.extend(states[:60-depth])
                for _ in range(60-depth):
                    y_train_early.append( (label, 1-label) )
                x_train_late.extend(states[60-depth:])
                for _ in range(depth-num_blank):
                    y_train_late.append( (label, 1-label) )
        # Since early part is less informative, we make the model
        # learn much from the late part
        model.fit(np.array(x_train_early), np.array(y_train_early), epochs=10)
        model.fit(np.array(x_train_late), np.array(y_train_late), epochs=20)
        x_train_early.clear()
        y_train_early.clear()
        x_train_late.clear()
        y_train_late.clear()


    ## save model
    print(f"save model to outfile: {outh5filename}")
    model.save(outh5filename)
