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

try:
    from xml.dom.ext.reader import Sax2
except:
    print "Ext.reader.Sax2 not found"

footsteps = {
    "GRASS": [
    "F_Grass",
    "F_Grass->Dirttop",
    "F_GrassLedge",
    "F_GrassRedge",
    "F_Grass_Alt_1",
    "F_Grass_Alt_2",
    "F_Grass_Alt_3",
    "F_Grass_Alt_4",
    "F_Grass_Alt_5",
    "F_Grass->DirtL",
    "F_Grass->DirtR",
    "F_Right_Ramp",
    "F_Left_Ramp",
    "F_RampJoinR",
    "F_RampJoinL",
    "F_Right_Halframp1",
    "F_Right_Halframp2",
    "F_Left_Halframp1",
    "F_Left_Halframp2",
    "F_HalframpJoinR",
    "F_HalframpJoinL"
    ],

    "DIRT": [
    "F_Dirttop->Grass",
    "F_Dirttop",

    ],

    "CONCRETE": [
    "C_Castle Floor 1",
    "C_Castle Floor 2",
    "C_Castle Floor 3",
    "C_Castle Floor 4",
    "C_Castle HRmR",
    "C_Castle HRR",
    "C_Castle HRmL",
    "C_Castle HRL",
    "C_Castle Floor Edge R",
    "C_Castle Floor Edge L",

    ],
    "SNOW": [
    "S_Ground1",
    "S_LRamp",
    "S_bLRamp",
    "S_RRamp",
    "S_bRRamp",
    "S_edgeleft",
    "S_edgeright",
    "S_edgewright1",
    "S_edgewright2",
    "S_ECright",
    "S_ECleft",
    "iC_Floor 1",
    "iC_Floor 2",
    "iC_Floor 3",
    "iC_TopR",
    "iC_TopL",
    ],
    }

footstep_types = {}

for key in footsteps:
    for t in footsteps[key]:
        footstep_types[t] = key

alt_fric = {
    "Dirttop": 0.2,

    "S_Ground1": 0.2,
    "S_LRamp": 0.2,
    "S_bLRamp": 0.2,
    "S_RRamp": 0.2,
    "S_bRRamp": 0.2,
    "S_edgeleft": 0.2,
    "S_edgeright": 0.2,
    "S_edgewright1": 0.2,
    "S_edgewright2": 0.2,
    "S_ECright": 0.2,
    "S_ECleft": 0.2,
    "iC_Floor 1": 0.1,
    "iC_Floor 2": 0.1,
    "iC_Floor 3": 0.1,
    "iC_TopR": 0.1,
    "iC_TopL": 0.1,

    }

ramps = {
    "F_Right_Ramp": "RIGHT_INCLINATION",
    "F_Right_Halframp1": "RIGHT_HINCLINATION1",
    "F_Right_Halframp2": "RIGHT_HINCLINATION2",

    "C_Castle HRR": "RIGHT_INCLINATION",
    
    "F_Left_Ramp": "LEFT_INCLINATION",
    "F_Left_Halframp1": "LEFT_HINCLINATION1",
    "F_Left_Halframp2": "LEFT_HINCLINATION2",

    "C_Castle HRL": "LEFT_INCLINATION",
    "S_LRamp": "LEFT_INCLINATION",
    "S_RRamp": "RIGHT_INCLINATION"
    }

backgrounds = [
    "F_Shrooms1", "F_Shrooms2", "F_Shrooms3", "F_Tuft1", "F_Tuft2",
    "F_ExitSign", "F_Stump", "C_Suit of Armour", "S_Tree", "S_Railing_L",
    "S_Railing_1", "S_Railing_2", "S_Railing_R", "S_Stones", "S_Pillar",
    "S_Tree2", "S_Pillartop"
    ]

muststoprain = [
    "F_Stump", "F_Shrooms1", "F_Shrooms3"
    ]

overheads = [
    "A_Foreground_Tile"
    ]

def getalt_fric(ttype):
    global alt_fric
    return alt_fric[ttype]

def bgfortheme(theme):
    return {"Forest": "Background_Forest_Backing.png",
            "Castle": "Background_Forest_Backing.png",
            "Snow": "Background_Snow_Backing.png",
            "Snowcave": "Background_SnowCave_Backing.png",
            }[theme]

def pbgfortheme(theme):
    return {
        "Forest": [
        ["forest_trees_3.png", None, 0.3],
        ["forest_trees_1.png", None, 1],
        ],
        "Castle": [
        ["Background_Castle_Backing.png", None, 1]
        ],
        "Snow": [],
        "Snowcave": [],
        }[theme]

def pfgfortheme(theme):
    return {
    "Forest": [
        ["Forest_Fore1.png", None, 1.5]
        ],
    "Castle": [
        ["Castle-standards.png", None, 1.5],
        ["castle-chains.png", None, 1.8]
        ],
    "Snow": [],
    "Snowcave": [["SC_top.png", None, 1.1]]
    }[theme]

