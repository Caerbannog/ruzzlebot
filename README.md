Usage
-----

To install it:

    git clone https://github.com/Caerbannog/ruzzlebot/

To run it:

    cd ruzzlebot
    python ./ruzzlebot


Description
-----------

This program connects to your Android phone over USB. It asks the user to enter
the letters of a Ruzzle game, then finds every allowed word and finally types 
them on your phone by simulating touch events.

You can enter the letters with whitespace anywhere, for instance:

    What are the 16 letters?
    ABCD
    EFGH
    IJKL MN OP

The script should give you the maximum score :
  * It doesn't miss any word
  * It simulates touches fast enough to type every word in a minute or so
  * It takes into account the bonuses when there are more than one path for a 
    given word

Technical
---------

Only Python 2 is supported because of the imaging library (PIL).

The dictionary is extracted on the fly from Ruzzle. You can generate a text file 
from it with the `extract_jet.py` script.

The bonuses are read from  the device screen with the `screencap` utility of 
the phone.

