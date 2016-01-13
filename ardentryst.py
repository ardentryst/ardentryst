#!/usr/bin/python
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

import pygame, sys, os, time, cPickle, socket, thread, traceback
import smtplib, email, math, sha, md5

# Above, I import important Python libraries

# The following block of code tries to change the working directory
# to the directory of Ardentryst. This is so that files and data
# can be accessed relative of the Ardentryst base folder.

try:
    if __name__ == "__main__":
        a = sys.argv[0][:sys.argv[0].rindex("ardentryst.py")]
        b = os.getcwd()

        os.chdir(
            os.path.join(
             b,
             a
             )
            )
except:
    pass

HOMEDIRECTORY = os.path.expanduser('~')

try:
    from win32com.shell import shellcon, shell
    HOMEDIRECTORY = shell.SHGetFolderPath(0, shellcon.CSIDL_APPDATA, 0, 0)
 
except ImportError:
    HOMEDIRECTORY = os.path.expanduser("~")

# Credit : http://snipplr.com/view/7354/home-directory-crossos/

SAVEDIRECTORY = os.path.join(HOMEDIRECTORY, ".ardentryst")


try:
    os.stat(SAVEDIRECTORY)
    try:
        # Just in case someone HAS a .ardentryst directory,
        # but didn't make these two.
        os.mkdir(os.path.join(SAVEDIRECTORY, "Saves"))
        os.mkdir(os.path.join(SAVEDIRECTORY, "Screenshots"))
    except:
        pass
except OSError:
    os.mkdir(SAVEDIRECTORY)
    os.mkdir(os.path.join(SAVEDIRECTORY, "Saves"))
    os.mkdir(os.path.join(SAVEDIRECTORY, "Screenshots"))

# If we can't, don't worry about it, and hope its working directory
# has already been set. (This should be fine in 99% of cases.)

VERSION = "20090726 (1.71-Comet Unstable) 1:11 PM AEST"
DVERSION = VERSION[VERSION.index("(")+1:VERSION.index(")")].replace("-", ":")

ALLOWED_OLDER_VERSIONS = [
    "1.7:Warp Speed Stable"
    ]

# This is the importing of my own modules.
from pygame.locals import *
from data import *
from loading_screen import *
from fade import *
from game import *
from play_level import *
from wordwrap import *
from controls import *
from helpers import *

set_savedirectory(SAVEDIRECTORY)

# I log the start of a new run-through. Reset log.txt too.
open(os.path.join(SAVEDIRECTORY, "log.txt"), "w")
logsave(SAVEDIRECTORY)
logfile("*** BEGIN ARDENTRYST LOGFILE ***")
logfile(time.ctime())
logfile("Python " + sys.version.replace("\n", "   "))
logfile("pygame v." + pygame.version.ver)

PLAYLOCALS = {}

# Here I set global values.

GAME_NAME = "Ardentryst"

CREDITS = ["# " + GAME_NAME + " v" + DVERSION,
           "",
           "An Action RPG and Software Major Project by Jordan Trudgett",
           "developed with text-editor GNU Emacs",
           "written in Python with use of pygame libraries",
           "",
           "Project started on 12th October 2007",
           "",
           "",
           "#Lead Game Designer, Storyboarding, Scripting,",
           "#Interface Design, Editor, Musical Talent,",
           "#Project Manager, Lead Game Developer, Project Leader,",
           "#Website Master, Digital Artist",
           "$Jordan Trudgett",
           "",
           "What did you expect? :)",
           "",
           "#Lead Game Artists",
           "$Amy Dunwoodie (Characters and Faces)",
           "$Isaac Nixon (Scenes and Landscapes)",
           "$Kanami Watabe (Items and Objects)",
           "",
           "#Head of Storyline",
           "$Rhys Stamnas",
           "",
           "#Storyline Co-Editor",
           "$Thomas Chiu",
           "",
           "#Voice Talent",
           "$Kendra Pietruszewski as Opening Scene Girl",
           "$Amy Dunwoodie as Nyx",
           "$Jordan Trudgett as Pyralis",
           "",
           "#Sound contribution (freesound.org users)",
           "Creative Commons 3.0 License",
           "$Anton",
           "$acclivity of freesound.org",
           "$adcbicycle",
           "$aust",
           "$Connum",
           "$decembered",
           "$www.digifishmusic.com",
           "$Erdie",
           "$ERH",
           "$FreqMan",
           "$Halion",
           "$HerbertBoland",
           "$inchadney",
           "$laurent",
           "$Leady",
           "$luffy",
           "$martian",
           "$redjim",
           "$reinsamba",
           "$Robinhood76",
           "$sagetyrtle",
           "$Stickinthemud",
           "$themfish",
           "$Wolfsinger",
           "$zebraphone",
           "",
           "#Game Testers",
           "$Blake Jones",
           "$Daniel Reay",
           "$Jabran Chaudhry",
           "$Kieran Frigo",
           "$Mitchell McEwan",
           "$Ranen Trudgett",
           "$Riley Boughton",
           "$Thomas Chiu",
           "",
           "#Game Inspiration",
           "$Muhunthan Jayanthakumaran",
           "$Thomas Chiu",
           "",
           "#Special thanks:",
           "$Simon Liu",
           "$Vitor Bosshard",
           "$Vladimir Slavik",
           "$Ben Trubshaw",
           "$Shelby Sinclair",
           "$All the supporters and players of Ardentryst",
           "$and... you!"
           ]

markdata = {
    "LEVEL": "Mark1.png",
    "LEVELBOSS": "Mark5.png",
    "SAVE" : "Mark2.png",
    "SHOP" : "Mark3.png",
    }

mapdata = [

     [

      "World_Map.png"            , # World Map
    
      {"name": "Sempridge" ,
       "position": (377, 260)    ,
       "up": None                ,
       "down": None              ,
       "left": "Snodom"          , 
       "right": None             ,
       },

      {"name": "Entarya",
       "position": (239, 241)    ,
       "up": None                ,
       "down": None              ,
       "left": None              , 
       "right": "Snodom"         ,
       },

      {"name": "Snodom" ,
       "position": (290, 342)    ,
       "up": "Kiripan"           ,
       "down": None              ,
       "left": "Entarya"         , 
       "right": "Sempridge"      ,
       },

      {"name": "Kiripan",
       "position": (365, 200),
       "down": "Snodom",
       "up": None,
       "left": None,
       "right": None
       },

     ],

     [

      "Map_Sempridge.png"        , # World 1:Sempridge
      
      {"name": "Flerrim's Forest",
       "position": (150, 347)    ,
       "type": "LEVEL"           ,
       "nextloc": None           ,
       "up": "Eternal Boulder"   ,
       "down": None              ,
       "left": "Exitworld"       ,
       "right": None             ,
       "map": "Sempridge1"       ,
      },

      {"name": "Eternal Boulder" ,
       "position": (129, 269)    ,
       "nextloc": "Tropical Track",
       "type": "SAVE"            ,
       "up": None                ,
       "down": "Flerrim's Forest",
       "left": None              ,
       "right": "Tropical Track" ,
       "map": None               ,
      },

      {"name": "Tropical Track"  ,
       "position": (337, 323)    ,
       "type": "LEVEL"           ,
       "nextloc": "Cedar Valley" ,
       "up": "Cedar Valley"      ,
       "down": None              ,
       "left": "Eternal Boulder" ,
       "right": None             ,
       "map": "Sempridge2"       ,
      },

      {"name": "Cedar Valley"    ,
       "position": (305, 179)    ,
       "type": "LEVEL"           ,
       "nextloc": "Wasp Willows" ,
       "up": None                ,
       "down": "Tropical Track"  ,
       "left": "Wasp Willows"    ,
       "right": None             ,
       "map": "Sempridge3"       ,
      },

      {"name": "Wasp Willows"    ,
       "position": (143, 124)    ,
       "type": "LEVEL"           ,
       "nextloc": None           ,
       "up": "Worm Woods"        ,
       "down": None              ,
       "left": "Elchim's Stall",
       "right": "Cedar Valley"   ,
       "map": "Sempridge4"       ,
      },

      {"name": "Worm Woods"      ,
       "position": (105, 38)     ,
       "type": "LEVEL"           ,
       "nextloc": "Bush Battle"  ,
       "up": None                ,
       "down": "Wasp Willows"    ,
       "left": None              ,
       "right": "Bush Battle"    ,
       "map": "Sempridge5"       ,
      },

      {"name": "Bush Battle"     ,
       "position": (380, 100)    ,
       "type": "LEVELBOSS"       ,
       "nextloc": "Exitworld2"   ,
       "up": "Exitworld2"        ,
       "down": None              ,
       "left": "Worm Woods"      ,
       "right": None             ,
       "map": "SempridgeBoss"    ,
      },

      {"name": "Elchim's Stall"  ,
       "position": (53, 209)     ,
       "type": "SHOP"            ,
       "nextloc": None           ,
       "up": None                ,
       "down": None              ,
       "left": None              ,
       "right": "Wasp Willows"   ,
       "map": None               ,
       },

      {"name": "Exitworld"       ,
       "position": (-30, 445)    ,
       "type": "EXIT_WORLD"      ,
       "up": None                ,
       "down": None              ,
       "left": None              ,
       "right": None             ,
       "map": None               ,
      },

      {"name": "Exitworld2"      ,
       "position": (353, -40)    ,
       "type": "EXIT_WORLD2"     ,
       "up": None                ,
       "down": None              ,
       "left": None              ,
       "right": None             ,
       "map": None               ,
      },

     ],
      
     [

      "Map_Entarya.png"          , # Entarya

      {"name": "Castle Centre"   ,
       "position": (50, 45)      ,
       "type": "LEVEL"           ,
       "nextloc": None           ,
       "up": None                ,
       "down": "Castle Keep"     ,
       "left": "Exitworld"       ,
       "right": None             ,
       "map": "Entarya1"         ,
      },

      {"name": "Castle Keep"     ,
       "position": (75, 110)     ,
       "type": "LEVEL"           ,
       "nextloc": "Eternal Boulder",
       "up": "Castle Centre"     ,
       "down": "Eternal Boulder" ,
       "left": None              ,
       "right": None             ,
       "map": "Entarya2"         ,
      },

      {"name": "Eternal Boulder" ,
       "position": (192, 222)    ,
       "nextloc": None,
       "type": "SAVE"            ,
       "up": "Castle Keep"       ,
       "down": None,
       "left": None              ,
       "right": "Tain's Woods"   ,
       "map": None               ,
      },

      {"name": "Tain's Woods"    ,
       "position": (405, 110)    ,
       "type": "LEVEL"           ,
       "nextloc": None           ,
       "up": None                ,
       "down": "Elchim's Shop"   ,
       "left": "Eternal Boulder" ,
       "right": "Shrub Hills"    ,
       "map": "Entarya3"         ,
      },

      {"name": "Elchim's Shop"  ,
       "position": (374, 196)    ,
       "type": "SHOP"            ,
       "nextloc": None           ,
       "up": "Tain's Woods"      ,
       "down": None              ,
       "left": None              ,
       "right": None             ,
       "map": None               ,
       },

      {"name": "Shrub Hills"     ,
       "position": (580, 135)    ,
       "type": "LEVEL"           ,
       "nextloc": "Doom Valley"  ,
       "up": None                ,
       "down": "Doom Valley"     ,
       "left": "Tain's Woods"    ,
       "right": None             ,
       "map": "Entarya4"         ,
      },

      {"name": "Doom Valley"     ,
       "position": (490, 335)    ,
       "type": "LEVEL"           ,
       "nextloc": "Danger Duel"  ,
       "up": "Shrub Hills"       ,
       "down": None              ,
       "left": "Danger Duel"     ,
       "right": None             ,
       "map": "Entarya5"         ,
      },

      {"name": "Danger Duel"     ,
       "position": (190, 335)    ,
       "type": "LEVELBOSS"       ,
       "nextloc": "Exitworld2"   ,
       "up": None                ,
       "down": None              ,
       "left": "Exitworld2"      ,
       "right": "Doom Valley"    ,
       "map": "EntaryaBoss"      ,
      },

      {"name": "Exitworld2"      ,
       "position": (-40, 300)    ,
       "type": "EXIT_WORLD2"     ,
       "up": None                ,
       "down": None              ,
       "left": None              ,
       "right": None             ,
       "map": None               ,
      },

      {"name": "Exitworld"       ,
       "position": (-40, -10)    ,
       "type": "EXIT_WORLD"      ,
       "up": None                ,
       "down": None              ,
       "left": None              ,
       "right": None             ,
       "map": None               ,
      },

     ],
      
     [

      "Map_Snodom.png"           , # Snodom

      {"name": "Frozen Path"     ,
       "position": (180, 75)     ,
       "type": "LEVEL"           ,
       "nextloc": "Chilly Road"  ,
       "up": "Exitworld"         ,
       "down": None              ,
       "left": "Ferna's Stall"   ,
       "right": "Chilly Road"    ,
       "map": "Snodom1"          ,
      },

      {
       "name": "Ferna's Stall",
       "position": (33, 83),
       "type": "SHOP",
       "nextloc": None,
       "up": None,
       "down": None,
       "left": None,
       "right": "Frozen Path",
       "map": None
      },
      
      {"name": "Chilly Road"     ,
       "position": (300, 60)     ,
       "type": "LEVEL"           ,
       "nextloc": "Frosty Frolic",
       "up": None                ,
       "down": None              ,
       "left": "Frozen Path"     ,
       "right": "Frosty Frolic"  ,
       "map": "Snodom2"          ,
      },
      
      {"name": "Frosty Frolic"   ,
       "position": (435, 75)     ,
       "type": "LEVEL"           ,
       "nextloc": None           ,
       "up": None                ,
       "down": "Eternal Boulder" ,
       "left": "Chilly Road"     ,
       "right": "Tyra's Shop"    ,
       "map": "Snodom3"          ,
      },

      {"name": "Eternal Boulder" ,
       "position": (465, 140)    ,
       "nextloc": None           ,
       "type": "SAVE"            ,
       "up": "Frosty Frolic"     ,
       "down": "Gargantuan Glacier",
       "left": None              ,
       "right": None             ,
       "map": None               ,
      },

      {"name": "Tyra's Shop"     ,
       "position": (535, 65)     ,
       "type": "SHOP"            ,
       "nextloc": None           ,
       "up": None                ,
       "down": None              ,
       "left": "Frosty Frolic"   ,
       "right": None             ,
       "map": None               ,
       },

      {"name": "Gargantuan Glacier",
       "position": (485, 190)    ,
       "type": "LEVEL"           ,
       "nextloc": "Mt. Malevolence",
       "up": "Eternal Boulder"   ,
       "down": "Mt. Malevolence" ,
       "left": None              ,
       "right": None             ,
       "map": "Snodom4"          ,
      },

      {"name": "Mt. Malevolence" ,
       "position": (520, 275)    ,
       "type": "LEVEL"           ,
       "nextloc": None           ,
       "up": "Gargantuan Glacier",
       "down": "Death Road"      ,
       "left": None              ,
       "right": None             ,
       "map": "Snodom5"          ,
      },

      {"name": "Death Road"      ,
       "position": (440, 375)    ,
       "type": "LEVEL"           ,
       "nextloc":"Radkelu's Cave",
       "up": "Mt. Malevolence"   ,
       "down": None              ,
       "left": "Radkelu's Cave"  ,
       "right": None             ,
       "map": "Snodom6"          ,
      },

      {"name": "Radkelu's Cave"  ,
       "position": (306, 306)    ,
       "type": "LEVELBOSS"       ,
       "nextloc": "Exitworld2"   ,
       "up": None                ,
       "down": None              ,
       "left": None              ,
       "right": "Death Road"     ,
       "map": "SnodomBoss"       ,
      },

      {"name": "Exitworld"       ,
       "position": (180, -40)    ,
       "type": "EXIT_WORLD"      ,
       "up": None                ,
       "down": None              ,
       "left": None              ,
       "right": None             ,
       "map": None               ,
      },

      {"name": "Exitworld2"      ,
       "position": (306, 306)    ,
       "type": "EXIT_WORLD2"     ,
       "up": None                ,
       "down": None              ,
       "left": None              ,
       "right": None             ,
       "map": None               ,
      },

     ],

     [],
      

    ]

shops = {
    "Elchim's Stall": {
        "Shopfront": "elchim.png",
        "Music": "shop.ogg",
        "Text_Welcome": "Well hello there! You have arrived at $SHOP.",
        "Text_Buy": "What can I interest you in?",
        "Text_Sell": "What have you got for sale?",
        "Text_CantAfford": "That's not enough silver.",
        "Text_CantSell": "I have no use for that.",
        "Text_Howmany": "How many?",
        "Text_Transaction": "Thanks!",
        "Text_Exit": "Come again! Remember to equip your items!",
        "Items": ["Potion", "Potion2", "Mana potion", "Mana potion2", "Silver ring", "Luck charm", "Steel gladius", "Steel cap", "Bronze battle axe2", "Steel halberd2", "Wingboots"],
        "ExchangeRate": 1.1
        },
    "Elchim's Shop": {
        "Shopfront": "elchim.png",
        "Music": "shop.ogg",
        "Text_Welcome": "Greetings ... you are at $SHOP.",
        "Text_Buy": "What would you like to buy?",
        "Text_Sell": "Do you have anything valuable?",
        "Text_CantAfford": "Sorry, you can't afford that.",
        "Text_CantSell": "Why would I want that?",
        "Text_Howmany": "How many will that be?",
        "Text_Transaction": "Thanks a bunch. Remember to equip your items.",
        "Text_Exit": "See you around.",
        "Items": ["Potion", "Potion2", "Mana potion", "Mana potion2", "Silver ring", "Luck charm", "Oak staff", "Blue hood", "Magic crossbow2", "Enchanted sickle2", "Wingboots"],
        "ExchangeRate": 1.1
        },
    "Ferna's Stall": {
        "Shopfront": "snowstall.png",
        "Music": "shop.ogg",
        "Text_Welcome": "Hi there, traveller! What can I get for you?",
        "Text_Buy": "Here are the items I have to offer.",
        "Text_Sell": "What are you going to sell me?",
        "Text_CantAfford": "It looks like you are a bit short on silver.",
        "Text_CantSell": "I think that is better kept with you.",
        "Text_Howmany": "How many?",
        "Text_Transaction": "Thank you, traveller!",
        "Text_Exit": "Good bye, and good luck on your quest!",
        "Items": ["Potion3", "Potion4", "Mana potion3", "Mana potion4","Antidote","Magic crossbow2","Magic crossbow3", "Bronze battle axe3", "Ancient pendant", "Wingboots", "Gripboots", "Rage pendant", "Nature pendant", "Confusion pendant", "Enchanted sickle2", "Enchanted sickle3"],
        "ExchangeRate": 1.1
        },

    "Tyra's Shop": {
        "Shopfront": "snowstall.png",
        "Music": "shop.ogg",
        "Text_Welcome": "Hi there, traveller! What can I interest you in?",
        "Text_Buy": "Here are the items I that have on sale.",
        "Text_Sell": "What can I buy from you?",
        "Text_CantAfford": "Sorry, not enough silver.",
        "Text_CantSell": "You can keep that.",
        "Text_Howmany": "How many?",
        "Text_Transaction": "Thanks!",
        "Text_Exit": "See you later! Remember to equip your items!",
        "Items": ["Crescent staff", "Broadsword", "Green hood", "Wingboots", "Gripboots", "Sorcerers hat", "Steel round helm", "Anneludine platebody", "Anneludine shell platelegs", "Nepthene platebody", "Frost robe", "Frost skirt", "Steel halberd3", "Sorcerers robe", "Sorcerers skirt"],
        "ExchangeRate": 1.1
        }
    }

# Function definitions begin here

def handleException(e):
    global screen, Fonts, PLAYLOCALS, SAVEDIRECTORY
    if len(e.args):
        if e.args[0] == 0: Quit()
    print "An error has occurred. "
    if str(e) not in ["Don't cheat!"]:
        traceback.print_exc()
    traceback.print_exc(file = open(os.path.join(SAVEDIRECTORY, "log.txt"), "a"))
    open("bugreport.txt", "w").write(open(os.path.join(SAVEDIRECTORY, "log.txt"), "r").read())
    
    screen.fill((0, 0, 0))

    if PLAYLOCALS.has_key("game"):
        savefilename = PLAYLOCALS["game"].savefilename[:-4] + "_backup.asf"
    else:
        savefilename = ""
    text = [
        "Ardentryst has experienced an unexpected crash.",
        "Please take the effort to report the bug to the forums at",
        "http://jordan.trudgett.com/",
        "(Quick sign-up required)",
        "",
        "By doing this, you may discover a solution to the bug,",
        "or help us fix it. You can even discuss it with other players!",
        "",
        "Your game has been saved to " + savefilename[:-4],
        "Press Escape or Return to quit."
        ]
    if not savefilename:
        text[8] = ""
    y = 100
    for line in text:
        screen.blit(Fonts[12].render(line, 1, (255, 255, 255)), (50, y))
        y += 25

    if savefilename:
        cPickle.dump(PLAYLOCALS["game"], open(os.path.join(SAVEDIRECTORY, "Saves", savefilename), "w"))

    myflip()
    while True:
        time.sleep(0.1)
        for ev in ge():
            if ev.type == KEYDOWN:
                if ev.key == K_RETURN or ev.key == K_ESCAPE:
                    Quit()

