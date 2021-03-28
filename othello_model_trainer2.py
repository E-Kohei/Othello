import csv
import argparse

import tensorflow as tf

from othello import *



def createData(data, moves, labels, epochs):
    # exclude the terminal state
    all_states = getAllStatesFromRecord(moves, False, True, True)[:-1]
    length = len(all_states)
    for i in range(length):
        data.append( (all_states[i], labels[i], epochs[i]) )

def createDataByPlayer(dark_data, light_data, moves, labels, epochs):
    dark_states = []
    light_states = []
    all_states = getAllStatesFromRecord(moves, False, True, True)
    length = len(all_states)
    next_mover = DARK_PLAYER
    for i in range(length-1):
        actual_mover = getPlayerFromStateChange(all_states[i], all_states[i+1], True)
        if next_mover == actual_mover == DARK_PLAYER:
            dark_data.append( (all_states[i], labels[i], epochs[i]) )
            next_mover = LIGHT_PLAYER
        elif next_mover == actual_mover == LIGHT_PLAYER:
            light_data.append( (all_states[i], labels[i], epochs[i]) )
            next_mover = DARK_PLAYER
        else:
            # either of players passed the turn
            dark_data.append( (all_states[i], labels[i], epochs[i]) )
            light_data.append( (all_states[i], labels[i], epochs[i]) )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Train neural network model by records"
    )
    parser.add_argument("-s", "--data-source", required=True,
                        help="csv file of records used for training")
    parser.add_argument("-m", "--model-file", required=True, nargs='+',
                        help="model files to train")
    parser.add_argument("-o", "--out-file", nargs='+',
                        help="output model files")
    
    parser.add_argument("--header-line", type=int, default=1,
                        help="line of header")
    parser.add_argument("--use-theoscore", action="store_true",
                        help="use file with theoretical scores")
    parser.add_argument("--separate-dark-and-light", action="store_true",
                        help="train models for dark and light player respectively")
    parser.add_argument("--order-included-model", action="store_true",
                        help="train a model whose input includes order of action")
    args = parser.parse_args()

    csvfilename = None
    
    inh5filename = None
    dark_inh5filename = None
    light_inh5filename = None
    
    outh5filename = None
    dark_outh5filename = None
    light_outh5filename = None
    
    if args.data_source:
        csvfilename = args.data_source
    if args.separate_dark_and_light:
        dark_inh5filename = args.model_file[0]
        light_inh5filename = args.model_file[1]
        if args.out_file:
            dark_outh5filename = args.out_file[0]
            light_outh5filename = args.out_file[1]
        else:
            dark_outh5filename = dark_inh5filename
            light_outh5filename = light_inh5filename
    else:
        inh5filename = args.model_file[0]
        if args.out_file:
            outh5filename = args.out_file[0]
        else:
            # save the trained model to the same file
            outh5filename = inh5filename


    ## retrieve data ##

    if args.separate_dark_and_light:
        print(f"load dark model from infile: {dark_inh5filename}")
        print(f"load light model from infile: {light_inh5filename}")
        dark_model = tf.keras.models.load_model(dark_inh5filename)
        light_model = tf.keras.models.load_model(light_inh5filename)
    else:
        print(f"load model from infile: {inh5filename}")
        model = tf.keras.models.load_model(inh5filename)


    # read all data in from csv file
    print(f"read all data in from csv file: {csvfilename}")
    with open(csvfilename) as f:
        
        if args.separate_dark_and_light:
            dark_data = []
            light_data = []
        else:
            data = []
            
        if args.header_line != 1:
            for _ in range(args.header_line-1):
                f.readline()
        reader = csv.DictReader(f)
        
        for row in reader:
            dark_score = int(row["dark_score"])
            light_score = int(row["light_score"])
            match_score = 0
            if dark_score > light_score:
                match_score = 1
            elif dark_score < light_score:
                match_score = 0
            else:
                match_score = 0.5
            moves = [row[f"{i}"] for i in range(60)]
            labels = []
            epochs = []
            if args.use_theoscore:
                for i in range(60):
                    try:
                        score = float(row[f"l{i}"])
                        labels.append( (score, 1-score) )
                        epochs.append(20)
                    except:
                        labels.append( (match_score, 1-match_score) )
                        epochs.append(10)
            else:
                for _ in range(60):
                    labels.append( (match_score, 1-match_score) )
                    epochs.append(10)
            
            if args.separate_dark_and_light:
                createDataByPlayer(dark_data, light_data, moves, labels, epochs)
            else:
                createDataByPlayer(data, moves, labels, epochs)


    # train neural network
    print("train neural network")

    # all states extracted by the records will be too large,
    # so separate data into some groups and train the model
    batch_size = 65536
    
    if args.separate_dark_and_light:
        num_dark_states = len(dark_data)
        for i in range(num_dark_states//batch_size + 1):
            print(f"training dark model with {i}th group")
            
            start = i * batch_size
            end = (i+1) * batch_size
            dark_x_train_weak = [t[0] for t in dark_data[start:end] if t[2] == 10]
            dark_x_train_strong = [t[0] for t in dark_data[start:end] if t[2] == 20]
            dark_y_train_weak = [t[1] for t in dark_data[start:end] if t[2] == 10]
            dark_y_train_strong = [t[1] for t in dark_data[start:end] if t[2] == 20]
            dark_model.fit(np.array(dark_x_train_weak),
                           np.array(dark_y_train_weak),
                           epochs=10)
            dark_model.fit(np.array(dark_x_train_strong),
                           np.array(dark_y_train_strong),
                           epochs=20)
            del dark_x_train_weak, dark_x_train_strong
            del dark_y_train_weak, dark_y_train_strong
        num_light_states = len(light_data)
        for i in range(num_light_states//batch_size + 1):
            print(f"training light model with {i}th group")
            
            start = i * batch_size
            end = (i+1) * batch_size
            light_x_train_weak = [t[0] for t in light_data[start:end] if t[2] == 10]
            light_x_train_strong = [t[0] for t in light_data[start:end]
                                    if t[2] == 20]
            light_y_train_weak = [t[1] for t in light_data[start:end] if t[2] == 10]
            light_y_train_strong = [t[1] for t in light_data[start:end]
                                    if t[2] == 20]
            light_model.fit(np.array(light_x_train_weak),
                            np.array(light_y_train_weak),
                            epochs=10)
            light_model.fit(np.array(light_x_train_strong),
                            np.array(light_y_train_strong),
                            epochs=20)
            del light_x_train_weak, light_x_train_strong
            del light_y_train_weak, light_y_train_strong
    else:
        num_states = len(data)
        for i in range(num_states//batch_size + 1):
            print(f"training model with {i}th group")
            
            start = i * batch_size
            end = (i+1) * batch_size
            x_train_weak = [t[0] for t in data[start:end] if t[2] == 10]
            x_train_strong = [t[0] for t in data[start:end] if t[2] == 20]
            y_train_weak = [t[1] for t in data[start:end] if t[2] == 10]
            y_train_strong = [t[1] for t in data[start:end] if t[2] == 20]
            model.fit(np.array(x_train_weak), np.array(y_train_weak), epochs=10)
            model.fit(np.array(x_train_strong), np.array(y_train_strong), epochs=20)
            del x_train_weak, x_train_strong
            del y_train_weak, y_train_strong


    ## save model
    if args.separate_dark_and_light:
        print(f"save dark model to outfile: {dark_outh5filename}")
        dark_model.save(dark_outh5filename)
        print(f"save light model to outfile: {light_outh5filename}")
        light_model.save(light_outh5filename)
    else:
        print(f"save model to outfile: {outh5filename}")
        model.save(outh5filename)

