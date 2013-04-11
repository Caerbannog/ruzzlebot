#include "mainwindow.h"
#include "ui_mainwindow.h"
#include "node.h"
#include "board.h"
#include "worker.h"

#include <QPair>

MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    ui->setupUi(this);

    phone = new PhoneHandler(ui->centralWidget);

    ui->label->setPixmap(QPixmap::fromImage(*phone->getScreen()));
}

MainWindow::~MainWindow()
{
    worker->terminate();

    delete ui;
}

void MainWindow::on_run_clicked()
{
    qDebug() << "Starting...";
    Board * b = new Board(ui->plainTextEdit->toPlainText(), phone);

    qDebug() << "Solving...";
    b->Solve();

    QString str;
    foreach(Solution s, b->solutions) {
        str += s.word + QString(" %1\n").arg(s.score);
    }
    ui->textBrowser->setText(str);

    qDebug() << "Playing...";
    worker = new Worker(b->solutions, phone);

    worker->start();
}

void MainWindow::on_solve_clicked()
{
    Board * b = new Board(ui->plainTextEdit->toPlainText(), phone);
    b->Solve();

    QString str;
    foreach(Solution s, b->solutions) {
        str += s.word + QString(" %1\n").arg(s.score);
    }
    ui->textBrowser->setText(str);
}