def verify_game(Game):
    template = Game_Object()
    for attr in dir(template):
        if not hasattr(Game, attr):
            setattr(Game, attr, getattr(template, attr))
    lga = len(Game.Accessible)
    if lga < len(template.Accessible):
        Game.Accessible += template.Accessible[lga:]
    for l in range(len(template.Accessible)):
        for x in template.Accessible[l]:
            if x not in Game.Accessible[l]:
                Game.Accessible[l].append(x)
    template = Character()
    for attr in dir(template):
        if not hasattr(Game.playerobject, attr):
            setattr(Game.playerobject, attr, getattr(template, attr))
    Game.playerobject.var_tick(0)
    # check scores and gems are appropriate length
    while len(Game.scores) < len(mapdata[0][1:]):
        Game.scores.append([])
    for w in range(len(mapdata[1:])):
        for l in mapdata[w+1][1:]:
            if len(Game.scores[w]) < len(mapdata[w+1][1:]):
                Game.scores[w].append(0)

    while len(Game.timegems) < len(mapdata[0][1:]):
        Game.timegems.append([])
    for w in range(len(mapdata[1:])):
        for l in mapdata[w+1][1:]:
            if len(Game.timegems[w]) < len(mapdata[w+1][1:]):
                Game.timegems[w].append(0)
        
    return Game

def cleanup(pl):
    """Cleans up player's variables after playing a level"""
    logfile("Cleanup")
    pl.spells = []

def namekey(keyname):
    """Returns the name of a key given the action (e.g. "Up")"""
    global p1c
    return pygame.key.name(p1c[keyname][0]).upper()

def strbon(num):
    """Takes a number, x, and turns it into a "+x", "-x", or "0"."""
    if num > 0:
        return "+" + str(num)
    else:
        return str(num)

def useshop(shop, game, player):
    """Visits a shop."""
    global shops, screen, Data, soundbox, Fonts, p1c
    logfile("Use shop")
    if shops.has_key(shop):
        shopname = shop
        shop = shops[shop]
    else:
        return
    pygame.key.set_repeat(400,50)

    soundbox.FadeoutMusic(1000)
    fade_to_black(screen)
    soundbox.PlaySong(shop["Music"], -1)

    Inshop = True
    selection = 0
    msg = shop["Text_Welcome"]
    vmsg = ""
    cost = 0
    tick = 0
    needfade = True
    wait = 0

    options = [
        "Buy",
        "Sell",
        "Exit"
        ]

    opcurs = 1 # VERY IMPORTANT: STARTS FROM 1..

    ReadyToGo = False
    Buy = False
    Sell = False

    Inventory = [Data.Itembox.GetItem(x) for x in shop["Items"]]
    if player.classtype == 0:
        Inventory = [x for x in Inventory if x.Warrior_Frames or (not x.Warrior_Frames and not x.Mage_Frames)]
    if player.classtype == 1:
        Inventory = [x for x in Inventory if x.Mage_Frames or (not x.Warrior_Frames and not x.Mage_Frames)]

        # These will make sure that the shops do not sell items to a player who cannot use them. :)
        
    pinv = [Data.Itembox.GetItem(x) for x in player.inventory]
    overlay = Data.images[shop["Shopfront"]][0].convert()
    overlay.set_alpha(25)
    MenuDisabled = False
    Howmany = -1
    while Inshop:

        pinvd = {}
        for i in pinv:
            if not i: continue
            if i.display in pinvd:
                pinvd[i.display][0] += 1
            else:
                pinvd[i.display] = [1, i]
        pinvdl = pinvd.keys()
        pinvdl.sort()

        msg = msg.replace("$SHOP", shopname).replace("$COST", str(cost))
        
        ti = pygame.time.get_ticks()
        screen.blit(Data.images[shop["Shopfront"]][0], (0,0))
        if needfade:
            fade_from_black(screen)
            needfade = False
        if wait > 0:
            wait -= 1
        elif len(vmsg) < len(msg):
            vmsg = msg[:len(vmsg)+1]
            wait = 0
            if len(vmsg):
                if vmsg[-1] == " ":
                    wait += 1

        screen.fill((0,0,0), Rect(0, 440, 640, 40))
        fs = Fonts[16].render(vmsg, 1, (255, 255, 255))
        fr = fs.get_rect()
        fr.midleft = (5, 460)
        screen.blit(fs, fr)

        y = 0
        if Buy:
            selection = max(min(selection, len(Inventory)-1), 0)
            pic, picr = Data.images[Inventory[selection].inv_image]
            Howmany = min(Howmany, game.silver / int(Inventory[selection].value*shop["ExchangeRate"]))
        elif Sell:
            selection = max(min(selection, len(pinvdl)-1), 0)
            if len(pinvdl):
                Howmany = min(Howmany, pinvd[pinvdl[selection]][0])
            else:
                Howmany = -1
            if len(pinvdl) == 0: picr = None
            else:
                pic, picr = Data.images[pinvd[pinvdl[selection]][1].inv_image]
        if Buy or Sell:
            screen.fill((0,0,0), Rect(10,60,305,320))
            screen.fill((0,0,0), Rect(325,60,305,320))
            yh_s = Fonts[17].render("You have", 1, (255,255,255))
            yh_r = yh_s.get_rect()

            sp_s = Fonts[16].render(str(game.silver) + " silver pieces", 1, (255,255,255))
            sp_r = sp_s.get_rect()
            yh_r.center = (477, 250)
            sp_r.center = (477, 270)
            screen.blit(yh_s, yh_r)
            screen.blit(sp_s, sp_r)
            if selection < 0: selection = 0

            if Howmany <= -1:
                pc_s = Fonts[16].render("Press " + namekey("B-1") + " to " + ["buy", "sell"][Sell] + " the selected item", 1, (255,255,255))
                pc_r = pc_s.get_rect()
                pc_r.center = (477, 310)
                screen.blit(pc_s, pc_r)

                pb_s = Fonts[16].render("Press " + namekey("B-2") + " to get out of " + ["Buy", "Sell"][Sell] + " mode", 1, (255,255,255))
                pb_r = pb_s.get_rect()
                pb_r.center = (477, 325)
                screen.blit(pb_s, pb_r)

                ii_s = Fonts[16].render("Press " + namekey("B-4") + " for item details", 1, (255,255,255))
                ii_r = ii_s.get_rect()
                ii_r.center = (477, 365)
                screen.blit(ii_s, ii_r)

            if Howmany > -1:
                screen.fill((0,0,0), Rect(80, 395, 80, 40))
                hms = Fonts[16].render("x" + str(Howmany), 1, (255, 255, 255))
                hmr = hms.get_rect()
                hmr.center = (120, 415)
                screen.blit(hms, hmr)

                hmt_s = Fonts[16].render("Directional keys change the amount.", 1, (255,50,50))
                hmt_r = hmt_s.get_rect()
                hmt_r.center = (477, 350)
                screen.blit(hmt_s, hmt_r)

                bi_s = Fonts[16].render("Press " + namekey("B-1") + " to " + ["buy", "sell"][Sell], 1, (255,255,255))
                bi_r = bi_s.get_rect()
                bi_r.center = (477, 310)
                screen.blit(bi_s, bi_r)

                pb_s = Fonts[16].render("Press " + namekey("B-2") + " to cancel the transaction", 1, (255,255,255))
                pb_r = pb_s.get_rect()
                pb_r.center = (477, 325)
                screen.blit(pb_s, pb_r)



            if picr:
                picr.center = (477, 140)
                screen.blit(pic, picr)

            if Sell and Howmany == -1:
                ei_s = Fonts[16].render("Equipped items cannot be sold", 1, (255,255,255))
                ei_r = ei_s.get_rect()
                ei_r.center = (477, 350)
                screen.blit(ei_s, ei_r)
            
        if Buy:
            selection = min(len(Inventory)-1, selection)
            for item in Inventory:
                c = [80, 255][y == selection]
                i_s =  Fonts[16].render(item.display, 1, (c,c,c))
                i_r = i_s.get_rect()
                i_r.midleft = (20, 85 + y * 20)
                p_s =  Fonts[16].render(str(int(item.value*shop["ExchangeRate"])), 1, (c,c,c))
                p_r = p_s.get_rect()
                p_r.midright = (300, 85 + y * 20)
                screen.blit(i_s, i_r)
                screen.blit(p_s, p_r)
                y += 1
            if Howmany > -1:
                screen.fill((0,0,0), Rect(420, 395, 150, 40))
                hms = Fonts[16].render("Costs " + str(Howmany*int(Inventory[selection].value*shop["ExchangeRate"])) + "s", 1, (255, 255, 255))
                hmr = hms.get_rect()
                hmr.center = (495, 415)
                screen.blit(hms, hmr)

        elif Sell:
            selection = min(len(player.inventory)-1, selection)
            for item in pinvdl:
                c = [80, 255][y == selection]
                i_s =  Fonts[16].render(pinvd[item][1].display + " x" + str(pinvd[item][0]), 1, (c,c,c))
                i_r = i_s.get_rect()
                i_r.midleft = (20, 85 + y * 20)
                p_s =  Fonts[16].render(str(max(0, int(pinvd[item][1].value/shop["ExchangeRate"]))), 1, (c,c,c))
                p_r = p_s.get_rect()
                p_r.midright = (300, 85 + y * 20)
                screen.blit(i_s, i_r)
                screen.blit(p_s, p_r)
                y += 1
            if Howmany > -1:
                screen.fill((0,0,0), Rect(420, 395, 150, 40))
                hms = Fonts[16].render("Worth " + str(Howmany*int(pinvd[pinvdl[selection]][1].value/shop["ExchangeRate"])) + "s", 1, (255, 255, 255))
                hmr = hms.get_rect()
                hmr.center = (495, 415)
                screen.blit(hms, hmr)

                

        screen.blit(overlay, (0,0))

        screen.fill((0,0,0), Rect(0, 0, 640, 40))
        c = 130 + math.sin(tick/10.0) * 120
        t_s = Fonts[17].render(shopname, 1, (c, c, c))
        t_r = t_s.get_rect()
        t_r.center = (320, 20)
        screen.blit(t_s, t_r)

        if not MenuDisabled and Howmany == -1:
            o = 1
            for option in options:
                c = 80
                if o == opcurs: c = 255
                fs = Fonts[17].render(option, 1, (0, 0, 0))
                fr = fs.get_rect()
                fr.center = (int(640.0/(len(options)+1)*o),410)
                for x in range(-1, 2):
                    for y in range(-1, 2):
                        screen.blit(fs, fr.move(x, y))
                fs = Fonts[17].render(option, 1, (c, c, c))
                screen.blit(fs, fr)

                o += 1



        for ev in ge():
            if ev.type == KEYDOWN:
                k = ev.key
                if k in p1c["Right"]:
                    if Howmany > -1:
                        Howmany += 1
                    elif not MenuDisabled:
                        opcurs = min(opcurs + 1, len(options))
                        interface_sound("menu-item")
                elif k in p1c["Left"]:
                    if Howmany > -1:
                        Howmany -= 1
                        if Howmany == -1: Howmany = 0
                    elif not MenuDisabled:
                        opcurs = max(1, opcurs - 1)
                        interface_sound("menu-item")
                elif k in p1c["Down"]:
                    if Howmany > -1:
                        Howmany -= 10
                        if Howmany < 0: Howmany = 0
                    elif Buy or Sell and MenuDisabled:
                        selection += 1
                        interface_sound("menu-item")
                elif k in p1c["Up"]:
                    if Howmany > -1:
                        Howmany += 10
                    elif Buy or Sell and MenuDisabled:
                        selection -= 1
                        interface_sound("menu-item")
                elif k in p1c["B-1"]:
                    interface_sound("menu-item")
                    if Buy:
                        if Howmany > -1:
                            # Already prompted
                            if Howmany:
                                player.inventory += [Inventory[selection].name]*Howmany
                                game.silver -= Howmany * int(Inventory[selection].value * shop["ExchangeRate"])
                                msg = shop["Text_Transaction"]
                                pinv = [Data.Itembox.GetItem(x) for x in player.inventory]                                
                                vmsg = ""
                                Howmany = -1
                            else:
                                msg = shop["Text_Buy"]
                                vmsg = ""
                                Howmany = -1

                                
                            options = ["Buy", "Sell", "Exit"]
                            opcurs = 1
                            MenuDisabled = True
                        else:
                            itemch = Inventory[selection]
                            if game.silver >= int(itemch.value * shop["ExchangeRate"]):
                                cost = int(itemch.value * shop["ExchangeRate"])
                                Howmany = 0
                                opcurs = 1
                                msg = shop["Text_Howmany"]
                                vmsg = ""
                            else:
                                msg = shop["Text_CantAfford"]
                                vmsg = ""
                    elif Sell:
                        if not len(pinvdl): continue
                        if Howmany > -1:
                            # Already prompted
                            if Howmany:
                                game.silver += Howmany * int(pinvd[pinvdl[selection]][1].value / shop["ExchangeRate"])
                                sellingitem = pinvd[pinvdl[selection]][1]
                                for x in range(Howmany):
                                    if sellingitem.name in player.inventory:
                                        player.inventory.remove(sellingitem.name)
                                    elif sellingitem.display in player.inventory:
                                        player.inventory.remove(sellingitem.display)
                                    else:
                                        logfile("Cheating? Couldn't remove enough from inventory at shop.")
                                        
                                pinv = [Data.Itembox.GetItem(x) for x in player.inventory]
                                msg = shop["Text_Transaction"]
                                vmsg = ""
                                Howmany = -1
                            else:
                                msg = shop["Text_Sell"]
                                vmsg = ""
                                Howmany = -1
                            options = ["Buy", "Sell", "Exit"]
                            opcurs = 2
                            MenuDisabled = True
                            
                        else:
                            itemch = pinv[selection]
                            if itemch.value <= 0:
                                msg = shop["Text_CantSell"]
                                vmsg = ""
                            else:
                                Howmany = 0
                                opcurs = 2
                                msg = shop["Text_Howmany"]
                                vmsg = ""
                    elif not MenuDisabled:
                        opch = options[opcurs-1]
                        if opch == "Buy":
                            selection = 0
                            Buy = True
                            msg = shop["Text_Buy"]
                            vmsg = ""
                            MenuDisabled = True
                        elif opch == "Sell":
                            selection = 0
                            Sell = True
                            msg = shop["Text_Sell"]
                            vmsg = ""
                            MenuDisabled = True
                        elif opch == "Exit":
                            ReadyToGo = True
                            MenuDisabled = True
                            msg = shop["Text_Exit"]
                            vmsg = ""
                elif k in p1c["B-2"] and not ReadyToGo:
                    if Howmany > -1:
                        Howmany = -1
                        msg = shop["Text_Buy"]
                        vmsg = ""
                    else:
                        if Buy or Sell or MenuDisabled or Howmany > -1:
                            vmsg = ""
                        interface_sound("menu-item")
                        Buy = False
                        Sell = False
                        msg = shop["Text_Welcome"]
                        options = ["Buy", "Sell", "Exit"]

                        MenuDisabled = False
                elif k in p1c["B-4"] and not ReadyToGo and Howmany == -1:
                    if not Buy and not Sell:
                        continue
                    if Buy:
                        selobj = Inventory[selection]
                    elif Sell:
                        if not len(pinvdl):
                            continue
                        selobj = pinvd[pinvdl[selection]][1]

                    showing = True
                    information = [
                        "Item: " + selobj.display,
                        "Description: " + selobj.description,
                        ]
                    if selobj.damage: information.append("Damage: " + str(selobj.damage))
                    if selobj.time: information.append("Recovery time: " + str(selobj.time))
                    if selobj.minrange: information.append("Minimum range: " + str(selobj.minrange))
                    if selobj.range: information.append("Maximum range: " + str(selobj.range))
                    if selobj.magic_drain: information.append("Magic drain: " + str(selobj.magic_drain))
                    if selobj.protection: information.append("Resistance: " + strbon(selobj.protection))                    

                    for key in ["strength", "endurance", "magic", "luck"]:
                        if selobj.usage_bonus[key]: information.append(key.capitalize() + " " + strbon(selobj.usage_bonus[key]))                    

                    sinfo = []
                    
                    for i in information:
                        surflist = string_to_paragraph(i, Fonts[17], 1, (255, 255, 255), 400)
                        sinfo.append(surflist)

                    bs = Fonts[17].render("Press " + namekey("B-2") + " to go back", 1, (180,180,180))
                    br = bs.get_rect()
                    br.midright = (630, 460)
                    
                    while showing:
                        ti = pygame.time.get_ticks()
                        screen.fill((0,0,0))
                        screen.blit(bs, br)
                        if picr:
                            screen.blit(pic, picr)

                        y = 0
                        for l in sinfo:
                            for s in l:
                                r = s.get_rect()
                                r.midleft = (10, 25 + y * 25)
                                screen.blit(s, r)
                                y += 1

                        myflip()
                        ti = wait_tick(ti)

                        for e in ge():
                            if e.type == KEYDOWN:
                                k = e.key
                                if k in p1c["B-2"]:
                                    showing = False
                                

        tick += 1
        ti = wait_tick(ti)
        myflip()
        
        if vmsg == msg:
            if ReadyToGo:
                soundbox.FadeoutMusic(2000)
                csleep(3)
                Inshop = False

    fade_to_black(screen)
    pygame.key.set_repeat()

def interface_sound(sound):
    """Plays an interface sound. Keeps raw filenames out of the mix as much as possible."""
    global soundbox

    code = {"error": "fail.ogg",
            "menu-item": "menu-item.ogg",
            "menu-select": "menu-select.ogg",
            "menu-back": "menu-back.ogg",
            "menu-small-select": "menu-small-select.ogg",
            }
    
    soundbox.PlaySound(code[sound.lower()])

class ac:
    # Controls AC
    def __init__(self):
        self.cf = [os.path.join("esaB"[::-1], x) for x in os.listdir("esaB"[::-1])] + [os.path.join("sleveL"[::-1], x) for x in os.listdir("sleveL"[::-1])]
        self.cf += ["yp.tsyrtnedra"[::-1], "yp.level_yalp"[::-1], "yp.cigam"[::-1], "yp.iaymene"[::-1]]
        self.dgests = dict.fromkeys(self.cf, "")
    def cds(self):
        self.cf.sort()
        print
        bh = ""
        mym = globals()["".join([chr(x) for x in [109, 100, 53]])]
        mys = globals()["".join([chr(x) for x in [115, 104, 97]])]
        exec("".join([chr(ord(x)+1) for x in "rdke-cfdrsr\x1f<\x1fbOhbjkd-kn`c'nodm'!chf-chf!+\x1f!q!(("]))
        rv = 1
        for f in self.cf:
            try:
                sh = getattr(mys.new(getattr(mym.new(open(f, "r").read()), "tsegidxeh"[::-1])()[::-1]), "tsegidxeh"[::-1])()
                bh += sh
                if self.dgests[f] != sh:
                    logfile(chr(42)+ " " + f +  ".erocs ruoy daolpu ot elba eb ton lliw uoY .elif lanigiro eht ton si "[::-1])
                    rv = len(f)^len(f)
                
            except Exception, e:
                pass
        return rv or cmp(len(f)^(len(f)), 0), getattr(mym.new(bh), "tsegidxeh"[::-1])()

def initscreen(screen, font):
    """Draw the screen prior to playing. This is only useful if DEBUG == True"""
    global VERSION
    dinfo = pygame.display.Info()

    lh = 30
    
    infolist = [
        VERSION,
        "",
        "OS Type: " + os.name,
        "Video memory allocated: " + str(dinfo.video_mem or "Unknown") + " Kb",
        "Bit depth: " + str(dinfo.bitsize or "Unknown"),
        "Hardware acclerated? " + str(dinfo.hw),
        "Display driver: " + pygame.display.get_driver()
        ]
    for x in range(len(infolist)):
        screen.blit(font.render(infolist[x], 1, (255,255,255)), (10,10+x*lh))
        print infolist[x]

    myflip()
    time.sleep(2)

