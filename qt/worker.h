#ifndef WORKER_H
#define WORKER_H

#include "phonehandler.h"
#include "solution.h"
#include <QThread>

class Worker : public QThread
{
public:

    Worker(QList<Solution> s, PhoneHandler * p);
    virtual void run();

    QList<Solution> solutions;
    PhoneHandler * phone;

};

#endif // WORKER_H


