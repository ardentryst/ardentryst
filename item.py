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

import os

class ItemBox:
    def __init__(self):
        "ItemBox holds all the items, their names, data, frames.. including\
        wearables in the game. It has to be done somewhere..."

        citem = "NULL"
        
        self.ITEM = {}

        for line in open(os.path.join("Base", "items.db"), 'r').readlines():
            line = line.strip()
            if len(line) == 0: continue
            if line[0] == "<":
                citem = line[1:-1]
                self.ITEM[citem] = Item(citem)
            elif line[0] == "#":
                continue
            elif line.lower().startswith("type"):
                self.ITEM[citem].type = " ".join(line.lower().split()[1:])
            elif line.lower().startswith("value"):
                self.ITEM[citem].value = int(line.lower().split()[1])
            elif line.lower().startswith("description"):
                self.ITEM[citem].description = " ".join(line.split()[1:])
            elif line.lower().startswith("hit-sound"):
                self.ITEM[citem].hit_sound = " ".join(line.split()[1:])
            elif line.lower().startswith("on-use"):
                self.ITEM[citem].on_use = " ".join(line.split()[1:])
            elif line.lower().startswith("location"):
                self.ITEM[citem].location = " ".join(line.lower().split()[1:]).capitalize()
            elif line.lower().startswith("range"):
                self.ITEM[citem].range = int("".join(line.lower().split()[1:]))
            elif line.lower().startswith("minrange"):
                self.ITEM[citem].minrange = int("".join(line.lower().split()[1:]))
            elif line.lower().startswith("damage"):
                self.ITEM[citem].damage = int("".join(line.lower().split()[1:]))
            elif line.lower().startswith("time"):
                self.ITEM[citem].time = int("".join(line.lower().split()[1:]))
            elif line.lower().startswith("inv-image"):
                self.ITEM[citem].inv_image = " ".join(line.split()[1:])
            elif line.lower().startswith("arrow"):
                self.ITEM[citem].arrow = " ".join(line.split()[1:])
            elif line.lower().startswith("wearable-image-prefix"):
                self.ITEM[citem].wearable_image_prefix = line.split()[1]
            elif line.lower().startswith("use-prefix"):
                self.ITEM[citem].use_prefix = " ".join(line.split()[1:])
            elif line.lower().startswith("use-sound"):
                self.ITEM[citem].use_sound = " ".join(line.split()[1:])
            elif line.lower().startswith("display"):
                self.ITEM[citem].display = " ".join(line.split()[1:])
            elif line.lower().startswith("magic-drain"):
                self.ITEM[citem].magic_drain = int(line.split()[1])
            elif line.lower().startswith("protection"):
                self.ITEM[citem].protection = int(line.split()[1])
            elif line.lower().startswith("bit"):
                self.ITEM[citem].bits.append(line.split()[1])
            elif line.lower().startswith("usage-bonus"):
                self.ITEM[citem].usage_bonus[line.split()[1].lower()] = int(line.split()[2])
            elif line.lower().startswith("bow"):
                self.ITEM[citem].bow = True
            elif line.lower().startswith("frames"):
                d = line.split()[1:]
                n = d[0]
                a = d[1]
                fs = " ".join(d[2:]).replace("(","").replace(")","").split(",")
                for i in range(len(fs)):
                    fs[i] = fs[i].strip().split()
                    for x in range(3):
                        try:
                            fs[i][x+1] = int(fs[i][x+1])
                        except:
                            print "Item loading failed. Check for extra commas."
                alter = [self.ITEM[citem].Warrior_Frames, self.ITEM[citem].Mage_Frames][{"W":0, "M":1}[n.upper()]]
                alter[a] = fs
#                self.ITEM[citem].wearable_image_prefix = line.split()[1]
#                print "Wearable image prefix:",self.ITEM[citem].wearable_image_prefix

    def Accumulate_Images(self):
        "Finds out every graphic file that is required in this module and passes back as a list."
        Graphics = []
        for key in self.ITEM.keys():
            ci = self.ITEM[key]
            for wkey in ci.Warrior_Frames.keys():
                cfs = ci.Warrior_Frames[wkey]
                for frame in cfs:
                    framefile = ci.wearable_image_prefix + frame[0] + ".png"
                    if framefile not in Graphics:
                        Graphics.append(framefile)
            for mkey in ci.Mage_Frames.keys():
                cfs = ci.Mage_Frames[mkey]
                for frame in cfs:
                    framefile = ci.wearable_image_prefix + frame[0] + ".png"
                    if framefile not in Graphics:
                        Graphics.append(framefile)
#            if ci.inv_image:
#                imagefile = ci.inv_image
#                if imagefile not in Graphics:
#                    Graphics.append(imagefile)
#                    print "a3 ", imagefile
        return Graphics

    def ItemInfo(self, name):
        for i in self.ITEM.keys():
            item = self.ITEM[i]
            if item.name == name:
                return [item.type, item.location, item.value, item.on_use, item.description, item.inv_image,\
                        item.wearable_image_prefix, item.Warrior_Frames, item.Mage_Frames]

    def GetItem(self, name):
        for i in self.ITEM.keys():
            item = self.ITEM[i]
            if item.name == name or item.display == name:
                return item
    

class Item:
    def __init__(self, name):
        self.name = name
        self.type = "NULL"
        self.location = "NULL"
        self.bits = []
        self.minrange = 0
        self.range = 0
        self.damage = 0
        self.time = 0
        self.value = 0
        self.on_use = ""
        self.description = ""
        self.inv_image = ""
        self.wearable_image_prefix = ""
        self.use_prefix = None
        self.display = self.name
        self.magic_drain = 0
        self.protection = 0
        self.bow = False
        self.arrow = ""
        self.use_sound = ""
        self.hit_sound = ""
        self.usage_bonus = {
                            "strength"  : 0,
                            "endurance" : 0,
                            "magic"     : 0,
                            "luck"      : 0
                            }

        self.Warrior_Frames = {}
        self.Mage_Frames = {}

        # Each key in dict, such as "Walking", contains a list of frame
        # information. Each frame has four values of information
        # such as ['1', 10, 5, 0].
        # These numbers represent:
        # Image Suffix, Relative X, Relative Y, Rotation
        # Suffix (then .png) will be appended to Prefix to get the right frame.