def Game_SlotMenu(gameobj = None):
    """Allows the player to create new game saves or load old ones."""
    global screen, Data, Fonts, p1c, soundbox, DVERSION, shc, ACC
    logfile("Entered slotmenu with parameter " + str(gameobj))
    Title = "Game Menu"
    NumSlots = 11 # Number of slots visible on the screen
    ge()
    newgame = False
    if gameobj: newgame = True
    mature = False
    inslotmenu = True
    dark = pygame.Surface((640,480))
    dark.set_alpha(180)
    savedir = os.path.join(SAVEDIRECTORY, "Saves")
    if not os.path.isdir(savedir):
        try:
            os.mkdir(savedir)
        except:
            raise Exception("Do not have a file called Saves in your ~/.ardentryst directory.")
    gamelist = [x for x in os.listdir(savedir) if x.endswith(".asf")]

    gamelist.sort(lambda x, y: cPickle.load(open(os.path.join(SAVEDIRECTORY, "Saves", x),"r")).startdate < cPickle.load(open(os.path.join(SAVEDIRECTORY, "Saves", y),"r")).startdate)

    cursor = 0
    csurf = Data.images["Menupiece.png"][0]
    crect = csurf.get_rect()

    instructions = "Choose the save file. Enter/Return selects, Esc exits. Shift+Del deletes file immediately!"

    tick = 0
    passwordstage = 0

    pygame.key.set_repeat(300, 50)

    scroll_factor = 0

    if newgame:
        gamelist.append("")
        cursor = len(gamelist) -1
        instructions = "Type the name of the new save file, then press Enter/Return. Esc exits."
        title = "New Quest"
    else:
        if len(gamelist) == 0:
            return
        title = "Resume Quest"
        try:
            gameobj = cPickle.load(open(os.path.join(SAVEDIRECTORY, "Saves", gamelist[0]),"r"))
        except:
            raise Exception("Corruption. Delete all saves you don't need in ~/.ardentryst/Saves directory")

    lasttick = pygame.time.get_ticks()

    password_prompt = ""
    password = ""

    firstpass = ""
    secondpass = ""

    incompat = False
    cursloaded = False

    while inslotmenu:
        #Background
        screen.blit(Data.images["Menu_Static.png"][0], (0,0))
        screen.blit(dark, (0,0))

        #Title
        titlerender = Fonts[14].render(title, 1, (255,255,255))
        titlerect = titlerender.get_rect()
        titlerect.center = (320, 50)
        screen.blit(titlerender, titlerect)


        if password_prompt != "":
            p_prompt_s = Fonts[16].render(password_prompt, 1, (255,255,255))
            p_prompt_r = p_prompt_s.get_rect()
            p_prompt_r.midleft = (200, 100 + cursor * 25 - scroll_factor * 25)
            screen.blit(p_prompt_s, p_prompt_r)

            p_entry_s = Fonts[16].render("+" * len(password), 1, (255,255,255))
            p_entry_r = p_entry_s.get_rect()
            p_entry_r.midleft = p_prompt_r.midright
            p_entry_r.move_ip(15,0)
            screen.blit(p_entry_s, p_entry_r)

        more_arrow_visible = False

        for x in range(len(gamelist)):
            torender = gamelist[x]
            if gamelist[x].endswith(".asf"):
                torender = gamelist[x][:-4]
            gsw = Fonts[16].render(torender+["","_"][newgame and (tick/20)%2 and x == cursor and not passwordstage], 1, (255,255,255))
            gsb = Fonts[16].render(torender+["","_"][newgame and (tick/20)%2 and x == cursor and not passwordstage], 1, (  0,  0,  0))
            gsr = gsw.get_rect()
            gsr.midleft = (70, 100 + x * 25 - scroll_factor * 25)
            if gsr.bottom < 450:
                screen.blit(gsb, gsr)
                screen.blit(gsw, gsr.move(-2,-2))
            else:
                more_arrow_visible = True
        crect.midleft = (65, 100 + cursor * 25 - scroll_factor * 25)
        screen.blit(csurf, crect)

        if more_arrow_visible:
            arrow, arrowrect = Data.images["Arrowmore.png"]
            arrowrect.center = (130, 450 + math.sin(tick/10.0)*5)
            screen.blit(arrow, arrowrect)

        hand, handr = Data.images["hand.png"]
        hand = pygame.transform.flip(hand, True, False)

        handr.midright = (60+abs(math.sin(tick/10.0))*10.0, 100 + cursor * 25 - scroll_factor * 25)
        screen.blit(hand, handr)

        inw = Fonts[9].render("Instructions: " + instructions, 1, (255,255,255))
        inb = Fonts[9].render("Instructions: " + instructions, 1, (  0,  0,  0))
        inr = inw.get_rect()
        inr.center = (320, 470)
        screen.blit(inb, inr)
        screen.blit(inw, inr.move(-1,-1))

        # Status side

        if not newgame:

            portrait = Data.images[gameobj.character+"_Head.png"]
            portraitr = portrait[1]
            portrait = portrait[0]

            portraitr.center = (480, 150)
            screen.blit(portrait, portraitr)

            charname = Fonts[16].render("(" + [gameobj.character,"..."][gameobj.character=="Nobody"] + ")", 1, (255,255,255))
            charrect = charname.get_rect()
            charrect.center = portraitr.midbottom
            charrect.move_ip(0, 22)
            screen.blit(charname, charrect)

            # info

            if gameobj.location[1]:
                place = "in " + mapdata[0][gameobj.location[0]]["name"] + ": " + mapdata[gameobj.location[0]][gameobj.location[1]]["name"]
            else:
                place = "around " + mapdata[0][gameobj.location[0]]["name"]
            if type(gameobj.startdate) == str:
                gameobj.startdate = 0
            info = [
                "(v." + gameobj.version + ")",
                "started on " + time.ctime(gameobj.startdate),
                "Last seen " + place,
                "Level:" + str(gameobj.playerobject.level)
                ]

            c = 0

            for line in info:
                line_s = Fonts[13].render(line, 1, (255,255,255))
                line_r = line_s.get_rect()
                line_r.center = portraitr.midbottom
                line_r.move_ip(0, 50 + c*20)
                screen.blit(line_s, line_r)
                c += 1

            # ->>> 

        if not mature:
            mature = True
            fade_from_black(screen)

        myupdate([Rect(0,0,200,480),Rect(0,60,640,420)])

        for e in ge():
            if e.type == KEYDOWN:
                k = e.key
                if k in p1c["Up"]:
                    if cursor > 0 and not newgame:
                        cursor -= 1
                        interface_sound("menu-item")
                        cursloaded = False
                        incompat = False
                elif k in p1c["Down"]:
                    if cursor < len(gamelist)-1:
                        cursor += 1
                        interface_sound("menu-item")
                        cursloaded = False
                        incompat = False
                elif k == K_DELETE and pygame.key.get_mods() & KMOD_SHIFT:
                    if gamelist[cursor]:
                        interface_sound("menu-select")
                        os.remove(os.path.join(SAVEDIRECTORY, "Saves", gamelist[cursor]))
                        gamelist = [x for x in os.listdir(os.path.join(SAVEDIRECTORY, "Saves")) if x.endswith(".asf")]
                        cursor = min(cursor, len(gamelist)-1)
                        cursloaded = False
                        incompat = False
                elif k == K_ESCAPE:
                    password = ""
                    if passwordstage:
                        passwordstage = 0
                        password_prompt = ""
                        if newgame:
                            instructions = "Type the name of the new save file, then press Enter/Return. Esc exits."
                        else:
                            instructions = "Choose the save file to play. Press Enter/Return to select. Esc exits."
                    else:
                        interface_sound("menu-back")
                        return False

                if k == K_RETURN or k == K_KP_ENTER:
                    if newgame:
                        if len(gamelist[-1]) < 2:
                            instructions = "Your name is too short. Type at least two characters."
                            interface_sound("error")
                        elif gamelist[-1].lower()+".asf" in [x.lower() for x in gamelist[:-1]]:
                            instructions = "That name is already taken."
                            interface_sound("error")
                        else:
                            if passwordstage == 2:
                                # Password given.
                                secondpass = password
                                if firstpass == secondpass:
                                    # passwords match
                                    inslotmenu = False
                                    gameobj.savefilename = gamelist[-1]+".asf"
                                    gameobj.password = md5.new(secondpass).hexdigest()
                                    gameobj.startdate = time.time()
                                    gameobj.version = DVERSION
                                    interface_sound("menu-small-select")
                                else:
                                    password = ""
                                    passwordstage = 1
                                    instructions = "The two passwords did not match. [Esc cancels]"
                                    password_prompt = "Your password:"
                            elif passwordstage == 1:
                                # Just entered initial password.
                                firstpass = password
                                if firstpass == "":
                                    passwordstage = 2
                                    password_prompt = "Confirm blank password?"
                                    instructions = "Press Enter/Return if you don't want a password, otherwise type something"
                                password = ""
                                password_prompt = "Confirm that password:"
                                passwordstage = 2
                                instructions = "Type it again to make sure it is correct. [Esc cancels]"
                            elif passwordstage == 0:
                                # Just entered name.
                                passwordstage = 1
                                password_prompt = "Your password:"
                                instructions = "Create a password to protect your game file. Leave blank for no password [Esc cancels]"
                            
                if (k in p1c["B-1"] or k == K_KP_ENTER or k == K_RETURN) and not newgame:
                    if gameobj.version != DVERSION and gameobj.version not in ALLOWED_OLDER_VERSIONS and k != K_KP_ENTER:
                        # You can press Numpad Enter to bypass this check, however it is not recommended unless you know
                        # what you're doing.
                        instructions = "This gamefile is incompatible."
                        interface_sound("error")
                        continue
                    if passwordstage == 1 or gameobj.password == "d41d8cd98f00b204e9800998ecf8427e": # (blank)
                        # Password just entered for loading
                        if md5.new(password).hexdigest() == gameobj.password:
                            inslotmenu = False
                            interface_sound("menu-select")
                    elif passwordstage == 0:
                        # Just chose a file with a password
                        password_prompt = "Password:"
                        passwordstage = 1
                        instructions = "You must enter the password for this file to play it."
                        continue
                        

                if newgame:
                    if passwordstage == 0:
                        #i.e. typing in a name:
                        cursor = len(gamelist) -1
                        if typekey(k): gamelist[-1] += typekey(k)
                        elif k == K_BACKSPACE:
                            gamelist[-1] = gamelist[-1][:-1]
                        elif k == K_SPACE:
                            gamelist[-1] += " "

                        gamelist[-1] = gamelist[-1][:15]
                    elif passwordstage > 0:
                        #i.e. typing in a password for a new file
                        if typekey(k): password += typekey(k)
                        elif k == K_BACKSPACE:
                            password = password[:-1]
                        elif k == K_SPACE:
                            password += " "
                elif passwordstage > 0:
                    #i.e. typing in a password for a file being loaded
                    if typekey(k): password += typekey(k)
                    elif k == K_BACKSPACE:
                        password = password[:-1]
                    elif k == K_SPACE:
                        password += " "


        # scroll codestart

        if cursor > NumSlots + scroll_factor:
            scroll_factor = (scroll_factor*9 + (cursor - NumSlots))/10.0
        if cursor < scroll_factor:
            scroll_factor = (scroll_factor*9 + cursor)/10.0

        # scroll code end

        tick += 1
        lasttick = wait_tick(lasttick)

        if not newgame and not cursloaded:
            gameobj = cPickle.load(open(os.path.join(SAVEDIRECTORY, "Saves", gamelist[cursor]),"r"))
            cursloaded = True

    pygame.key.set_repeat()
    gameobj.shc = shc
    gameobj.ACC = ACC
    if not ACC:
        gameobj.hc = True
    return gameobj

def typekey(k):
    """Checks if a key can be typed and if so, return it."""
    pkgp = pygame.key.get_pressed()
    pknk = pygame.key.name(k)
    banned = ["/", "\\", ".", ",",
              ";", "-", "=", "'", "`"]
    if len(pknk) == 1:
        if pknk in banned:
            return ""
        if pkgp[K_LSHIFT] or pkgp[K_RSHIFT]:
            return pknk.upper()
        else:
            return pknk.lower()

    return False

def choose_character(screen):
    """Function to choose which character to play."""
    global Data, Fonts, soundbox, p1c

    temp_char = Character() # To leech data from

    tick = 0
    CHAR = 0

    NAME = [
        "Pyralis",
        "Nyx"
        ]

    PORTRAIT = [
        "Portrait_" + NAME[0] + ".png",
        "Portrait_" + NAME[1] + ".png"
        ]

    HEAD = [
        NAME[0] + "_Head.png",
        NAME[1] + "_Head.png"
        ]

    DESC = [
        "Pyralis, the 12-Arden-year old brave adventurer, loves catching butterflies- but don't"
        " let his gentle nature misguide you! He can be a ferocious warrior in battle; his physical"
        " and solar-oriented spiritual power overwhelms those around him in his hometown, Sempridge."
        " Only recently has he discovered, through Nyx's advisors, that his parents were killed in"
        " the Nightbringer's attack on Kiripan. He swears to avenge them. Pyralis recovers HP at an increased rate."
        " Pyralis begins in Sempridge.",

        "A bookworm by nature, Nyx is the astrological queen of the era. Her knowledge of stars and"
        " planets in the sky gives her an exceptional connection with the gods. Her magical power"
        " runs through her half-Kiripian blood, in touch with lunar magicks. As Queen Amee's 13-"
        "Arden-year old daughter, she is an important mage in Ardentrystian history. Nyx recovers MP at an increased rate."
        " Nyx begins in Entarya."
        ]

    charpic, charrect = Data.images[PORTRAIT[0]]
    if Data.images[PORTRAIT[1]][1][2] > charrect[2]:
        charrect = Data.images[PORTRAIT[1]][1]

    charrect.midleft = (10,240) # 10 px from edge
    headpic, headrect = Data.images[HEAD[CHAR]]
    headrect.topleft = charrect.topright
    headrect.move_ip(10,0) # to get that 10px border
    namesurf = Fonts[14].render(NAME[CHAR], 1, (255,255,255))
    namerect = namesurf.get_rect()
    namerect.top = headrect.bottom
    namerect.centerx = (charrect.right + 640) / 2 # Average of Charrect.right and 640
    namerect.move_ip(0, 10) # to get that 10px border

    DESCSURFS = [
        string_to_paragraph(DESC[0], Fonts[13], 1, (255,255,255), 640 - 20 - charrect.right),
        string_to_paragraph(DESC[1], Fonts[13], 1, (255,255,255), 640 - 20 - charrect.right)
        ]

    Chosen = False
    maxstat = 18
    full_length = 200
    calpha = 0

    word_stats_surf = Fonts[13].render("Stats", 1, (255,255,255))
    word_stats_rect = word_stats_surf.get_rect()
    word_stats_rect.midtop = namerect.midtop
    word_stats_rect.top = 10

    return_surf = Fonts[9].render("Press Return or " + namekey("B-1") + " to choose this character", 1, (255,255,255))
    return_rect = return_surf.get_rect()
    return_rect.bottomright = (635, 475)

    icons = [
        Data.images["Stat_Icon_Sword.png"],
        Data.images["Stat_Icon_Heart.png"],
        Data.images["Stat_Icon_Magic.png"]
        ]

    bgs = [
        Data.images["redbg.png"][0].convert(),
        Data.images["bluebg.png"][0].convert()
        ]

    stats = []
    realstats = getattr(temp_char, ['WARRIOR_BASE', 'MAGE_BASE'][CHAR])[:3]

    pygame.event.clear()

    needfade = True

    while True:
        t = pygame.time.get_ticks()

        bgs[0].set_alpha(calpha)
        screen.blit(bgs[1], (-tick%640,0))
        screen.blit(bgs[1], (-tick%640-640,0))
        screen.blit(bgs[0], (-tick%640,0))
        screen.blit(bgs[0], (-tick%640-640,0))

        if not stats:
            stats = realstats
        else:
            stats[0] = (realstats[0] + stats[0] * 5)/6.0
            stats[1] = (realstats[1] + stats[1] * 5)/6.0
            stats[2] = (realstats[2] + stats[2] * 5)/6.0

        sc = 0
        for stat in stats:
            statrect = pygame.Rect(0,0,full_length/float(maxstat) * stat,12)
            statrect.topleft = headrect.topright
            statrect.move_ip(35, 25 + sc*20)
            screen.fill((255-(255.0/maxstat)*stat*0.75,(255.0/maxstat)*stat*0.75,0), statrect.inflate(6,6))
            screen.fill((255-(255.0/maxstat)*stat,(255.0/maxstat)*stat,0), statrect)

            iconsurf, iconrect = icons[sc]
            iconrect.midright = statrect.midleft
            iconrect.move_ip(-7,0)

            screen.blit(iconsurf, iconrect)

            stattext = [" strength", " endurance", " magic"][sc]
            rstat = int(realstats[sc])
            snumsurf = Fonts[9].render(str(rstat) + stattext, 1, (255,255,255))
            snumsurfb = Fonts[9].render(str(rstat) + stattext, 1, (0,0,0))
            snumrect = snumsurf.get_rect()
            snumrect.midleft = statrect.midright
            snumrect.move_ip(5,0)
            screen.blit(snumsurfb, snumrect.move(1,1))
            screen.blit(snumsurf, snumrect)
            sc+=1


        charpic = Data.images[PORTRAIT[CHAR]][0] # Omitting charrect.midleft..
                                                 # assumes portraits are = in size
        headpic = Data.images[HEAD[CHAR]][0]     # same here

        namesurf = Fonts[14].render(NAME[0], 1, (255,255,255))
        namerect = namesurf.get_rect()
        namerect.top = headrect.bottom
        namerect.centerx = (charrect.right + 640) / 2 # Average of Charrect.right and 640
        namerect.move_ip(-((640-charrect.right)/3), 10) # to get that 10px border, and move it left

        namesurf2 = Fonts[14].render(NAME[1], 1, (255,255,255))
        namerect2 = namesurf2.get_rect()
        namerect2.top = headrect.bottom
        namerect2.centerx = (charrect.right + 640) / 2 # Average of Charrect.right and 640
        namerect2.move_ip(((640-charrect.right)/3), 10) # to get that 10px border, and move it right

        # the namesurf stuff above is a bit of a bother, but shouldn't be too slow.

        if CHAR == 0:
            hand = Data.images["hand.png"][0]
            handrect = hand.get_rect()
            handrect.midleft = namerect.midright
            handrect.move_ip(20+abs(math.sin(tick/10.0)*10),0)
        else:
            hand = pygame.transform.flip(Data.images["hand.png"][0], True, False)
            handrect = hand.get_rect()
            handrect.midright = namerect2.midleft
            handrect.move_ip(-20-abs(math.sin(tick/10.0)*10),0)

        screen.blit(headpic, headrect)
        screen.blit(namesurf, namerect)
        screen.blit(namesurf2, namerect2)
        screen.blit(hand, handrect)
        screen.blit(word_stats_surf, word_stats_rect)
        screen.blit(return_surf, return_rect)


        for x in range(len(DESCSURFS[CHAR])):
            screen.blit(DESCSURFS[CHAR][x], (charrect.right + 10, headrect.bottom + 50 + 17 * x))

        if needfade:
            fade_from_black(screen)
            needfade = False
 
        calpha = max(0, min(255, calpha+[10,-10][CHAR]))
        screen2 = pygame.Surface((640,480))
        screen2.blit(screen, (0,0))
        screen2.set_alpha([255-calpha,calpha][CHAR])
        screen.blit(charpic, charrect)
        screen.blit(screen2, charrect, charrect)
        screen2.set_alpha(None)
 
        myflip()

        if Chosen: break

        for event in ge():
            if event.type == KEYDOWN:
                key = event.key
                if key == K_ESCAPE:
                    return 0
                if key == K_RIGHT or key == K_LEFT or key in p1c["Left"] or key in p1c["Right"]:
                    interface_sound("menu-item")
                    CHAR = abs(CHAR - 1)
                    realstats = getattr(temp_char, ['WARRIOR_BASE', 'MAGE_BASE'][CHAR])[:3]
                elif key == K_RETURN or key == K_SPACE or key == K_KP_ENTER or key in p1c["B-1"]:
                    interface_sound("menu-small-select")
                    Chosen = True
                    break

        t = wait_tick(t)
        tick += 1


    return ["Pyralis", "Nyx"][CHAR]

def PlaceHolderScreen(screen, fonts, msg = None):
    """A place holder screen so that going to parts of the game won't crash it (its a stub.)"""
    nscreen = screen.copy()
    nscreen.fill((0,0,0))
    viewmsg = "Sorry, this feature is not implemented yet! Press a key."
    if msg: viewmsg = msg
    TRS = fonts[13].render(viewmsg, 1, (255,255,255))
    # Oh, by the way, TRS stands for Text:Rendered(Surface)
    TRR = TRS.get_rect() # And this one is Text:Rendered(Rect)
    TRR.center = (320, 240)
    
    
    nscreen.blit(TRS, TRR)
    fade_screens(screen, nscreen)
    ge()
    Waiting = True
    while Waiting:
        for e in ge():
            if e.type == KEYDOWN:
                Waiting = False

