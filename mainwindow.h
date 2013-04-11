#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include "worker.h"
#include "phonehandler.h"

namespace Ui {
class MainWindow;
}

class MainWindow : public QMainWindow
{
    Q_OBJECT
    
public:
    explicit MainWindow(QWidget *parent = 0);
    ~MainWindow();
    
private slots:
    void on_run_clicked();
    void on_solve_clicked();

private:
    Ui::MainWindow *ui;
    PhoneHandler * phone;
    Worker * worker;
};

#endif // MAINWINDOW_H
