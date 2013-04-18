#ifndef NODE_H
#define NODE_H

#include <QString>

class Node;

class Node
{
public:
    Node();
    void insertWord(QString word);

    Node* children[26];
    bool validLeaf;

    static Node * dictionary();

private:
    static Node * _dictionary;
};

#endif // NODE_H
