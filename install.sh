#!/bin/bash

cp icon.png /usr/share/pixmaps/ardentryst.png
cp ardentryst /usr/bin
mkdir /usr/share/games/ardentryst
cp -R * /usr/share/games/ardentryst/
chmod 0755 /usr/bin/ardentryst
echo Installation complete!