def design_character(Game, player):
    """A function that allows the player to design their character"""
    global screen, Data, Fonts, soundbox, p1c
    who = Game.character
    CHARNAME = Fonts[10].render(who, 1, (255,255,255))
    CHARNAMERECT = CHARNAME.get_rect()
    STATS = Fonts[10].render("Stats", 1, (255,255,255))
    STATSRECT = STATS.get_rect()

    bgs = [
    Data.images["vert_redbg.png"][0],
    Data.images["vert_bluebg.png"][0]
    ]

    bgs2 = [
    Data.images["redbg.png"][0],
    Data.images["bluebg.png"][0]
    ]

    darksurf = pygame.Surface((640,480))
    darksurf.set_alpha(100)

    anims = {"Walking": 8,
             "Stopped": 4}

    canims = anims.keys()
    cframes = [Data.pframes, Data.pframes2][player.classtype]
    ca = 0

    PLAYERSURF = pygame.Surface((400, 200))
    PLAYERSURF.set_colorkey((255,0,255))

    wchosen = 0
    weapons = [
    # Warrior weapons
    [
        ("Bronze gladius", "BronzeGladius.png"),
        ("Bronze battle axe", "BronzeBattleAxe.png"),
        ("Steel halberd", "SteelHalberd.png")
    ],
    # Mage weapons
    [
        ("Training staff", "StaffA.png"),
        ("Magic crossbow", "Crossbow.png"),
        ("Enchanted sickle", "EnchantedSickle.png")
    ]
    ][who == "Nyx"]


    STATS_LIST = [
        "Health",
        "Mana",
        "Strength",
        "Luck"
        ]

    STATS_SURFS = []
    P_REM = 12
    # P_REM means Points Remaining

    for stat in STATS_LIST:
        STATS_SURFS.append(Fonts[12].render(stat, 1, (255,255,255)))

    ih = 35

    Bonuses = [0,0,0,0]

    ih2 = 50
       
    ALLOTPHASE = True
    Cursor = 0
    CURS_SURF = pygame.Surface((368, ih2))
    CURS_SURF.fill((255,255,255))
    CURS_SURF.set_alpha(100)

    tick = 0

    ge() # Flush events that allow player to change settings before seeing them

    while ALLOTPHASE:
        t = pygame.time.get_ticks()
        tick += 1
        screen.fill((0,0,0))
        screen.blit(bgs2[not player.classtype], (-tick%640,0))
        screen.blit(bgs2[not player.classtype], (-tick%640-640,0))

        screen.blit(bgs[player.classtype], (0,-tick%480))
        screen.blit(bgs[player.classtype], (0,-tick%480-480))
        screen.blit(darksurf, (0,0))

        ALLOTSURF = Fonts[10].render("Distribute points to these areas.", 1, (255,255,255))
        ALLOTSURF2 = Fonts[12].render("Decide where " + who + "'s strong points are.", 1, (255,255,255))
        ALLOTSURF3 = Fonts[13].render("This will affect your stats on the left.", 1, (255,255,255))
        ALR = ALLOTSURF.get_rect()
        ALR2 = ALLOTSURF2.get_rect()
        ALR3 = ALLOTSURF3.get_rect()

        ALR.center = (415, 50)
        ALR2.center = (415, 80)
        ALR3.center = (415, 110)

        screen.blit(ALLOTSURF, ALR)
        screen.blit(ALLOTSURF2, ALR2)
        screen.blit(ALLOTSURF3, ALR3)

        c = 0

        for stat_surf in STATS_SURFS:
            screen.blit(stat_surf, (45,290 + ih * c))
            c += 1

        CHARNAMERECT.center = (111, 50)
        STATSRECT.center = (111, 263)
        screen.blit(CHARNAME, CHARNAMERECT)
        screen.blit(STATS, STATSRECT)



        # Previous -->

        c = 0
        
        for stat in [("Strength"+" (+"+str(Bonuses[0])+")",Bonuses[0]),
                     ("Endurance"+" (+"+str(Bonuses[1])+")",Bonuses[1]),
                     ("Magic"+" (+"+str(Bonuses[2])+")",Bonuses[2]),
                     ("Luck"+" (+"+str(Bonuses[3])+")",Bonuses[3]),
                     ("",Bonuses[0]),
                     ("Points Remaining",None)]:

            if stat[1] is not None:
                cl = stat[1]*21
                SS = Fonts[11].render(stat[0], 1, (255-cl,255,255-cl))
            else:
                SS = Fonts[11].render(stat[0], 1, (255,255,255))
            SR = SS.get_rect()
            SR.midleft = (260, 195 + ih2 * c)
            screen.blit(SS, SR)
            c += 1

        PST = player.strength[0] + Bonuses[0]
        PEN = player.endurance[0] + Bonuses[1]
        PMA = player.magic[0] + Bonuses[2]
        PLU = player.luck[0] + Bonuses[3]

        c = 0

        for pstat in [PST, PEN, PMA, PLU, "", P_REM]:
            SS = Fonts[11].render(str(pstat), 1, (255,255,255))
            SR = SS.get_rect()
            SR.midright = (580, 195 + ih2 * c)
            screen.blit(SS, SR)
            c += 1

        #Rendering bottom-left stats

        PHP = int(PEN ** 1.4452)
        PMP = int(PMA ** 1.4452)
        #PST is just PST from above ;)
        #PLU is just PLU from above ;)

        c = 0

        for pstat in [PHP, PMP, PST, PLU]:
            statsurf = Fonts[12].render(str(pstat), 1, (255,255,255))
            statrect = statsurf.get_rect()
            statrect.topright = (180, 290 + ih * c)
            screen.blit(statsurf, statrect).inflate(20,0)
            c += 1


        for e in ge():
            if e.type == KEYDOWN:
                k = e.key
                if k == K_ESCAPE:
                    return -1
                if k == K_DOWN or k in p1c["Down"]:
                    if Cursor < 3:
                        Cursor += 1
                        interface_sound("menu-item")
                elif k == K_UP or k in p1c["Up"]:
                    if Cursor > 0:
                        Cursor -= 1
                        interface_sound("menu-item")
                elif k == K_RIGHT or k in p1c["Right"]:
                    if P_REM > 0:
                        Bonuses[Cursor] += 1
                        P_REM -= 1
                        interface_sound("menu-item")
                elif k == K_LEFT or k in p1c["Left"]:
                    if Bonuses[Cursor] > 0:
                        Bonuses[Cursor] -= 1
                        P_REM += 1
                        interface_sound("menu-item")
                elif k == K_RETURN or k in p1c["B-1"]:
                    if P_REM == 0:
                        ALLOTPHASE = False
                        interface_sound("menu-small-select")

        # Blit cursor

        if (tick/8)%2:
            CURS_SURF.set_alpha(100)
        else:
            CURS_SURF.set_alpha(60)
            
        screen.blit(CURS_SURF, (240, 170 + Cursor * ih2))

        # Blit status message

        if P_REM == 12: status = "Right/left keys adds/subtracts points and up/down changes the selection."
        elif P_REM > 0: status = "Completely distribute all the points."
        elif P_REM == 0: status = "Press Return or " + namekey("B-1") + " to finalise the distribution!"
        status2 = ["Str: Capacity to hurt an enemy, and dexterity to wield weapons.",
                   "End: Capacity to endure damage. More endurance, longer life.",
                   "Mag: Magical ability. Spells and summons benefit from this.",
                   "Luck: Increases your chance of critical hits and finding good treasures."][Cursor]

        screen.blit(Fonts[9].render(status, 1, (0,0,0)), (241,401))
        if (tick/16)%3:
            screen.blit(Fonts[9].render(status, 1, (255,255,255)), (240,400))
        else:
            screen.blit(Fonts[9].render(status, 1, (150,150,150)), (240,400))

        screen.blit(Fonts[9].render(status2, 1, (255,255,255)), (240,145))

        # Blit character
        PLAYERSURF.fill((255,0,255))
        char_anim = canims[int(ca)]

        fa = tick/[7,13][ca]%anims[char_anim]
        ti, li = cframes[char_anim+str(fa+1)+".png"]
        ts, tr = ti
        ls, lr = li

        tr.topleft = (50,50)
        lr.topleft = (50,100)

        PLAYERSURF.blit(ls, (180, 100))
        PLAYERSURF.blit(ts, (180-(tr[2]-40)/2, 100))

        prefix = weapons[wchosen][0]
        wep = Data.Itembox.GetItem(prefix)
        fa %= len([wep.Warrior_Frames, wep.Mage_Frames][player.classtype][char_anim])
        frameinfo = [wep.Warrior_Frames, wep.Mage_Frames][player.classtype][char_anim][fa]

        surf = Data.images[wep.wearable_image_prefix + frameinfo[0] + ".png"][0]
        surf = pygame.transform.rotate(surf, frameinfo[3])
        PLAYERSURF.blit(surf, (180 + frameinfo[1], 100 + frameinfo[2]))

        screen.blit(PLAYERSURF, (-100 ,0))

        if not (tick+1)%224:
            ca = ca + 1
            ca %= len(canims)

        myflip()
        wait_tick(t)

    player.Init_RPG_Elements([PST, PEN, PMA, PLU], [])

    WEAPONPHASE = True

    TITLESURF = Fonts[10].render("Choose your primary weapon!", 1, (255,255,255))
    TR = TITLESURF.get_rect()
    TR.midtop = (420, 40)

    ARROWSURF = Data.images["Arrowright.png"][0]
    ARROWRECT = ARROWSURF.get_rect()
    ARROWSURF2 = pygame.transform.flip(ARROWSURF, True, False)
    ARROWRECT2 = ARROWSURF2.get_rect()

    descriptions = [
        # Warrior's
        [
        "This gladius is a two-edged Roman short-sword measuring 70cm in length. It is"
        " quite light and is most appropriate for quicker attacks. The versatility"
        " of the gladius makes it good for cutting and thrusting." 
        " It is forged from bronze. Medium attack strength, quick attacks, poor range.",

        "This standard two-handed battle axe reaches 90cm. Its powerfully designed"
        " axehead delivers a crushing and slicing blow simultaneously. The weight on"
        " the end of the axe requires the attacker to pause between swings. It is forged"
        " from bronze. High attack strength, slow attacks, mediocre range.",

        "Halberds have exceptional reach. This one can extend to 140cm. Halberds are"
        " versatile weapons because they offer a ranged attack with nearly as much force as"
        " a melee weapon. The axehead and spike at the end of the halberd are versatile, but still can not deliver"
        " as much force as conventional melee weapons, and as such, the halberd is"
        " considered a defensive weapon. This halberd is made of steel. Low-Medium attack strength,"
        " quick attacks, good range."
        ],
        # Mage's
        [
        "The training staff passed down to Nyx by Queen Amee. It flows with magical energy"
        " and will allow the holder to cast spells more efficiently. It is made from tough"
        " wood, and can still strike a close enemy. The staff's attack does not consume MP."
        " Great magical bonus, very low physical damage, mediocre range.",

        "This magic crossbow draws magical energy from the user to supply them with an"
        " unlimited supply of spiritual arrows. The bow can reach the farthest out of"
        " all weapon types. It uses MP per arrow, and cannot fire without it."
        " Mediocre magical bonus, medium magical damage, no physical damage, excellent range.",

        "The enchanted sickle transfers magical power from the attacker through to the"
        " defender, causing extra damage. It uses MP when the attack hits."
        " Good magical bonus, high magical damage, low physical damage, very poor range."
        ]
        ][who == "Nyx"] # Breaks it down into one half or the other depending on char

    while WEAPONPHASE:
       
        t = pygame.time.get_ticks()
        tick += 1

        screen.fill((0,0,0))
        screen.blit(bgs2[not player.classtype], (-tick%640,0))
        screen.blit(bgs2[not player.classtype], (-tick%640-640,0))

        screen.blit(bgs[player.classtype], (0,-tick%480))
        screen.blit(bgs[player.classtype], (0,-tick%480-480))
        screen.blit(darksurf, (0,0))

        c = 0

        for stat_surf in STATS_SURFS:
            screen.blit(stat_surf, (45,290 + ih * c))
            c += 1

        CHARNAMERECT.center = (111, 50)
        STATSRECT.center = (111, 263)
        screen.blit(CHARNAME, CHARNAMERECT)
        screen.blit(STATS, STATSRECT)

        # Previous ->

        #Rendering bottom-left stats
        c = 0

        for pstat in [PHP, PMP, PST, PLU]:
            statsurf = Fonts[12].render(str(pstat), 1, (255,255,255))
            statrect = statsurf.get_rect()
            statrect.topright = (180, 290 + ih * c)
            screen.blit(statsurf, statrect).inflate(20,0)
            c += 1

        
        screen.blit(TITLESURF, TR)

        c = 0

        WEPSURF = Data.images[weapons[wchosen][1]][0]
        NAMESURF = Fonts[12].render(weapons[wchosen][0], 1, (255,255,255))

        WEPRECT = WEPSURF.get_rect()
        NAMERECT = NAMESURF.get_rect()

        WEPRECT.center = (420,170)
        NAMERECT.midtop = (420, 250)

        screen.blit(WEPSURF, WEPRECT)
        screen.blit(NAMESURF, NAMERECT).inflate(300,0)

        ARROWRECT.midleft = NAMERECT.midright
        ARROWRECT.move_ip(20+5*math.sin(tick/5.0),0)
        ARROWRECT2.midright = NAMERECT.midleft
        ARROWRECT2.move_ip(-20-5*math.sin(tick/5.0),0)
        screen.blit(ARROWSURF, ARROWRECT).inflate(20,0)
        screen.blit(ARROWSURF2, ARROWRECT2).inflate(20,0)

        y=0
        for surf in string_to_paragraph(descriptions[wchosen], Fonts[9], 1, (255,255,255), 360):
            screen.blit(surf, (240, 300 + y*15))
            y+= 1

        # Blit character
        PLAYERSURF.fill((255,0,255))
        char_anim = canims[int(ca)]

        fa = tick/[7,13][ca]%anims[char_anim]
        ti, li = cframes[char_anim+str(fa+1)+".png"]
        ts, tr = ti
        ls, lr = li

        tr.topleft = (50,50)
        lr.topleft = (50,100)

        PLAYERSURF.blit(ls, (180, 100))
        PLAYERSURF.blit(ts, (180-(tr[2]-40)/2, 100))

        prefix = weapons[wchosen][0]
        wep = Data.Itembox.GetItem(prefix)
        fa %= len([wep.Warrior_Frames, wep.Mage_Frames][player.classtype][char_anim])
        frameinfo = [wep.Warrior_Frames, wep.Mage_Frames][player.classtype][char_anim][fa]

        surf = Data.images[wep.wearable_image_prefix + frameinfo[0] + ".png"][0]
        surf = pygame.transform.rotate(surf, frameinfo[3])
        PLAYERSURF.blit(surf, (180 + frameinfo[1], 100 + frameinfo[2]))

        screen.blit(PLAYERSURF, (-100 ,0))

        if not (tick+1)%224:
            ca = ca + 1
            ca %= len(canims)

        myflip()
        for e in ge():
            if e.type == KEYDOWN:
                k = e.key
                if k == K_RIGHT or k in p1c["Right"]:
                    wchosen += 1
                    if wchosen == len(weapons):
                        wchosen = 0
                    interface_sound("menu-item")
                if k == K_LEFT or k in p1c["Left"]:
                    wchosen -= 1
                    if wchosen == -1:
                        wchosen = len(weapons)-1
                    interface_sound("menu-item")
                if k == K_RETURN or k in p1c["B-1"]:
                    WEAPONPHASE = False
                    interface_sound("menu-small-select")


        wait_tick(t)
    primary_weapon = weapons[wchosen][0]


    return primary_weapon
        
class snowflake:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(2,4)
        self.surface = pygame.Surface((self.size*2,self.size*2))
        self.surface.fill((255,0,255))
        self.surface.set_colorkey((255,0,255))
        self.alpha = 0
        self.spawn = True
        self.phase = random.randint(1,3141)/100.0
        c = random.randint(180,255)
        self.col = (c,c,c)
        self.swerve = random.randint(80,120)/100.0
    def tick(self):
        if self.spawn and self.alpha < 255:
            self.alpha += 20
        if self.alpha >= 255:
            self.alpha = 255
            self.spawn = False
        if not self.spawn:
            self.alpha -= 4

        self.y += self.size/8.0
        self.phase += 0.2

    def location(self):
        return int(self.x + math.sin(self.phase)*self.swerve*4), int(self.y)

    def blit(self):
        pygame.draw.circle(self.surface,self.col,(self.size,self.size),self.size,0)
        self.surface.set_alpha(self.alpha)
        return self.surface

def Save_intermission(game, pic, must = False, leavemus = False):
    """Save the game"""
    global Data, screen, soundbox, Fonts, p1c, wmc, wms
    fade_to_black(screen)
    if not leavemus:
        soundbox.PlaySong("theme1_raw.ogg", -1)
    screen.blit(Data.images[pic][0], (0,0))
    fade_from_black(screen)
    myflip()

    info = ["You come across an ancient altar.", "It glows with the radiance of good magic."]
    info += ["Do you wish to save your game?"]

    count = 1
    vmsg = ""
    msg = info[0]

    seeing = True
    ready = False
    tick = 0
    while seeing and not must:
        screen.blit(Data.images[pic][0], (0,0))
        ti = pygame.time.get_ticks()

        sks = Fonts[16].render("Press " + namekey("B-1") + " to skip", 1, (0,0,0))
        skr = sks.get_rect()
        skr.midright = (635, 465)
        screen.blit(sks, skr)

        if not tick%5:
            if vmsg == msg:
                ready = True
            vmsg = msg[:len(vmsg)+1]

        m_s = Fonts[16].render(vmsg, 1, (255,255,255))
        m_sb = Fonts[16].render(vmsg, 1, (0,0,0))
        m_r = m_s.get_rect()
        m_r.midleft = (320-Fonts[16].size(msg)[0]/2, 350)
        for xp in range(-1,2):
            for yp in range(-1,2):
                screen.blit(m_sb, m_r.move(xp,yp))
        screen.blit(m_s, m_r)

        npi, npi_r = Data.images["Next_Page_Icon.png"]
        if ready:
            npi_r.center = (320, 400+abs(math.sin(tick/10.0)*15))
            screen.blit(npi, npi_r)

        myflip()
        wait_tick(ti)
        tick += 1

        for event in ge():
            if event.type == KEYDOWN:
                key = event.key
                if (key in p1c["B-1"] or key == K_RETURN):
                    if ready:
                        ready = False
                        if count == len(info):
                            seeing = False
                            break
                        msg = info[count]
                        count += 1
                        vmsg = ""
                    else:
                        vmsg = msg

    answering = True
    pointer = 0
    while answering and not must:
        screen.blit(Data.images[pic][0], (0,0))
        ti = pygame.time.get_ticks()

        y = 0
        for vmsg in ["Save the game", "Do not save the game"]:
            if y/40 == pointer:
                m_s = Fonts[16].render(vmsg, 1, (255,255,255))
            else:
                m_s = Fonts[16].render(vmsg, 1, (50,50,50))
            m_sb = Fonts[16].render(vmsg, 1, (0,0,0))
            m_r = m_s.get_rect()
            m_r.midleft = (320-Fonts[16].size(msg)[0]/2, 350+y)
            for xp in range(-1,2):
                for yp in range(-1,2):
                    screen.blit(m_sb, m_r.move(xp,yp))
            screen.blit(m_s, m_r)
            y += 40

        myflip()
        wait_tick(ti)
        tick += 1

        for event in ge():
            if event.type == KEYDOWN:
                key = event.key
                if key in p1c["Down"]:
                    pointer = 1
                elif key in p1c["Up"]:
                    pointer = 0
                elif key in p1c["B-1"] or key == K_RETURN:
                    answering = False

    saved = False
    if not pointer or must:
        cPickle.dump(game, open(os.path.join(SAVEDIRECTORY, "Saves", game.savefilename), "w"))
        saved = True
    fade_to_black(screen, 1)
    if saved:
        gss = Fonts[17].render("Game Successfully Saved: " + game.savefilename.replace(".asf", ""), 1, (255,255,255))
        gsr = gss.get_rect()
        gsr.center = (320, 240)
        screen.blit(gss, gsr)
        fade_from_black(screen, 1)
        csleep(1)
    fade_to_black(screen)
    if not leavemus:
        soundbox.PlaySong(wmc, -1)

def seeSpirit(game):
    """See the spirit. You see her when you die"""
    global Data, screen, soundbox, Fonts, p1c
    soundbox.PlaySong("holy.ogg", -1)
    tick = 0
    count = 0
    msgs = ["I will ressurrect you then.", "Go on. But be more careful!"]
    msg = "Oh dear, you have fallen...."
    vmsg = ""
    ready = False
    seeing = True
    while seeing:
        ti = pygame.time.get_ticks()

        if not tick%2:
            if vmsg == msg:
                ready = True
            vmsg = msg[:len(vmsg)+1]
    
        screen.fill((0,0,0))

        sks = Fonts[16].render("Press " + namekey("B-1") + " to skip", 1, (255,255,255))
        skr = sks.get_rect()
        skr.midright = (635, 465)
        screen.blit(sks, skr)

        aura, aura_r = Data.images["white_aura.png"]
        
        aura_r.center = (320,200)
        screen.blit(aura, aura_r)

        glow, glow_r = Data.images["glow_texture.png"]
        glow_r.midleft = (224, 200)
        screen.blit(glow, glow_r, Rect(tick*3.5%480,0,192,192))
        glow_r.midleft = (224, 200)
        screen.blit(glow, glow_r, Rect(tick*3.5%480-480,0,192,192))

        face, face_r = Data.images["spiritguardian.png"]
        face_r.center = (320,200)
        screen.blit(face, face_r)

        wait_tick(ti)
        tick += 1

        m_s = Fonts[16].render(vmsg, 1, (255,255,255))
        m_r = m_s.get_rect()
        m_r.midleft = (320-Fonts[16].size(msg)[0]/2, 350)
        screen.blit(m_s, m_r)

        npi, npi_r = Data.images["Next_Page_Icon.png"]
        if ready:
            blacksurf = pygame.Surface(npi_r.size)
            npi_r.center = (320, 400+abs(math.sin(tick/10.0)*15))
            screen.blit(npi, npi_r)
            blacksurf.set_alpha(255-abs(math.sin(tick/10.0)*255))
            screen.blit(blacksurf, npi_r)
        
        myflip()

        for event in ge():
            if event.type == KEYDOWN:
                key = event.key
                if (key in p1c["B-1"] or key == K_RETURN):
                    if ready:
                        ready = False
                        if count == 2:
                            seeing = False
                            break
                        msg = msgs[count]
                        count += 1
                        vmsg = ""
                    else:
                        vmsg = msg

    fade_to_black(screen)
    return True

