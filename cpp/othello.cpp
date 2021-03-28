//
//  othello.cpp
//  
//
//  Created by 江崎航平 on 2021/03/17.
//

#include "othello.hpp"
#include <iostream>
#include <string>
#include <sstream>

#include <chrono>
// debug
int debugCounter = 0;
std::chrono::system_clock::time_point start = std::chrono::system_clock::now();
std::chrono::system_clock::time_point end;
/** Othello state */
State::State(int size) : sz(size), discs(new Disc[size*size]) {
    for (int i = 0; i < size*size; i++) {
        discs[i] = 0;
    }
}

State::State(const State& s) : sz(s.sz), discs(new Disc[s.sz*s.sz]) {
    memcpy(discs, s.discs, sizeof(Disc)*sz*sz);
}

State::~State() {
    delete[] discs;
}

int State::size() const {
    return sz;
}

const Disc& State::get(int i, int j) const {
    return discs[sz*i + j];
}

void State::set(int i, int j, Disc val) {
    discs[sz*i + j] = val;
}

Disc* const State::getRawDiscs() const {
    return discs;
}

void State::setAll(Disc ds[]) {
    memcpy(discs, ds, sizeof(Disc)*sz*sz);
}

std::ostream& operator<<(std::ostream& os, const State& state) {
    int sz = state.size();
    for (int i = 0; i < sz; i++) {
        for (int j = 0; j < sz; j++) {
            switch (state.get(i,j)) {
                case BLACK:
                    os << "o ";
                    break;
                case WHITE:
                    os << "x ";
                    break;
                default:
                    os << "  ";
                    break;
            }
        }
        os << std::endl;
    }
    return os;
}

bool operator<(const Cell& c1, const Cell& c2) {
    if (c1.row < c2.row)
        return true;
    else if (c1.row == c2.row)
        return c1.col < c2.col;
    else
        return false;
}

bool operator==(const Cell& c1, const Cell& c2) {
    return !(c1 < c2) && !(c2 < c1);
}


bool isAvailablePosition(const State& state, int row, int col,
                         Disc playerDisc) {
    int size = state.size();
    
    if (state.get(row, col) != BLANK) {
        return false;
    }
    
    Disc opponentDisc = -playerDisc;
    int m = size - 3;
    std::set<Vec> directions;
    if (col <= m && state.get(row, col+1) == opponentDisc) {
        // right
        directions.insert( Vec(0,1) );
    }
    if (col >= 2 && state.get(row, col-1) == opponentDisc) {
        // left
        directions.insert( Vec(0,-1) );
    }
    if (row <= m && state.get(row+1, col) == opponentDisc) {
        // bottom
        directions.insert( Vec(1,0) );
    }
    if (row >= 2 && state.get(row-1, col) == opponentDisc) {
        // top
        directions.insert( Vec(-1,0) );
    }
    if (row >= 2 && col <= m &&
        state.get(row-1, col+1) == opponentDisc) {
        // top-right
        directions.insert( Vec(-1,1) );
    }
    if (row >= 2 && col >= 2 &&
        state.get(row-1, col-1) == opponentDisc) {
        // top-left
        directions.insert( Vec(-1,-1) );
    }
    if (row <= m && col >= 2 &&
        state.get(row+1, col-1) == opponentDisc) {
        // bottom-left
        directions.insert( Vec(1, -1) );
    }
    if (row <= m && col <= m &&
        state.get(row+1, col+1) == opponentDisc) {
        // bottom-right
        directions.insert( Vec(1,1) );
    }
    if (directions.empty()) {
        return false;
    }
    
    std::set<Vec>::iterator iter = directions.begin();
    for (;iter != directions.end(); iter++) {
        // check if the action is valid in this direction
        int n = 2;
        while (true) {
            int nextRow = row + n*(iter->row);
            int nextCol = col + n*(iter->col);
            n++;
            if (nextRow < 0 || size-1 < nextRow ||
                nextCol < 0 || size-1 < nextCol ||
                state.get(nextRow, nextCol) == BLANK) {
                // not a valid action
                break;
            }
            else if (state.get(nextRow, nextCol) == playerDisc) {
                // now, you get (row,col) is a valid action
                return true;
            }
            // else case, opponentDisc, continue
        }
    }
    
    return false;
}

