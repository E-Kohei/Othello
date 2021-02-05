import tensorflow as tf

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

# csv file is required
if csvfilename is None:
    raise SyntaxError("Enter csv filename for data source!")
if inh5filename is None:
    raise SyntaxError("Enter h5 filename to load model!")


## evaluate model ##

model = tf.keras.models.load_model(inh5filename)

# read all data in from csv file
print("read all data in from csv file")
with open(csvfilename) as f:
    reader = csv.reader(f)
    
    filedata = next(reader)
    num_matches = int(filedata[2].split(':')[1])
    next(reader)

    data = []
    for row in reader:
        try:
            last_move_index = row.index("0_0")
        except ValueError:
            last_move_index = 65
        theo_score = int(row[4])
        #num_disc = last_move_index - 1
        #states = getAllStatesFromRecord(row[5:last_move_index])
        data.append({
            "record": row[5:last_move_index],
            "label": 1 if theo_score > 32 else 0  # 1 if dark side won
        })


# evaluate neural network
print("evaluate neural network")
model.compile(
    optimizer="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

x_test = []
y_test = []
# all states extracted by the records will be too large,
# so separate data into some groups and evaluate the model
for i in range(num_matches//500 + 1):
    print(f"evaluating with {i}th group")
    for j in range(500*i, min(num_matches, 500*(i+1))):
        states = getAllStatesFromRecord(data[j]["record"], True, True, True)
        label = data[j]["label"]
        x_test.extend(states)
        y_test.extend([ (label, 1-label) for k in range(len(states)) ])
    result = model.evaluate(np.array(x_test), y_test, verbose=2)
    print(f"{i}th result: ", result)
    x_test.clear()
    y_test.clear()


## pick one match and evaluate model by this match
def denormalizeDisc(disc):
    if disc == 1:    # black
        return BLACK
    elif disc == -1: # white
        return WHITE
    else:            # blank
        return BLANK


states = getAllStatesFromRecord(data[430]["record"])
statesForAI = getAllStatesFromRecord(data[430]["record"], False, True, True)
game = Othello(8)
for i, s in enumerate(statesForAI):
    print(f"{i}th state, predict: ", model.predict(s.reshape(1,64)))
    game.state = states[i]
    print(game)
if data[430]["label"] == 1:
    print("dark player won")
else:
    print("light player won")
