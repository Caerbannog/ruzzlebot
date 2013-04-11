#include "worker.h"
#include <QDebug>

Worker::Worker(QList<Solution> solutions, PhoneHandler * phone) : solutions(solutions), phone(phone)
{
}

void Worker::run()
{
    QList<QString> typed;
    foreach(Solution s, solutions) {
        if(typed.contains(s.word)) {
            qDebug() << "Skipping " + s.word;
            continue;
        }
        typed.append(s.word);

        qDebug() << s.word + QString(" %1").arg(s.score);


        QLinkedListIterator<QPair<int,int> > iter(s.path);
        while (iter.hasNext()) {
            QPair<int,int> pair = iter.next();

            bool up = !iter.hasNext(); // Remove the finger if this is the last letter.

            phone->touchCell(pair.first, pair.second, true, up);
            msleep(40);
        }
    }
}
