#include "board.h"
#include <QStringList>
#include <QtAlgorithms>
#include "phonehandler.h"


// TODO values for K X Z
const int Board::valueLUT[] = { 1, // A
                                3, // B
                                3, // C
                                2, // D
                                1, // E
                                4, // F
                                2, // G
                                4, // H
                                1, // I
                                8, // J
                                10, // K ?
                                2, // L
                                2, // M
                                1, // N
                                1, // O
                                3, // P
                                8, // Q
                                1, // R
                                1, // S
                                1, // T
                                1, // U
                                5, // V
                                10, // W
                                10, // X ?
                                10, // Y
                                10 // Z ?
                              };

/*
 taille   bonus
1 à 4       0
  5         5
  6         10
  7         15
  8         20
  9         25
  10        30
*/

Board::Board(QString dump, PhoneHandler * phone) : solutions()
{
    QStringList lines(dump.toLower().split("\n"));

    for(int i = 0; i < 4; i++) {
        for(int j = 0; j < 4; j++) {
            int letter = lines[i].at(j).toAscii() - 'a';

            int letterMultiplier = 1;
            int wordMultiplier = 1;
            if(phone != NULL)
                phone->getBonus(i, j, letterMultiplier, wordMultiplier);

            letters[i][j] = letter;
            letterValues[i][j] = valueLUT[letter] * letterMultiplier;
            wordMultipliers[i][j] = wordMultiplier;

            letterUsed[i][j] = false;
        }
    }
}

void Board::searchWords(int i, int j, Node * treePosition, QLinkedList<QPair<int, int> > history, QString word, int score, int wordMultiplier)
{
    if(i < 0 || i >= 4 || j < 0 || j >= 4)
        return;

    if(letterUsed[i][j])
        return;

    Node * child = treePosition->children[letters[i][j]];
    if(child == NULL)
        return;

    treePosition = child;
    word += 'a' + letters[i][j];

    history.append(QPair<int,int>(i, j));
    score += letterValues[i][j];
    wordMultiplier *= wordMultipliers[i][j];

    if(treePosition->validLeaf) { // We found a new word.
        int bonus = 0;
        if(word.length() >= 5)
            bonus = (word.length() - 4 ) * 5; // Bonus de longueur.

        solutions.append(Solution(score * wordMultiplier + bonus, history, word));
    }

    letterUsed[i][j] = true;
    for(int a = -1; a <= +1; a++) {
        for(int b = -1; b <= +1; b++) {
            searchWords(i + a, j + b, treePosition, history, word, score, wordMultiplier);
        }
    }
    letterUsed[i][j] = false;
}

void Board::Solve()
{
    if(!solutions.empty())
        return;

    Node * root = Node::dictionary();

    for(int i = 0; i < 4; i++) {
        for(int j = 0; j < 4; j++) {
            searchWords(i, j, root, QLinkedList<QPair<int, int> >(), "", 0, 1);
        }
    }

    qSort(solutions);
}
