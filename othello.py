import re
import numpy as np

#from base81 import *


# Error class which will be raised when a user took some invalid action
class ActionError(ValueError):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

# player identifier
DARK_PLAYER = 0
LIGHT_PLAYER = 1

# disc identifier
BLANK = 1
WHITE = 2
BLACK = 3

# Environment
class Othello():

    def __init__(self, sz, player1=None, player2=None):
        # use szxsz matrix with the value range [1,2,3] to represent states
        self.size = sz
        self.state = np.full((sz, sz), BLANK, dtype=np.int16)
        self.state[sz//2-1,sz//2-1] = WHITE; self.state[sz//2-1,sz//2] = BLACK
        self.state[sz//2,sz//2-1] = BLACK; self.state[sz//2,sz//2] = WHITE
        self.player1 = player1
        self.player2 = player2
        if player1 is not None:
            # the first mover
            player1.setEnvironment(self)
            player1.setOrder(0)
        if player2 is not None:
            # the second mover
            player2.setEnvironment(self)
            player2.setOrder(1)

    def __repr__(self):
        string = ""
        marks = ["\u25A1", "\u25EF", "\u25CF"] # [blank, white, black]
        for i in range(self.size):
            for j in range(self.size):
                string += marks[self.state[i][j] - 1]
            string += "\n"
        return string

    def __str__(self):
        return self.__repr__()

    def getState(self):
        return self.state.copy()

    def actions(self, player, state=None):
        """Get available actions"""
        if state is None:
            state = self.state
        if player == DARK_PLAYER:  # black
            player_disc = BLACK
            opponent_disc = WHITE
        else:                      # white
            player_disc = WHITE
            opponent_disc = BLACK
        acts = []
        for row in range(self.size):
            for col in range(self.size):
                if self.isAvailablePosition(state, row, col,
                                       player_disc, opponent_disc):
                    acts.append( (row,col) )
        # if no available actions, pass
        if len(acts) == 0:
            acts.append("pass")
        return acts

    def actionsVerbose(self, player, state=None):
        """Get available actions in verbose format
           (includes discs to be reversed)"""
        if state is None:
            state = self.state
        if player == DARK_PLAYER:  # black
            player_disc = BLACK
            opponent_disc = WHITE
        else:                      # white
            player_disc = WHITE
            opponent_disc = BLACK
        acts = []
        for row in range(self.size):
            for col in range(self.size):
                tobeReversed = self.getDiscsToBeReversed(state, row, col,
                                                    player_disc, opponent_disc)
                if len(tobeReversed) > 0:
                    acts.append(tobeReversed)
        # if no available actions, pass
        if len(acts) == 0:
            acts.append(("pass", "pass"))
        return acts

    def takeAction(self, action, which_player):
        """For Human player"""
        # action is represented by tuple (row,col)

        # pass
        if type(action) != tuple:
            return

        if which_player == DARK_PLAYER:  # first mover uses black discs
            player_disc = BLACK
            opponent_disc = WHITE
        else:                  # second mover uses white discs
            player_disc = WHITE
            opponent_disc = BLACK

        tobeReversed = self.getDiscsToBeReversed(self.state,
                                                 action[0], action[1],
                                                 player_disc, opponent_disc)
        if len(tobeReversed) > 1:  # if this is a valid action
            for coord in tobeReversed:
                self.state[coord] = player_disc

        else:
            raise ActionError("invalid action!")

    def takeActionVerbose(self, action_verbose, which_player):
        """For AI player"""
        # action_verbose is represented by tuple
        # ((row,col), discs to be reversed...)

        # pass
        if action_verbose == ("pass","pass"):
            return

        if which_player == DARK_PLAYER:  # first mover uses black discs
            player_disc = BLACK
        else:                  # second mover uses white discs
            player_disc = WHITE

        for coord in action_verbose:
            self.state[coord] = player_disc

    def terminal(self, state=None):
        """Check if the game is over."""
        if state is None:
            state = self.state
        for row in range(self.size):
            for col in range(self.size):
                if self.isAvailablePosition(state, row, col, BLACK, WHITE):
                    return False
                if self.isAvailablePosition(state, row, col, WHITE, BLACK):
                    return False
        return True

    def utility(self, state=None):
        """Get utility (indicates which player won) of the state."""
        score = self.score(state)
        if score[0] > score[1]:   # dark player won
            return 1
        elif score[0] < score[1]: # light player won
            return -1
        else:                     # draw
            return 0

    def score(self, state=None):
        if state is None:
            state = self.state
        num_black = 0
        num_white = 0
        for row in range(self.size):
            for col in range(self.size):
                if state[row, col] == BLACK:
                    num_black += 1
                elif state[row, col] == WHITE:
                    num_white += 1
        return (num_black, num_white)

    def play(self):
        """Start the game."""
        if self.player1 is None or self.player2 is None:
            print("The game is not ready! Please set players.")
            return
        print(self.player1, ", you are the first mover")
        print(self.player2, ", you are the second mover")
        turn_counter = 0
        turn = 0
        while True:
            print("State: ")
            print(self)
            if turn_counter == DARK_PLAYER:
                print("turn ", turn, ": ", self.player1, ", it's your turn.")
                while True:
                    try:
                        action = self.player1.chooseAction()
                        if action == "pass":            # pass
                            print(self.player1, " passed turn")
                        elif type(action[0]) == int:      # simple format
                            self.takeAction(action, DARK_PLAYER)
                            print(self.player1,
                                  f" chose ({action[0]},{action[1]})")
                        else:                           # verbose format
                            self.takeActionVerbose(action, DARK_PLAYER)
                            print(self.player1,
                                  f" chose ({action[0][0]},{action[0][1]})")
                    except ActionError:
                        print("Invalid action. Retry again.")
                        continue
                    break
            else:
                print("turn ", turn, ": ", self.player2, ", it's your turn.")
                while True:
                    try:
                        action = self.player2.chooseAction()
                        if action == "pass":            # pass
                            print(self.player2, " passed turn")
                        elif type(action[0]) == int:      # simple format
                            self.takeAction(action, LIGHT_PLAYER)
                            print(self.player2,
                                  f" chose ({action[0]},{action[1]})")
                        else:                           # verbose format
                            self.takeActionVerbose(action, LIGHT_PLAYER)
                            print(self.player2,
                                  f" chose ({action[0][0]},{action[0][1]})")
                    except ActionError:
                        print("Invalid action. Retry again.")
                        continue
                    break
            # check if the game is over and notify players of the state
            if self.terminal():
                print("The game is over!")
                print("State:")
                print(self)
                util = self.utility()
                print(self.score())
                if util == 1:
                    print("Winner is ", self.player1, "!")
                    self.player1.notifyStateAndReward(turn_counter,
                                                      self.state, 1)
                    self.player2.notifyStateAndReward(turn_counter,
                                                      self.state, -1)
                    break
                elif util == -1:
                    print("Winner is ", self.player2, "!")
                    self.player1.notifyStateAndReward(turn_counter,
                                                      self.state, -1)
                    self.player2.notifyStateAndReward(turn_counter,
                                                      self.state, 1)
                    break
                else:
                    print("Draw!")
                    self.player1.notifyStateAndReward(turn_counter,
                                                      self.state, 0)
                    self.player2.notifyStateAndReward(turn_counter,
                                                      self.state, 0)
                    break
            else:
                self.player1.notifyStateAndReward(turn_counter, self.state, 0)
                self.player2.notifyStateAndReward(turn_counter, self.state, 0)
            turn_counter += 1
            turn_counter %= 2
            turn += 1


    def silent_play(self):
        """Play the game to train AI agents."""
        if self.player1 is None or self.player2 is None:
            print("The game is not ready! Please set players")
            return
        turn_counter = 0
        while True:
            if turn_counter == DARK_PLAYER:
                action = self.player1.chooseAction()
                if action == "pass":
                    pass
                else:
                    self.takeAction(action, 0)
            else:
                action = self.player2.chooseAction()
                if action == "pass":
                    pass
                else:
                    self.takeAction(action, 1)
            # check if the game is over and notify players of the result
            if self.terminal():
                util = self.utility()
                if util == 1:         # first mover won
                    self.player1.notifyStateAndReward(turn_counter,
                                                      self.state, 1)
                    self.player2.notifyStateAndReward(turn_counter,
                                                      self.state, -1)
                    break
                elif util == -1:      # second mover won
                    self.player1.notifyStateAndReward(turn_counter,
                                                      self.state, -1)
                    self.player2.notifyStateAndReward(turn_counter,
                                                      self.state, 1)
                    break
                else:                 # draw
                    self.player1.notifyStateAndReward(turn_counter,
                                                      self.state, 0)
                    self.player2.notifyStateAndReward(turn_counter,
                                                      self.state, 0)
                    break
            else:
                self.player1.notifyStateAndReward(turn_counter, self.state, 0)
                self.player2.notifyStateAndReward(turn_counter, self.state, 0)
            turn_counter += 1
            turn_counter %= 2


    @staticmethod
    def isAvailablePosition(state, row, col, player_disc, opponent_disc):
        """Check if the coordinate is valid action."""
        size = state.shape[0]
        
        if row < 0 or size-1 < row or col < 0 or size-1 < col or \
           state[row,col] != BLANK:
            return False

        size = state.shape[0]
        m = size - 3
        directions = set()
        if col <= m and state[row,col+1] == opponent_disc:  # right
            directions.add( (0,1) )
        if col >= 2 and state[row,col-1] == opponent_disc:  # left
            directions.add( (0,-1) )
        if row <= m and state[row+1,col] == opponent_disc:  # bottom
            directions.add( (1,0) )
        if row >= 2 and state[row-1,col] == opponent_disc:  # top
            directions.add( (-1,0) )
        if row >= 2 and col <= m and state[row-1,col+1] == opponent_disc: # rt
            directions.add( (-1,1) )
        if row >= 2 and col >= 2 and state[row-1,col-1] == opponent_disc: # lt
            directions.add( (-1,-1) )
        if row <= m and col >= 2 and state[row+1,col-1] == opponent_disc: # lb
            directions.add( (1,-1) )
        if row <= m and col <= m and state[row+1,col+1] == opponent_disc: # rb
            directions.add( (1,1) )

        i = 2
        while True:
            if len(directions) == 0:
                return False

            remove_directions = set()
            for d in directions:
                next_row, next_col = row + i*d[0], col + i*d[1]
                if next_row < 0 or size-1 < next_row or \
                   next_col < 0 or size-1 < next_col:
                    # not valid for this direction
                    remove_directions.add(d)
                elif state[next_row, next_col] == player_disc:
                    # this action is valid
                    return True
                elif state[next_row, next_col] == opponent_disc:
                    # maybe valid
                    continue
                elif state[next_row, next_col] == BLANK:
                    # not valid for this direction
                    remove_directions.add(d)
            directions.difference_update(remove_directions)
            i += 1

    @staticmethod
    def getDiscsToBeReversed(state, row, col, player_disc, opponent_disc):
        """Find all coordinates of discs to be reversed if you put on (row,col)."""
        size = state.shape[0]
        
        if row < 0 or size-1 < row or col < 0 or size-1 < col or \
           state[row,col] != BLANK:
            return ()

        m = size - 3
        directions = set()
        if col <= m and state[row,col+1] == opponent_disc:  # right
            directions.add( (0,1) )
        if col >= 2 and state[row,col-1] == opponent_disc:  # left
            directions.add( (0,-1) )
        if row <= m and state[row+1,col] == opponent_disc:  # bottom
            directions.add( (1,0) )
        if row >= 2 and state[row-1,col] == opponent_disc:  # top
            directions.add( (-1,0) )
        if row >= 2 and col <= m and state[row-1,col+1] == opponent_disc: # rt
            directions.add( (-1,1) )
        if row >= 2 and col >= 2 and state[row-1,col-1] == opponent_disc: # lt
            directions.add( (-1,-1) )
        if row <= m and col >= 2 and state[row+1,col-1] == opponent_disc: # lb
            directions.add( (1,-1) )
        if row <= m and col <= m and state[row+1,col+1] == opponent_disc: # rb
            directions.add( (1,1) )
        if len(directions) == 0:  # no candidates
            return ()

        tobeReversed = []
        for d in directions:
            i = 2
            tobeReversedInDirection = [(row+d[0],col+d[1])]
            while True:
                next_row, next_col = row + i*d[0], col + i*d[1]
                i += 1
                if next_row < 0 or size-1 < next_row or \
                   next_col < 0 or size-1 < next_col:
                    # not a valid action
                    break
                elif state[next_row, next_col] == player_disc:
                    # now, you get (row,col) is a valid action
                    tobeReversed.extend(tobeReversedInDirection)
                    break
                elif state[next_row, next_col] == opponent_disc:
                    # maybe a valid action
                    tobeReversedInDirection.append( (next_row, next_col) )
                elif state[next_row, next_col] == BLANK:
                    # not a valid action
                    break
        if len(tobeReversed) > 0:  # if valid action, insert (row,col)
            tobeReversed.insert(0, (row,col) )
        return tuple(tobeReversed)

    @staticmethod
    def smActions(player, state):
        """Get available actions."""
        if player == DARK_PLAYER:  # black
            player_disc = BLACK
            opponent_disc = WHITE
        else:                      # white
            player_disc = WHITE
            opponent_disc = BLACK
        acts = []
        size = state.shape[0]
        for row in range(size):
            for col in range(size):
                if Othello.isAvailablePosition(state, row, col,
                                               player_disc, opponent_disc):
                    acts.append( (row,col) )
        # if no available actions, pass
        if len(acts) == 0:
            acts.append("pass")
        return acts

    @staticmethod
    def smResult(state, action, which_player):
        """Get next state of state by taking action."""
        # action is represented by tuple (row,col)

        new_state = state.copy()

        # pass
        if type(action) != tuple:
            return new_state
        
        if which_player == DARK_PLAYER:  # first mover uses black discs
            player_disc = BLACK
            opponent_disc = WHITE
        else:                  # second mover uses white discs
            player_disc = WHITE
            opponent_disc = BLACK

        tobeReversed = Othello.getDiscsToBeReversed(state,
                                                    action[0], action[1],
                                                    player_disc, opponent_disc)
        if len(tobeReversed) > 1:  # if this is a valid action
            for coord in tobeReversed:
                new_state[coord] = player_disc
            return new_state
        else:
            raise ActionError("invalid action!")

    @staticmethod
    def smTerminal(state):
        size = state.shape[0]
        for row in range(size):
            for col in range(size):
                if Othello.isAvailablePosition(state, row, col, BLACK, WHITE):
                    return False
                if Othello.isAvailablePosition(state, row, col, WHITE, BLACK):
                    return False
        return True

    @staticmethod
    def smUtility(state):
        """Get utility (indicates which player won) of the state."""
        score = Othello.smScore(state)
        if score[0] > score[1]:   # dark player won
            return 1
        elif score[0] < score[1]: # light player won
            return -1
        else:                     # draw
            return 0

    @staticmethod
    def smScore(state):
        num_black = 0
        num_white = 0
        size = state.shape[0]
        for row in range(size):
            for col in range(size):
                if state[row, col] == BLACK:
                    num_black += 1
                elif state[row, col] == WHITE:
                    num_white += 1
        return (num_black, num_white)


# base class of othello player
class OthelloPlayer():
    def __init__(self, name, env=None):
        self.name = name
        self.environment = env
        self.order = None

    def __repr__(self):
        return self.name
    def __str__(self):
        return self.name

    def setEnvironment(self, env):
        self.environment = env

    def setOrder(self, order):
        self.order = order

    def chooseAction(self):
        pass

    def notifyStateAndReward(self, turn, new_state, reward):
        pass

# othello player used by program
class PlayerProgram(OthelloPlayer):
    # register next action
    def registerNextAction(action):
        self.next_action = action

    # override
    def chooseAction(self):
        if self.next_action is None:
            raise ActionError("Next action is not registered!")
        return self.next_action

# othello player used by command line user
class PlayerYou(OthelloPlayer):

    # override
    def chooseAction(self):
        while True:
            your_action = input("Enter a coordinates where you put your disc: ")
            try:
                action = self.parseAction(your_action)
            except ValueError:
                print("Invalid input for action. Retry again.")
                continue
            break
        return action

    @staticmethod
    def parseAction(action_str):
        if re.search("\(\s*\d\s*,\s*\d\s*\)", action_str):
            coord = re.findall("\d", action_str)
            action = (int(coord[0]), int(coord[1]))
            return action
        elif re.search("^\d\d$", action_str):
            coord = re.findall("\d", action_str)
            action = (int(coord[0]), int(coord[1]))
            return action
        elif action_str == "pass":
            return "pass"
        else:
            raise ValueError("Invalid string for action")



## helper functions ##

def isSameArray(v1, v2):
    l = len(v1)
    for i in range(l):
        if v1[i] != v2[i]:
            return False
    return True


def hashState(state):
    """hash state to compress data."""
    # used for optimization
    if type(state) != np.ndarray:
        return state
    result = ""
    size = state.shape[0]
    flatten = state.flatten() - 1
    for i in range(size*size//4):
        decimal = flatten[4*i] + flatten[4*i+1]*3 + flatten[4*i+2]*9 + flatten[4*i+3]*27
        result += toBase81Digit(decimal)
    decimal = 0
    for j in range(size*size%4):
        decimal += flatten[(size*size//4)*4+j] * pow(3,j)
    result += toBase81Digit(decimal)
    return result[::-1]
    

def hashStateAction(state, action):
    """hash pair of state and action."""
    h_s = hashState(state)
    h_a = f"{action[0]},{action[1]}" if type(action) == tuple else "p"
    return h_s + "|" + h_a


def retrieveState(hash_str, shape):
    """get state from hash string"""
    flatten = []
    for c in reversed(hash_str):
        decimal = fromBase81Digit(c)
        flatten.append(decimal%3)
        decimal = decimal // 3
        flatten.append(decimal%3)
        decimal = decimal // 3
        flatten.append(decimal%3)
        decimal = decimal // 3
        flatten.append(decimal%3)
    flatten = flatten[:shape[0]*shape[1]]
    return np.array(flatten, dtype=np.int16).reshape(shape) + 1


def isRotationalSymmetry(state, theta):
    """Check if the state is rotational symmetry."""
    size = state.shape[0]
    if theta == 90 or theta == -90:
        for i in range(size):
            v1 = state[i,:]
            v2 = state[:,size-1-i]
            if not isSameArray(v1, v2):
                return False
        return True
    elif theta == 180 or theta == -180:
        for i in range(size//2):
            v1 = state[size//2-1-i,:]
            v2 = state[size//2+i,::-1]  # reverse line
            if not isSameArray(v1, v2):
                return False
        return True
    else:
        raise ValueError("Invalid theta: theta must be +-90 or +-180")


def isReflectionSymmetry(state, axis):
    """Check if the state is reflection symmetry."""
    size = state.shape[0]
    if axis == 0:  # horizontal line
        for i in range(size//2):
            v1 = state[size//2-1-i,:]
            v2 = state[size//2+i,:]
            if not isSameArray(v1, v2):
                return False
        return True
    elif axis == 1:  # diagonal line of y = x
        for i in range(size):
            v1 = np.fliplr(state).diagonal(offset=i, axis1=0, axis2=1)
            v2 = np.fliplr(state).diagonal(offset=i, axis1=1, axis2=0)
            if not isSameArray(v1, v2):
                return False
        return True
    elif axis == 2:  # vertical line
        for i in range(size//2):
            v1 = state[:,size//2-1-i]
            v2 = state[:,size//2+i]
            if not isSameArray(v1, v2):
                return False
        return True
    elif axis == 3:  # diagonal line of y = -x
        for i in range(size):
            v1 = state.diagonal(offset=i, axis1=0, axis2=1)
            v2 = state.diagonal(offset=i, axis1=1, axis2=0)
            if not isSameArray(v1, v2):
                return False
        return True
    else:
        raise ValueError("Invalid axis: axis must be within range [0,3]")


def isRotationalSymmetryVectors(v1, v2):
    """Check if two vectors are rotational symmetry."""
    for i in range(len(v1)):
        if v1[i] != v2[-i-1]:
            return False
    return True

def isReflectionSymmetryVectors(v1, v2):
    """Check if two vectors are reflection symmetry."""
    for i in range(len(v1)):
        if v1[i] != v2[i]:
            return False
    return True

def isRotRefSymVectors(v1, v2):
    """Check if two vectors are rotation symmetry and reflection symmetry."""
    for i in range(len(v1)):
        if not (v1[i] == v1[-i-1] == v2[i] == v2[-i-1]):
            return False
    return True


def decideDirectionForRefSym(v1, v2):
    """Return 0 if v1 and v2 are rotational symmetry, and 1 or -1 otherwise.
       This function is used to decide direction for reflection-symmetrical vectors."""
    
    half = len(v1) // 2
    last = len(v1) %  2
    for i in range(half):
        lt = v1[i]; rt = v1[-i-1];
        lb = v2[i]; rb = v2[-i-1];
        # firstly, compare top-product with bottom-product
        if (lt * rt) > (lb * rb):
            return 1
        elif (lt * rt) < (lb * rb):
            return -1
        # if top-product == bottom-product,
        # compare right-product with left-product next
        elif (lt * lb) > (rt * rb):
            return 1
        elif (lt * lb) < (rt * rb):
            return -1
    # compare the last elements if len(v1) is odd
    if last:
        t = v1[half]
        b = v2[half]
        if t > b:
            return 1
        elif t < b:
            return -1
    # if right-product == left-product and top-product == bottom-product
    # for all 0 <= i <= half,
    # it turns out that lt == rb and rt == lb  ->  rotational symmetry! (v1 == reversed(v2))
    return 0

def decideDirectionForRotSym(v1, v2):
    """Return 0 if v1 and v2 are reflection symmetry, and 1 or -1 otherwize.
       This function is used to decide direction for rotational-symmetrical vectors."""

    half = len(v1) // 2
    last = len(v1) %  2
    for i in range(half):
        lt = v1[i]; rt = v1[-i-1];
        lb = v2[i]; rb = v2[-i-1];
        # firstly, compare top-product with bottom-product
        if (lt * rt) > (lb * rb):
            return 1
        elif (lt * rt) < (lb * rb):
            return -1
        # if top-product == bottom-product,
        # complare determinant of [[lt,rt], [lb,rb]] with 0
        if (lt*rb - rt*lb) > 0:
            return 1
        elif (lt*rb - rt*lb) < 0:
            return -1
    # compare the last elements if len(v1) is odd
    if last:
        t = v1[half]
        b = v2[half]
        if t > b:
            return 1
        elif t < b:
            return -1
    # if top-product == bottom-product and det([[lt,rt], [lb,rb]]) == 0
    # for all 0 <= i <= half,
    # it turns out that lt == rt and lb == rb  ->  reflection symmetry! (v1==v2)
    return 0

def decideDirectionForNonSym(v1, v2):
    """Return 0 if v1 and v2 are 'semi-symmetry' and 1 or -1 otherwise.
       This function is used to decide direction for non-symmetrycal vectors."""

    half = len(v1) // 2
    last = len(v1) %  2
    for i in range(half):
        lt = v1[i]; rt = v1[-i-1];
        lb = v2[i]; rb = v2[-i-1];
        # only compare top-sum with bottom-sum
        if (lt * rt) > (lb * rb):
            return 1
        elif (lt * rt) < (lb * rb):
            return -1
    # compare the last elements if len(v1) is odd
    if last:
        t = v1[half]
        b = v2[half]
        if t > b:
            return 1
        elif t < b:
            return -1
    # if the vectors consist of rotational symmetry part and refection symmetry
    # part (semi-symmetry), return 0
    # e.g. [1, 2, 2, 1, 1, 3] and [3, 1, 2, 1, 2, 1]
    return 0


def decideDirectionForVectors(v1, v2):
    """Return 0 if v1 and v2 are rotational symmetry or reflection symmetry,
       and 1 or -1 otherwise.
       This function can be used to decide direction for semi-symmetrycal vectors."""
    
    half = len(v1) // 2
    last = len(v1) % 2
    d_for_rotsym = None   # direction for rotational symmetrical elements
    d_for_refsym = None   # direction for reflection symmetrical elements
    d_for_nonsym = None   # direction for non symmetrical elements
    for i in range(half):
        _v1 = [v1[i], v1[-i-1]];
        _v2 = [v2[i], v2[-i-1]];
        # if completely symmetry, no direction
        if isRotRefSymVectors(_v1, _v2):
            continue
        # rotational symmetrical elements
        elif isRotationalSymmetryVectors(_v1, _v2):
            if d_for_rotsym is None:
                d_for_rotsym = decideDirectionForRotSym(_v1, _v2)
        # reflection symmetrical elements
        elif isReflectionSymmetryVectors(_v1, _v2):
            if d_for_refsym is None:
                d_for_refsym = decideDirectionForRefSym(_v1, _v2)
        # non symmetrical elements
        else:
            d_for_nonsym = decideDirectionForNonSym(_v1, _v2)
            return d_for_nonsym

    # compare the last elements if len(v1) is odd
    if last:
        t = v1[half]
        b = v2[half]
        if t > b:
            return 1
        elif t < b:
            return -1
    
    # if the vectors are semi-symmetry, decide direction
    if d_for_rotsym is not None and d_for_refsym is not None:
        return d_for_rotsym * d_for_refsym
    # else (the vectors are rotational symmetry or reflection symmetry), return 0
    else:
        return 0


def decideDirectionForMatrices(m1, m2):
    """Return 0 if m1 and m2 are rotational symmetry or reflection symmetry,
       and 1 or -1 otherwise.
       This function can be used to decide direction for semi-symmetrical matrices."""

    row = len(m1)
    d_for_rotsym = None   # direction for rotational symmetrical elements
    d_for_refsym = None   # direction for reflection symmetrical elements
    d_for_nonsym = None   # direction for non symmetrical elements
    for i in range(row):
        v1 = m1[-i-1]
        v2 = m2[i]
        # if completely symmetry, no direction
        if isRotRefSymVectors(v1, v2):
            continue
        # rotational symmetrical vectors
        elif isRotationalSymmetryVectors(v1, v2):
            if d_for_rotsym is None:
                d_for_rotsym = decideDirectionForRotSym(v1, v2)
        # reflection symmetrical vectors
        elif isReflectionSymmetryVectors(v1, v2):
            if d_for_refsym is None:
                d_for_refsym = decideDirectionForRefSym(v1, v2)
        # non symmetrical (or semi-symmetrical) vectors
        else:
            d_for_nonsym = decideDirectionForVectors(v1, v2)
            return d_for_nonsym

    # if the matrices are semi-symmetry, decide direction
    if d_for_rotsym is not None and d_for_refsym is not None:
        return d_for_rotsym * d_for_refsym
    # else (the matrices are rotational symmetry or reflection symmetry), return 0
    else:
        return 0

def decideDirectionForVectorList(vs1, vs2):
    """Return 0 if all vectors in vs1 and vs2 are symmetry (rotational or reflection),
       and 1 or -1 otherwise.
       This function can be used for list of vectors of difference sizes."""

    l = len(vs1)
    d_for_rotsym = None   # direction for rotational symmetrical elements
    d_for_refsym = None   # direction for reflection symmetrical elements
    d_for_nonsym = None   # direction for non symmetrical elements
    for i in range(l):
        v1 = vs1[i]
        v2 = vs2[i]
        # if completely symmetry, no direction
        if isRotRefSymVectors(v1, v2):
            continue
        # rotational symmetrical vectors
        elif isRotationalSymmetryVectors(v1, v2):
            if d_for_rotsym is None:
                d_for_rotsym = decideDirectionForRotSym(v1, v2)
        # reflection symmetrical vectors
        elif isReflectionSymmetryVectors(v1, v2):
            if d_for_refsym is None:
                d_for_refsym = decideDirectionForRefSym(v1, v2)
        # non symmetrical (or semi-symmetrical) vectors
        else:
            d_for_nonsym = decideDirectionForVectors(v1, v2)
            return d_for_nonsym

    # if vs1 and vs2 are semi-symmetry, decide direction
    if d_for_rotsym is not None and d_for_refsym is not None:
        return d_for_rotsym * d_for_refsym
    # else return 0
    else:
        return 0

def getAxesDirections(state, premise):
    """decide x-axis and y-axis and their directions for the state."""
    size = state.shape[0]
    
    h_direction = None
    v_direction = None
    
    isRotSym = premise["isRotSym"]
    isRefSymWithHLine = premise["isRefSymWithHLine"]
    isRefSymWithVLine = premise["isRefSymWithVLine"]

    # rotational-symmetry and reflection-symmetry
    # (RotSym and RefSymWithVLine indicates RefSymWithHLine in fact)
    if isRotSym and isRefSymWithVLine:
        return ("left", "top")

    
    # rotational-symmetry of order 2 but not reflection-symmetry
    elif isRotSym:
        # choose one from four (size//2 x size//2) squares
        # to do that, compare two squares on the top
        vs1 = []
        vs2 = []
        left = np.flipud(state[:size//2,:size//2])
        right = state[:size//2,size//2:].transpose()
        for i in range(size-1):
            vs1.append(right.diagonal(i-(size//2-1)))
            vs2.append(left.diagonal(i-(size//2-1)))
        d = decideDirectionForVectorList(vs1, vs2)
        if d == 1:
            # choose top-left square
            return ("left", "top")
        elif d == -1:
            # choose top-right square
            return ("right", "top")
        # If all vectors are same, this state is actually rotational-symmetry
        # of order 4. In this case, you can choose whichever
        return ("left", "top")


    # reflection-symmetry with the vertical line
    elif isRefSymWithVLine:
        # you can choose either of horizontal directions
        h_direction = "left"
        # decide vertical direction
        v_d = decideDirectionForMatrices(state[:size//2,:], state[size//2:,:])
        if v_d == 1:
            v_direction = "top"
        elif v_d == -1:
            v_direction = "bottom"
        
        if v_direction is None:
            raise ValueError("The state must not be refsym with hline! why!?")
        return (h_direction, v_direction)

    
    # reflection-symmetry with the horizontal line
    elif isRefSymWithHLine:
        # you can choose either of vertical directions
        v_direction = "top"
        # decide horizontal direction
        h_d = decideDirectionForMatrices(state[:,:size//2].transpose(),
                                         state[:,size//2:].transpose())
        if h_d == 1:
            h_direction = "left"
        elif h_d == -1:
            h_direction = "right"
        
        if h_direction is None:
            raise ValueError("The state must not be refsym with vline! why!?")
        return (h_direction, v_direction)

    
    # no symmetry
    else:
        # decide horizontal direction
        h_d = decideDirectionForMatrices(state[:,:size//2].transpose(),
                                         state[:,size//2:].transpose())
        v_d = decideDirectionForMatrices(state[:size//2,:], state[size//2:,:])
        if h_d == 1:
            h_direction = "left"
        elif h_d == -1:
            h_direction = "right"
        if v_d == 1:
            v_direction = "top"
        elif v_d == -1:
            v_direction = "bottom"

        if h_direction is None or v_direction is None:
            raise ValueError("The state must have no symmetry! why!?")
        return (h_direction, v_direction)


def getZDirection(state):
    """decide z-axis direction (up or down) for the state."""
    size = state.shape[0]
    for i in range(size):
        v1 = state.diagonal(offset=i, axis1=0, axis2=1)
        v2 = state.diagonal(offset=i, axis1=1, axis2=0)
        d = decideDirectionForRotSym(v1, v2)
        if d == 1:
            return "up"
        elif d == -1:
            return "down"
    # the state is reflection-symmetry with the diagonal line,
    # so you can choose any directions
    return "up"


def normalizeState(othello_state):
    """transform (rotate or reflect) state so as to fit its axes
       to certain directions."""

    transformations = []

    # get information about symmetry of the state
    isRotSym = isRotationalSymmetry(othello_state, 180)
    isRefSymWithHLine = isReflectionSymmetry(othello_state, 0)
    if isRotSym and isRefSymWithHLine:
        isRefSymWithVLine = True
    else:
        isRefSymWithVLine = isReflectionSymmetry(othello_state, 2)
    premise = { "isRotSym": isRotSym,
                "isRefSymWithHLine": isRefSymWithHLine,
                "isRefSymWithVLine": isRefSymWithVLine }

    # decide the direction of the two axes and reflect the state
    # to fit axes to ("left", "top")
    hori_axis, vert_axis = getAxesDirections(othello_state, premise)
    converted = othello_state.copy()
    if hori_axis == "right":
        transformations.append("fliplr")
        converted = np.fliplr(converted)
    if vert_axis == "bottom":
        transformations.append("flipud")
        converted = np.flipud(converted)

    # finally, decide the direction of z axis and reflect the state
    # to fit z axis to "up"
    z_axis = getZDirection(converted)
    if z_axis == "up":
        return (transformations, converted)
    else:
        transformations.append("transpose")
        return (transformations, np.transpose(converted))


def transformAction(action, transformations, state_size):
    """transform action in order to fit to transformed state"""
    a = [action[0], action[1]]
    for t in reversed(transformations):
        if t == "fliplr":
            a[1] = state_size - 1 - a[1]
        elif t == "flipud":
            a[0] = state_size - 1 - a[0]
        elif t == "transpose":
            a[0], a[1] = a[1], a[0]
    return tuple(a)


def _normalizeDisc(disc):
    if disc == BLANK:
        return 0
    elif disc == WHITE:
        return -1
    else:      # black
        return 1

normalizeDisc = np.vectorize(_normalizeDisc, otypes=[np.int16])

def getAllStatesFromRecord(record, normalize_state=False, normalize_disc=False, flatten=False):
    """simulate game and get all states from record"""
    states = []
    moves = []
    for i, m in enumerate(record):
        if m == "---":
            # end of the game
            break
        else:
            splitted = m.split('-')
            r = int(splitted[0])
            c = int(splitted[1])
            moves.append( (r,c) )
    game = Othello(8)

    # simulate moves
    next_mover = DARK_PLAYER
    for i, m in enumerate(moves):
        
        if next_mover == DARK_PLAYER:
            if Othello.isAvailablePosition(game.state, m[0], m[1], BLACK, WHITE):
                game.takeAction(m, DARK_PLAYER)
                next_mover = LIGHT_PLAYER
            elif Othello.isAvailablePosition(game.state, m[0], m[1], WHITE, BLACK):
                # This case means that the move m is not one of dark-player
                # but one of light-player because dark-player had no choice
                # but to pass his turn.
                game.takeAction(m, LIGHT_PLAYER)
                next_mover = DARK_PLAYER
            else:
                # unexpcted behavior
                raise ActionError("This move is invalid for both players!")
        elif next_mover == LIGHT_PLAYER:
            if Othello.isAvailablePosition(game.state, m[0], m[1], WHITE, BLACK):
                game.takeAction(m, LIGHT_PLAYER)
                next_mover = DARK_PLAYER
            elif Othello.isAvailablePosition(game.state, m[0], m[1], BLACK, WHITE):
                # This case means that the move m is not one of light-player
                # but one of dark-player because light-player had no choice
                # but to pass his turn.
                game.takeAction(m, DARK_PLAYER)
                next_mover = LIGHT_PLAYER
            else:
                # unexpcted behavior
                raise ActionError("This move is invalid for both players!")
        states.append(game.getState())

    if normalize_state:
        for i, s in enumerate(states):
            states[i] = normalizeState(s)[1]
    if normalize_disc:
        for i, s in enumerate(states):
            states[i] = normalizeDisc(s)
    if flatten:
        for i, s in enumerate(states):
            states[i] = s.flatten()
    
    return states
