import sys
import re
import csv

import tensorflow as tf

from othello import *


## deal with command line arguments ##
if len(sys.argv) == 1:
    raise SyntaxError("Enter some file for othello data!")

csvfilename = None
inh5filename = None
outh5filename = None

# deal with explicit arguments
if "--data-source" in sys.argv:
    # get csv filename for data source
    index = sys.argv.index("--data-source")
    try:
        csvfilename = sys.argv[index+1]
        sys.argv.pop(index)
        sys.argv.pop(index)
    except IndexError:
        raise SyntaxError("Enter csv filename for data source!")

if "--model-file" in sys.argv:
    # load model from h5 file
    index = sys.argv.index("--model-file")
    try:
        inh5filename = sys.argv[index+1]
        sys.argv.pop(index)
        sys.argv.pop(index)
    except IndexError:
        raise SyntaxError("Enter h5 filename to load a model!")

if "--out-file" in sys.argv:
    index = sys.argv.index("--out-file")
    try:
        outh5filename = sys.argv[index+1]
        sys.argv.pop(index)
        sys.argv.pop(index)
    except:
        raise SyntaxError("Enter h5 file for output!")

# deal with left arguments
if csvfilename is None and len(sys.argv) > 1:
    maybe_csvfile = sys.argv[1]
    if re.match("^--", maybe_csvfile):
        raise SyntaxError("Invalid csv filename")
    else:
        csvfilename = maybe_csvfile
        sys.argv.pop(1)
if inh5filename is None and len(sys.argv) > 1:
    maybe_h5file = sys.argv[1]
    if re.match("^--", maybe_h5file):
        raise SyntaxError("Invalid h5 filename")
    else:
        inh5filename = maybe_h5file
        sys.argv.pop(1)
if outh5filename is None and len(sys.argv) > 1:
    maybe_h5file = sys.argv[1]
    if re.match("^--", maybe_h5file):
        raise SyntaxError("Invalid h5 filename")
    else:
        outh5filename = maybe_h5file
        sys.argv.pop(1)

# csv file is required
if csvfilename is None:
    raise SyntaxError("Enter csv filename for data source!")

# h5 file for model is required
if inh5filename is None:
    raise SyntaxError("Enter h5 filename to load a model!")

# if h5 file to save the model is specified, use same file as infile
if outh5filename is None:
    outh5filename = inh5filename


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
    
    filedata = next(reader)
    num_matches = int(filedata[2].split(':')[1])
    depth = int(filedata[7].split(':')[1])
    print("number of matches: ", num_matches)
    print("depth of theorical score: ", depth)
    next(reader)

    data = []
    for row in reader:
        try:
            end_index = row.index("---")
        except ValueError:
            end_index = 60
        real_score = int(row[3])
        theo_score = int(row[4])
        num_disc = end_index + 4
        if num_disc <= 64 - depth:
            # use real score
            data.append({
                "record": row[5:],
                "label": 1 if score > (num_disc/2) else 0
            })
        else:
            # use theorical score
            data.append({
                "record": row[5:],
                "label": 1 if theo_score > 32 else 0  # 1 if dark side would win
            })


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
        states = getAllStatesFromRecord(data[j]["record"], False, True, True)
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
    model.fit(np.array(x_train_early), y_train_early, epochs=10)
    model.fit(np.array(x_train_late), y_train_late, epochs=20)
    x_train_early.clear()
    y_train_early.clear()
    x_train_late.clear()
    y_train_late.clear()


## save model
print(f"save model to outfile: {outh5filename}")
model.save(outh5filename)