def fallingobjstylefortheme(theme):
    return {
        "Forest": "leaf",
        "Castle": "",
        "Snow": "snowflakes",
        "Snowcave": "",
        }[theme]

def framesfalling(thing):
    return {"leaf": 8,
            "snowflakes": 1}[thing]

def map_to_array(file):
    f = open(file, 'r')
    reader = Sax2.Reader()
    xmldoc = reader.fromStream(f)
    array = [[None for y in range(12)] for x in range(999)]
    row = 0

    for node in xmldoc.childNodes[1].childNodes:
        if node.nodeName == "name":
            levelname = node.firstChild.data
        if node.nodeName == "music":
            bg_music = node.firstChild.data
        if node.nodeName == "theme":
            theme = node.firstChild.data
        if node.nodeName == "row":
            cellc = 0
            for cell in node.childNodes:
                if cell.nodeName == "cell":
                    celldetails = {}
                    for attr in ["map", "object", "enemy"]:
                        temp = cell.attributes.getNamedItem(attr)
                        if temp:
                            celldetails[attr] = temp.value
                    array[cellc][row] = celldetails
                    cellc += 1
            row += 1

    mapinfo = levelname, theme, bg_music
    return array, mapinfo

def def_to_dict(file):
    f = open(file, 'r')
    reader = Sax2.Reader()
    xmldoc = reader.fromStream(f)
    mydict = {}
    myodict = {}
    myedict = {}
    for node in xmldoc.childNodes[1].childNodes:
        if node.nodeName == "image-dictionary":
            for defs in node.childNodes:
                if defs.nodeName == "map":
                    for tiledef in defs.childNodes:
                        if tiledef.attributes:
                            mydict[tiledef.attributes.getNamedItem("name").value] = tiledef.attributes.getNamedItem("filename").value
                elif defs.nodeName == "objects":
                    for objectdef in defs.childNodes:
                        if objectdef.attributes:
                            myodict[objectdef.attributes.getNamedItem("name").value] = objectdef.attributes.getNamedItem("filename").value
                elif defs.nodeName == "enemies":
                    for enemydef in defs.childNodes:
                        if enemydef.attributes:
                            myedict[enemydef.attributes.getNamedItem("name").value] = enemydef.attributes.getNamedItem("prefix").value
    return mydict, myodict, myedict

class Map:
    def __init__(self):
        # Background music to play for level, provided it is loaded
        # Default to None, it is safer.
        self.bgmusic = None
        self.theme = "Forest"
        self.name = "An Untitled Level"
        # Map where each list is a column (x value) and each value in those lists
        # are cells (y value), so in effect, map[x][y] will give map at coord (x,y)
        self.map = [[None for y in range(12)] for x in range(128)]
        self.obj = [[None for y in range(12)] for x in range(128)]        
        self.enemy = [[None for y in range(12)] for x in range(128)]
        self.tiledef = {}
        self.objdef = {}
        self.endef = {}

    def compile_from_xml(self, xml_file):
        print "Making map array..."
        map_array, data = map_to_array(xml_file)
        self.name, self.theme, self.bgmusic = data
        print "Defining..."
        rc = 0
        for row in map_array:
            cc = 0
            for cell in row:
                if type(cell) == dict:
                    if cell.has_key("map"):
                        self.map[rc][cc] = Tile(cell['map'])
                    if cell.has_key("object"):
                        self.obj[rc][cc] = cell['object']
                    if cell.has_key("enemy"):
                        self.enemy[rc][cc] = cell['enemy']
                        
                cc += 1
            rc += 1

    def make_tiledef(self, xml_file):
        self.tiledef, self.objdef, self.endef = def_to_dict(xml_file)

class Tile:
    def __init__(self, tiletype):
        global ramps, backgrounds, overheads, muststoprain
        self.type = tiletype
        self.friction = 1.0
        if alt_fric.has_key(self.type):
            self.friction = alt_fric[self.type]
        if ramps.has_key(self.type):
            self.collidetype = ramps[self.type]
        elif self.type in backgrounds:
            if self.type in muststoprain:
                self.collidetype = "NONE_R"
            else:
                self.collidetype = "NONE"
        else:
            self.collidetype = "BOX"
        self.overhead = self.type in overheads
        
if __name__ == "__main__":
    a_map = Map()
    a_map.compile_from_xml('testmap.xml')
    print "Compiled!"
    while True:
        a = raw_input("x,y: ").split(",")
        print "Type:", a_map.map[int(a[0])][int(a[1])].type
        print "Collision:", a_map.map[int(a[0])][int(a[1])].collidetype
        print "Overhead?", a_map.map[int(a[0])][int(a[1])].overhead
