#ifndef SOLUTION_H
#define SOLUTION_H

#include <QString>
#include <QLinkedList>
#include <QPair>

class Solution;

class Solution
{
public:
    Solution(int score, QLinkedList<QPair<int, int> > path, QString word);

    bool operator<(const Solution s) const;

    int score;
    QLinkedList<QPair<int, int> > path;
    QString word;
};

#endif // SOLUTION_H