def handle_game(Game, loaded = False):
    """This handles everything after you load your game"""
    global screen # The only section running. Shouldn't be a problem
    global real_screen, wmc, wms
    global Data, mapdata, soundbox
    global Fonts, g_options, a_options, p_options, p1c
    global PLAYLOCALS

    mus = {1: "World_Map.ogg",
           2: "World_Map.ogg",
           3: "World_Map2.ogg",
           }

    if Game.location[1] == 0:
        wms = "World_Map.ogg"
    else:
        wms = mus[Game.location[0]]
    wmc = wms

    logfile("Entered handle_game with parameters: " + str(Game) + ", " + str(loaded))
    logfile("Account: " + Game.savefilename)

    flipme = False

    # Handle game should know whether the game object is mature or
    # infantile
    if not loaded:
        # Choose a character
        Game.character = choose_character(screen)
        if Game.character == 0: return
        player = Character()
        Game.playerobject = player
        if Game.character == "Nyx":
            player.classtype = 1
            Game.Accessible = [[2], [], [1], [1, 2]]
            Game.location = [2, 0]
        player.combo_list = player.combo_list[player.classtype]

        fade_to_black(screen)

        player.Init_RPG_Elements([player.WARRIOR_BASE, player.MAGE_BASE][Game.character=="Nyx"], [])

        primary_weapon = design_character(Game, player)
        if primary_weapon == -1:
            return
        # In this function, RPG Elements are updated.


        player.Init_Items(Data, [primary_weapon], [])

        fade_to_black(screen)
        for x in mapdata[0][1:]:
            Game.scores.append([])
            Game.timegems.append([])
        for w in range(len(mapdata[1:])):
            for l in mapdata[w+1][1:]:
                Game.scores[w].append(0)
                Game.timegems[w].append(0)
        cPickle.dump(Game, open(os.path.join(SAVEDIRECTORY, "Saves", Game.savefilename), "w"))
    else:
        player = Game.playerobject

    Tutorial_Active = False

    IMMATURE = True

    oldpos = [None, None]
    needfade = True
    needlevelfade = False

    time.sleep(0.1)
    soundbox.PlaySong(wmc, -1)
    worldpic = None
    ticker = pygame.time.get_ticks()

    tick = 0
    snowflakes = []
    # Load up the relevant map
    # And handle map movements
    overmap = None
    marks = []
    while True:
        if Game.location[1] == 0:
            wms = "World_Map.ogg"
        else:
            wms = mus[Game.location[0]]

        if wmc != wms:
            wmc = wms
            soundbox.PlaySong(wmc, -1)


        if player.classtype and 1 in Game.Accessible[0]:
            Game.Accessible[0].remove(1)
        if not player.classtype and 2 in Game.Accessible[0]:
            Game.Accessible[0].remove(2)


        snowflakes = snowflakes [-40:]
        mylocmark = ["LocationMark.png", "LocationMark2.png"][player.classtype]
        tick +=1
        cloudlayer = False

        # worldbox stuff

        worldbox_msg = ""
        worldbox_surfs = []
        worldbox_pos = 0

        # ----------


        # CONTENT ->

        if Game.location[1] == 0 and Game.KIRI_HEIGHT == 0 and Game.ENDSCENE == 0:
            Game.ENDSCENE = 1
            playerpos = [290, 342]
        
        if Game.world_tut <= 1:
            if Game.location == [1, 0]:
                worldbox_msg = "This is the map of Ardentryst. This overview of the region shows you all the great locations in the continent. For now, we start in Sempridge. Press " + namekey("B-1") + " to enter Sempridge."
                worldbox_pos = 330
            elif Game.location == [2, 0]:
                worldbox_msg = "This is the map of Ardentryst. This overview of the region shows you all the great locations in the continent. For now, we start in Entarya. Press " + namekey("B-1") + " to enter Entarya."
                worldbox_pos = 330

            if Game.world_tut == 1:
                worldbox_surfs = []
            Game.world_tut = 0

        if Game.location == [1,1] and Game.world_tut <= 1:
            worldbox_msg = "This is the forest town of Sempridge. We must first start here in this location. Press " + namekey("B-1") + " to enter this area...."
            worldbox_pos = 150
            if Game.world_tut == 0:
                worldbox_surfs = []
            Game.world_tut = 1

        if Game.location == [2,1] and Game.world_tut <= 1:
            worldbox_msg = "This is Queen Amee's castle! We must first start here in this location. Press " + namekey("B-1") + " to enter...."
            worldbox_pos = 150
            if Game.world_tut == 0:
                worldbox_surfs = []
            Game.world_tut = 1

        if Game.world_tut == 2:
            if Game.location == [1,1]:
                worldbox_msg = "Now the level name at the bottom shows us our level completion percentage. Let's move on. Visit the next place by moving to it, press " + namekey("Up") + " to get there!"
                worldbox_pos = 150
            elif Game.location == [1,2]:
                worldbox_msg = "Enter this area if you wish to save your game. Press " + namekey("B-1") + " to go here. Move on to the next area by proceeding east by pressing " + namekey("Right") + "!"
                worldbox_pos = 150

            elif Game.location == [2,1]:
                worldbox_msg = "Now the level name at the bottom shows us our level completion percentage. Let's move on. Visit the next place by moving to it, press " + namekey("Down") + " to get there!"
                worldbox_pos = 160
            elif Game.location == [2,2]:
                worldbox_msg = "Now we are further into Queen Amee's castle. After going through this level, save your game at the Eternal boulder coming up...."
                worldbox_pos = 180

        if Game.world_tut == 3:
            if Game.location == [2,3]:
                worldbox_msg = "Enter this area if you wish to save your game. Press " + namekey("B-1") + " to go here. Move on to the next area by proceeding east by pressing " + namekey("Right") + "!"
                worldbox_pos = 250
            elif Game.location == [1,8]:
                worldbox_msg = "You can fill up on supplies or grab some needed equipment here at Elchim's Stall. Collect silver to buy new items!"
                worldbox_pos = 100

        if Game.world_tut == 4:
            if Game.location == [2,5]:
                worldbox_msg = "You can fill up on supplies or grab some needed equipment here at Elchim's Shop. Collect silver to buy new items!"
                worldbox_pos = 350

        if Game.world_tut == 5 and Game.location in [[1,7],[2,8]]:
            worldbox_msg = "Look out! Rumour has is there is a giant forest guardian lurking in this area. Stay strong!"
            worldbox_pos = 220
        


        # <-

        marks = []

        if Game.location[1] == 0:
            bgmap = Data.images[mapdata[0][0]][0]
            overmap = None
            if mapdata[0][0] == "World_Map.png":
                cloudlayer = True
              
            Ondata = mapdata[0][Game.location[0]]
            if not Game.ENDSCENE or Game.ENDSCENE == 60:
                playerpos = [Ondata["position"][0], Ondata["position"][1]]
            placename = Ondata["name"]
            realplacename = placename
        else:
            bgmap = Data.images[mapdata[Game.location[0]][0]][0]
            overmap = Data.images[mapdata[Game.location[0]][0].replace("Map", "Map_Top")][0]
            altarpic = mapdata[Game.location[0]][0].replace("Map", "Altar")
            Ondata = mapdata[Game.location[0]][Game.location[1]]
            if not Game.ENDSCENE or Game.ENDSCENE == 60:
                playerpos = [Ondata["position"][0], Ondata["position"][1]]
            placename = Ondata["name"]
            realplacename = placename
            # Generate mark data ->
            for location in mapdata[Game.location[0]][1:]:
                if markdata.has_key(location["type"]):
                    if mapdata[Game.location[0]].index(location) in Game.Accessible[Game.location[0]]:
                        mtype = markdata[location["type"]]
                        if Game.scores[Game.location[0]-1][mapdata[Game.location[0]].index(location)-1] >= 100: mtype = "Mark4.png"
                        if Game.scores[Game.location[0]-1][mapdata[Game.location[0]].index(location)-1] >= 200: mtype = "Mark6.png"
                        marks.append((location["position"], mtype))
            # <-
            if Ondata["type"] == "SAVE":
                placename += " (save location)"
            elif Ondata["type"] == "SHOP":
                placename += " (shop)"
            elif "LEVEL" in Ondata["type"]:
                placename += " (" + str(Game.scores[Game.location[0]-1][Game.location[1]-1]) + "%)"
                if Game.location[0] >= 3:
                    tg = Game.timegems[Game.location[0]-1][Game.location[1]-1]
                    placename += " ... " + {0: "No Gem (Slow)", 1: "Yellow (Fast)", 2: "Red (Faster)", 3:"Blue (Fastest)"}[tg]
            if Ondata["map"]:
                level = Data.levels[Ondata["map"]]
                levelscript = Ondata["map"] + ".script"
                npcscript = Ondata["map"] + ".npcs"
                if Game.location in [[1,1], [2,1]] and Game.game_tut == 0:
                    Tutorial_Active = True
                else:
                    Tutorial_Active = False

        if oldpos == [None, None]:
            oldpos = playerpos[:]

        if oldpos != playerpos:
            temppos = playerpos[:]
            if 0 < Game.ENDSCENE < 60:
                xdif = float(playerpos[0] - oldpos[0]) / 79.0
                ydif = float(playerpos[1] - oldpos[1]) / 79.0
            else:
                xdif = float(playerpos[0] - oldpos[0]) / 19.0
                ydif = float(playerpos[1] - oldpos[1]) / 19.0
            playerpos = oldpos[:]
            if cloudlayer:
                screen.blit(Data.images["earth.png"][0], (0,0))                    
            screen.blit(bgmap, (0,0))
            if cloudlayer:
                if Game.ENDSCENE:
                    screen.blit(Data.images["kiripan.png"][0], (290, 81 + Game.ENDSCENE))
                elif Game.KIRI_HEIGHT:
                    screen.blit(Data.images["kiripan.png"][0], (290, 141 - Game.KIRI_HEIGHT*60 + math.sin(tick/30.0)*6))
                else:
                    screen.blit(Data.images["kiripan.png"][0], (290, 141))
                screen.blit(Data.images["maptop.png"][0], (0,0))
                if not tick%5:
                    snowflakes.append(snowflake(random.randint(275,400),random.randint(285,340)))
                for flake in snowflakes:
                    flake.tick()
                    screen.blit(flake.blit(), flake.location())

            # blit marks -->
            for mark in marks:
                ms, mr = Data.images[mark[1]]
                mr.center = mark[0]
                screen.blit(ms, mr)
            # <--
            if cloudlayer:
                screen.blit(Data.images["cloudlayer.png"][0], (-tick%1280,0))
                screen.blit(Data.images["cloudlayer.png"][0], (-tick%1280-1280,0))
           
            if overmap:
                screen.blit(overmap, (0,0))
#            myflip()
            for x in range([20, 80][60>Game.ENDSCENE>0]):
                playerpos[0] = oldpos[0] + xdif * x
                playerpos[1] = oldpos[1] + ydif * x
                if cloudlayer:
                    screen.blit(Data.images["earth.png"][0], (0,0))                    
                screen.blit(bgmap, (0,0))
                if cloudlayer:
                    if Game.ENDSCENE:
                        screen.blit(Data.images["kiripan.png"][0], (290, 81 + Game.ENDSCENE))
                    elif Game.KIRI_HEIGHT:
                        screen.blit(Data.images["kiripan.png"][0], (290, 141 - Game.KIRI_HEIGHT*60 + math.sin(tick/30.0)*6))
                    else:
                        screen.blit(Data.images["kiripan.png"][0], (290, 141))
                    
                    screen.blit(Data.images["maptop.png"][0], (0,0))
                    if not tick%5:
                        snowflakes.append(snowflake(random.randint(275,400),random.randint(285,340)))
                    for flake in snowflakes:
                        flake.tick()
                        screen.blit(flake.blit(), flake.location())

                # blit marks -->
                for mark in marks:
                    ms, mr = Data.images[mark[1]]
                    mr.center = mark[0]
                    screen.blit(ms, mr)
                # <--

                if flipme:
                    screen.blit(pygame.transform.flip(Data.images[mylocmark][0], True, False), (int(playerpos[0]) - 16, int(playerpos[1]) - 44))
                else:
                    screen.blit(Data.images[mylocmark][0], (int(playerpos[0]) - 16, int(playerpos[1]) - 44))
                if overmap:
                    screen.blit(overmap, (0,0))
                if cloudlayer:
                    screen.blit(Data.images["cloudlayer.png"][0], (-tick%1280,0))
                    screen.blit(Data.images["cloudlayer.png"][0], (-tick%1280-1280,0))
                myflip()
                ticker = wait_tick(ticker)
                tick += 1

            oldpos = temppos[:]
            playerpos = temppos[:]
            ge()

        if Ondata.has_key("type"):
            if "EXIT_WORLD" in Ondata["type"]:
                Game.location[1] = 0
                oldpos = [None, None]
                fade_to_black(screen)
                needfade = True
                continue
            elif Ondata["type"] == "SAVE" or Game.scores[Game.location[0]-1][Game.location[1]-1]:
                unlocked = [mapdata[Game.location[0]][Game.location[1]][k] for k in ["up", "down", "left", "right"]]
                while None in unlocked:
                    unlocked.remove(None)
                for loc in unlocked:
                    for x in range(1, len(mapdata[Game.location[0]])):
                        if x not in Game.Accessible[Game.location[0]]:
                            if mapdata[Game.location[0]][x]["name"] == loc:
                                Game.Accessible[Game.location[0]].append(x)
                
        if cloudlayer:
            screen.blit(Data.images["earth.png"][0], (0,0))
        screen.blit(bgmap, (0,0))
        if cloudlayer:
            if Game.ENDSCENE:
                screen.blit(Data.images["kiripan.png"][0], (290, 81 + Game.ENDSCENE))
            elif Game.KIRI_HEIGHT:
                screen.blit(Data.images["kiripan.png"][0], (290, 141 - Game.KIRI_HEIGHT*60 + math.sin(tick/30.0)*6))
            else:
                screen.blit(Data.images["kiripan.png"][0], (290, 141))
            screen.blit(Data.images["maptop.png"][0], (0,0))
            if not tick%5:
                snowflakes.append(snowflake(random.randint(275,400),random.randint(285,340)))
            for flake in snowflakes:
                flake.tick()
                screen.blit(flake.blit(), flake.location())

        # blit marks -->
        for mark in marks:
            ms, mr = Data.images[mark[1]]
            mr.center = mark[0]
            screen.blit(ms, mr)
        # <--
        if flipme:
            screen.blit(pygame.transform.flip(Data.images[mylocmark][0], True, False), (int(playerpos[0]) - 16, int(playerpos[1]) - 44))
        else:
            screen.blit(Data.images[mylocmark][0], (int(playerpos[0]) - 16, int(playerpos[1]) - 44))

        # over map
        if overmap:
            screen.blit(overmap, (0,0))

        # arrows

        if not Game.ENDSCENE or Game.ENDSCENE == 60:

            if Ondata["up"]:
                for entry in [mapdata[Game.location[0]][1:], mapdata[0][1:]][Game.location[1]==0]:
                    if entry["name"] == Ondata["up"]:
                        lookin = [Game.location[0], 0][Game.location[1] == 0]
                        if [mapdata[Game.location[0]], mapdata[0]][Game.location[1]==0].index(entry) in Game.Accessible[lookin] or entry.has_key("type") and entry["type"]== "EXIT_WORLD":
                            ars, ar = Data.images["nav-arrow-up.png"]
                            ar.center = playerpos[0], playerpos[1] - 48
                            screen.blit(ars, ar)

            if Ondata["down"]:
                for entry in [mapdata[Game.location[0]][1:], mapdata[0][1:]][Game.location[1]==0]:
                    if entry["name"] == Ondata["down"]:
                        lookin = [Game.location[0], 0][Game.location[1] == 0]
                        if [mapdata[Game.location[0]], mapdata[0]][Game.location[1]==0].index(entry) in Game.Accessible[lookin] or entry.has_key("type") and entry["type"]== "EXIT_WORLD":
                            ars, ar = Data.images["nav-arrow-down.png"]
                            ar.center = playerpos[0], playerpos[1] + 48
                            screen.blit(ars, ar)

            if Ondata["left"]:
                for entry in [mapdata[Game.location[0]][1:], mapdata[0][1:]][Game.location[1]==0]:
                    if entry["name"] == Ondata["left"]:
                        lookin = [Game.location[0], 0][Game.location[1] == 0]
                        if [mapdata[Game.location[0]], mapdata[0]][Game.location[1]==0].index(entry) in Game.Accessible[lookin] or entry.has_key("type") and entry["type"]== "EXIT_WORLD":
                            ars, ar = Data.images["nav-arrow-left.png"]
                            ar.center = playerpos[0] - 48, playerpos[1]
                            screen.blit(ars, ar)

            if Ondata["right"]:
                for entry in [mapdata[Game.location[0]][1:], mapdata[0][1:]][Game.location[1]==0]:
                    if entry["name"] == Ondata["right"]:
                        lookin = [Game.location[0], 0][Game.location[1] == 0]                    
                        if [mapdata[Game.location[0]], mapdata[0]][Game.location[1]==0].index(entry) in Game.Accessible[lookin] or entry.has_key("type") and entry["type"]== "EXIT_WORLD":
                            ars, ar = Data.images["nav-arrow-right.png"]
                            ar.center = playerpos[0] + 48, playerpos[1]
                            screen.blit(ars, ar)

        # <-----

        # menu text
        menutext = Fonts[17].render(namekey("B-9") + ": Menu", 1, (255,255,255))
        menutextb = Fonts[17].render(namekey("B-9") + ": Menu", 1, (0,0,0))
        menurect = menutext.get_rect()
        menurect.midright = (632+math.cos(tick/20.0)*3, 30+math.sin(tick/20.0)*10)
        for x in range(-1,2):
            for y in range(-1,2):
                screen.blit(menutextb,menurect.move(x,y))
        screen.blit(menutext, menurect)

        #place text
        
        placetext = Fonts[2].render(placename, 1, (255, 255, 255))
        placetext_black = Fonts[2].render(placename, 1, (0, 0, 0))
        placerect = placetext.get_rect()
        placerect.center = (320, 452+math.sin(tick/20.0)*6)

        for x in range(-1, 2):
            for y in range(-1, 2):
                screen.blit(placetext_black, placerect.move(x,y))
        screen.blit(placetext, placerect)

        ticker = wait_tick(ticker)

        if cloudlayer:
            screen.blit(Data.images["cloudlayer.png"][0], (-tick%1280,0))
            screen.blit(Data.images["cloudlayer.png"][0], (-tick%1280-1280,0))

        if needfade:
            fade_from_black(screen)
            ge()
            needfade = False

        if IMMATURE:
            myflip()
            IMMATURE = False

        if worldbox_msg:
            if not worldbox_surfs:
                worldbox_surfs = wordwrap.string_to_paragraph(worldbox_msg, Fonts[13], 1, (0,0,0), 600)

            height = len(worldbox_surfs)*16 + 20
            mbacksurf = pygame.Surface((640, height))

            bws = Data.images["BlueWhiffBG.png"][0]
            bws2 = Data.images["BlueWhiffBG2.png"][0]
            bws3 = Data.images["BlueWhiffBG3.png"][0]

            x = 0.5
            for b in [bws, bws2, bws3]:
                atick = int(tick * x)
                mbacksurf.blit(b, (-atick%640,-atick%480))
                mbacksurf.blit(b, (-atick%640-640,-atick%480))
                mbacksurf.blit(b, (-atick%640,-atick%480-480))
                mbacksurf.blit(b, (-atick%640-640,-atick%480-480))
                x += 1

            mbacksurf.set_alpha(160+math.sin(tick/60.0)*90)

            screen.blit(mbacksurf, (0, worldbox_pos))
            screen.blit(Data.images["BWBGW.png"][0], (0, worldbox_pos-20))
            screen.blit(pygame.transform.flip(Data.images["BWBGW.png"][0], False, True), (0, worldbox_pos+height))

            y = 0
            for s in worldbox_surfs:
                r = s.get_rect()
                r.midtop = (320, worldbox_pos)
                r.move_ip(0, 5 + 16*y)
                screen.blit(s, r)
                y += 1

        myflip()

        if 0 < Game.ENDSCENE < 60:
            Game.ENDSCENE += 0.3
        if Game.ENDSCENE > 60:
            Game.ENDSCENE = 60
            Game.location[0] = 4
            playerpos = [365, 200]
            flipme = False

        for event in ge():
            if event.type == KEYDOWN and (Game.ENDSCENE==0 or Game.ENDSCENE==60):

                # anywhere stuff
                if event.key in p1c["B-9"]:
                    r = Ingame_Menu((screen, Data, Fonts, p1c, soundbox, ticker, Game, player, False))
                    if r:
                        if r == -1:
                            return
                
                if Game.location[1] == 0:
                    # ENTIRE WORLD MAP STUFF
                    if event.key in p1c["Up"]:
                        if Ondata["up"]:
                            for entry in mapdata[0][1:]:
                                if entry["name"] == Ondata["up"]:
                                    oldpos = playerpos[:]
                                    if mapdata[0].index(entry) in Game.Accessible[0]:
                                        Game.location[0] = mapdata[0].index(entry)
                    elif event.key in p1c["Down"]:
                        if Ondata["down"]:
                            for entry in mapdata[0][1:]:
                                if entry["name"] == Ondata["down"]:
                                    oldpos = playerpos[:]
                                    if mapdata[0].index(entry) in Game.Accessible[0]:
                                        Game.location[0] = mapdata[0].index(entry)
                    elif event.key in p1c["Left"]:
                        if Ondata["left"]:
                            for entry in mapdata[0][1:]:
                                if entry["name"] == Ondata["left"]:
                                    oldpos = playerpos[:]
                                    if mapdata[0].index(entry) in Game.Accessible[0]:
                                        Game.location[0] = mapdata[0].index(entry)
                                        flipme = True
                    elif event.key in p1c["Right"]:
                        if Ondata["right"]:
                            for entry in mapdata[0][1:]:
                                if entry["name"] == Ondata["right"]:
                                    oldpos = playerpos[:]
                                    if mapdata[0].index(entry) in Game.Accessible[0]:
                                        Game.location[0] = mapdata[0].index(entry)
                                        flipme = False
                    elif event.key in p1c["B-1"]:
