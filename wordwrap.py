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

def string_to_paragraph(string, font, antialiasbool, colour, size):
    "Converts a long string to a list of rendered surfaces that don't exceed the size in width."
    try:
        srender = font.render(string, antialiasbool, colour)
    except:
        srender = pygame.Surface((size+1, 1))
    if srender.get_width() > size:
        surf_list = []

        while True:
            lastspace = None
            torender = string
#            prender = font.render(string, antialiasbool, colour)

            if font.size(torender)[0] <= size:
                surf_list.append(font.render(torender, antialiasbool, colour))
                return surf_list
            while font.size(torender)[0] > size:
                lastspace = string[:lastspace].rfind(" ")
                torender = string[:lastspace]
            prender = font.render(torender, antialiasbool, colour)
            surf_list.append(prender)
            string = string[lastspace+1:]

        
    else:
        return [srender]
