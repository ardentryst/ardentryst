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

import pygame, os, cPickle, sys
from item import *
from loading_screen import *
from helpers import logfile

def load_image(name, colorkey=None, blur = False, prefix = 'Data'):
    fullname = os.path.join(prefix, name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', fullname
        raise SystemExit, message
    if blur:
        image.set_alpha(blur, RLEACCEL)
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    image = image.convert_alpha()
    return image, image.get_rect()

class Storage:
    def __init__(self):
        self.ItemAccumulation = None
        self.imagefiles = [x for x in os.listdir(os.path.join(os.getcwd(), "Data")) if x.lower().endswith(".png")]

        self.invitems = [x for x in os.listdir(os.path.join(os.getcwd(), "Data", "InvItems")) if x.lower().endswith(".png")]

        self.eio = [x for x in os.listdir(os.path.join("Data","ObjectIcons")) if x.endswith(".png")]

        self.images = {}

        self.tilelist = [x for x in os.listdir(os.path.join("Data","tiles")) if x.endswith(".png")]

        self.mag_image_sets = [
            "fire1",
            "burst",
            "ice1",
            "ice2",
            "implosion1",
            ]

        self.mag_sub_img_lists = []

        for mag_image_set in self.mag_image_sets:
            self.mag_sub_img_lists.append([mag_image_set] + [x for x in os.listdir(os.path.join("Data", "Magic", mag_image_set)) if x.lower().endswith(".png")])

        self.mag_images = {}

        self.pframefiles = [
            # Player animation sprites

            "Stopped1.png",
            "Stopped2.png",
            "Stopped3.png",
            "Stopped4.png",
            "Walking1.png",
            "Walking2.png",
            "Walking3.png",
            "Walking4.png",
            "Walking5.png",
            "Walking6.png",
            "Walking7.png",
            "Walking8.png",

            "Jumping1.png",
            "Cast1.png",

            "Attack1.png",
            "Attack2.png",
            "Attack3.png",
            "Attack4.png"
            ]

        self.pframes = {}
        self.pframes2 = {}

#        self.numbers = [str(x) + ".png" for x in range(10)] + \
#                       [str(x) + "b.png" for x in range(10)] + \
#                       [str(x) + "c.png" for x in range(10)]

        self.numbers = [x for x in os.listdir(os.path.join("Data", "Numbers")) if x.endswith(".png")]                       

        self.storysceneimages = [x for x in os.listdir(os.path.join("Data", "StorySceneImages")) if x.endswith(".png")]

        self.SSI = {}

        self.levelfiles = [[x for x in os.listdir(os.path.join("Levels")) if "." not in x]]

        self.levels = {}

        self.SONGS = [(x, x) for x in os.listdir(os.path.join("Music")) if x.endswith(".ogg") or x.endswith(".mp3")]

        self.SOUNDS = [(x, x) for x in os.listdir(os.path.join("Sounds")) if x.endswith(".ogg")]
        self.SOUNDS += [(os.path.join("PYR", x), x) for x in os.listdir(os.path.join("Sounds", "PYR")) if x.endswith(".ogg")]
        self.SOUNDS += [(os.path.join("NYX", x), x) for x in os.listdir(os.path.join("Sounds", "NYX")) if x.endswith(".ogg")]

        self.crawl_npc_files()

        self.Itembox = ItemBox()

        # <-- No more pre-loading filenames.

        self.Monster_Data = {}
        self.animlist = []

        self.stage = 0
        dofinal(self.makefinal())
        self.showload = False

        self.mimages = {}

        self.crown_frames = []

    def crawl_npc_files(self):
        self.npc_image_data = []
        self.npc_face_data = []
        npclist = os.listdir(os.path.join("Data","NPCs","Frames"))
        npcfacelist = os.listdir(os.path.join("Data", "NPCs", "Faces"))
        for npc in npclist:
            for frame in os.listdir(os.path.join("Data","NPCs","Frames",npc)):
                if frame.lower().endswith(".png"):
                    self.npc_image_data.append(npc + "-" + frame)
        for npcface in npcfacelist:
            if npcface.endswith(".png"):
                self.npc_face_data.append(npcface)

    def dostage(self, filename, inc = 1):
        if not self.showload: return
        self.stage += inc
        Update_Loading(self.stage, filename)
        logfile("DATA: Successfully loaded: " + filename)

    def makefinal(self):
        lc = 0
        for x in self.levelfiles:
            for y in x:
                lc += 2
        self.ItemAccumulation = self.Itembox.Accumulate_Images()
        return len(self.imagefiles) + len(self.tilelist) + 4*len(self.pframefiles)+\
                             len(self.ItemAccumulation)+ len(self.numbers) + \
                             len(self.eio) + len(self.storysceneimages) + len(self.invitems) + \
                             sum([len(x)-1 for x in self.mag_sub_img_lists]) + \
                             self.process_monster_file() + len(self.npc_image_data) + \
                             len(self.npc_face_data) + lc

    def process_monster_file(self):
        monfile = open(os.path.join("Base", "monsters.db"), "r")
        data = monfile.readlines()
        monname = None
        mondata = {}
        animlist = []
        msoundlist = []
        for line in data:
            line = line.strip()
            if not line or line[0] == "#": continue
            if line[0] == "<":
                monname = line[1:-1]
                mondata[monname] = {"animations":[], "sounds":{}}
                animlist.append([monname, "static.png"])
                animlist.append([monname, "face.png"])
            if ":" in line:
                var = line[:line.index(":")]
                val = line[line.index(":")+1:]
                
                if var == "animation":
                    frames = int(val[val.index(";")+1:])
                    val = val[:val.index(";")]
                    for x in range(1, frames+1):
                        animlist.append([monname, val+str(x)+".png"])
                    mondata[monname]["animations"].append(val)
                elif var == "sound":
                    sounds = int(val[val.index(";")+1:])
                    val = val[:val.index(";")]
                    mondata[monname]["sounds"][val] = []
                    for x in range(1, sounds+1):
                        msoundlist.append([monname, val+str(x)+".ogg"])
                        mondata[monname]["sounds"][val].append(val+str(x)+".ogg")
                        self.SOUNDS.append((os.path.join("MonsterSounds", monname.lower(),val+str(x)+".ogg"),monname+"_"+val+str(x)+".ogg"))
                    
                else:
                    mondata[monname][var] = val

        self.Monster_Data = mondata

        self.animlist = animlist
        self.msoundlist = msoundlist
        return len(animlist)

    def precache_images(self):
       
        for image in self.imagefiles:
            self.images[image] = load_image(image)
            self.dostage("Image: " + image)
        for image in self.invitems:
            self.images[image] = load_image(image, None, False, os.path.join("Data", "InvItems"))
            self.dostage("Inventory image: " + image)
        for imagedata in self.animlist:
            mon, image = imagedata
            if not self.mimages.has_key(mon): self.mimages[mon] = {}
            self.mimages[mon][image] = load_image(image, None, False, os.path.join("Data", "MonsterFrames", mon.lower()))
            self.dostage("Monster frame: " + mon + "/" + image)
        for mag_image_set in self.mag_sub_img_lists:
            magset = mag_image_set[0]
            for image in mag_image_set[1:]:
                self.mag_images[image] = load_image(image, None, False, os.path.join("Data", "Magic", magset))
                self.dostage("Magic frame: " + image)
        for image in self.storysceneimages:
            self.SSI[image] = load_image(image, None, False, os.path.join("Data", "StorySceneImages"))
            self.dostage("Story scene image: " + image)
        for image in self.eio:
            self.images[image] = load_image(image, None, False, os.path.join("Data", "ObjectIcons"))
            self.dostage("Object icon: " + image)
        for image in self.tilelist:
            self.images[image] = load_image(image, None, False, os.path.join('Data', 'tiles'))
            self.dostage("Tile image: " + image)
        for image in self.numbers:
            self.images[image] = load_image(image, None, False, os.path.join('Data', 'Numbers'))
            self.dostage("Sprite font: " + image)
        for image in self.pframefiles:
            self.pframes[image] = [load_image("T_"+image, None, False, os.path.join('Data','Pyralis')),
                                   load_image("L_"+image, None, False, os.path.join('Data','Pyralis'))]
            self.pframes2[image] = [load_image("T_"+image, None, False, os.path.join('Data','Nyx')),
                                   load_image("L_"+image, None, False, os.path.join('Data','Nyx'))]
            self.dostage("Player animation: " + image, 4)
        for npcdata in self.npc_image_data:
            npcname, framefile = npcdata.split("-")
            self.images["NPC-" + npcname + "-" + framefile] = load_image(
                framefile, None, False, os.path.join("Data", "NPCs", "Frames", npcname))
            self.dostage("NPC Frame: " + npcname + "/" + framefile)
        for npcdata in self.npc_face_data:
            self.images[npcdata] = load_image(
                npcdata, None, False, os.path.join("Data", "NPCs", "Faces"))
            self.dostage("NPC Face: " + npcdata)

        for image in self.ItemAccumulation:
            self.images[image] = load_image(image, None, False, os.path.join('Data', 'Items'))
            self.dostage("Item overlay image: " + image)

    def precache_levels(self):
        for x in range(len(self.levelfiles)):
            for levelfile in self.levelfiles[x]:
                self.levels[levelfile] = cPickle.load(open(os.path.join("Levels", levelfile), "r"))
                self.dostage(levelfile, 2)