/// Return the result of the action to the state
/// - parameter state: othello state
/// - paramter row: row of the cell to place a disc on
/// -parameter col: column of the cell to place a dsic on
/// - paramter playerDisc: disc of the player who takes an action
/// - returns: the next state after the action if valid else nullptr
State* result(const State& state, int row, int col,
              Disc playerDisc) {
    int size = state.size();
    
    if (state.get(row, col) != BLANK) {
        return nullptr;
    }
    
    Disc opponentDisc = -playerDisc;
    int m = size - 3;
    std::set<Vec> directions;
    if (col <= m && state.get(row, col+1) == opponentDisc) {
        // right
        directions.insert( Vec(0,1) );
    }
    if (col >= 2 && state.get(row, col-1) == opponentDisc) {
        // left
        directions.insert( Vec(0,-1) );
    }
    if (row <= m && state.get(row+1, col) == opponentDisc) {
        // bottom
        directions.insert( Vec(1,0) );
    }
    if (row >= 2 && state.get(row-1, col) == opponentDisc) {
        // top
        directions.insert( Vec(-1,0) );
    }
    if (row >= 2 && col <= m &&
        state.get(row-1, col+1) == opponentDisc) {
        // top-right
        directions.insert( Vec(-1,1) );
    }
    if (row >= 2 && col >= 2 &&
        state.get(row-1, col-1) == opponentDisc) {
        // top-left
        directions.insert( Vec(-1,-1) );
    }
    if (row <= m && col >= 2 &&
        state.get(row+1, col-1) == opponentDisc) {
        // bottom-left
        directions.insert( Vec(1, -1) );
    }
    if (row <= m && col <= m &&
        state.get(row+1, col+1) == opponentDisc) {
        // bottom-right
        directions.insert( Vec(1,1) );
    }
    if (directions.empty()) {
        return nullptr;
    }
    
    State* result = nullptr;
    
    std::set<Vec>::iterator iter = directions.begin();
    for (;iter != directions.end(); iter++) {
        int n = 2;
        bool isValidDirection;
        while (true) {
            int nextRow = row + n*(iter->row);
            int nextCol = col + n*(iter->col);
            n++;
            if (nextRow < 0 || size-1 < nextRow ||
                nextCol < 0 || size-1 < nextCol ||
                state.get(nextRow, nextCol) == BLANK) {
                // not a valid action
                isValidDirection = false;
                break;
            }
            else if (state.get(nextRow, nextCol) == playerDisc) {
                // now, you get (row,col) is a valid action
                isValidDirection = true;
                break;
            }
            // else case, opponentDisc, continue
        }
        if (isValidDirection) {
            if (!result) {
                // if result is still null, initialize state
                result = new State(state);
                result->set(row, col, playerDisc);
            }
            for (int i = 1; i < n-1; i++) {
                int r = row + i*(iter->row);
                int c = col + i*(iter->col);
                result->set(r, c, playerDisc);
            }
        }
    }
    
    return result;
}

/** Get available actions and their results */
std::list<ActionResult> getActionStates(const State& state,
                                        Disc playerDisc) {
    int sz = state.size();
    std::list<ActionResult> action_and_state;
    for (int row = 0; row < sz; row++) {
        for (int col = 0; col < sz; col++) {
            State* nextState = result(state, row, col, playerDisc);
            if (nextState)
                action_and_state.emplace_back(row, col, nextState);
        }
    }

    if (action_and_state.empty()) {
        // (-1, -1) means pass
        action_and_state.emplace_back(-1, -1, new State(state));
    }
    
    return action_and_state;
}

/** Check if the state is terminal */
bool isTerminal(State state) {
    int sz = state.size();
    for (int row = 0; row < sz; row++) {
        for (int col = 0; col < sz; col++) {
            if (isAvailablePosition(state, row, col, BLACK))
                return false;
            if (isAvailablePosition(state, row, col, WHITE))
                return false;
        }
    }
    return true;
}

/** Utility score of the game */
int getUtility(const State& state) {
    int sz = state.size();
    int ss = sz*sz;
    int numBlack = 0;
    int numWhite = 0;
    Disc* rawDiscs = state.getRawDiscs();
    for (int i = 0; i < ss; i++) {
        switch (rawDiscs[i]) {
            case BLACK:
                numBlack++;
                break;
            case WHITE:
                numWhite++;
                break;
            default:
                break;
        }
    }
    if (numWhite < numBlack)
        return 1;
    else if (numBlack < numWhite)
        return -1;
    else
        return 0;
}

