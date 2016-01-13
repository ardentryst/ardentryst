#------------------------------------------------------------------------
#
#    This file is part of Ardentryst.
#
#    Ardentryst is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Ardentryst is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Ardentryst.  If not, see <http://www.gnu.org/licenses/>.
#
#    Copyright 2007, 2008, 2009 Jordan Trudgett
#
#------------------------------------------------------------------------

import pygame

class SET1:
    def __init__(self, keycodes, x, y, set):
        #WSAD / UP DOWN LEFT RIGHT
        self.set = set
        self.keys = [
            Key(keycodes[0], x, y, "Up", set),
            Key(keycodes[1], x, y+30, "Down", set),
            Key(keycodes[2], x-32, y+30, "Left", set),
            Key(keycodes[3], x+32, y+30, "Right", set),
            ]

class SET2:
    def __init__(self, keycodes, x, y, set):
        self.set = set
        self.keys = [Key(keycodes[c], x + ((8-c)%3) * 32, y + (c/3)*30, "B-" + str(((11-c)/3)*3 - (11-c)%3), set) for c in range(9)]

class Key:
    def __init__(self, keycode, x, y, binding, set):
        self.binding = binding
        self.set = set
        self.state = 0
        self.keycode = keycode
        self.x, self.y = x, y
        self.label = pygame.key.name(self.keycode)
        if self.label.startswith("unknown"):
            self.label = "???"
