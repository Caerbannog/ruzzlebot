#ifndef PHONEHANDLER_
#define PHONEHANDLER_

#include <QObject>
#include <QPoint>
#include <QString>
#include <QProcess>
#include <QTcpSocket>


class PhoneHandler : public QObject
{
    Q_OBJECT

public:

    PhoneHandler(QWidget * parent);

    void touchCell(int i, int j, bool down, bool up);
    void sendEvent(int type, int code, int value);
    QPoint screenToEvent(QPoint screen);
    QImage * getScreen();
    void getBonus(int i, int j, int &letter, int &word);

    QTcpSocket socket;
    QWidget * parent;
    QImage * image;


    const QPoint cellSize;
    const QPoint center00;
    const QPoint corner00;
};

#endif // PHONEHANDLER_
