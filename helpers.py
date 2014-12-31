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

# It is truly OVER 9000

import pygame, sys, os, time, cPickle
from pygame.locals import *

sd = ""

videoticker = 0
videotake = False
                  # Put on true to record a bunch of tga files (Screenshot directory)
                  # use mencoder to make them a video: (unix command)
                  # mencoder "mf://*.tga" -vf scale=320:240 -mf type=tga:fps=20 -ovc lavc -o output.avi

WIDESCREENBIT = False
WSSURF = None
LOGGING = True
PROFILING = False

ABILITY_DESC = {
    "Attack": "The standard single attack. This is the staple of any fight in Ardentryst. This will usually "\
              "be a swing with a sword, a whack with a staff or a shot from a bow. In some cases, this is "\
              "impossible, for example if you run out of mana to shoot magical arrows.",
    "Lunge": "Pyralis is able to extend his arm whilst lunging forward to create a momentum-based attack. "\
             "This is a great finisher attack as it has slow recharge time but can do a lot of damage if "\
             "you are running fast.",
    "Spin-slash": "A spinning attack, where the attack power of each slash increases with each spin for 3 spins. Best for when there are enemies on both sides of you.",
    "Uppercut": "An uppercut attack. If you can jump, you will jump with the attack. Better for enemies above you.",
    "Focus Magic": "Before any spell can be cast, a magician must focus their mind. Focus Magic does this, "\
                   "and for a short amount of time, spells can be cast. It requires nothing to use, because it "\
                   "does nothing by itself. This move must be followed up by a spell move to create an attack.",
    "Fire": "Releases a wave of fire from your fingertips. This fire is relatively weak, but is great for getting "\
            "rid of pests that cannot be easily reached. Use the up and down keys to sway the flames higher or lower."\
            "Mana cost: 4 MP",
    "Blaze": "A stronger fire spell. Use the up and down keys to sway the flames higher or lower. Mana cost: 12 MP",
    "Burst": "A defensive spell that requires no mana. Burst forces soul energy in all directions, but is strongest "\
             "at the source. Many enemies will be repelled by this.",
    "Ice": "Creates magical vortexes around nearby enemies that attract cold particles. This will hurt enemies by freezing "\
           "them. Mana cost: 4 MP per enemy",
    "Implosion": "Implodes an enemy by forcing magical power into the air around them. Does tremendous damage as they are "\
                 "squashed. Mana cost: 15 MP",
    "Frost": "A stronger ice spell. Mana cost: 8 MP per enemy",
    "Teleport": "Nyx can teleport to the beginning of a level. Mana cost: 10 MP",
    "Quake": "An earthquake which will shake up ground enemies. Mana cost: 10 MP",
    "Focus Summon": "Focuses your thoughts in preparation for summoning.",
    "Summon Maea": "Summons the dragon god Maea. Mana cost: 80 MP",
    }

def set_savedirectory(sd):
    global SAVEDIRECTORY
    SAVEDIRECTORY = sd

def set_profiling():
    global PROFILING
    PROFILING = True

def logsave(SD):
    global sd
    sd = SD

def logfile(text):
    global LOGGING, sd
    if not LOGGING: return
    if type(text) != str:
        try:
            text = str(text)
        except:
            print "Warning, logfile call incorrect:", str(text), "(Got type", str(type(text))
            return
    try:
        src = open(os.path.join(sd, "log.txt"), "r").readlines()
    except:
        open("log.txt", "w")
        src = []
        
    if len(src) and "|" in src[-1]:
        if src[-1][src[-1].index("|")+1:].strip() == text.strip():
            return
    src.append(time.ctime() + "| " + text+"\n")
    fileobj = open(os.path.join(sd, "log.txt"), "w")
    fileobj.writelines(src)

def WS_PIC(pic):
    global WSSURF
    WSSURF = pic

def Quit():
    global PROFILING
    pygame.display.quit()
    pygame.mixer.quit()
    if not PROFILING:
        sys.exit(0)

def myupdate(rects):
    global WIDESCREENBIT, WSSCREEN
    if WIDESCREENBIT:
        sc_copy = SCREEN.convert()
        WSSCREEN.fill((0,0,0))
        WSSCREEN.blit(sc_copy, (100, 22))

        if type(rects) != list:
            rects = [rects]
        for rect in rects:
            rect.move_ip(100, 22)
    pygame.display.update(rects)

def myflip():
    global WIDESCREENBIT, SCREEN, WSSCREEN

    if WIDESCREENBIT:
        sc_copy = SCREEN.convert()
        WSSCREEN.fill((0,0,0))
        WSSCREEN.blit(sc_copy, (100, 22))
        pygame.display.update(Rect(100,22,640,480))
    else:
        pygame.display.flip()

def definescreen(SCR):
    global SCREEN
    SCREEN = SCR

def defineWSscreen(SCR):
    global WIDESCREENBIT, WSSCREEN

    if SCR == False:
        WIDESCREENBIT = False
        return

    WSSCREEN = SCR
    WIDESCREENBIT = True

def ge():
    global screen, SCREEN, videoticker, videotake, WIDESCREENBIT, SAVEDIRECTORY
    try:
        saveimage = screen
    except:
        try:
            saveimage = SCREEN
        except:
            print "Fallback! Not processing GE properly."
            return pygame.event.get()

    if pygame.event.peek(QUIT):
        Quit()
    evlist = pygame.event.get()
    for i in range(len(evlist)):
        event = evlist[i]
        if event.type == KEYDOWN:
            if event.key == K_RETURN and ((pygame.key.get_mods() & KMOD_LALT) or (pygame.key.get_mods() & KMOD_RALT)):
                pygame.display.toggle_fullscreen()
            elif event.key == K_F12:
                if WIDESCREENBIT:
                    sc_copy = saveimage.convert()
                    saveimage.blit(sc_copy, (100, 22))
                    saveimage.blit(WSSURF, (0,0))
                scrshotnum = 0
                for entry in os.listdir(os.path.join(os.getcwd(), "Screenshots")):
                    if entry.startswith("Screenshot") and entry.endswith(".tga"):
                        scrshotnum = int(entry[10:-4]) + 1
                pygame.image.save(saveimage, os.path.join(SAVEDIRECTORY, "Screenshots","Screenshot"+str(scrshotnum).zfill(5)+".tga"))
                evlist[i] = None
                print "\a"

    if videotake:
        scrshotnum = 0
        for entry in os.listdir(os.path.join(os.getcwd(), "Screenshots")):
            if entry.startswith("Screenshot") and entry.endswith(".tga"):
                scrshotnum = int(entry[10:-4]) + 1
        pygame.image.save(pygame.transform.scale(saveimage, (320, 240)), os.path.join("Screenshots","Screenshot"+str(scrshotnum).zfill(5)+".tga"))

    videoticker += 1

    while None in evlist:
        evlist.remove(None)

    return evlist
