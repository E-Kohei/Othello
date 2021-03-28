//
//  othello.hpp
//  
//
//  Created by 江崎航平 on 2021/03/17.
//

#ifndef othello_hpp
#define othello_hpp

#include <stdio.h>
#include <memory.h>
#include <iostream>
#include <algorithm>
#include <list>
#include <set>
#include <utility>


using Disc = signed char;

const int DARK_PLAYER = 0;
const int LIGHT_PLAYER = 1;

const Disc BLANK = 0;
const Disc WHITE = -1;
const Disc BLACK = 1;

/** Cell in the othello board */
struct Cell {
    int row;
    int col;
    Cell(int r, int c) : row(r), col(c) {}
};

/** Direction in the othello board */
using Vec = Cell;

/** State of the othello game */
class State {
private:
    int sz;
    Disc* discs;
public:
    State(int size);
    State(const State& s);
    ~State();
    
    int size() const;
    const Disc& get(int i, int j) const;
    void set(int i, int j, Disc val);
    Disc* const getRawDiscs() const;
    void setAll(Disc ds[]);
};

/** Action and Pointer to its result */
struct ActionResult {
    int row;
    int col;
    State* result;
    ActionResult(int r, int c, State* p) : row(r), col(c), result(p) {}
};

/** Actoin and expected score */
struct ActionScore {
    int row;
    int col;
    float score;
    ActionScore(int r, int c, float s) : row(r), col(c), score(s) {}
};

std::ostream& operator<<(std::ostream& os, const State& state);

bool operator<(const Cell& c1, const Cell& c2);
bool operator==(const Cell& c1, const Cell& c2);


bool isAvailablePosition(const State& state, int row, int col,
                         Disc playerDisc);
State* result(const State& state, int row, int col, Disc playerDisc);
std::list<ActionResult> getActionStates(const State& state,
                                        Disc playerDisc);
bool isTerminal(const State& state);
int getUtility(const State& state);
std::pair<int, int> getScore(const State& state);

float evaluate(const State& state);
void findMaxInMins(const State& state, int depth, ActionScore& as);


#endif /* othello_hpp */