#                        if Game.location[0] == 3: PlaceHolderScreen(screen, Fonts, "Congratulations! But Snodom isn't made yet. Thanks for playing!")
 #                       else:
                        if Game.location[0] == 4:
                            Game.story_scene("End", screen, Data, Fonts, soundbox)
                            fade_to_black(screen)
                            Save_intermission(Game, "EndSave.png", True, True)
                            return
                        else:
                            Game.location[1] = 1
                            fade_to_black(screen)
                            needfade = True
                            oldpos = [None, None]
                else:
                    # INDIVIDUAL WORLD MAP STUFF
                    if event.key in p1c["Up"]:
                        if Ondata["up"]:
                            for entry in mapdata[Game.location[0]][1:]:
                                if entry["name"] == Ondata["up"]:
                                    oldpos = playerpos[:]
                                    if mapdata[Game.location[0]].index(entry) in Game.Accessible[Game.location[0]] or entry["type"] == "EXIT_WORLD":
                                        Game.location[1] = mapdata[Game.location[0]].index(entry)
                    if event.key in p1c["Down"]:
                        if Ondata["down"]:
                            for entry in mapdata[Game.location[0]][1:]:
                                if entry["name"] == Ondata["down"]:
                                    oldpos = playerpos[:]
                                    if mapdata[Game.location[0]].index(entry) in Game.Accessible[Game.location[0]] or entry["type"] == "EXIT_WORLD":
                                        Game.location[1] = mapdata[Game.location[0]].index(entry)
                    if event.key in p1c["Right"]:
                        if Ondata["right"]:
                            for entry in mapdata[Game.location[0]][1:]:
                                if entry["name"] == Ondata["right"]:
                                    oldpos = playerpos[:]
                                    if mapdata[Game.location[0]].index(entry) in Game.Accessible[Game.location[0]] or entry["type"] == "EXIT_WORLD":
                                        Game.location[1] = mapdata[Game.location[0]].index(entry)
                                        flipme = False
                    if event.key in p1c["Left"]:
                        if Ondata["left"]:
                            for entry in mapdata[Game.location[0]][1:]:
                                if entry["name"] == Ondata["left"]:
                                    oldpos = playerpos[:]
                                    if mapdata[Game.location[0]].index(entry) in Game.Accessible[Game.location[0]] or entry["type"] == "EXIT_WORLD":
                                        Game.location[1] = mapdata[Game.location[0]].index(entry)
                                        flipme = True
                    elif event.key in p1c["B-1"]:
                        leveltype = mapdata[Game.location[0]][Game.location[1]]["type"]
                        if leveltype == "SAVE":
                            Save_intermission(Game, altarpic)
                            needlevelfade = True
                        elif leveltype == "SHOP":
                            useshop(mapdata[Game.location[0]][Game.location[1]]["name"], Game, player)
                            soundbox.PlaySong(wmc, -1)                        

                        elif "LEVEL" in leveltype:
                            level.name = realplacename
                            ovscreen = screen.convert()
                            fade_to_black(screen)
                            Result = playlevel(player, level, [levelscript, npcscript], screen, Data, Fonts, soundbox, Game,
                                               [g_options,
                                                a_options,
                                                p_options,
                                                p1c],
                                                Tutorial_Active, ovscreen,
                                                PLAYLOCALS)#, "DEMO.dem")

                            cleanup(player)
                            needlevelfade = True
                            logfile("Level Result: " + str(Result))
                            if Game.scores[Game.location[0]-1][Game.location[1]-1] < Result[1]:
                                Game.scores[Game.location[0]-1][Game.location[1]-1] = Result[1]
                            if Game.timegems[Game.location[0]-1][Game.location[1]-1] < Result[2]:
                                Game.timegems[Game.location[0]-1][Game.location[1]-1] = Result[2]
                            if Result[0] == "Quit":
                                return
                            elif Result[0] == "Failed.LoseLife":
                                seeSpirit(Game)
                            elif Result[0] == "Level_Complete":
                                player.obelisk_save = []
                                if Game.location in [[1,1], [2,1]] and Game.world_tut == 1:
                                    Game.world_tut = 2
                                    Game.game_tut = 1
                                elif Game.location in [[2,2], [1,3]] and Game.world_tut == 2:
                                    Game.world_tut = 3
                                elif Game.location in [[2,4]] and Game.world_tut == 3:
                                    Game.world_tut = 4
                                elif Game.location in [[1,6], [2,6]] and Game.world_tut < 5:
                                    Game.world_tut = 5
                                elif Game.location in [[1,7], [2,8]] and Game.world_tut == 5:
                                    Game.world_tut = 6
                                    
                                if mapdata[Game.location[0]][Game.location[1]]["nextloc"] and Result[1] != -1:
                                    for x in range(1, len(mapdata[Game.location[0]])):
                                        if mapdata[Game.location[0]][x]["name"] == mapdata[Game.location[0]][Game.location[1]]["nextloc"]:
                                            Game.location[1] = x
                                            Game.Accessible[Game.location[0]].append(x)
                                            break
                                if leveltype == "LEVELBOSS":
                                    if Game.location[0] < 3:
                                        Game.Accessible[0].append(3)
                                    else:
                                        if not Game.location[0] + 1 in Game.Accessible[0]:
                                            # (Snodom and further) Boss killed for first time
                                            Game.Accessible[0].append(Game.location[0]+1)
                                            Game.KIRI_HEIGHT -= 1
                            soundbox.PlaySong(wmc, -1)    

        if needlevelfade:
            screen.blit(bgmap, (0,0))
            if flipme:
                screen.blit(pygame.transform.flip(Data.images[mylocmark][0], True, False), (int(playerpos[0]) - 16, int(playerpos[1]) - 44))
            else:
                screen.blit(Data.images[mylocmark][0], (int(playerpos[0]) - 16, int(playerpos[1]) - 44))

            if overmap:
                screen.blit(overmap, (0,0))
            placetext = Fonts[2].render(placename, 1, (255, 255, 255))
            placerect = placetext.get_rect()

            fade_from_black(screen)
            ge()
            needlevelfade = False

                            
        myflip()

def csleep(sec, all=False):
    """Sleeps (time delay), but allows interruption"""
    global p1c
    startti = pygame.time.get_ticks()
    while pygame.time.get_ticks() < startti + 1000 * sec:
        time.sleep(0.01)
        for ev in ge():
            if ev.type == KEYDOWN:
                if all: return True
                k = ev.key
                if k in p1c["B-1"]:
                    return True
            if ev.type == MOUSEBUTTONDOWN and all:
                return True
    return False

def wait_tick(t):
    """Waits a minimum of 20 ms"""
    pygt = pygame.time.get_ticks
    timebeen = (pygt() - t)
    if timebeen < 20:
        time.sleep((20 - timebeen) / 1000.0)
    return pygt()

def OptionsScreen(o_g_options, o_a_options, o_p_options, p1c):
    """Options screen where some variables can be customised"""
    global screen, mcurs, oldmcurs, Data

    g_options = o_g_options.copy()
    a_options = o_a_options.copy()
    p_options = o_p_options.copy()

    cont_p1_m = [
        p1c["Up"][0], p1c["Down"][0], p1c["Left"][0], p1c["Right"][0]
        ]
    cont_p1_a = [
        p1c["B-7"][0], p1c["B-8"][0], p1c["B-9"][0], p1c["B-4"][0], p1c["B-5"][0],
        p1c["B-6"][0], p1c["B-1"][0], p1c["B-2"][0], p1c["B-3"][0]
        ]
#    cont_p2_m = [
#        p2c["Up"][0], p2c["Down"][0], p2c["Left"][0], p2c["Right"][0]
#        ]
#    cont_p2_a = [
#        p2c["B-7"][0], p2c["B-8"][0], p2c["B-9"][0], p2c["B-4"][0], p2c["B-5"][0],
#        p2c["B-6"][0], p2c["B-1"][0], p2c["B-2"][0], p2c["B-3"][0]
#        ]

    # controls stuff --- >

    kset_movement1 = SET1(cont_p1_m, 410, 275, 1)
    kset_action1 = SET2(cont_p1_a, 250, 245, 1)
#    kset_movement2 = SET1(cont_p2_m, 410, 350, 2)
#    kset_action2 = SET2(cont_p2_a, 250, 320, 2)

    # < ---

    turn = 1

    pscreen = screen.copy().convert()
    nscreen = pygame.Surface((640,480))

    ti = pygame.time.get_ticks()

    OptionsScreenActive = True

    mpsurf, mprect = Data.images["Menupiece.png"]
    mtsurf = pygame.transform.flip(Data.images["MenuEndpiece.png"][0], False, True)
    mbsurf = Data.images["MenuEndpiece.png"][0]
    mssurf = Data.images["Selectorpiece.png"][0]

    bg = Data.images["Menu_Static.png"][0].copy().convert()

    optiontabs = [
        "Graphics",
        "Audio",
        "Game",
        "Controls",
        "Back",
        ]

    tabdesc = {
        "Graphics": "Change the way the game looks. Click to toggle options",
        "Audio": "Change what you hear from " + GAME_NAME + ". Click to toggle options.",
        "Game": "Change the gameplay. Click to toggle options.",
        "Controls": "Customise controls. Click a key, then press new key to redefine. Press keys to test them.",
        "Network": "Set networking options. Click to toggle options (I guess)",
        "Back": "",
        "": GAME_NAME + " options menu: select a tab on the left with the mouse."
        }
    
    tabover = {
        0: "Graphics options",
        1: "Sound options",
        2: "Gameplay options",
        3: "Control options",
        4: "Back to main menu",
        None: ""
        }

    graphicsflags = [
        ["Fullscreen", ["No", "Yes"]],
        ["Widescreen", ["No", "Yes"]],
        ["Parallax Backgrounds", ["Off", "One", "All"]],
        ["Parallax Foregrounds", ["Off", "One", "All"]],
        ["Moving BG Objects", ["Off", "On"]],
        ["Rain", ["Disallowed", "Allowed"]],
        ["Heat Shimmer", ["Off", "On"]],
        ["Particle Effects", ["Off", "Less", "More"]],
        ["Shake screen", ["No", "Yes"]],
        ["Pixellise screen", ["No", "Yes"]],
        ["Tint screen", ["No", "Yes"]],
        ["Shake battle window", ["No", "Yes"]],
        ]

    graphicsflags = [x+[g_options[[x[0],x[0][1:]][x[0].startswith("?")]]] for x in graphicsflags]

    audioflags = [
        ["Sound effects", ["Off", "Low", "Medium", "High"]],
        ["Music", ["Off", "Low", "Medium", "High"]],
        ]

    audioflags = [x+[a_options[[x[0],x[0][1:]][x[0].startswith("?")]]] for x in audioflags]

    gameflags = [
        ["Help", ["Off", "On"]],
        ]

    gameflags = [x+[p_options[[x[0],x[0][1:]][x[0].startswith("?")]]] for x in gameflags]
        

    descriptions = {
        "Fullscreen": {
        "No": GAME_NAME + " will be played in a window.",
        "Yes": GAME_NAME + " will take up the whole screen."
        },
        "Widescreen": {
        "No": "Game resolution ratio is 4:3.",
        "Yes": "If your monitor is 16:10, leave it on Yes. Affects fullscreen only."
        },
        "Parallax Backgrounds": {
        "Off": "No parallax backgrounds will be drawn.",
        "One": "Only the most important parallax background will be drawn.",
        "All": "All parallax backgrounds will be drawn."
        },
        "Parallax Foregrounds": {
        "Off": "No parallax foregrounds will be drawn.",
        "One": "Only the most important parallax foreground will be drawn.",
        "All": "All parallax foregrounds will be drawn."
        },
        "Moving BG Objects": {
        "Off": "No leaves, snow, etc. will be drawn.",
        "On": "Leaves, snow, etc. will be drawn."
        },
        "Rain": {
        "Disallowed": "No rain will be seen or heard, and nor will rain splashes.",
        "Allowed": "Rain and rain splashes will be seen and heard at various times."
        },
        "Heat Shimmer": {
        "On": "Some heat sources will cause shimmering effects.",
        "Off": "No shimmering effects will occur from heat."
        },
        "Particle Effects": {
        "Off": "No particles will be drawn.",
        "Less": "Half of all particles will be drawn.",
        "More": "All particles will be drawn."
        },
        "Shake screen": {
        "No": "Screen won't shake when damage is taken.",
        "Yes": "Screen will shake when damage is taken."
        },
        "Pixellise screen": {
        "No": "Screen won't become pixellised for a short time after taking damage.",
        "Yes": "Screen will become pixellised for a short time after taking damage."
        },
        "Tint screen": {
        "No": "Screen won't tint to certain colours.",
        "Yes": "Screen will tint to certain colours."
        },
        "Shake battle window": {
        "No": "Battle window will not shake when attacking an enemy.",
        "Yes": "Battle window will shake."
        },
        "Sound effects": {
        "Off": "No sound effects will be heard.",
        "Low": "Sound effects will be soft.",
        "Medium": "Sound effects will be medium volume.",
        "High": "Sound effects will be highest volume."
        },
        "Music": {
        "Off": "No music will be heard.",
        "Low": "Music will be soft.",
        "Medium": "Music will be medium volume.",
        "High": "Music will be highest volume."
        },
        "Help": {
        "Off": "No help messages will appear--good for advanced players during speedruns",
        "On": "Help messages will guide beginner players."
        },
        
        }

    menu_items = [
        (Fonts[16].render(x, 1, (255, 255, 255)),
         Fonts[16].render(x, 1, (255, 0, 0)),
         Fonts[16].render(x, 1, (0, 0, 0))) for x in optiontabs
        ]

    menu_select = None
    tab = ""
    s_select = 0
    alterlist = []

    do = ""

    menurect = Rect(0,200,160,29*len(menu_items))
    rvar = None

    yend = 0

    whiterectsurf = pygame.Surface((500, 20))
    whiterectsurf.fill((255,255,255))
    whiterectsurf.set_alpha(50)
    whiterectrect = whiterectsurf.get_rect()

    s_key = None
    cset = 0

    confirmmenu = False
    sti = 0
    conf_select = 0
    while OptionsScreenActive:
        bg.set_alpha(50)
        nscreen.fill((0,0,0))
        nscreen.blit(bg, (0,0))
        mprect.midleft = (0, 186)
        if not confirmmenu:
            nscreen.blit(mtsurf, mprect)
            for x in range(len(optiontabs)):
                mprect.midleft = (0, 215 + x*29)
                nscreen.blit(mpsurf, mprect)

                if x == menu_select:
                    nscreen.blit(mssurf, mprect)

                isurfs = menu_items[x]
                irect = isurfs[0].get_rect()
                irect.midleft = (5, 215 + x*29)
                if optiontabs[x] == tab: y = 1
                else: y = 2
                nscreen.blit(isurfs[y], irect)
                nscreen.blit(isurfs[0], irect.move(-1,-1))
            mprect.midleft = (0, 244 + x*29)
            nscreen.blit(mbsurf, mprect)

        oldmcurs = mcurs

        ti = wait_tick(ti)
        sti += 1
        h_key = None

        # Tab-specific options

        if tab == "Graphics":
            alterlist = graphicsflags
            optionchangelist = g_options
        elif tab == "Audio":
            alterlist = audioflags
            optionchangelist = a_options
        elif tab == "Game":
            alterlist = gameflags
            optionchangelist = p_options
        elif tab == "Controls":
            pygame.event.pump()
            pkgp = pygame.key.get_pressed()
            for s in [kset_movement1.keys, kset_action1.keys]:
                for k in s:

                    im2blit = "Keyup.png"
                    if abs(mcurs[0] - k.x) < 16:
                        if abs(mcurs[1] - k.y) < 15:
                            im2blit = "Keyup_h.png"
                            h_key = k

                    mycol = [(150,150,150), (255,255,255)][k == h_key]

                    #key
                    
                    if pkgp[k.keycode]: im2blit = "Keydown.png"; mycol = (0,0,0)

                    keypic, keyrect = Data.images[im2blit]
                    keyrect.center = (k.x, k.y)
                    nscreen.blit(keypic, keyrect)

                    #label
                    
                    finallabel = [k.label[:3], "_"][k == s_key]
                    labelsurf = Fonts[13].render(finallabel, 1, mycol)
                    labelrect = labelsurf.get_rect()
                    labelrect.center = (k.x, k.y - [3,0][pkgp[k.keycode]])
                    nscreen.blit(labelsurf, labelrect)

            if h_key:
                keysurf = Fonts[13].render(h_key.binding.replace("B-", "Action button ") + ": " + h_key.label, 1, (255,255,255))
                keyrect = keysurf.get_rect()
                keyrect.center = (348, 420)
                nscreen.blit(keysurf, keyrect)

        # Tab option printing

        if tab != "" and tab != None and tab != "Controls":
            for x in range(len(alterlist)):
                col = (255,255,255)
                if alterlist[x][0].startswith("?"):
                    rendername = alterlist[x][0][1:]
                    col = (255,255,0)
                else:
                    rendername = alterlist[x][0]

                if x != s_select:
                    col = (col[0]*0.5, col[1]*0.5, col[2]*0.4)
                else:
                    whiterectsurf.set_alpha(50 + 30 * math.sin(ti/100.0))
                    whiterectrect.midleft = (190, 100 + x * 20)
                    nscreen.blit(whiterectsurf, whiterectrect)

                ops=Fonts[13].render(rendername+": "+alterlist[x][1][alterlist[x][2]],1,col)
                opr = ops.get_rect()
                opr.midleft = (200, 100 + x * 20)
                nscreen.blit(ops, opr)
            yend = 109 + x*20
