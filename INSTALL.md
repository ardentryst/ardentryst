To install a system-wide Ardentryst on your linux machine, you need to
be root (administrator). You can install a local copy yourself, too.

Type

    sudo ./install.sh

to run the installer script, which will copy the game data files to
your system, and set up the command 'ardentryst'.

Alternatively, and if that didn't work, you can copy this directory
to /usr/share/games/ardentryst, copy icon.png to
/usr/share/pixmaps/ardentryst.png, copy ardentryst (executable) to
/usr/bin/ or /usr/games/ and then it is installed. You can use
the .desktop file to create a launcher too.

Once that is completed, you should be able to run Ardentryst from
a terminal window (in X) by typing 'ardentryst'.

To run the game without doing a system-wide install, just run
ardentryst.py (with Python) and you're ready to go.


To use Python virtual env you can run:

```
$ python3 -m venv  venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ python ardentryst.py

```
