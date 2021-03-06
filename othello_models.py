#import winsound
import time
import random
import tensorflow as tf

from othello import *


# abstract class  Othello AI which apply min-max
class MinMaxOthelloAgent(OthelloPlayer):

    def __init__(self, env=None, depth=1):
        super().__init__("MinMaxAI", env)

        self.win_util = None
        self.depth = depth
        self.epsilon = 0   # randomness of choosing action
        self.debug_counter = 0;

    def setOrder(self, order):
        self.order = order
        if order == DARK_PLAYER:
            self.win_util = 1
        else:
            self.win_util = -1

    def chooseAction(self):
        if random.random() < self.epsilon:
            actions = Othello.smActions(self.order, self.environment.getState())
            return random.choice(actions)
        else:
            self.debug_counter = 0
            action, score = self.findMaxInMins(self.environment.getState(),
                                               self.depth)
            print(self.debug_counter)
            # debug
            state = self.environment.getState()
            print(f"current score: {self.evaluate(state)}")
            print(f"expected score: {score}")
            #for i in range(2):
            #    winsound.MessageBeep()
            #    time.sleep(0.7)
            return action

    def evaluate(self, state):
        """Evaluate function, which calculates 'score' of the state."""
        raise NotImplementedError("This class is abstract!")

    def findMaxInMins(self, state, depth):
        """Find an action of maximum score in minimum scores within depth."""
        self.debug_counter += 1;
        if Othello.smTerminal(state) or depth <= 0:
            return (None, self.evaluate(state))

        max_score = -np.inf
        max_action = None
        player_me = self.order
        opponent = 1 - self.order
        actions = Othello.smActions(player_me, state)

        # just check evaluations of all of possible next states
        if depth == 1:
            action_scores = \
                [(action,
                  self.evaluate(Othello.smResult(state, action, player_me)))
                 for action in actions]
            return max(action_scores, key=lambda pair: pair[1])

        # find the maximum score in minimum scores
        for action in actions:
            new_state = Othello.smResult(state, action, player_me)
            
            # if the next state is terminal, check its utility and continue
            if Othello.smTerminal(new_state):
                # if the action makes you win, choose it
                if Othello.smUtility(new_state) == self.win_util:
                    return (action, self.evaluate(new_state))
                # otherwise it must be the case you lose or draw,
                # but remember the action in order to compare it later
                evaluation = self.evaluate(new_state)
                if max_score < evaluation:
                    max_score = evaluation;
                    max_action = action
                continue

            actions2 = Othello.smActions(opponent, new_state)
            _min_score = np.inf
            # find the minimum score in child nodes
            for action2 in actions2:
                new_state2 = Othello.smResult(new_state, action2, opponent)
                _min_score = min(_min_score,
                                 self.findMaxInMins(new_state2, depth-2)[1])
                # If the current min-of-maxs opponent may choose is less than
                # the current max-of-mins (you choose), this your action
                # is not best choice because the minimum score of action2 must
                # be less than the current max-of-mins.
                # That is, you should not choose this action anymore.
                if _min_score < max_score:
                    break
            # If min-of-maxs is larger than the current max score,
            # this is better choice for you
            if max_score < _min_score:
                max_score = _min_score
                max_action = action

        if max_action == None:
            # no way but lose!
            return (random.choice(actions), max_score)
        else:
            return (max_action, max_score)

    def findMinInMaxs(self, state, depth):
        """Find an action of minimum score in maximum scores within depth."""
        if Othello.smTerminal(state) or depth <= 0:
            return (None, self.evaluate(state))

        min_score = np.inf
        min_action = None
        player_me = self.order
        opponent = 1 - self.order
        actions = Othello.smActions(player_me, state)

        # just check evaluations of all of possible next states
        if depth == 1:
            action_scores = \
                [(action,
                  self.evaluate(Othello.smResult(state, action, player_me)))
                 for action in actions]
            return min(action_scores, key=lambda pair: pair[1])

        # find the minimum score in maximum scores
        for action in actions:
            new_state = Othello.smResult(state, action, player_me)
            
            # if the next state is terminal, check its utility and continue
            if Othello.smTerminal(new_state):
                # if the action makes you win, choose it
                if Othello.smUtility(new_state) == self.win_util:
                    return (action, self.evaluate(new_state))
                # otherwise it must be the case you lose or draw,
                # but remember the action in order to compare it later
                evaluation = self.evaluate(new_state)
                if evaluation < min_score:
                    min_score = evaluation
                    min_action = action
                continue
            
            actions2 = Othello.smActions(opponent, new_state)
            _max_score = -np.inf
            # find the minimum score in child nodes
            for action2 in actions2:
                new_state2 = Othello.smResult(new_state, action2, opponent)
                _max_score = max(_max_score,
                                 self.findMinInMaxs(new_state2, depth-2)[1])
                # If the current max-of-mins opponent may choose is more than
                # the current min-of-maxs (you choose), this your action
                # is not best choice because the maximum score of action2 must
                # be more than the current min-of-maxs.
                # That is, you should not choose this action anymore.
                if min_score < _max_score:
                    break
            # If min-of-maxs is larger than the current max score,
            # this is better choice for you
            if _max_score < min_score:
                min_score = _max_score
                min_action = action

        if min_action == None:
            # no way but lose!
            return (random.choice(actions), min_score)
        else:
            return (min_action, min_score)