std::pair<int, int> getScore(const State& state) {
    int sz = state.size();
    int ss = sz*sz;
    int numBlack = 0;
    int numWhite = 0;
    Disc* rawDiscs = state.getRawDiscs();
    for (int i = 0; i < ss; i++) {
        switch (rawDiscs[i]) {
            case BLACK:
                numBlack++;
                break;
            case WHITE:
                numWhite++;
                break;
            default:
                break;
        }
    }
    return std::make_pair(numBlack, numWhite);
}

float evaluate(const State& state) {
    int sz = state.size();
    int ss = sz*sz;
    int numBlack = 0;
    int numWhite = 0;
    Disc* rawDiscs = state.getRawDiscs();
    for (int i = 0; i < ss; i++) {
        switch (rawDiscs[i]) {
            case BLACK:
                numBlack++;
                break;
            case WHITE:
                numWhite++;
                break;
            default:
                break;
        }
    }
    float total = numBlack + numWhite;
    return float(numBlack) / total;
}

/**
  Find an action with maximum score in minumum scores within depth
 */
void findMaxInMins(const State& state, int depth, ActionScore& as) {
    debugCounter += 1;
    if (debugCounter % 1000000 == 0) {
        std::cout << "current debugCounter = " << debugCounter
                  << std::endl;
        end = std::chrono::system_clock::now();
        auto dur = end - start;
        double msec = std::chrono::duration_cast<std::chrono::milliseconds>(dur).count();
        std::cout << msec << "milliseconds spent\n";
        start = std::chrono::system_clock::now();
    }
    if (depth == 0 || depth == -1) {
        float score = evaluate(state);
        as.row = -1; as.col = -1;
        as.score = score;
        return;
    }
    
    float maxScore = -10.0;
    // -2 means not initialized
    int maxActionRow = -2;
    int maxActionCol = -2;
    
    // Note: this function uses Max-player, i.e. dark player
    std::list<ActionResult> ar1 = getActionStates(state, BLACK);
    std::list<ActionResult>::const_iterator iter1 = ar1.begin();
    std::list<ActionResult>::const_iterator end1 = ar1.end();
    for (; iter1 != end1; iter1++) {
        std::list<ActionResult> ar2 = getActionStates(*(iter1->result),
                                                      WHITE);
        std::list<ActionResult>::const_iterator iter2 = ar2.begin();
        std::list<ActionResult>::const_iterator end2 = ar2.end();
        
        if (iter1->row == -1 && iter2->row == -1) {
            // state is already terminal state because both players
            // have no choice but pass
            as.row = -1; as.col = -1;
            as.score = evaluate(state);
            // cleanup
            for (; iter1 != end1; iter1++)
                delete iter1->result;
            for (; iter2 != end2; iter2++)
                delete iter2->result;
            
            return;
        }
        
        float _minScore = 10.0;
        for (; iter2 != end2; iter2++) {
            ActionScore nextAS(0,0,0);
            findMaxInMins(*(iter2->result), depth-2, nextAS);
            _minScore = std::min<float>(_minScore, nextAS.score);
            
            // If the current _minScore (this is Min-player's action)
            // is smaller than the current maxScore (Max-player's
            // action), the current player's action is not the
            // best choice because the minimum score of ar2 must be
            // smaller than the current maxScore.
            // That is, Max-player should not choose this action.
            if (_minScore < maxScore) {
                // cleanup
                for (; iter2 != end2; iter2++)
                    delete iter2->result;
                break;
            }
            delete iter2->result;
        }
        
        // If Min-player's expected score is larger than the
        // current maxScore, this is better choice for Max-player
        if (maxScore < _minScore) {
            maxScore = _minScore;
            maxActionRow = iter1->row;
            maxActionCol = iter1->col;
        }
        delete iter1->result;
    }
    
    if (maxActionRow == -2) {
        // no way but lose!
        std::list<ActionResult>::const_iterator first = ar1.begin();
        as.row = first->row; as.col = first->col;
        as.score = maxScore;
        return;
    }
    else {
        as.row = maxActionRow; as.col = maxActionCol;
        as.score = maxScore;
        return;
    }
}

/**
  Find an action with minimum score in maximum scores within depth
 */