#            ynotice = Fonts[13].render("Yellow options will take effect the next time you run " + GAME_NAME, 1, (200, 200, 0))
#            yrect = ynotice.get_rect()
#            yrect.bottomright = (635, 455)
#            nscreen.blit(ynotice, yrect)

            if s_select != None:
                oname, oopts, osel = alterlist[s_select]
                info = Fonts[13].render(
                    [oname, oname[1:]][oname.startswith("?")] + ": " +\
                    oopts[osel] + ": " +\
                    descriptions[oname][oopts[osel]],
                    1, (255,255,255)
                    )
                inforect = info.get_rect()
                inforect.bottomright = (635, 475)
                nscreen.blit(info, inforect)

            for option in alterlist:
                oc = option[0]
                if oc.startswith("?"): oc = oc[1:]
                optionchangelist[oc] = option[2]

        topsurf = Fonts[13].render(tabdesc[tab], 1, (255,255,255))
        toprect = topsurf.get_rect()
        toprect.center = (320, 60)

        bottomsurf = Fonts[13].render(tabover[menu_select], 1, (255,255,255))
        bottomrect = bottomsurf.get_rect()
        bottomrect.midleft = (10, 420)

        nscreen.blit(topsurf, toprect)
        nscreen.blit(bottomsurf, bottomrect)

        for event in ge():
            t = event.type
            if t == MOUSEMOTION:
                mcurs = list(event.pos)
            elif t == MOUSEBUTTONDOWN:
                b = event.button
                if b == 1:
                    if s_select != None:
                        alterlist[s_select][2] += 1
                        if alterlist[s_select][2] == len(alterlist[s_select][1]):
                            alterlist[s_select][2] = 0

                        if alterlist[0][0] == "Sound effects":
                            soundbox.set_svol(alterlist[0][2])
                            soundbox.set_mvol(alterlist[1][2])
                        
                    if menurect.collidepoint(mcurs) and menu_select != None:
                        do = optiontabs[menu_select]

                    if h_key: s_key = h_key
                    else: s_key = None

                    if conf_select == 3:
                        confirmmenu = False
                        do = ""
                        tab = ""
                        menu_select = None
                        conf_select = 0
                    elif conf_select == 2:
                        do = "OUT.discard"
                    elif conf_select == 1:
                        do = "OUT.save"

            elif t == KEYDOWN:
                k = event.key
                notusable = [K_ESCAPE, K_RETURN, K_BACKQUOTE, K_PAUSE]
                if k == K_RETURN:
                    cset = abs(cset - 1)
                if k in notusable:
                    s_key = None
                    continue
                if s_key:
                    s_key.keycode = k
                    s_key.label = pygame.key.name(k)
                    if s_key.label[:3] == "unk":
                        s_key.label = "???"
                    s_key = None

        # Handle mcurs

        if menurect.collidepoint(mcurs) and not confirmmenu:
            menu_select = (mcurs[1] - 200) / 29
        else:
            menu_select = None

        if 200 <= mcurs[0] <= 640 and 90 <= mcurs[1] <= yend:
            s_select = (mcurs[1] - 90) / 20
        else:
            s_select = None

        # Confirm Menu
        if confirmmenu:
            if 290 <= mcurs[1] <= 315:
                if 0 <= mcurs[0] <= 150:
                    if conf_select != 1: sti = 0
                    conf_select = 1
                elif 230 <= mcurs[0] <= 410:
                    if conf_select != 2: sti = 0
                    conf_select = 2
                elif 430 <= mcurs[0] <= 640:
                    if conf_select != 3: sti = 0
                    conf_select = 3
                else:
                    conf_select = 0
            else:
                conf_select = 0
            tab = ""
#            nscreen.fill((0,0,0), Rect(100, 200, 440, 140))
            cbit = pygame.Surface((640,100))
            bws = Data.images["BlueWhiffBG.png"][0]
            bws2 = Data.images["BlueWhiffBG2.png"][0]
            bws3 = Data.images["BlueWhiffBG3.png"][0]

            m1 = 0.05
            m2 = 0.1
            m3 = 0.15

            cbit.blit(bws, ((ti*m1)%640,0))
            cbit.blit(bws, ((ti*m1)%640-640,0))
            cbit.blit(bws2, ((ti*m2)%640,0))
            cbit.blit(bws2, ((ti*m2)%640-640,0))
            cbit.blit(bws3, ((ti*m3)%640,0))
            cbit.blit(bws3, ((ti*m3)%640-640,0))

            nscreen.blit(cbit, (0,220))
            nscreen.blit(Data.images["BWBGW.png"][0], (0, 200))
            nscreen.blit(pygame.transform.flip(Data.images["BWBGW.png"][0], False, True), (0, 320))
            ts = Fonts[16].render("Save changes?", 1, (0,0,0))
            tr = ts.get_rect()
            tr.center = (320, 230)
            nscreen.blit(ts, tr)

            c1, c2, c3 = [[100, 10][conf_select==x+1] for x in range(3)]

            mitems = [
                Fonts[16].render("Save changes", 1, (c1,c1,c1)),
                Fonts[16].render("Discard changes", 1, (c2,c2,c2)),
                Fonts[16].render("Cancel, back to options", 1, (c3,c3,c3))
                ]                

            sv = math.sin(sti/10.0)*8

            mr = []
            for m in mitems:
                mr.append(m.get_rect())
            mr[0].midleft = (10, 300+[0,sv][conf_select==1])
            mr[1].center = (320, 300+[0,sv][conf_select==2])
            mr[2].midright = (630, 300+[0,sv][conf_select==3])

            nscreen.blit(mitems[0], mr[0])
            nscreen.blit(mitems[1], mr[1])
            nscreen.blit(mitems[2], mr[2])

        nscreen.blit(Data.images["MouseCurs2.png"][0], mcurs)
        if turn < 41:
            screen.blit(nscreen, (0,0))
            pscreen.set_alpha(255-turn*6)
            screen.blit(pscreen, (0,0))
            turn += 1
        else:
            screen.blit(nscreen, (0,0))

        myflip()

        if do == "Back":
            confirmmenu = True
            conf_select = 0
            tab = ""
            do = ""
        elif do == "OUT.save":
            OptionsScreenActive = False

            # Alright, here we have to map the keys back to the controls.
            for set in [kset_movement1, kset_action1]:
                playercontrols = p1c
                for key in set.keys:
                    playercontrols[key.binding] = [key.keycode]
            
            rvar = g_options, a_options, p_options, p1c
        elif do == "OUT.discard":
            OptionsScreenActive = False
            rvar = o_g_options, o_a_options, o_p_options, p1c
            soundbox.set_svol(o_a_options["Sound effects"])
            soundbox.set_mvol(o_a_options["Music"])

        else:
            tab = do

    return rvar

def BranchScreenTemplate():
    """A template for branching off the main menu"""
    global screen, mcurs, oldmcurs, Data

    turn = 1

    pscreen = screen.copy().convert()
    nscreen = pygame.Surface((640,480))

    ti = pygame.time.get_ticks()

    Active = True

    bg = Data.images["Menu_Static.png"][0].copy().convert()

    while Active:
        bg.set_alpha(50)
        nscreen.fill((0,0,0))
        nscreen.blit(bg, (0,0))

        oldmcurs = mcurs

        ti = wait_tick(ti)

        for event in ge():
            t = event.type
            if t == MOUSEMOTION:
                mcurs = event.pos

        nscreen.blit(Data.images["MouseCurs2.png"][0], mcurs)
        if turn < 41:
            screen.blit(nscreen, (0,0))
            pscreen.set_alpha(255-turn*6)
            screen.blit(pscreen, (0,0))
            turn += 1
        else:
            screen.blit(nscreen, (0,0))
        myflip()


def main():
    """The game, from init"""
    global screen, Fonts, soundbox, Data
    global mcurs, oldmcurs, ACC, shc
    global g_options, a_options, p_options, p1c
    global VERSION, DEBUG, WIDESCREENBIT, DVERSION

    KEY_PRESSED = False

    SLOW = True
    SOUND = True

    HZ = None
    
    # Handle command parameters
    sri = None
    x = 0
    try:
        if len(sys.argv) > 1:
            
            parameters = sys.argv[1:]
            logfile("Ardentryst parameters: " + str(parameters))
            for option in parameters:
                x += 1
                if option == "-w":
                    FULLSCREENBIT = False
                elif option == "-f":
                    FULLSCREENBIT = True
                elif option == "-ws" and FULLSCREENBIT:
                    WIDESCREENBIT = True
                elif option == "-q":
                    SLOW = False
                    NOFADES()
                elif option == "-ns":
                    SOUND = False
                elif option == "-sr":
                    sri = x
                else:
                    if sri:
                        if x == sri + 1:
                            HZ = int(option)
    except:
        print "Command-line option malformed and options after were not processed"

    if not SLOW: fade_set_slow()

    print "\n-------------------------------------------------------------------------------"
    print (GAME_NAME + " v." + VERSION).center(79)
    print "by Jordan Trudgett".center(79)
    print "-------------------------------------------------------------------------------\n"

    print "    Ardentryst Copyright (C) 2007, 2008, 2009 Jordan Trudgett"
    print "    This program comes with ABSOLUTELY NO WARRANTY."
    print "    This is free software, and you are welcome to redistribute it"
    print "    under certain conditions; for details, see the COPYING file."


    logfile(GAME_NAME + " v." + VERSION)

    ACC, shc = getattr(ac(), "sdc"[::-1])()
    logfile("Secure hash code: " + shc)
    logfile("ACC" + str(ACC))
#    ACC = True

    if not ACC:
        print "Your score can not be uploaded to the server because your version of Ardentryst is not the original version."

    logfile("Configuring game settings...")
    # These are default options!

    g_options = {
        "Fullscreen": 0,
        "Widescreen": 0,
        "Parallax Backgrounds": 2,
        "Parallax Foregrounds": 2,
        "Moving BG Objects": 1, 
        "Rain": 1,
        "Heat Shimmer": 1,
        "Particle Effects": 2,
        "Shake screen": 1,
        "Pixellise screen": 1,
        "Tint screen": 1,
        "Shake battle window": 1,
        }

    a_options = {
        "Sound effects": 3,
        "Music": 3,
        }

    p_options = {
        "Help": 1,
        "MustOP": 1,
        }

    p1c = {
        "Up": [K_UP],
        "Down": [K_DOWN],
        "Left": [K_LEFT],
        "Right": [K_RIGHT],
        "B-1": [K_c],
        "B-2": [K_x],
        "B-3": [K_z],
        "B-4": [K_d],
        "B-5": [K_s],
        "B-6": [K_a],
        "B-7": [K_e],
        "B-8": [K_w],
        "B-9": [K_q]
        }

    # Load options from file

    try:
        optionsfile = open(os.path.join(SAVEDIRECTORY, "options.dat"), "r")

        graphic_o = cPickle.load(optionsfile)
        audio_o = cPickle.load(optionsfile)
        play_o = cPickle.load(optionsfile)
        controls_o = cPickle.load(optionsfile)

        for dp in [(graphic_o, g_options), (audio_o, a_options), (play_o, p_options), (controls_o, p1c)]:
            for key in dp[0]:
                dp[1][key] = dp[0][key]
    except EOFError:
        raise Exception("** Please remove your options.dat file (in your ~/.ardentryst/ directory) and run Ardentryst again. **")
    except IOError:
        # First time, no options file. Just stick to defaults :)
        # It will be created once changes are made to the options, then saved.
        pass

    FULLSCREENBIT = g_options["Fullscreen"]
    WIDESCREENBIT = g_options["Widescreen"] and FULLSCREENBIT # No point having a window bigger than needed

    # Start up sound system

    import Conch

    if SOUND:
        Conch.conchinit(HZ)
    else:
        print "Not starting sound module"
        
    soundbox = Conch.soundbox

    soundbox.set_svol(a_options["Sound effects"])
    soundbox.set_mvol(a_options["Music"])

    logfile("Soundbox successfuly created.")

##     print "Fullscreen: " + str(FULLSCREENBIT)
##     if FULLSCREENBIT:
##         print "You can play in a window with:"
##         print "    python "+sys.argv[0]+" -w"
##     else:
##         print "You can play in fullscreen with:"
##         print "    python "+sys.argv[0]+" -f"

    pygame.display.init()
    pygame.display.set_caption("Ardentryst v."+VERSION)
    pygame.font.init()
    pygame.mouse.set_visible(False)                  # Don't want to see the mouse!

    res = [(640, 480), (840, 525)][WIDESCREENBIT]

    window = pygame.display.set_mode(res, [0, FULLSCREEN][FULLSCREENBIT])
    pygame.display.set_icon(load_image("icon.png")[0])

    if not WIDESCREENBIT:
        screen = pygame.display.get_surface()

    if WIDESCREENBIT:
        wsscreen = pygame.display.get_surface()
        screen = pygame.Surface((640,480))
        defineWSscreen(wsscreen)

    definescreen(screen)

    scr_size = screen.get_size()

    clock = pygame.time.Clock() # MUST be kept in for timer to begin.

    # Fonts initialise

    fontlist = [
        ("FreeSans.ttf", 25),  #0
        ("FreeSans.ttf", 20),        #1
        ("FreeSerif.ttf", 25),      #2
        ("FreeSans.ttf", 14),        #3
        ("FreeSans.ttf", 50),         #4
        ("FreeSans.ttf", 22),          #5
        ("FreeSans.ttf", 12),        #6
        ("FreeSerif.ttf", 14),     #7
        ("FreeSerif.ttf", 16),      #8
        ("FreeSerif.ttf", 14),     #9
        ("FreeSerif.ttf", 20),      #10
        ("FreeSerif.ttf", 30),      #11
        ("FreeSerif.ttf", 16),      #12
        ("FreeSerif.ttf", 16),     #13
        ("FreeSerif.ttf", 32),     #14
        ("FreeSerif.ttf", 12),     #15
        ("FreeSerif.ttf", 18),     #16
        ("FreeSerif.ttf", 26),     #17
        ("FreeSans.ttf", 15),   #18
        ("FreeSans.ttf", 12),   #19
        ("FreeSans.ttf", 20),        #20
        ("FreeSans.ttf",25),         #21
        ("FreeSerif.ttf", 32),     #22
        ("FreeSans.ttf", 14),        #23
        ]

    Fonts = {}

    for x in range(len(fontlist)):
        Fonts[x] = pygame.font.Font(os.path.join("Fonts", fontlist[x][0]), fontlist[x][1])

    
    logfile("Fonts loaded!")
    # End fonts

    # Before precaching, show initialisation screen for debugging purposes
    if DEBUG:
        initscreen(screen, Fonts[12])

    Data = Storage() # Data is the Storage container.
    Data.showload = True

    # Show loading screen and precache data
    loading_pics = load_image("Title.png")
    Loading_Screen(screen, loading_pics, Fonts[21], ACC)
    myflip()

    if SOUND:
        pygame.mixer.music.load(os.path.join("Music", "theme1.ogg"))
        pygame.mixer.music.set_volume(soundbox.music_volume)
        pygame.mixer.music.play(-1)

    Data.precache_images()
    Data.precache_levels()

    Update_Loading(-1, "Please wait, precaching sound effects...")

    for song in Data.SONGS:
        soundbox.LoadSong(song[0], song[1])
    for sound in Data.SOUNDS:
        soundbox.LoadSound(sound[0], sound[1])

    fade_to_black(screen, 2*SLOW)
    if SLOW: time.sleep(1)

#    soundbox.PlaySong("theme1.ogg", -1)

    ELABORATE_INTRO = True

    eclx = 0

    events = ge()
    for event in events:
        if event.type == KEYDOWN:
            ELABORATE_INTRO = False
    GAMELOOP = True
    while GAMELOOP:
        # Show game info slide(s)
        for scrp in [
            ("Dedication.png", 4),
            ("DevelopedWith.png", 5),
            ]:
            screen.blit(Data.images[scrp[0]][0], (0,0))
            skipsurf = Fonts[13].render("Press a key to skip", 1, (155,155,155))
            skiprect = skipsurf.get_rect()
            skiprect.bottomright = (635,475)
            screen.blit(skipsurf, skiprect)

            fade_from_black(screen, 5)
            csleep(scrp[1], True)
            fade_to_black(screen)

        ON_MENU = True
        menu_items = ["New quest",
                      "Resume quest",
                      "Options",
                      "Credits",
                      "About the game",
                      "Online play rules",
                      "Quit"]

        if p_options["MustOP"]:
            activeitem = dict.fromkeys(menu_items, False)
            activeitem["Online play rules"] = True
            menu_select = 5
            handy = 218 + menu_select * 29
            ahandy = handy
        else:
            activeitem = dict.fromkeys(menu_items, True)
            menu_select = 0
            handy = 218 + menu_select * 29
            ahandy = handy

        ge()                                # Flush events (most likely during fade)
                                            # Don't want to start new game
                                            # if enter was pressed twice accidentally

        ticker = 0
        t = pygame.time.get_ticks()

        MENU_STATUS = GAME_NAME + ": A 2007-2009 Software Project created by Jordan Trudgett. Written in 100% Python and pygame. This game is open source software. Please distribute it to your friends!"
        sttext = Fonts[7].render(MENU_STATUS, 1, (255,245,235))
        sttextb = Fonts[7].render(MENU_STATUS, 1, (0,0,0))
        slen = sttext.get_rect()[2]

        vtextW = Fonts[9].render("Version " + DVERSION, 1, (255,255,255))
        vtextlen = vtextW.get_rect()[2]

        svtexts = Fonts[9].render("Ardentryst, by Jordan Trudgett: http://jordan.trudgett.com/", 1, (255,255,255))
        svtextr = svtexts.get_rect()
        svtextr.midleft = (5,25)
        
        s1x = 627
        s2x = 647 + slen

        mcurs = list(pygame.mouse.get_pos())
        oldmcurs = [0,0]
        currentcurs = Data.images["MouseCurs2.png"][0]
        glow = Data.images["Glow.png"][0]
        glowrect = glow.get_rect()

        menu_texts = [] # List of rendered menu item surfs

        miw = 0
        for x in range(len(menu_items)):
            menu_texts.append((Fonts[16].render(menu_items[x], 1, (255,255,255)),
                               Fonts[16].render(menu_items[x], 1, (0  ,0  ,0  ))))
            tmiw = menu_texts[-1][0].get_rect()[2] #Menu Item Width
            if tmiw > miw: miw = tmiw
        mih = 24
        addy = menu_texts[-1][0].get_rect()[3]-27

        selector = Data.images["Selectorpiece.png"][0]
        endpiecebottom = Data.images["MenuEndpiece.png"][0]
        endpiecetop = pygame.transform.flip(Data.images["MenuEndpiece.png"][0],False,True)
        menupiece = Data.images["Menupiece.png"][0]

##         screen.blit(vtextW, (5, 5))

##         eptr = endpiecetop.get_rect()
##         eptr.midleft = (0, 186)
##         screen.blit(endpiecetop, eptr)

##         for i in range(len(menu_texts)):
##             mprect = menupiece.get_rect()
##             mprect.midleft = (0, 215 + i * 29)
##             screen.blit(menupiece,mprect)

##             mtrect = menu_texts[i][1].get_rect()
##             mtrect.midleft = (10, 215 + i * 29)
##             screen.blit(menu_texts[i][1], mtrect)
##             screen.blit(menu_texts[i][0], mtrect.move(-1,-1))

##         epbr = endpiecebottom.get_rect()
##         epbr.midleft = (0, 215 + (i+1) * 29)
##         screen.blit(endpiecebottom, epbr)


        old_ms = 0
        selected = ""

        Menu_Item_Data = {
            "New quest": "Start a new quest from the very beginning.",
            "Resume quest": "Continue a saved quest!",
            "Options": "Tweak the game's settings.",
            "Credits": "See who developed and contributed to " + GAME_NAME + ".",
            "About the game": "A little bit of information about " + GAME_NAME + ".",
            "Online play rules": "Read the rules of playing Ardentryst Online before you start!",
            "Quit": "Finish playing, quit " + GAME_NAME + "."
            }

        ONTEXT = ""
        ontextmov = 0

