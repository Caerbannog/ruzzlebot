#ifndef BOARD_H
#define BOARD_H

#include "solution.h"
#include "node.h"
#include "phonehandler.h"

class Board
{
public:
    Board(QString dump, PhoneHandler * phone = NULL);
    void Solve();

    int letters[4][4];
    int letterValues[4][4];
    int wordMultipliers[4][4];

    QList<Solution> solutions;

private:
    bool letterUsed[4][4];
    static const int valueLUT[26];

    void searchWords(int i, int j, Node * treePosition, QLinkedList<QPair<int, int> > history, QString word, int score, int wordMultiplier);
};

#endif // BOARD_H
