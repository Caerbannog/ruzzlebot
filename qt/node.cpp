#include "node.h"
#include <QFile>
#include <QMessageBox>
#include <QTextStream>


Node::Node() : children(), validLeaf(false)
{

}

void Node::insertWord(QString word)
{
    if(word.isEmpty())
        validLeaf = true;
    else {
        int i = word.at(0).toAscii() - 'a';

        if(children[i] == NULL)
            children[i] = new Node();

        children[i]->insertWord(word.right(word.length() - 1));
    }
}

Node * Node::_dictionary(NULL);

Node * Node::dictionary()
{
    if(_dictionary == NULL) {

        QFile file("dict.txt");
        if(!file.open(QIODevice::ReadOnly)) {
            QMessageBox::information(0, "error", file.errorString());
        }

        QTextStream in(&file);

        _dictionary = new Node();

        while(!in.atEnd()) {
            QString word = in.readLine().trimmed();

            _dictionary->insertWord(word);
        }

        file.close();
    }

    return _dictionary;
}
