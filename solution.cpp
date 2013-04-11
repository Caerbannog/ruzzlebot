#include "solution.h"

Solution::Solution(int score, QLinkedList<QPair<int, int> > path, QString word) : score(score), path(path), word(word)
{
}

bool Solution::operator<(const Solution s) const
{
    return score > s.score;
}
