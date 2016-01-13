#------------------------------------------------------------------------
#
#    Ardentryst: Action/RPG
#    Copyright (C) 2008  Jordan Trudgett
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    Project started  12th October 2007
#
#------------------------------------------------------------------------

import os

def parse_scriptfile(sf):
    try:
        file_sf = open(os.path.join("Levels", sf), "r")
        lines_sf = file_sf.readlines()
    except:
        return []

    rules = []
    
    for line in lines_sf:
        line = line.strip()
        if not line: continue
        if line[0] == "#": continue

        condition = ""

        if line[0] == "/":
            condition = line[1:line.index(",")].split(" and ")
            if condition[0].lower().startswith("when "):
                condition = ["when"] + condition
                condition[1] = condition[1][5:]
            if condition[0].lower().startswith("while "):
                condition = ["while"] + condition
                condition[1] = condition[1][6:]

            condition = [x.strip() for x in condition]

            event = line[line.index(",")+1:].split(";")
#            event = line[line.index(",")+1:]
            event = [x.strip().replace("&",";") for x in event]

            rule = [condition, event]
            rules.append(rule)

    return rules