void findMinInMaxs(const State& state, int depth, ActionScore& as) {
    debugCounter += 1;
    if (debugCounter % 1000000 == 0) {
        std::cout << "current debugCounter = " << debugCounter
                  << std::endl;
        end = std::chrono::system_clock::now();
        auto dur = end - start;
        double msec = std::chrono::duration_cast<std::chrono::milliseconds>(dur).count();
        std::cout << msec << "milliseconds spent\n";
        start = std::chrono::system_clock::now();
    }
    if (depth == 0 || depth == -1) {
        float score = evaluate(state);
        as.row = -1; as.col = -1;
        as.score = score;
        return;
    }
    
    float minScore = 10.0;
    // -2 means not initialized
    int minActionRow = -2;
    int minActionCol = -2;
    
    // Note: this function uses Min-player, i.e. light player
    std::list<ActionResult> ar1 = getActionStates(state, WHITE);
    std::list<ActionResult>::const_iterator iter1 = ar1.begin();
    std::list<ActionResult>::const_iterator end1 = ar1.end();
    for (; iter1 != end1; iter1++) {
        std::list<ActionResult> ar2 = getActionStates(*(iter1->result),
                                                      BLACK);
        std::list<ActionResult>::const_iterator iter2 = ar2.begin();
        std::list<ActionResult>::const_iterator end2 = ar2.end();
        
        if (iter1->row == -1 && iter2->row == -1) {
            // state is already terminal state because both players
            // have no choice but pass
            as.row = -1; as.col = -1;
            as.score = evaluate(state);
            // cleanup
            for (; iter1 != end1; iter1++)
                delete iter1->result;
            for (; iter2 != end2; iter2++)
                delete iter2->result;
            
            return;
        }
        
        float _maxScore = -10.0;
        for (; iter2 != end2; iter2++) {
            ActionScore nextAS(0,0,0);
            findMinInMaxs(*(iter2->result), depth-2, nextAS);
            _maxScore = std::max<float>(_maxScore, nextAS.score);
            
            // If the current _maxScore (this is Max-player7s action)
            // is greater than the current minScore (Min-player's
            // action), the current player's action is not the
            // best choice because the maximum score of ar2 must be
            // greater than the current minScore.
            // That is, Min-player should not choose this action.
            if (minScore < _maxScore) {
                // cleanup
                for (; iter2 != end2; iter2++)
                    delete iter2->result;
                break;
            }
            delete iter2->result;
        }
        
        // If Max-player's expected score is smaller than the
        // current minScore, this is better choice for Min-player
        if (_maxScore < minScore) {
            minScore = _maxScore;
            minActionRow = iter1->row;
            minActionCol = iter1->col;
        }
        delete iter1->result;
    }
    
    if (minActionRow == -2) {
        // no way but lose!
        std::list<ActionResult>::const_iterator first = ar1.begin();
        as.row = first->row; as.col = first->col;
        as.score = minScore;
        return;
    }
    else {
        as.row = minActionRow; as.col = minActionCol;
        as.score = minScore;
        return;
    }
}



int main(int argc, char* argv[]) {
    
    if (argc != 4) {
        std::cerr << "Error: Wrong number of arguments" << std::endl;
        std::cout << "0,0,0" << std::endl;
        exit(1);
    }
    
    Disc discs[64];
    std::string stateString(argv[1], 127);
    std::string::const_iterator iter = stateString.cbegin();
    std::string::const_iterator end = stateString.cend();
    
    int i = 0;
    for (; iter != end; iter++) {
        if (i == 64)
            std::cerr << "Invalid argument of state!" << std::endl;
        switch (*iter) {
            case '1':   // BLANK
                discs[i] = 0;
                i++;
                break;
            case '2':   // WHITE
                discs[i] = -1;
                i++;
                break;
            case '3':   // BLACK
                discs[i] = 1;
                i++;
                break;
            default:
                break;
        }
    }
    
    State state(8);
    state.setAll(discs);
    
    int depth;
    std::stringstream depthss(argv[3]);
    depthss >> depth;
    
    ActionScore as(0,0,0);
    if (argv[2][0] == '0') {
        // dark player's action
        findMaxInMins(state, depth, as);
        std::cout << as.row << "," << as.col << "," << as.score
                  << std::endl;
        exit(0);
    }
    else if (argv[2][0] == '1') {
        // ligtht player's action
        findMinInMaxs(state, depth, as);
        std::cout << as.row << "," << as.col << "," << as.score
                  << std::endl;
        exit(0);
    }
    else {
        std::cerr << "Invalid paramter of order!" << std::endl;
        std::cout << "0,0,0" << std::endl;
    }
}