class CornerWeightedMinMaxOthelloAgent(MinMaxOthelloAgent):

    # override evaluate function
    def evaluate(self, state):
        """Evaluate function which gives weight to the corners"""
        # if self.order = DARK_PLAYER(=0),  AI tries to maximize score[0]/total
        # if self.order = LIGHT_PLAYER(=1), AI tries to maximize score[1]/total
        num_discs = [0,0,0]    # number of discs of [BLANK, WHITE, BLACK]
        size = state.shape[0]
        for row in range(1, size-1):
            for col in range(1, size-1):
                num_discs[ state[row,col]-1 ] += 1
        # have weights on discs on the edge
        for row in range(1, size-1):
            num_discs[ state[row,0]-1 ] += 5
        for row in range(1, size-1):
            num_discs[ state[row,size-1]-1 ] += 5
        for col in range(1, size-1):
            num_discs[ state[0,col]-1 ] += 5
        for col in range(1, size-1):
            num_discs[ state[size-1,col]-1 ] += 5
        # have weights on discs on the corner
        num_discs[ state[0,0]-1 ] += 10
        num_discs[ state[0,size-1]-1 ] += 10
        num_discs[ state[size-1,0]-1] += 10
        num_discs[ state[size-1,size-1]-1 ] += 10

        score = (num_discs[2], num_discs[1])  # score of (dark, light)
        return score[self.order] / (score[0] + score[1])

class ModelMinMaxOthelloAgent(MinMaxOthelloAgent):

    def __init__(self, env=None, depth=1, model_file=None,
                 state_start=0, state_end=61, learn_epoch=10):
        super().__init__(env, depth)

        self.all_states = []
        self.isLearning = False
        self.state_start = state_start
        self.state_end = state_end
        self.learn_epoch = learn_epoch

        # load or create neural network model
        if model_file is None:
            self.model = tf.keras.models.Sequential([
                tf.keras.layers.Dense(16, input_shape=(64,), activation="relu"),
                tf.keras.layers.Dense(2, activation="softmax")
            ])
        else:
            print(f"load model file: {model_file}")
            self.model = tf.keras.models.load_model(model_file)

    # override evaluate function
    def evaluate(self, state):
        """Evaluate function using neural network"""
        if Othello.smTerminal(state):
            util = Othello.smUtility(state)
            if util == self.win_util:
                return np.inf
            elif util == -self.win_util:
                return -np.inf
            else:
                return self.model.predict(
                    normalizeDisc(state).flatten().reshape(1,64)
                    )[0][self.order]
        
        return self.model.predict(
            normalizeDisc(state).flatten().reshape(1,64)
            )[0][self.order]

    # override the behavior when state and reward are notified
    def notifyStateAndReward(self, turn, state, reward):
        if self.isLearning:
            print("notified and append")
            # remember all states in order to train the model later
            self.all_states.append(normalizeDisc(state.flatten()))
        if self.isLearning and Othello.smTerminal(state):
            print("len of all states: ", len(self.all_states))
            print(self.all_states[-1])
            # train the model
            print(self.learn_epoch)
            self.train_model(reward=reward,
                             start=self.state_start, end=self.state_end,
                             epoch=self.learn_epoch)
            self.all_states.clear()

    def train_model(self, reward, start, end, epoch):
        if reward == 0:
            label = 0.5
        elif reward == 1:
            label = 1 - self.order
        else: # reward == -1:
            label = self.order
        print(f"label: {label}")
        length = len(self.all_states)
        states = self.all_states[start*length//61 : end*length//61]
        print("train model for states: ", states)
        y_train = [ (label, 1-label) for _ in range(len(states))]
        self.model.fit(np.array(states), y_train, epochs=epoch)

    def saveModel(self, filename):
        self.model.save(filename)


class HybridOthelloAgent(MinMaxOthelloAgent):

    def __init__(self, env=None, depth=1, model_file=None):
        super().__init__(env, depth)

        # load or create neural network model
        if model_file is None:
            self.model = tf.keras.models.Sequential([
                tf.keras.layers.Dense(16, input_shape=(64,), activation="relu"),
                tf.keras.layers.Dense(2, activation="softmax")
            ])
        else:
            print(f"load model file: {model_file}")
            self.model = tf.keras.models.load_model(model_file)

    # override evaluate function
    def evaluate(self, state):
        """Evaluate function using neural network or my function"""
        num_discs = sum(Othello.smScore(state))
        if num_discs < 40:
            # in the earlier state, evaluate with corner weighted function
            num_discs = [0,0,0]
            size = state.shape[0]
            for row in range(1, size-1):
                for col in range(1, size-1):
                    num_discs[ state[row,col]-1 ] += 1
            # have weights on discs on the edge
            for row in range(1, size-1):
                num_discs[ state[row,0]-1 ] += 5
            for row in range(1, size-1):
                num_discs[ state[row,size-1]-1 ] += 5
            for col in range(1, size-1):
                num_discs[ state[0,col]-1 ] += 5
            for col in range(1, size-1):
                num_discs[ state[size-1,col]-1 ] += 5
            # have weights on discs on the corner
            num_discs[ state[0,0]-1 ] += 10
            num_discs[ state[0,size-1]-1 ] += 10
            num_discs[ state[size-1,0]-1] += 10
            num_discs[ state[size-1,size-1]-1 ] += 10

            score = (num_discs[2], num_discs[1])  # score of (dark, light)
            return score[self.order] / (score[0] + score[1])
        else:
            # in the later state, evaluate with neural network
            return self.model.predict(
                normalizeDisc(state).flatten().reshape(1,64))[0][self.order]
