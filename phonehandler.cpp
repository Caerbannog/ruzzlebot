#include "phonehandler.h"
#include "mainwindow.h"
#include <QDebug>
#include <QLabel>

// TODO
// nettoyer code
// faire le total des points
// mieux gérer le début

/* Format event0
octets faible en premiers
16 octets

second zero tps,,,0, zer type code, value,,,,,,
BB 58 00 00 C1 61 0C 00 03 00 35 00 33 44 55 66
BB 58 00 00 EA 9C 0C 00 03 00 35 00 01 00 00 00
*/
struct input_event {
    int32_t tv_sec;
    int32_t uv_sec;
    u_int16_t type;
    u_int16_t code;
    int32_t value;
};


PhoneHandler::PhoneHandler(QWidget * parent) : socket(parent), parent(parent), image(NULL), cellSize(115, 118), center00(66, 263), corner00(16, 230)
{
    QProcess adb(parent);
    QStringList arguments;
    arguments << "forward" << "tcp:1234" << "dev:/dev/input/event0";

    adb.start("adb", arguments);
    if(!adb.waitForFinished())
        qDebug() << "Cannot forward port.";

    socket.connectToHost("127.0.0.1", 1234);
    if(!socket.waitForConnected() ) {
        qDebug() << "Cannot connect socket.";
    }
}

void PhoneHandler::sendEvent(int type, int code, int value)
{
    struct input_event ev;

    ev.tv_sec = 0;
    ev.uv_sec = 0;
    ev.type = type;
    ev.code = code;
    ev.value = value;

    socket.write((char*)&ev, sizeof(ev));
}

QImage * PhoneHandler::getScreen()
{
    QProcess adb(parent);
    QStringList arguments;
    arguments << "pull" << "/dev/graphics/fb0" << "fb0.data";

    adb.start("adb", arguments);
    if(!adb.waitForFinished())
        qDebug() << "Cannot pull framebuffer.";

    QProcess ffmpeg(parent);
    QStringList arguments2;
    arguments2 << "-vframes" << "1" << "-vcodec" << "rawvideo" << "-f" << "rawvideo"
               << "-pix_fmt" << "rgb32" << "-s" << "480x800" << "-i" << "fb0.data"
               << "-f" << "image2" << "-vcodec" << "png" << "fb0.png";

    ffmpeg.start("ffmpeg", arguments2);
    if(!ffmpeg.waitForFinished())
        qDebug() << "Cannot convert picture.";

    image = new QImage("fb0.png");
    return image;
}

/* Typical colors :

  255!  158     0     DW
  137     4!    8     TW
   16   134    16!    DL
    8!   73   132     TL
  165   175   181    rien
*/
void PhoneHandler::getBonus(int i, int j, int &letter, int &word)
{
    if(image == NULL)
        getScreen();

    QPoint offset(j * cellSize.x(), i * cellSize.y());
    QPoint position = corner00 + offset;

    QColor color(image->pixel(position));
    /*
    QString rgb(QString("%1,%2,%3").arg(color.red()).arg(color.green()).arg(color.blue()));
    QLabel * item = new QLabel(rgb, parent);
    item->move(j * 80, i * 27);
    item->setStyleSheet("background-color: rgb(" + rgb + "); color: white");
    item->show();
    //*/

    if(color.red() > 210)
        word = 2;
    else if(color.green() < 30)
        word = 3;
    else if(color.blue() < 50)
        letter = 2;
    else if(color.red() < 100)
        letter = 3;
}

QPoint PhoneHandler::screenToEvent(QPoint screen)
{
    return QPoint(screen.x() * 1000 / 480, screen.y() * 1000 / 800);
}

// http://fangmobile.com/2012/11/06/android-low-level-shell-click-on-screen-for-ics-and-may-be-jelly-bean/
void PhoneHandler::touchCell(int i, int j, bool down, bool up)
{
    Q_ASSERT(0 <= i && i <= 3);
    Q_ASSERT(0 <= j && j <= 3);

    QPoint offset(j * cellSize.x(), i * cellSize.y());
    QPoint position = screenToEvent(center00 + offset);

    if (down) {
        sendEvent(3, 53, position.x());
        sendEvent(3, 54, position.y());
        sendEvent(3, 58, 71);
        sendEvent(3, 48, 4);
        sendEvent(3, 57, 0);
        sendEvent(0, 2, 0);
        sendEvent(0, 0, 0);
    }

    if (up) {
        sendEvent(0, 2, 0);
        sendEvent(0, 0, 0);
    }
}