#        fade_from_black(screen)
        needfade = True
        sinselect = 0

        sparks = []

        silsurf = pygame.Surface((350,350))
        silalpha = -90
        cursil = "1"
        sildir = 3

        logfile("Entering main menu.")

        LIGHTNING = []

        WHITESURF = pygame.Surface((640,480))
        WHITESURF.fill((255,255,255))

        LIGHTNINGCUES = [[879, 160], [1059, 200], [1488, 150], [2007, 170], [13890, 240], [14700, 130], [15350, 120], [16000, 100], [40592, 255], [41700, 100], [42486, 70], [43524, 70], [54394, 120], [61790, 50], [81900, 250], [82000, 180], [82100, 160], [83200, 100], [83400, 100], [83600, 90], [83800, 80], [85605, 80], [95798, 255], [96800, 200], [97920, 120], [98820, 100], [116996, 100]]
        DONELIGHTNINGCUES = []
        if SOUND:
            ms = pygame.mixer.music.get_pos()
            for lc in LIGHTNINGCUES:
                if ms > lc[0]:
                    DONELIGHTNINGCUES.append(lc)

        gv = globals()

        defmmpic(screen)

        while ON_MENU:

            if SOUND:
                music_ms = pygame.mixer.music.get_pos() % 135604

                if music_ms < LIGHTNINGCUES[0][0]:
                    DONELIGHTNINGCUES = []

                if len(DONELIGHTNINGCUES) < len(LIGHTNINGCUES):

                    if music_ms > LIGHTNINGCUES[len(DONELIGHTNINGCUES)][0]:
                        DONELIGHTNINGCUES.append(LIGHTNINGCUES[len(DONELIGHTNINGCUES)])
                        LIGHTNING.append([random.randint(0,1), random.randint(0,640), random.randint(0,30), LIGHTNINGCUES[len(DONELIGHTNINGCUES)-1][1]])
                
            ticker += 1
            sinselect = math.sin(ticker/20.0) * 30
            silalpha += sildir
            if silalpha >= 600:
                sildir = -3
            if silalpha < -100:
                sildir = 3
                cursil = ["1","2"][cursil=="1"]
            screen.blit(Data.images["Menu_Static.png"][0], (0,0))
            screen.blit(Data.images["ECL2.png"][0], (-int(eclx)%640,160))
            screen.blit(Data.images["ECL2.png"][0], (-int(eclx)%640-640,160))


            # Flying birds
            screen.blit(Data.images["mbirds" + str(abs(ticker/10%6 - 3)+1) + ".png"][0], ((ticker/1.8)%2000 - 180, 125 + math.sin(ticker/50.0)*15))
            screen.blit(Data.images["mbirds" + str(abs((ticker-18)/10%6 - 3)+1) + ".png"][0], ((ticker/1.9)%2000 - 130,  120 + math.sin((ticker-15)/59.0)*12))
            screen.blit(Data.images["mbirds" + str(abs((ticker-39)/10%6 - 3)+1) + ".png"][0], ((ticker/2)%2000 - 60,  110 + math.sin((ticker-8)/75.0)*19))
            screen.blit(Data.images["mbirds" + str(abs(ticker/10%6 - 3)+1) + ".png"][0], ((ticker/1.8)%2000 - 680, 125 + math.sin(ticker/50.0)*15))
            screen.blit(Data.images["mbirds" + str(abs((ticker-18)/10%6 - 3)+1) + ".png"][0], ((ticker/1.9)%2000 - 730,  120 + math.sin((ticker-15)/59.0)*12))
            screen.blit(Data.images["mbirds" + str(abs((ticker-39)/10%6 - 3)+1) + ".png"][0], ((ticker/2)%2000 - 860,  110 + math.sin((ticker-8)/75.0)*19))

            for x in range(len(LIGHTNING)):
                lightning = LIGHTNING[x]
                SCREENBIT = pygame.Surface((319, 203))
                rx, ry = (lightning[1]-160, 260+lightning[2])
                SCREENBIT.blit(screen, (-rx,-ry))
                if lightning[0] == 0:
                    screen.blit(Data.images["lightning.png"][0], (lightning[1]-160, 260+lightning[2]))
                    lightning[1] -= 1
                    SCREENBIT.set_alpha(255-lightning[3])
                    screen.blit(SCREENBIT, (lightning[1]-160, 260+lightning[2]))
                    lightning[3] *= 0.9
                    lightning[3] = int(lightning[3])
                    if lightning[3] <= 0.5:
                        LIGHTNING[x] = None

            while None in LIGHTNING:
                LIGHTNING.remove(None)

            screen.blit(Data.images["ECL1.png"][0], (-int(eclx*3)%640, 259))
            screen.blit(Data.images["ECL1.png"][0], (-int(eclx*3)%640-640, 259))

            for x in range(len(LIGHTNING)):
                lightning = LIGHTNING[x]
                SCREENBIT = pygame.Surface((319, 203))
                rx, ry = (lightning[1]-160, 290+lightning[2])
                SCREENBIT.blit(screen, (-rx,-ry))
                if lightning[0] == 1:
                    screen.blit(Data.images["lightning.png"][0], (lightning[1]-160, 340+lightning[2]))
                    lightning[1] -= 1
                    SCREENBIT.set_alpha(255-lightning[3])
                    screen.blit(SCREENBIT, (lightning[1]-160, 290+lightning[2]))
                    lightning[3] -= 7
                    if lightning[3] <= 0:
                        LIGHTNING[x] = None

            while None in LIGHTNING:
                LIGHTNING.remove(None)


            if len(LIGHTNING):
                LBRIGHT = sum([x[3] for x in LIGHTNING])/float(len(LIGHTNING))
            else:
                LBRIGHT = 0

            # screenwhite
            if len(LIGHTNING):
                WHITESURF.set_alpha(LBRIGHT * 0.3)
                screen.blit(WHITESURF, (0,0))

            # Scrolling status bar text
            screen.blit(sttextb, (s1x, 461))
            screen.blit(sttext, (s1x-1, 460))
            screen.blit(sttextb, (s2x, 461))
            screen.blit(sttext, (s2x-1, 460))
            #Cliff over status bar text
            screen.blit(Data.images["Cliff.png"][0], (0,0))

            # lit cliff
            if len(LIGHTNING):
                lcs, lcr = Data.images["LitCliff.png"]

                lcr.bottomright = (640,480)
                SCREENBIT = pygame.Surface(lcr.size)
                SCREENBIT.blit(screen, (0,0), lcr)
                SCREENBIT.set_alpha(max(0,255-2*LBRIGHT))
                screen.blit(lcs, lcr)
                screen.blit(SCREENBIT, lcr)

            # silhouette

            for cursil in range(2):
                posm = cursil*12
                cursil = str(cursil+1)
                silalpha = 255
                if len(LIGHTNING):
                    fractionlit = min(LBRIGHT*2/255.0, 1)

                    silsurf.blit(screen, (-400-posm, -30))
                    silsurf.blit(Data.images["Silhouette"+cursil+".png"][0], (0,0))
                    fsilalpha = max(min(255, silalpha), 0)

                    unlitalpha = (fsilalpha) * (1-fractionlit)

                    silsurf.set_alpha(255) # unlitalpha)
                    screen.blit(silsurf, (400+posm, 30))

                    silsurf.blit(screen, (-400-posm, -30))
                    silsurf.blit(Data.images["LSilhouette"+cursil+".png"][0], (0,0))

                    litalpha = fsilalpha - unlitalpha

                    silsurf.set_alpha(litalpha)
                    screen.blit(silsurf, (400+posm, 30))

                else:
                    silsurf.blit(screen, (-400-posm, -30))
                    silsurf.blit(Data.images["Silhouette"+cursil+".png"][0], (0,0))
                    fsilalpha = max(min(255, silalpha), 0)

                    silsurf.set_alpha(fsilalpha)
                    screen.blit(silsurf, (400+posm, 30))




            
            # Version text
            vtr = screen.blit(vtextW, (5, 5))
            screen.blit(svtexts, svtextr)
        
            if needfade: fade_from_black(screen); needfade = False

            s1x -= 1
            s2x -= 1
            if s1x < -slen - 20: s1x = slen + 20
            if s2x < -slen - 20: s2x = slen + 20

            t = wait_tick(t)
            oldmcurs = mcurs

            eclx += 0.25

            for x in range(6):
                sparks.append(Spark(mcurs, ticker))
            for s in range(len(sparks)):
                sparks[s].blit(screen)
                if sparks[s].removeme:
                    sparks[s] = None

            while None in sparks:
                sparks.remove(None)


            # Menu items (just above sparks so that they don't hinder reading)
            # (MOVED DOWN 50 px)
            # now moved up again! haha.

            eptr = endpiecetop.get_rect()
            eptr.midleft = (0, 214)
            screen.blit(endpiecetop, eptr)

            if ahandy != handy:
                ahandy = int(round((ahandy * 2 + handy)/3.0))
            if abs(ahandy-handy) < 2: ahandy = handy
            screen.blit(Data.images["hand.png"][0], (150+abs(math.sin(ticker/10.0)*10), ahandy))
            for i in range(len(menu_texts)):
                mprect = menupiece.get_rect()
                mprect.midleft = (0, 243 + i * 29)
                screen.blit(menupiece,mprect)
                if i == menu_select:
                    srect = selector.get_rect()
                    srect.midleft = (-30 + sinselect, 243 + i * 29)
                    screen.blit(selector, srect)

                mtrect = menu_texts[i][1].get_rect()
                mtrect.midleft = (10 + [0,6][i==menu_select], 243 + i * 29)

                screen.blit(menu_texts[i][1], mtrect)
                if activeitem[menu_items[i]]:
                    screen.blit(menu_texts[i][0], mtrect.move(-1,-1))

            epbr = endpiecebottom.get_rect()
            epbr.midleft = (0, 243 + (i+1) * 29)
            screen.blit(endpiecebottom, epbr)

            if menu_select != -1:
                ONTEXT = Menu_Item_Data[menu_items[menu_select]]
            ONTEXTSURF = Fonts[16].render(ONTEXT, 1, (255,255,255))
            ONTEXTSURFG = Fonts[16].render(ONTEXT, 1, (0,0,0))
            ONTEXTRECT = ONTEXTSURF.get_rect()

            ONTEXTRECT.topleft = (25-ontextmov, 440)
            screen.blit(ONTEXTSURFG, ONTEXTRECT.move(1,1))
            screen.blit(ONTEXTSURF, ONTEXTRECT)


            glowrect.center = mcurs
            screen.blit(glow,glowrect)

            screen.blit(currentcurs, mcurs)
            menuur = Rect(0,185,miw+40,(mih+5)*len(menu_items)+20)
            versiontextur = Rect(vtr[0],vtr[1],vtr[2]+2,vtr[3]+2)


            for event in ge():
                if event.type == KEYDOWN:
                    k = event.key
                    if k == K_l:
                        LIGHTNING.append([random.randint(0,1), random.randint(0,640), random.randint(0,30), 255])
                    if k == K_DOWN or k in p1c["Down"]:
                        if menu_select < len(menu_items)-1 and activeitem[menu_items[menu_select+1]]:
                            menu_select += 1
                            handy = 218 + menu_select * 29
                    elif k == K_UP or k in p1c["Up"]:
                        if menu_select > 0 and activeitem[menu_items[menu_select-1]]:
                            menu_select -= 1
                            handy = 218 + menu_select * 29
                    elif k == K_RETURN or k == K_SPACE or k == K_KP_ENTER or k in p1c["B-1"]:
                        if menu_select == -1:
                            menu_select = 0
                            handy = 218 + menu_select * 29
                            continue
                        selected = menu_items[menu_select]
                elif event.type == MOUSEMOTION:
                    mcurs = list(pygame.mouse.get_pos())
                    #check if on menu items
                    if 150 > mcurs[0] > 0 and 230 + 29 * (len(menu_items)) > mcurs[1] > 230:
                        if activeitem[menu_items[(mcurs[1]-230) / 29]]:
                            menu_select = (mcurs[1]-230) / 29
                            handy = 218 + menu_select * 29
                            if menu_select >= len(menu_items): menu_select = -1


                elif event.type == MOUSEBUTTONDOWN:
                    button = event.button
                    if button == 1:
                        if menu_select == -1:
                            continue
                        if 150 > mcurs[0] > 0 and 230 + 29 * (len(menu_items)) > mcurs[1] > 230:
                            selected = menu_items[menu_select]

            if menu_select != old_ms:
                old_ms = menu_select
                ontextmov = Fonts[13].size(Menu_Item_Data[menu_items[menu_select]])[0]
                interface_sound("menu-item")

            if selected:
                interface_sound("menu-select")
                logfile("(Main Menu) Selected " + selected)

            if selected == "Quit":
                soundbox.FadeoutMusic(1500)
                fade_to_black(screen, 35)
                Quit()
                ON_MENU = False
                GAMELOOP = False

            elif selected == "Crash":
                raise Exception("Intentionally raised exception")
            elif selected == "New quest":
                Game = Game_Object()
                fade_to_black(screen, 2*SLOW)
                Game = Game_SlotMenu(Game)
                if Game:
                    soundbox.FadeoutMusic(1000)
                    fade_to_black(screen, 4*SLOW)
                    ge() #Flush events before story
                    Game.text_intro(screen, Data, Fonts, soundbox)
                    fade_to_black(screen, 4*SLOW)
                    Game.story_scene("Introduction", screen, Data, Fonts, soundbox)
                    fade_to_black(screen, 2*SLOW)
                    # Play!
                    handle_game(Game)
                    soundbox.PlaySong("theme1.ogg", -1)
                selected = ""
                needfade = True
            elif selected == "Resume quest":
                fade_to_black(screen, 2*SLOW)
                Game = Game_SlotMenu()
                if Game:
                    # Firstly verify the game file/player
                    # (has all the vars we use)
                    Game = verify_game(Game)
                    soundbox.FadeoutMusic(1000)
                    fade_to_black(screen, 2*SLOW)
                    handle_game(Game, True)
                    soundbox.PlaySong("theme1.ogg", -1)
                selected = ""
                needfade = True
            elif selected == "Options":
                oops = g_options, a_options, p_options, p1c # Original OPtionS
                rv = OptionsScreen(g_options, a_options, p_options, p1c)

                # This just catches up on the lightning (haha)
                if SOUND:
                    ms = pygame.mixer.music.get_pos()
                    for lc in LIGHTNINGCUES:
                        if ms > lc[0]:
                            DONELIGHTNINGCUES.append(lc)

                if rv:
                    g_options, a_options, p_options, p1c = rv
                    # If chosen to discard, these values will not have changed anyway.

                    if oops[0]["Fullscreen"] + g_options["Fullscreen"] == 1 or \
                            oops[0]["Widescreen"] + g_options["Widescreen"] == 1: # I.e. "Fullscreen" or "Widescreen" has changed

                        FULLSCREENBIT = g_options["Fullscreen"]
                        WIDESCREENBIT = g_options["Widescreen"] and FULLSCREENBIT

                        res = [(640, 480), (840, 525)][WIDESCREENBIT]

                        window = pygame.display.set_mode(res, [0, FULLSCREEN][FULLSCREENBIT])
                        pygame.display.set_icon(load_image("icon.png")[0])
                        if not WIDESCREENBIT:
                            screen = pygame.display.get_surface()
                            defineWSscreen(False)

                        if WIDESCREENBIT:
                            wsscreen = pygame.display.get_surface()
                            screen = pygame.Surface((640,480))
                            defineWSscreen(wsscreen)

                        definescreen(screen)

                        # restart display mode to windowed or fullscreen/4:3 or 16:10 depending on new options

                    # Save options to file
                    optionsfile = open(os.path.join(SAVEDIRECTORY, "options.dat"), "w")
                    cPickle.dump(g_options, optionsfile)
                    cPickle.dump(a_options, optionsfile)
                    cPickle.dump(p_options, optionsfile)
                    cPickle.dump(p1c, optionsfile)

                fade_to_black(screen, 5)
                selected = ""
                needfade = True
            elif selected == "Credits":
                fade_to_black(screen)
                crediting = True
                tick = 0
                screen.blit(Data.images["Not_Quite_Black.png"][0], (0,0))
                fade_from_black(screen)
                while crediting:
                    ctime = pygame.time.get_ticks()
                    tick += 1
                    screen.blit(Data.images["Not_Quite_Black.png"][0], (0,0))
                    x = 0
                    for line in CREDITS:
                        if len(line) > 0:
                            linecol = (180,180,180)
                            if line[0] == "#":
                                line = line[1:]
                                linecol = (100,150,255)
                            elif line[0] == "$":
                                line = line[1:]
                                linecol = (100,255,150)
                        thisline = Fonts[8].render(line, 1, linecol)
                        thisrect = thisline.get_rect()
                        screen.blit(thisline, (320-thisrect[2]/2, 480 - tick + x * thisrect[3]))
                        x += 1
                        if x == len(CREDITS) and 480-tick+x*thisrect[3] < 0:
                            crediting = False
                    for ev in ge():
                        if ev.type == KEYDOWN:
                            crediting = False
                    myflip()

                    timedif = pygame.time.get_ticks() - ctime
                    if timedif > 20: timedif = 20
                    time.sleep((20 - timedif)/1000.0)

                IN_LIMBO = False
                needfade = True
                fade_to_black(screen)
                selected = ""
                needfade = True

            elif selected == "What's new?":
                fade_to_black(screen)
                ge()
                InNew = True
                screen.blit(Data.images["whatsnewbg.png"][0], (0,0))
                wnsrc = [x.strip() for x in open("WhatsNew.txt", "r")]
                y = 0
                for line in wnsrc:
                    screen.blit(Fonts[23].render(line, 1, (255,255,255)), (5, 5+y))
                    y += 14
                fade_from_black(screen)
                while InNew:
                    time.sleep(0.01)
                    for e in ge():
                        if e.type == KEYDOWN:
                            InNew = False
                selected = ""
                needfade = True
                    

            elif selected == "About the game":
                fade_to_black(screen)
                Back = False
                ge()
                mx, my = pygame.mouse.get_pos()
                for x in range(4):
                    screen.blit(Data.images["INFO" + str(x+1) + ".png"][0], (0,0))
                    fade_from_black(screen)
                    Waiting = True
                    while Waiting:
                        time.sleep(0.03)
                        screen.blit(Data.images["INFO" + str(x+1) + ".png"][0], (0,0))
                        screen.blit(Data.images["MouseCurs2.png"][0], (mx,my))
                        for e in ge():
                            if e.type == KEYDOWN:
                                Back = True
                                Waiting = False
                            elif e.type == MOUSEBUTTONDOWN:
                                mx, my = pygame.mouse.get_pos()
                                if mx < 90 and my > 440:
                                    Back = True
                                    Waiting = False
                                elif mx > 550 and my > 440 and x < 3:
                                    Waiting = False
                            elif e.type == MOUSEMOTION:
                                mx, my = pygame.mouse.get_pos()
                        myflip()
                    fade_to_black(screen)
                    if Back: break
                selected = ""
                needfade = True

            elif selected == "Online play rules":
                fade_to_black(screen)
                ge()
                InOPR = True
                screen.blit(Data.images["whatsnewbg.png"][0], (0,0))
                oprsrc = [x.strip() for x in open("OPR.txt", "r")]
                y = 0
                for line in oprsrc:
                    screen.blit(Fonts[23].render(line, 1, (255,255,255)), (5, 5+y))
                    y += 14
                fade_from_black(screen)
                while InOPR:
                    time.sleep(0.01)
                    for e in ge():
                        if e.type == KEYDOWN:
                            InOPR = False

                needfade = True
                selected = ""
                activeitem = dict.fromkeys(menu_items, True)
                p_options["MustOP"] = 0
                optionsfile = open(os.path.join(SAVEDIRECTORY, "options.dat"), "w")
                cPickle.dump(g_options, optionsfile)
                cPickle.dump(a_options, optionsfile)
                cPickle.dump(p_options, optionsfile)
                cPickle.dump(p1c, optionsfile)
                
            elif selected == "Code Listing":
                listing = True
                fade_to_black(screen)
                screen.blit(Data.images["Not_Quite_Black.png"][0], (0,0))
                fade_from_black(screen)
                source = open("alldata", "r").readlines()
                scroll = -20
                lines = 0
                inert = 0
                ge()
                while listing:
                    ti= pygame.time.get_ticks()
                    screen.blit(Data.images["Not_Quite_Black.png"][0], (0,0))

                    y = 0
                    for line in source:
                        line = line.rstrip()
                        if scroll+60 > y > scroll:
                            line_s = Fonts[19].render(line, 1, (255,255,255))
                            line_r = line_s.get_rect()
                            line_r.midleft = (5, (y-scroll)*10)

                            screen.blit(line_s, line_r)
                        y += 1

                    screen.fill((0,0,0), Rect(0, 450, 640, 30))

                    lc_s = Fonts[17].render(str(max(0, int(scroll))) + "/" + str(len(source)) + " lines of code", 1, (255,255,255))
                    lc_r = lc_s.get_rect()
                    lc_r.midright = (630, 465)

                    screen.blit(lc_s, lc_r)
                    myflip()
                    wait_tick(ti)

                    for e in ge():
                        if e.type == KEYDOWN:
                            listing = False
                            
                    scroll +=inert
                    inert = min(inert + 0.006, 12)
                    if scroll >= len(source):
                        scroll = len(source)
                        inert = 0
                fade_to_black(screen)
                selected = ""
                needfade = True

            if not ticker%10:
                defmmpic(screen)
            myflip()
            if ontextmov > 0: ontextmov *= 0.8
            if ontextmov < 0.5: ontextmov = 0

def Quit():
    """Shut down the game"""
    pygame.display.quit()
    pygame.mixer.quit()
    sys.exit(0)

class Spark:
    # A spark is a little coloured circle that appears on your wand and fades/blows away.
    def __init__(self, pos, tick):
        tick += random.randint(0,40) # This makes some out of time, as in some are red before they're supposed to be etc
        self.x, self.y = pos
        self.size = random.randint(2,5)
        scale = random.randint(20,100)/100.0

        r = int(100 * (1+math.sin(tick/50.0)))
        g = int(130 * scale)
        b = int((255 * (1-math.sin(tick/50.0)))/2)

        self.inertia = [random.randint(-15,15)/10.0, random.randint(int(-8),10)/10.0]
        spinoff = random.randint(0,100)
        if spinoff == 100:
            self.inertia[0] += random.randint(-30,30)/10.0

        if spinoff >= 95:
            self.inertia[1] += random.randint(-5,15)/10.0

        self.colour = (r, g, b)

        self.removeme = False

        self.img = pygame.Surface((self.size*3,self.size*3))
        self.img.set_colorkey((255,0,255))
        self.img.fill((255,0,255))

        mid = int(round(self.size * 1.5))

        pygame.draw.circle(self.img, self.colour, (mid,mid), self.size, 0)
        self.imrect = self.img.get_rect()

        self.alpha = 120
        
    def blit(self, surf):

        self.img.set_alpha(self.alpha)
        self.imrect.center = (self.x, self.y)
        surf.blit(self.img, self.imrect)

        self.x += self.inertia[0]
        self.y += self.inertia[1]

        self.x -= random.randint(1,10)/10.0*(6-self.size)

        self.inertia[1] += 0.1
        self.alpha -= 3

        if self.alpha == 0:
            self.removeme = True

#DEBUG = True
PROFILING = False
DEBUG = False

logfile("Debugging is " + ["disabled", "enabled"][DEBUG] + ".")

if __name__ == "__main__":
    if DEBUG:
        if PROFILING:
            import profile
            profile.run('main()')
        else:
            main()
        Quit()
    try:
        main()
    except SystemExit:
        pass
    except Exception, e: # This catches errors
        handleException(e)
    pygame.display.quit()
    pygame.mixer.quit()


