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

import pygame, time, sys, random, math, os, cPickle, urllib
import enemyai, tutorial, wordwrap, magic, md5, copy, thread, traceback
import level_script, item as item_module
from pygame.locals import *
from fade import *
from helpers import *
from mapping import bgfortheme, pbgfortheme, pfgfortheme, fallingobjstylefortheme, framesfalling, footstep_types, getalt_fric

# Global values and hard-coded data here
PLAYDEMO = False
eventd = {}
monsterd = {}
playerd = {}

PLAYERFRAMES = {
    "Cast": ["Cast1.png"],
    "Stopped": ["Stopped1.png",
                "Stopped2.png",
                "Stopped3.png",
                "Stopped1.png",
                "Stopped2.png",
                "Stopped3.png",
                "Stopped1.png",
                "Stopped2.png",
                "Stopped3.png",
                "Stopped1.png",
                "Stopped2.png",
                "Stopped3.png",
                "Stopped1.png",
                "Stopped4.png",
                "Stopped3.png"],
    "Walking": ["Walking1.png",
                "Walking2.png",
                "Walking3.png",
                "Walking4.png",
                "Walking5.png",
                "Walking6.png",
                "Walking7.png"],
    "Jumping": ["Walking1.png",
                "Walking2.png",
                "Walking3.png",
                "Walking4.png",
                "Walking5.png",
                "Walking6.png",
                "Walking7.png",
                "Walking8.png"],
    "Attack": ["Attack1.png",
               "Attack2.png",
               "Attack3.png",
               "Attack4.png"],
    }

def check_quest(PLAYER, GAME):
    questnames = {
        "Collector1": "Anneludine shell collector",
        "01*20*Slayer*Nepthene": "Slayer Easy: Nepthene",
        "02*25*Slayer*Forest Arex": "Slayer Easy: Forest Arex",
        "03*40*Slayer*Wasp": "Slayer Easy: Wasp",
        "04*50*Slayer*Anneludine": "Slayer Medium: Anneludine",
        "05*10*Slayer*Snought": "Slayer Medium: Snought",
        "06*30*Slayer*Flust": "Slayer Medium: Flust",
        "07*15*Slayer*Gelatice": "Slayer Pro: Gelatice",
        "08*30*Slayer*Venom Nepthene": "Slayer Pro: Venom Nepthene",
        "09*120*Slayer*Wasp": "Slayer Pro: Wasp Frenzy",
        "10*30*Slayer*Mega Annelud.": "Slayer Xtreme: Mega Anneludine",
        "11*100*Slayer*Nepthene": "Slayer Xtreme: Nepthene Crazy",
        "12|500|Speed": "Speed Demon",
        "13|650|Speed": "Speed Devil",
        "14&20000": "Investor",
        "15&40000": "Pro Investor",
        "16%3%hunt": "Relic Hunter",
        "17%10%collect": "Relic Collector",
        } 
#    questlist = ["Collector1", "1.20.Slayer.Nepthene", "1.50.Slayer.Forest Arex"]
    questlist = questnames.keys()
    questlist.sort()

    questlist = [questlist[-1]] + questlist[:-1]

    for q in questlist:
        if "*" in q:
            t, num, sl, mon = q.split("*")
            num = int(num)

            if q not in PLAYER.quests:
                PLAYER.quests[q] = [False, "For this quest I need to slay " + str(num) + " " + mon + " monsters.", 0]

            if q in PLAYER.quests:
                if mon in PLAYER.slayer:
                    PLAYER.quests[q][2] = PLAYER.slayer[mon]
                    PLAYER.quests[q][1] = "I have slain " + str(min(num,PLAYER.slayer[mon])) + "/" + str(num) + " " + mon + " monsters."

                    if PLAYER.slayer[mon] >= num:
                        PLAYER.quests[q][0] = True

        if "|" in q:
            # is a speed quest
            u, speed, SP = q.split("|")
            speed = int(speed)
            if q not in PLAYER.quests:
                PLAYER.quests[q] = [False, "For this quest I need to break a horizontal speed record of " + str(speed), 0]

            if q in PLAYER.quests:
                PLAYER.quests[q][2] = max(PLAYER.quests[q][2], PLAYER.speedrecord)
                PLAYER.quests[q][1] = "I have attained a horizontal speed of " + str(PLAYER.quests[q][2]) + "/" + str(speed)
                if PLAYER.quests[q][2] >= speed:
                    PLAYER.quests[q][0] = True
                
        if "&" in q:
            # is a money quest
            u, cash = q.split("&")
            cash = int(cash)
            if q not in PLAYER.quests:
                PLAYER.quests[q] = [False, "For this quest I need to accumulate " + str(cash) + " silver pieces.", 0]

            if q in PLAYER.quests:
                PLAYER.quests[q][2] = max(PLAYER.quests[q][2], GAME.silver)
                PLAYER.quests[q][1] = "I have saved up " + str(PLAYER.quests[q][2]) + "/" + str(cash) + " silver pieces."
                if PLAYER.quests[q][2] >= cash:
                    PLAYER.quests[q][0] = True
                if PLAYER.quests[q][0] == True:
                    PLAYER.quests[q][1] = "I have proved my money saving skills."
                
        if "%" in q:
            # is a money quest
            u, relics, l = q.split("%")
            relics = int(relics)
            if q not in PLAYER.quests:
                PLAYER.quests[q] = [False, "For this quest I need to find " + str(relics) + " relics.", 0]

            if q in PLAYER.quests:
                PLAYER.quests[q][2] = max(PLAYER.quests[q][2], PLAYER.relics)
                PLAYER.quests[q][1] = "I have found " + str(PLAYER.quests[q][2]) + "/" + str(relics) + " relics."
                if PLAYER.quests[q][2] >= relics:
                    PLAYER.quests[q][0] = True
                if PLAYER.quests[q][0] == True:
                    PLAYER.quests[q][1] = "I have found the required amount of relics."
                
                

    return [[questnames[qn], qn] for qn in questlist]
    

def quest_npc(qname):
    global PLAYER, DATA
    if PLAYER.quests.has_key(qname):
        # Quest has been started (could be finished.)
        if qname == "Collector1":
            # Anneludine Shell Collector

            happy = ""

            while "Anneludine shell" in PLAYER.inventory and PLAYER.quests["Collector1"][2] < 10:
                PLAYER.inventory.remove("Anneludine shell")
                PLAYER.quests["Collector1"][2] += 1
                happy = "That's great! You've given me " + str(PLAYER.quests["Collector1"][2]) + " so far. "
                PLAYER.quests["Collector1"][1] = "I've given the stranger " + str(PLAYER.quests["Collector1"][2]) + "/10 Anneludine shells."
            
            if PLAYER.quests["Collector1"][2] < 10:
                if PLAYER.quests["Collector1"][2] == 9: p = ""
                else: p = "s"
                message_box(happy + "Find me " + str(10 - PLAYER.quests["Collector1"][2]) + " more Anneludine Shell" + p + ".", ["Stranger.png"])
            elif PLAYER.quests["Collector1"][2] == 10:
                if PLAYER.classtype:
                    PLAYER.inventory.append("Green hood")
                else:
                    PLAYER.inventory.append("Steel round helm")
                NOTICE_VIEW.add("Acquired " + DATA.Itembox.GetItem(PLAYER.inventory[-1]).display + "!")
                PIC_VIEW.pics.append([DATA.Itembox.GetItem(PLAYER.inventory[-1]).inv_image, 400])
                message_box("Thank you so much, adventurer.", ["Stranger.png"])
                if PLAYER.classtype:
                    message_box("Rewards: Green hood, 150 silver pieces, 200 experience points")
                else:
                    message_box("Rewards: Steel round helmet, 150 silver pieces, 200 experience points")
                NOTICE_VIEW.add("Awarded 150 silver pieces!")
                GAME.silver += 150
                PIC_VIEW.pics.append(["silverpouch.png", 400])
                PLAYER.exp += 200
                PLAYER.quests["Collector1"][2] = 11
                PLAYER.quests["Collector1"][0] = True
                PLAYER.quests["Collector1"][1] = "I gave the last shell to the stranger and he rewarded me for my kindness."
            elif PLAYER.quests["Collector1"][2] == 11:
                message_box("I think I will just rest here for a while and catch my breath.", ["Stranger.png"])
                
    else:
        # Begin quest?
        if qname == "Collector1":
            # Anneludine Shell Collector
            if PLAYER.level < 4:
                message_box("Come and see me when you're a bit stronger.", ["Stranger.png"])
            else:
                message_box("I have been sent here to gather 20 Anneludine Shells. I have been running around to and fro, and I am tired already with only 10! If you can gather the other 10, and give them to me, I'll gladly reward you for your assistance.", ["Stranger.png"])
                PLAYER.quests["Collector1"] = [False, "I talked to a stranger in the woods who looked surprisingly like a ninja... He asked me to gather up Anneludine shells-- those worm snake turtle monsters have them on their backs. I need to give him 10.", 0]

def action(object_type, ID, attr, val):
    global Objects
    c = 0
    for o in Objects:
        if o.id == object_type:
            c += 1
            if c == ID:
                setattr(o, attr, val)

def uploadscore(game):
    # If you cheat, you cannot get a ranking on the Public Scoreboard

    wearing = []
    for area in ["Head", "Torso", "Legs", "Boots", "Weapon"]:
        wearing.append(game.playerobject.wearing[area][0])

    data = [game.savefilename[:-4],
            str(game.playerobject.classtype),
            cPickle.dumps(game.scores).replace("\n","\\"),
            str(game.playerobject.exp),
            str(game.playerobject.level),
            str(game.playerobject.questsdone()),
            cPickle.dumps(game.timegems).replace("\n","\\"),
            cPickle.dumps(wearing).replace("\n","\\"),
            game.shc,
            game.ac_code,
            game.GID
            ]

    import sha
    sd = [data, sha.new(cPickle.dumps(data)).hexdigest()]

    senddata = cPickle.dumps(sd).replace("\n","/").replace(" ", "%20")

    msg = urllib.urlopen("http://jordan.trudgett.com/cgi-bin/submit.py?code="+senddata).read().strip()
    return msg.split("\n")
    

def strbon(num):
    """Takes a number, x, and turns it into a "+x", "-x", or "+0"."""
    # Why is this the only function with a docstring? :|
    if num > 0:
        return "+" + str(num)
    elif num == 0:
        return "+0"
    else:
        return str(num)
    

def namekey(keyname, c=None):
    global CONTROLS
    if c:
        return pygame.key.name(c[keyname][0]).upper()
    else:
        return pygame.key.name(CONTROLS[keyname][0]).upper()


def Level_Up_Screen():
    global finalscreen, CONTROLS, Start_Level_Time, DATA, PLAYER, FONTS, NOTICE_VIEW
    countdown = Hourglass(5)
    starttick = pygame.time.get_ticks()
    oldscreen = finalscreen.convert()
    darksurf = pygame.Surface((640, 480))
    scr_active = True
    tick = 0

    lusurf, lurect = DATA.images["levelup.png"]
    lurect.midtop = (320, 15)

    new = PLAYER.statsfor(PLAYER.level)
    bt = "   ...   was " # beginning text
    mt = ", is now " # middle text

    lastnote = ""
    lastnote2 = ""
    learnt = []
    for move in PLAYER.combo_list:
        if move[2] == PLAYER.level:
            learnt.append(PLAYER.movelist[move[1]])
    if learnt:
        lastnote = "Learnt " + ", ".join(learnt) + "!"
        lastnote2 = "Look under Ability in your status menu!"
        NOTICE_VIEW.add("Learnt " + ", ".join(learnt) + "!")

    information = [
        "You are now Level " + str(PLAYER.level) + "!",
        "",
        "Strength: " + bt + str(PLAYER.strength[1]) + mt + str(new[0]) + "    (" + strbon(new[0]-PLAYER.strength[1]) + ")",
        "Endurance: " + bt + str(PLAYER.endurance[1]) + mt + str(new[1]) + "    (" + strbon(new[1]-PLAYER.endurance[1]) + ")",
        "Magic: " + bt + str(PLAYER.magic[1]) + mt + str(new[2]) + "    (" + strbon(new[2]-PLAYER.magic[1]) + ")",
        "Luck: " + bt + str(PLAYER.luck[1]) + mt + str(new[3]) + "    (" + strbon(new[3]-PLAYER.luck[1]) + ")",
        "",
        lastnote,
        lastnote2
        ]

    for i in range(len(information)):
        c = (255, 255, 255)
        if i >= len(information) - 2:
            c = (255, 0, 255)
            information[i] = FONTS[22].render(information[i], 1, c)
        else:
            information[i] = FONTS[17].render(information[i], 1, c)

    while scr_active:
        lt = pygame.time.get_ticks()
        finalscreen.blit(oldscreen, (0, 0))
        darksurf.set_alpha(min(15 * tick, 210))
        finalscreen.blit(darksurf, (0, 0))

        tscreen = finalscreen.convert()
        finalscreen.blit(lusurf, lurect)
        tscreen.set_alpha(max(200 - tick*15, 0))
        finalscreen.blit(tscreen, (0,0))

        y = 0
        for line in information:
            lrect = line.get_rect()
            lrect.midleft = (40, 160 + y * 30)
            finalscreen.blit(line, lrect)
            y += 1

        countdown.update((300 - min(tick, 300))/3.0)
        countdown.tick()
        countdown.rect.center = (620, 460)
        finalscreen.blit(countdown.image, countdown.rect)

        for ev in ge():
            if ev.type == KEYDOWN:
                k = ev.key
                if k in CONTROLS["B-1"]:
                    if tick > 300:
                        scr_active = False
                    else:
                        tick += 75

        lt = mywait(lt)

        myflip()

        tick += 1
    Start_Level_Time += pygame.time.get_ticks() - starttick

def interface_sound(sound, sb = None):
    global SOUNDBOX
    if sb:
        mysb = sb
    else:
        mysb = SOUNDBOX

    code = {"error": "fail.ogg",
            "equip": "equip.ogg",
            "menu-item": "menu-item.ogg",
            "menu-select": "menu-select.ogg",
            "menu-back": "menu-back.ogg",
            "menu-small-select": "menu-small-select.ogg",
            "message": "Msg.ogg"}
    
    mysb.PlaySound(code[sound.lower()])

def message_box(message, face = None, csounds = None):
    global lasttick, SOUNDBOX, finalscreen, FONTS, DATA, PLAYER, MESSAGE_JUST_DONE, CONTROLS
    global Start_Level_Time, PLAYDEMO
    if PLAYDEMO: return

    countdown = Hourglass(1)
    
    ntick = pygame.time.get_ticks()
    tick = 0

    handpos = None

    sc_copy = finalscreen.convert()
    if type(message) == list:
        for m in message:
            finalscreen.blit(sc_copy, (0,0))
            message_box(m, face, csounds)
        return

    handdir = 0

    if message[0] == "#": message = message[1:]; face = None; csounds = None
    if message.startswith("**"): message = message[2:]; PLAYER.ignore_move = False
    if "$" in message:
        handpos = tuple([int(x) for x in message.split("$")[1].split(",")])
        message = "".join(message.split("$")[::2])
    if "&" in message:
        handdir = 1
        message = message.replace("&", "")
    if "*" in message:
        if face:
            face = face[int(message[message.index("*")+1])]
            message = message[:message.index("*")]+message[message.index("*")+2:]
    elif type(face) == list:
        face = face[0]

    if MESSAGE_JUST_DONE > 5:
        if not csounds:
            interface_sound("message")
        else:
            if type(csounds) == str:
                SOUNDBOX.PlaySound(csounds)
            elif type(csounds) == list:
                SOUNDBOX.PlaySound(csounds[random.randint(0,len(csounds)-1)])
        MESSAGE_JUST_DONE = 0

    DARKSURF = pygame.Surface((640,480))
    DARKSURF.set_alpha(150)
    finalscreen.blit(DARKSURF, (0,0))

    FACESURF = None

    if face:
        FACESURF, FACERECT = DATA.images[face]

    MBSURF = pygame.Surface((460,110))
    MBSURF.fill((255,255,255))

    MBSURF.fill((255,0,255), pygame.Rect(5,5,450,100))

    MBSURF.set_colorkey((255,0,255))
    MBRECT = MBSURF.get_rect()
    MBRECT.midtop = [(320 + [55,0][face is None], 260),(320 + [55,0][face is None], 40)][PLAYER.y > 320]
    # The monster of a line above chooses whether the box goes near the top or near the bottom
    # and automatically centres if there is or is not a portrait that goes with it (dialogue)
    finalscreen.blit(MBSURF, MBRECT)

    for x in range(1,21):
        c = (21-x, 50-2*x,250-10*x)
        if PLAYER.classtype == 0:
            c = (250-10*x, 50-2*x, 21-x)
        MBSURF.fill(c, pygame.Rect(5,5*x,450,105-5*x))

    DARKSURF.set_alpha(200)
    MBSURF.blit(DARKSURF, (0,0))
    DARKSURF.set_alpha(150)

#    MBSURF.set_alpha(60)
    finalscreen.blit(MBSURF, MBRECT)

    tsurfs = wordwrap.string_to_paragraph(message, FONTS[13], True, (255,255,255), 440)

    y = 0
    for surf in tsurfs:
        mbx = MBRECT.left
        mby = MBRECT.top
        finalscreen.blit(surf, (mbx+10, mby+10+y*16))
        y += 1

    if FACESURF:
        FACERECT.midright = MBRECT.midleft
        FACERECT.move_ip(-5, 0)
        finalscreen.fill((15,15,15), FACERECT.inflate(10,10))
        finalscreen.blit(FACESURF, FACERECT)

    myflip()

    box = True
    while box:
        finalscreen.blit(sc_copy, (0,0))
        finalscreen.blit(DARKSURF, (0,0))

        if handpos:
            if (tick/6)%2 and tick > 10:
                if not handdir:
                    finalscreen.blit(DATA.images["hand.png"][0], handpos)
                else:
                    finalscreen.blit(pygame.transform.flip(DATA.images["hand.png"][0], True, False), handpos)
            elif tick > 10:
                finalscreen.blit(sc_copy, (0,0))
                finalscreen.blit(DARKSURF, (0,0))

            DATA.images["hand.png"][1].topleft = (0,0)

        finalscreen.blit(MBSURF, MBRECT)
        y = 0
        for surf in tsurfs:
            mbx = MBRECT.left
            mby = MBRECT.top
            finalscreen.blit(surf, (mbx+10, mby+10+y*16))
            y += 1

        if FACESURF:
            FACERECT.midright = MBRECT.midleft
            FACERECT.move_ip(-5, 0)
            finalscreen.fill((105,105,105), FACERECT.inflate(10,10))
            finalscreen.blit(FACESURF, FACERECT)


        countdown.update((10-min(tick, 10)) * 10)
        countdown.tick()
        countdown.rect.center = MBRECT.bottomright
        countdown.rect.move_ip(25,0)
        finalscreen.blit(countdown.image, countdown.rect)

        if tick >= 10:
            ssurf = FONTS[9].render("Press " + namekey("B-1") + " to continue", 1, (255,255,255))
            srect = ssurf.get_rect()
            srect.bottomright = MBRECT.bottomright
            srect.move_ip(-5,-4)
            finalscreen.blit(ssurf, srect)

           
        myflip()

        el = ge()
        for e in el:
            if e.type == KEYDOWN:
                if e.key in CONTROLS["B-1"] and tick >= 10:
                    box = False
        time.sleep(0.05)
        tick += 1
    lasttick = pygame.time.get_ticks()
    Start_Level_Time += pygame.time.get_ticks()-ntick

def finalise_screen():
    global SCREEN, finalscreen
    finalscreen.blit(SCREEN, (0,0))

def mswait(t, ms):
    ct = pygame.time.get_ticks()
    d = ct - t
    if d > ms: tw = 0
    else: tw = ms-d
    time.sleep(tw/1000.0)
    return pygame.time.get_ticks()

def mywait(lasttick, fps = 40):
    global SKIPNEXT, DELAY, fsol, CONSOLE_ACTIVE, DEBUG, CSPEEDARRAY

    if fsol or CONSOLE_ACTIVE: return pygame.time.get_ticks()
    FPS = fps
    # 1000 ms in a second. FPS frames per second means
    msdelay = int(1000.0/FPS)
    if lasttick == 0: return pygame.time.get_ticks()
    ctick = pygame.time.get_ticks()
    
    CSPEEDARRAY.append(100+int(100 * (lasttick + msdelay - ctick)/float(msdelay)))
    CSPEEDARRAY = CSPEEDARRAY[-10:]

    if ctick < lasttick + msdelay:
        pygame.time.wait(lasttick + msdelay - ctick)
        DELAY = lasttick + msdelay - ctick
        ctick = pygame.time.get_ticks()
    else:
        SKIPNEXT += ((ctick - (lasttick+msdelay))/float(msdelay))
        DELAY = ctick - (lasttick+msdelay)
    return ctick

def my_raw_wait(lasttick, fps = 40):

    FPS = fps
    # 1000 ms in a second. FPS frames per second means
    msdelay = int(1000.0/FPS)
    if lasttick == 0: return pygame.time.get_ticks()
    ctick = pygame.time.get_ticks()
    
    if ctick < lasttick + msdelay:
        pygame.time.wait(lasttick + msdelay - ctick)
        ctick = pygame.time.get_ticks()
    return ctick


def Get_Objects(LEVEL):
    global PLAYER, TreasureCount
    objlist = []
    x = 0
    for col in LEVEL.obj:
        y = 0
        for unit in col:
            if unit:
                o = unit
                if o == "Butterfly":
                    objlist.append(Butterfly(x,y))
                elif o == "ButterflyB":
                    objlist.append(ButterflyB(x,y))
                elif o == "ButterflyC":
                    objlist.append(ButterflyC(x,y))
                elif o == "FallingRock":
                    objlist.append(FallingRock(x,y))
                elif o == "Walltorch":
                    objlist.append(Walltorch(x,y))
                elif o == "Torchref":
                    objlist.append(Torchref(x,y))
                elif o == "Shield":
                    objlist.append(StaticObj("Shield", "Shield.png", x,y))
                elif o == "Sword":
                    objlist.append(StaticObj("Sword", "Sword.png", x,y))
                elif o == "TreasureBox":
                    objlist.append(TreasureBox(x,y))
                    TreasureCount += 1
                elif o == "TreasureBoxB":
                    objlist.append(TreasureBoxB(x,y))
                    TreasureCount += 1
                elif o == "TreasureBoxC":
                    objlist.append(TreasureBoxC(x,y))
                    TreasureCount += 1
                elif o == "Obelisk_Snow":
                    objlist.append(Obelisk(x, y, 'Snow'))
                elif o == "Lever_Snow":
                    objlist.append(Lever(x, y))
                elif o == "Firepit":
                    objlist.append(Firepit(x, y))
                elif o == "Player_Start":
                    PLAYER.x, PLAYER.y = x * 40 + 20, (y+1)*40
                    PLAYER.start = x * 40 + 20, (y+1)*40
                    LEVEL.STARTSET = True
                elif o == "Level_End":
                    LEVEL.endpoint = x*40
                elif o == "Sign":
                    objlist.append(Sign(x,y))
            y += 1
        x += 1
    return objlist

def Init_Monsters(LEVEL):
    global PLAYDEMO
    enemylist = []
    x = 0
    for col in LEVEL.enemy:
        y = 0
        for unit in col:
            if unit:
                e = unit
                enemyobj = eval("enemyai."+unit.lower()+"()")
                enemyobj.PLAYDEMO = PLAYDEMO
                enemyobj.update(x*40+20,(y+1)*40)
                enemyobj.m_init()
                enemylist.append(enemyobj)
            y += 1
        x += 1
    LEVEL.Monster_Objs = enemylist
    return enemylist

def Object_Tick(Objects, In_Front):
    global CAMERA_X, SCREEN, DATA, PLAYER
    for Object in Objects:
        if Object._needinfo:
            Object._giveinfo(PLAYER)
        opoll = None
        if Object._inscreen(CAMERA_X):
            if not In_Front:
                Object._tick()
            opoll = Object._poll()
        elif Object._runtime == "All":
            if not In_Front:
                Object._tick()
        if opoll:
            if In_Front and Object._infront or not In_Front and not Object._infront:
                if hasattr(Object, "_alpha"):
                    OLDSCREEN = SCREEN.convert()
                    OLDSCREEN.set_alpha(255 - Object._alpha)
                if len(opoll) == 4:
                    SCREEN.blit(opoll[0], opoll[3].move(-CAMERA_X, 0))
                else:
                    SCREEN.blit(DATA.images[opoll[0]][0], (opoll[1]-CAMERA_X, opoll[2]))
                if hasattr(Object, "_alpha"):
                    SCREEN.blit(OLDSCREEN, (0,0))


def Monster_Tick(Monsters):
    global CAMERA_X, SCREEN, DATA, SOUNDBOX, PLAYER, LEVEL
    global ORBS, NOTICE_VIEW, PIC_VIEW, Objects
    for Monster in Monsters:

        Monster.info(PLAYER, LEVEL)

        if hasattr(Monster, "imgheight"):
            if abs(Monster.x - PLAYER.x) < Monster.collision_dist and abs((Monster.y-Monster.imgheight/2)-(PLAYER.y-40)) < Monster.collision_hdist/2 + 32:
                if not Monster.isdead:
                    Monster.collision(PLAYER)

                    if Monster.name == "pod":
                        TUTBOX.playeraction("pod_collide")
                    elif Monster.name == "cspider":
                        TUTBOX.playeraction("cspider_collide")
        if Monster.useprojectilecollision:
            for projectile in Monster.projectiles:
                if abs(projectile[1] - PLAYER.x) < 12 and abs(projectile[2] - (PLAYER.y-40)) < 25:
                    Monster.projectiles[Monster.projectiles.index(projectile)] = None
                    PLAYER.raw_hit(Monster.projectile_damage)

        if Monster.EXECUTE:
            cmd = Monster.EXECUTE
            Monster.EXECUTE = ""
            exec(cmd) in globals()

        while None in Monster.projectiles:
            Monster.projectiles.remove(None)

        if Monster.SPAWN_GOODIES:
            # Okay, it's dead, or at least it wants to spawn goodies...
            Monster.SPAWN_GOODIES = False
            PLAYER.exp += Monster.reward_exp
            PLAYER.possible_level_up()
            rcmrh = random.choice(Monster.reward_hp)
            rcmrm = random.choice(Monster.reward_mp)
            if type(rcmrh) != type([]):
                rcmrh = [rcmrh]
            if type(rcmrm) != type([]):
                rcmrm = [rcmrm]
            if rcmrh != [0]:
                for val in rcmrh:
                    ORBS.append(Orb("Health", Monster.x, Monster.y - 30, val))
            if rcmrm != [0]:
                for val in rcmrm:
                    ORBS.append(Orb("Mana", Monster.x, Monster.y - 30, val))

            if Monster.reward_items:
                spawnitem = None
                chv = random.randint(0,10000)/100.0 #Chance Value
                if random.randint(0, 1):
                    chv -= PLAYER.luck[0] / 2.0

                if chv <= 0: chv = 0.01

                Monster.reward_items.sort()
                for i in Monster.reward_items:
                    if chv < i[0]:
                        spawnitem = i
                        spawnitemobj = DATA.Itembox.GetItem(spawnitem[1])
                        if spawnitemobj.Warrior_Frames and not spawnitemobj.Mage_Frames and PLAYER.classtype:
                            continue
                        if spawnitemobj.Mage_Frames and not spawnitemobj.Warrior_Frames and not PLAYER.classtype:
                            continue
                        break
                if spawnitem:
                    try:
                        PLAYER.inventory.append(spawnitem[1])
                        NOTICE_VIEW.add("Acquired " + DATA.Itembox.GetItem(PLAYER.inventory[-1]).display + "!")
                        PIC_VIEW.pics.append([DATA.Itembox.GetItem(PLAYER.inventory[-1]).inv_image, 400])
                    except:
                        pass
        
        if Monster.SOUND:
            if Monster.SOUNDTIME == 0:
                pos_sounds = DATA.Monster_Data[Monster.name]["sounds"][Monster.SOUND]
                SOUNDBOX.PlaySound(Monster.name + "_" + pos_sounds[random.randint(0, len(pos_sounds)-1)])
                Monster.SOUNDTIME = Monster.AFTERSOUND
            Monster.SOUND = ""
        if Monster.inscreen(CAMERA_X) or Monster.active:
            Monster.active = True
            Monster.tick()

            if Monster.diedyet and not Monster.slayercount:
                if Monster.presentable_name not in PLAYER.slayer:
                    PLAYER.slayer[Monster.presentable_name] = 1
                else:
                    PLAYER.slayer[Monster.presentable_name] += 1

                Monster.slayercount = True

        if Monster.inscreen(CAMERA_X):
            try:
                monimg, monrect = DATA.mimages[Monster.name][Monster.a_prefix+str(int(Monster.a_frame))+".png"]
                Monster.imgheight = monrect.height
            except:
                raise Exception("Invalid frame ("+str(Monster.a_frame)+") for animation "+Monster.a_prefix+ " on monster " + Monster.name)
                
            monrect.midbottom = (Monster.x-CAMERA_X, Monster.y)
            if Monster.ALPHA < 255:
                mbuffer_surf = pygame.Surface((200,200))
                mbuffer_surf.set_colorkey((255,0,255))

                mbuffer_surf.fill((255,0,255))
                mbuffer_surf.blit(monimg, (0,0))
                mbuffer_surf.set_alpha(Monster.ALPHA)
                SCREEN.blit(mbuffer_surf, monrect)
            else:
                if Monster.FLIPME:
                    monimg = pygame.transform.flip(monimg, True, False)
                SCREEN.blit(monimg, monrect)
                for p in Monster.projectiles:
                    p_s, p_r = DATA.images[p[0]]
                    p_r.center = (p[1], p[2])
                    SCREEN.blit(p_s, p_r.move(-CAMERA_X, 0))
            

            if len(Monster.numbers) > 0:
                tempDIGSURF = pygame.Surface((320,100))
                tempDIGSURF.set_colorkey((255,0,255))

                for number in Monster.numbers: #Iterates over the numbers
                    curative = number[0]
                    digits = number[1:]
                    if sum([int(x[0]) for x in digits]) == 0: continue
                    cd = 1
                    tempDIGSURF.fill((255,0,255))
                    for digit in digits:
                        digpair = DATA.images[digit[0]+".png"]
                        dr = digpair[1]
                        rs = 18*len(digits)
                        bx = 100 -(rs-40)/2 + int((float(rs)/(len(digits)+1)) * cd) - dr[2]/2
                        bounce = 500.0/(digit[1]+5)
                        if digit[1] > 32: bounce = 0
                        by = 60 - abs(int((math.sin(digit[1]/5.0)*bounce)))
                        tempDIGSURF.blit(digpair[0], (bx, by))
                        cd += 1
                    dsa = 340-digit[1]*4
                    if dsa > 255: dsa = 255
                    tempDIGSURF.set_alpha(dsa)

                    SCREEN.blit(tempDIGSURF, (monrect[0]+monrect[2]/2-120,monrect[1]-65))

            Monster.Advance_Numbers()
    return [x for x in Monsters if not x.REMOVEME]

def Tutorial_Tick(THISFLIP):
    global PLAYER, TUTBOX, TUT_ACTIVE, RAIN_HEAVINESS
    TUTBOX.tick()
    TUTBOX.playerat(PLAYER.x)
    
    TutMsg, CPT, TutFace = TUTBOX.poll()

    if TutMsg and THISFLIP:
        message_box(TutMsg, TutFace)

    if TUTBOX.RAIN is not None:
        RAIN_HEAVINESS = TUTBOX.RAIN

def Orb_Tick(orbs):
    global SCREEN, CAMERA_X, PLAYER
    for orb in orbs:
        orb.blit(SCREEN, -CAMERA_X)
        orb.tick(PLAYER)

    for i in range(len(orbs)):
        if orbs[i].removeme is True:
            orbs[i] = None

    while None in orbs:
        orbs.remove(None)

def Particle_Tick(particles):
    global CAMERA_X, SCREEN
    # Blits/ticks the particles.
    for particle in particles:
        particle.blit(SCREEN, -CAMERA_X)
        particle.tick()

    for i in range(len(particles)):
        if particles[i].removeme is True:
            particles[i] = None

    while None in particles:
        particles.remove(None)

def Poison_Tick():
    global DSCREEN, SCREEN, POISONFACTOR, PLAYER
    pfactor = 4
    pm = POISONFACTOR % 20

    if pm == 19:
        PLAYER.Take_Damage(PLAYER.hp[1]/24, False, "c")
        PLAYER.painsound(PLAYER.hp[1]/24)

    greensurf = pygame.Surface((640,480))
    greensurf.fill((100, 180, 0))
    greensurf.set_alpha(60 + math.sin(POISONFACTOR/10) * 25)

    SCREEN.blit(greensurf, (0,0))
    
    POISONFACTOR += 0.5

    if POISONFACTOR >= 700:
        POISONFACTOR = 0
        PLAYER.bits["poisoned"] = False

def controldown(control):
    global CONTROLS, PLAYDEMO, simpressed
    if PLAYDEMO:
        for x in CONTROLS[control]:
            if simpressed[x]: return True
        return False

    pygame.event.pump()
    pkgp = pygame.key.get_pressed()
    for c in CONTROLS[control]:
        if pkgp[c]:
            return True
    return False

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

def defmmpic(pic):
    global mmpic
    mmpic = pygame.transform.scale(pic, (320, 240))

def Ingame_Menu(data):
    # Menu in the game. Accessible from ardentryst.py as well

    screen, DATA, FONTS, CONTROLS, SOUNDBOX, lasttick, game, player, abortable = data
    uploadresult = ""

    global mmpic, ovscreen
    
    inmenu = True
    playscreen = pygame.Surface((640,480))
    playscreen.blit(screen, (0,0))
    splayscreen = pygame.transform.scale(playscreen, (320,240))
    darksurf = pygame.Surface((640,480))
    darksurf.fill((0,0,0))
    dsa = 0
    menusurf = DATA.images[["IGM-red.png", "IGM-blue.png"][player.classtype]][0]
    hand = DATA.images["hand.png"][0]

    handcol = 0
    handpos = 0
    vhandabsy = 130
    oldhandpos = 0
    invhandpos = 0

    mmconfirm = False

    rv = 0

    menuitems = [
        "Status",
        "Inventory",
        "Equipped",
        "Abilities",
        "Quest Log",
        "",
        "Return",
        "Upload Score",
        "Main Menu",
        "",
        "Help",
        ]

    if abortable:
        menuitems[-2] = "Abort level"
    if not game.ACC or game.hc:
        menuitems[-4] = "-----"

    descs = {
        "Status": "Information about your character",
        "Inventory": "What you are carrying",
        "Equipped": "What you are wearing or using",
        "Abilities": "What your character can do",
        "Return": "Back to the level or overview map",
        "Upload Score": "Put your score on the Ardentryst Online Scoreboard",
        "Help": "Help! Enter help by pressing " + namekey("B-1", CONTROLS),
        "Main Menu": "Exit this game and return to the Main Menu.",
        "Abort level": "Return to Overview Map.",
        "Quest Log": "View quests.",
        "-----": "Cannot upload score. Gamefile not legitimate."
        }

    pygame.key.set_repeat(400,50)

    statusbar = ""

    SOUNDBOX.MusicVol(0.3)
    tick = 0

    sel_obj = None
    tab = "Status"
    pic = ""

    inv_items = []
    invlist = []
    invscroll = 0
    eqdirection = 1
    renaming = False
    renameto = ""

    MITEMHEIGHT = 26

    while inmenu:
        ti = pygame.time.get_ticks()

        player.var_tick(1)

        # Blitting
        
        darksurf.set_alpha(min(255, max(0, dsa+math.sin(tick/10.0)*7)))
        menusurf.set_alpha(dsa)
        screen.blit(playscreen, (0,0))
        screen.blit(darksurf, (0,0))
        screen.blit(menusurf, (0,0))

        hps = FONTS[17].render("HP: " + str(player.hp[0]) + "/" + str(player.hp[1]), 1, (255,255,255))
        hpr = hps.get_rect()
        mps = FONTS[17].render("MP: " + str(player.mp[0]) + "/" + str(player.mp[1]), 1, (255,255,255))
        mpr = mps.get_rect()

        hpr.midleft = (10, 460)
        mpr.midright = (630, 460)

        screen.blit(hps, hpr)
        screen.blit(mps, mpr)

        # Text

        for x in range(len(menuitems)):
            if x == oldhandpos and handcol > 0 or handcol == 0 and x == handpos:
                c = (255, 255, 50)
            elif menuitems[x] == "Main Menu":
                c = (255, 55, 50)
            else:
                c = (255, 255, 255)
            cmis = FONTS[17].render(menuitems[x], 1, c)
            cmisb = FONTS[17].render(menuitems[x], 1, (0,0,0))
            # cmis is CurrentMenuItemSurface! >:3
            cmir = cmis.get_rect()
            cmir.center = (146, 150 + MITEMHEIGHT*x)
            screen.blit(cmisb, cmir.move(1,1))
            screen.blit(cmis, cmir)

        if handcol == 0:
            statusbar = descs[menuitems[handpos]]
            if tab == "Inventory":
                ministatus = " (Press " + namekey("Right", CONTROLS) + " or " + namekey("B-1", CONTROLS) + " to move cursor to Inventory)"
            elif tab == "Equipped":
                ministatus = " (Press " + namekey("Right", CONTROLS) + " or " + namekey("B-1", CONTROLS) + " to move cursor to Equipment)"
            elif tab == "Abilities":
                ministatus = " (Press " + namekey("Right", CONTROLS) + " or " + namekey("B-1", CONTROLS) + " to move cursor to Abilites)"
            elif tab == "Help":
                ministatus = " (Press " + namekey("B-1", CONTROLS) + " to enter Help)"
            elif tab == "Upload Score":
                ministatus = " (Press " + namekey("B-1", CONTROLS) + " to submit your score)"
            else:
                ministatus = ""
        else:
            statusbar = ""

        sb = FONTS[13].render(statusbar, 1, (255,255,255))
        sbb = FONTS[13].render(statusbar, 1, (0,0,0))

        sbr = sb.get_rect()
        sbr.center = (320, 440)
        
        screen.blit(sbb, sbr.move(1,1))
        screen.blit(sb, sbr)

        if (tick/9)%4:
            mini_s = FONTS[13].render(ministatus, 1, (255,255,255))
            mini_r = mini_s.get_rect()
            mini_r.center = (420, 80)
            screen.blit(mini_s, mini_r)

        # Cursor

        handabsx = [210, -100, -100][handcol]
        if handcol == 0:
            handabsy = 130 + MITEMHEIGHT * handpos
        else:
            # cursor not on menu
            if tab == "Inventory": handabsy = -50; vhandabsy = -50

        if vhandabsy < 0:
            vhandabsy = handabsy
        else:
            vhandabsy = (vhandabsy * 2 + handabsy)/3.0

        screen.blit(hand, (handabsx+abs(math.sin(tick/10.0)*10), vhandabsy))

        # Tab title

        ti_s = FONTS[14].render(tab, 1, (255,255,255))
        ti_r = ti_s.get_rect()

        ti_r.center = (420, 50)

        screen.blit(ti_s, ti_r)

        # TAB INFORMATION

        if tab == "Status":
            information = [
                "Player: " + [game.savefilename[:-4], renameto][renaming] + [" --- Press R to rename.", " --- Type name, hit return"][renaming],
                "Activation Code: " + game.ac_code,
                "",
                game.character + ", level " + str(player.level),
                "",
                "Health Points: " + str(player.hp[0]) + "/" + str(player.hp[1]),
                "Mana Points: " + str(player.mp[0]) + "/" + str(player.mp[1]),
                "Experience: " + str(player.exp) + "    (Next level at " + str(player.expfor(player.level+1)) + " exp.)",
                "Strength: " + str(player.strength[0]) + "  (" + strbon(player.bonuses["strength"]) + ")",
                "Endurance: " + str(player.endurance[0]) + "  (" + strbon(player.bonuses["endurance"]) + ")",
                "Magical Ability: " + str(player.magic[0]) + "  (" + strbon(player.bonuses["magic"]) + ")",
                "Luck: " + str(player.luck[0]) + "  (" + strbon(player.bonuses["luck"]) + ")",
                "",
                "Resistance: damage " + strbon(-player.protection),
                ""
                "Silver: " + str(game.silver) + " pieces",
                ]

            y = 0

            for line in information:
                l_s = FONTS[13].render(line, 1, (255,255,255))
                l_r = l_s.get_rect()
                l_r.midleft = (275, 150 + 16 * y)
                screen.blit(l_s, l_r)
                y += 1

        elif tab == "Inventory":
            if handcol == 0: oldhp = handpos; handpos = 0
#            screen.fill((0,0,0), Rect(275, 145, 180, 280))
#            screen.fill((0,0,0), Rect(460, 280, 130, 100))

            if handcol == 1:
                if handpos >= len(invlist):
                    handpos = len(invlist) - 1
                    invscroll = max(0, handpos-14)
                elif handpos < 0:
                    handpos = 0
            else:
                if invhandpos >= len(invlist):
                    invhandpos = len(invlist) - 1
                    invscroll = max(0, invhandpos-14)
                elif invhandpos < 0:
                    invhandpos = 0

            inv_items = [DATA.Itembox.GetItem(x) for x in player.inventory]
            inv_dict = {}
            if handcol == 1:
                invhandpos = handpos
            if handcol == 0:
                invhandpos = 0
            if invhandpos < 0:
                sel_obj = None
                invhandpos = 0
            if invhandpos < len(inv_items):
                sel_obj = inv_items[invhandpos]

            eq_items = []

            for k in player.wearing.keys():
                x = player.wearing[k]
                if len(x):
                    if k == "Accessories":
                        for item in x:
                            eq_items += [item]
                    elif x[0] is not None:
                        if len(inv_items) == invhandpos:
                            sel_obj = x[3]
                        eq_items.append(x[3])

            for i in inv_items:
                if i.display in inv_dict:
                    inv_dict[i.display] += 1
                else:
                    inv_dict[i.display] = 1
            for e in eq_items:
                if e.display+" (eq.)" in inv_dict:
                    inv_dict[e.display+" (eq.)"] += 1
                else:
                    inv_dict[e.display+" (eq.)"] = 1
                
            invlist = inv_dict.keys()
            invlist.sort()

            invhandpos = min(invhandpos, len(invlist)-1)

            sel_obj = DATA.Itembox.GetItem(invlist[invhandpos].replace(" (eq.)", ""))

            if handcol == 1:
                ministatus = invlist[invhandpos] + " -- Press " + namekey("Right", CONTROLS) + " or " + namekey("B-1", CONTROLS) +  " to select action menu"
            elif handcol == 2 and sel_obj:
                act = actions[handpos].lower()
                if "can't" in act or act == "?":
                    ministatus = "Unable to activate"
                else:
                    ministatus = "Press " + namekey("B-1", CONTROLS) + " to " + act + " " + sel_obj.display
            if len(invlist) == 0:
                handcol = 0
                sel_obj = None
                pic = None
                actions = []

            y = 0
            actionchange = False

            if sel_obj:
                pic = sel_obj.inv_image
            else:
                pic = None

            for item in invlist[invscroll:invscroll+17]:
                if y+invscroll == invhandpos and handcol >= 1:
                    if handcol == 1:
                        c = (255, 200, 65)
                    elif handcol == 2:
                        c = (80, 60, 20)
                    if item.endswith("(eq.)"):
                        actionchange = True
                else:
                    c = (100,100,100)
                    if item.endswith("(eq.)"):
                        c = (20,100,120)
                
                i_s = FONTS[13].render(item+["", " x" + str(inv_dict[item])][inv_dict[item] > 1], 1, c)
                i_r = i_s.get_rect()
                i_r.midleft = (277, 155 + 16 * y)
                screen.blit(i_s, i_r)
                y += 1

            actions = []

            if sel_obj:
                actions = [["Use", "Equip"][sel_obj.type=="wearable"],
                           "Discard",
                           "Examine"]

                if sel_obj.use_prefix: actions[0] = sel_obj.use_prefix
                if sel_obj.type.lower() == "accessory" and len(player.wearing["Accessories"]) >= 5:
                    actions[0] = "Can't wear more"

                if actionchange:
                    actions[0] = ["Remove", "Unequip"][sel_obj.type=="wearable"]

                    if sel_obj.location.lower() == "weapon":
                        actions[0] = "Can't unequip"

            if handcol == 2:
                if handpos >= 3:
                    handpos = 2
                elif handpos < 0:
                    handpos = 0

            y = 0
            for action in actions:
                c = (150,150,150)
                if "Can't" in action or action == "?":
                    c = (150, 20, 20)
                if handcol == 2 and handpos == y:
                    c = (255, 200, 65)
                    if "Can't" in action or action == "?":
                        c = (255, 80, 50)
                a_s = FONTS[13].render(action, 1, c)
                a_r = a_s.get_rect()
                a_r.midleft = (462, 290 + 16 * y)
                screen.blit(a_s, a_r)
                y += 1
            if pic:
                screen.blit(DATA.images[pic][0], (460, 145))
            if handcol == 0:
                handpos = oldhp

        elif tab == "Equipped":
            eqhandpos = None
            iteminfo = []
            if handcol == 1:
                eqhandpos = handpos
                ministatus = "Press " + namekey("Left", CONTROLS) + " to get back to Menu"
            equipment = []
            if len(player.wearing) and player.wearing["Weapon"][0]:
                equipment.append("#Weapon")
                equipment.append(player.wearing["Weapon"][3].display)
                equipment.append("")
            Armouradded = False
            for k in ["Head", "Torso", "Legs", "Gloves", "Boots"]:
                x = player.wearing[k]
                if not len(x): continue
                if x[0]:
                    if not Armouradded:
                        Armouradded = True
                        equipment.append("#Armour")
                    equipment.append(x[3].display)
            if Armouradded:
                equipment.append("")
            if len(player.wearing["Accessories"]):
                equipment.append("#Accessories")
                equipment += [x.display for x in player.wearing["Accessories"]]

            if eqhandpos >= len(equipment):
                eqhandpos = len(equipment) - 1
                eqdirection = 0
            if eqhandpos < 0:
                eqhandpos = 0
                eqdirection = 1

            if eqhandpos is not None:
                ply = 0
                while equipment[eqhandpos].startswith("#") or not equipment[eqhandpos]:
                    eqhandpos += [-1, 1][eqdirection]
                    if eqhandpos < 0:
                        eqhandpos = 0
                        eqdirection = 1
                    if eqhandpos >= len(equipment):
                        eqhandpos = len(equipment) - 1
                        eqdirection = 0
                    ply += 1
                    if ply > 5: eqhandpos = None; handcol = 0
            
            y = 0
            sel_item = None
            for line in equipment:
                if not line: y+=1;continue
                colour = (128, 128, 128)
                if line[0] == "#":
                    line = line[1:]
                    colour = (90, 215, 120)
                if y == eqhandpos and handcol == 1:
                    colour = (255, 200, 65)
                    sel_item = line
                i_s = FONTS[13].render(line, 1, colour)
                i_r = i_s.get_rect()
                i_r.midleft = (277, 155 + 16 * y)
                screen.blit(i_s, i_r)
                y += 1

            if handcol == 1: handpos = eqhandpos

            pic = None
            if sel_item:
                sel_obj = DATA.Itembox.GetItem(sel_item)
                pic = DATA.images[sel_obj.inv_image][0]
                for key in ["strength", "endurance", "magic", "luck"]:
                    if sel_obj.usage_bonus[key]:
                        iteminfo.append(key.capitalize() + " " + strbon(sel_obj.usage_bonus[key]))                
                if not sel_obj.bow:
                    if sel_obj.protection:
                        iteminfo.append("Resistance " + strbon(sel_obj.protection))
                    if sel_obj.damage:
                        iteminfo.append("Damage: " + str(sel_obj.damage))
                    if sel_obj.minrange:
                        iteminfo.append("Minimum range: " + str(sel_obj.minrange))
                    if sel_obj.range:
                        iteminfo.append("Maximum range: " + str(sel_obj.range))
                else:
                    iteminfo.append("(Bow)")

                if sel_obj.time:
                    iteminfo.append("Recovery time: " + str(sel_obj.time))
                if sel_obj.magic_drain:
                    iteminfo.append("Magic drain: " + str(sel_obj.magic_drain))
                iteminfo.append("")
                iteminfo.append("Approx. Value: " + str(max(0, sel_obj.value)) + "s")

                y = 0
                for line in iteminfo:
                    if not line: y+=1;continue
                    colour = (200, 200, 200)
                    i_s = FONTS[13].render(line, 1, colour)
                    i_r = i_s.get_rect()
                    i_r.midleft = (459, 290 + 16 * y)
                    screen.blit(i_s, i_r)
                    y += 1


            if pic:
                screen.blit(pic, (457, 145))

        elif tab == "Abilities":
            lhead_s = FONTS[13].render("Ability", 1, (255,255,255))
            chead_s = FONTS[13].render("Key Combination", 1, (255,255,255))
            rhead_s = FONTS[13].render("Level", 1, (255,255,255))

            lhead_r = lhead_s.get_rect()
            chead_r = chead_s.get_rect()
            rhead_r = rhead_s.get_rect()

            lhead_r.midleft = (280, 155)
            chead_r.midright = (520, 155)
            rhead_r.midright = (585, 155)

            screen.blit(lhead_s, lhead_r)
            screen.blit(chead_s, chead_r)
            screen.blit(rhead_s, rhead_r)

            y = 0

            curlen = len([x for x in player.combo_list if x[2] <= player.level])
            if handpos >= curlen:
                handpos = curlen-1

            if handcol == 1:
                ministatus = namekey("Left", CONTROLS) + ": Menu ... " + namekey("B-1", CONTROLS) + ": Information"

            for ability in player.combo_list:
                if player.level < ability[2]: continue
                c = [(180, 180, 180), (255, 255, 0)][y == handpos and handcol == 1]
                name_s = FONTS[16].render(player.movelist[ability[1]], 1, c)
                name_r = name_s.get_rect()

                real = list(ability[0])

                longcontrols = {
                    "LEFT SHIFT": "LShf",
                    "RIGHT SHIFT": "RShf",
                    "LEFT ALT": "LAlt",
                    "RIGHT ALT": "RAlt",
                    "LEFT CTRL": "LCtl",
                    "RIGHT CTRL": "RCtl",
                    "CAPS LOCK": "Caps",
                    "SCROLL LOCK": "ScLk",
                    "TAB": "Tab",
                    "MENU": "Mnu",
                    "UP": "Up",
                    "DOWN": "Down",
                    "LEFT": "Left",
                    "RIGHT": "Rght",
                    "PRINT": "Prnt",
                    "PAUSE": "Paus",
                    "INSERT": "Ins",
                    "HOME": "Home",
                    "PAGE UP": "PgUp",
                    "PAGE DOWN": "PgDn",
                    "DELETE": "Del",
                    "END": "End",
                    "ENTER": "Entr",
                    "BACKSPACE": "Bksp",
                    "SPACE": "Spce"
                    }
                
                for l in range(len(real)):
                    letter = real[l]
                    if letter.isdigit():
                        lettercode = namekey("B-"+letter, CONTROLS)
                        if lettercode[0] == "[" and lettercode[-1] == "]":
                            lettercode = "Num" + lettercode[1:-1]
                        if lettercode in longcontrols:
                            lettercode = longcontrols[lettercode]
                        elif len(lettercode) > 1:
                            lettercode = lettercode[:4].capitalize()
                        real[l] = lettercode
                        
                key_s = FONTS[16].render(", ".join(real), 1, (180, 180, 180))
                key_r = key_s.get_rect()

                level_s = FONTS[16].render(str(ability[2]), 1, (180, 180, 180))
                level_r = level_s.get_rect()

                name_r.midleft = (280, 175 + y * 16)
                key_r.midright = (520, 175 + y * 16)
                level_r.midright = (585, 175 + y * 16)

                screen.blit(name_s, name_r)
                screen.blit(key_s, key_r)
                screen.blit(level_s, level_r)
                y += 1

        elif tab == "Quest Log":
            quests = check_quest(player, game)
            y = 0
            for qname, qid in quests:
                if player.quests.has_key(qid):
                    message = player.quests[qid][1]
                    if player.quests[qid][0]:
                        col = (10, 200, 0)
                    else:
                        col = (195, 185, 10)
                else:
                    col = (190, 10, 0)
                surf = FONTS[13].render(qname, 1, col)
                rect = surf.get_rect()

                rect.midleft = (255, 150 + 14 * y)

                screen.blit(surf, rect)

                y += 1

            if handcol == 1:
                if handpos >= len(quests):
                    handpos = len(quests) - 1
                elif handpos < 0:
                    handpos = 0
                screen.blit(DATA.images["hand.png"][0], (450, 128 + 14 * handpos))
                message = "I have not started this quest yet."
                ministatus = quests[handpos][0] + ": Not Yet Begun"
                if player.quests.has_key(quests[handpos][1]):
                    message = player.quests[quests[handpos][1]][1]

                    if player.quests[quests[handpos][1]][0]:
                        ministatus = quests[handpos][0] + ": Quest Complete!"
                    else:
                        ministatus = quests[handpos][0] + ": Quest Incomplete"

                surfs = wordwrap.string_to_paragraph(message, FONTS[13], 1, (235, 235, 235), 120)
                y = 0
                for surf in surfs:
                    rect = surf.get_rect()
                    rect.midleft = (510, 150 + 14 * y)
                    screen.blit(surf, rect)
                    y += 1

        elif tab == "Upload Score":
            information = [
                "Player: " + game.savefilename[:-4],
                "Character: " + game.character + ", level " + str(player.level),
                "",
                "Your score (calculated by the server.)",
                "",
                "---------------------------------",
                "The above information will be",
                "submitted to a public scoreboard.",
                "",
                "See the scoreboard at jordan.trudgett.com.",
                "",
                "Status Message:",
                ]

            information += uploadresult

            for l in range(len(information)):
                if l > 11:
                    c = (255, 255, 0)
                else:
                    c = (255, 255, 255)

                ls = FONTS[23].render(information[l], 1, c)
                lr = ls.get_rect()
                lr.midleft = (275, 150 + 16 * l)
                screen.blit(ls, lr)

##             for line in information:
##                 line = line.strip()
##                 if information.index(line) >= len(information)-len(uploadresult):
##                     l_s = FONTS[23].render(line.strip(), 1, (255,255,0))
##                 elif information.index(line) < 4:
##                     l_s = FONTS[23].render(line.strip(), 1, (0,255,255))
##                 else:
##                     l_s = FONTS[16].render(line.strip(), 1, (255,255,255))
##                 l_r = l_s.get_rect()
##                 l_r.midleft = (275, 150 + 16 * y)
##                 screen.blit(l_s, l_r)
##                 y += 1

        elif tab == "Return":
            screen.blit(splayscreen, (265,140))

        elif tab == "Main Menu":
            if mmconfirm:
                mmcs = FONTS[23].render("Are you sure? Your game is not automatically saved.", 1, (255,255,0))
                mmcs2 = FONTS[23].render("Press the Main Menu item again to confirm.", 1, (255,255,0))
                mmcr = mmcs.get_rect()
                mmcr2 = mmcs2.get_rect()
                mmcr.center = (425, 250)
                mmcr2.center = (425, 265)
                screen.blit(mmcs, mmcr)
                screen.blit(mmcs2, mmcr2)
            else:
                screen.blit(mmpic, (265, 130))
        elif tab == "Abort level":
            screen.blit(ovscreen, (265, 130))

        # Handle input

        for event in ge():
            if event.type == KEYDOWN:
                k = event.key
                tk = typekey(k)
                if k == K_r and tab == "Status" and not renaming:
                    interface_sound("menu-select", SOUNDBOX)
                    renameto = ""
                    renaming = True
                elif tk and renaming and len(renameto) < 15:
                    renameto += tk
                elif k == K_BACKSPACE and renaming:
                    renameto = renameto[:-1]
                elif k == K_RETURN and renaming:
                    sfiles = os.listdir("Saves")
                    if renameto+".asf" in sfiles:
                        interface_sound("error", SOUNDBOX)
                    elif len(renameto) == 0:
                        interface_sound("error", SOUNDBOX)
                    else:
                        interface_sound("menu-small-select", SOUNDBOX)
                        tempgobj = cPickle.load(open(os.path.join("Saves", game.savefilename),"r"))
                        os.rename(os.path.join("Saves", game.savefilename), os.path.join("Saves", renameto+".asf"))
                        tempgobj.savefilename = renameto + ".asf"
                        cPickle.dump(tempgobj, open(os.path.join("Saves", renameto+".asf"), "w"))
                        game.savefilename = renameto + ".asf"
                        renaming = False
                        renameto = ""
                    
                if k in CONTROLS["Down"] and not renaming:
                    mmconfirm = False
                    eqdirection = 1
                    if handcol == 0:
                        if handpos < len(menuitems) - 1:
                            handpos += 1
                            interface_sound("menu-item", SOUNDBOX)
                        while menuitems[handpos] == "":
                            handpos += 1
                    elif handcol == 1:
                        interface_sound("menu-item", SOUNDBOX)
                        handpos += 1
                        invscroll = max(0, max(invscroll, handpos-14))
                    elif handcol == 2 and handpos < 2:
                        interface_sound("menu-item", SOUNDBOX)
                        handpos += 1
                if k in CONTROLS["Up"] and not renaming:
                    mmconfirm = False
                    eqdirection = 0
                    if handpos > 0:
                        interface_sound("menu-item", SOUNDBOX) 
                        handpos -= 1
                        if handcol == 1:
                            invscroll = max(min(invscroll, handpos-2), 0)
                    while handcol == 0 and menuitems[handpos] == "":
                        handpos -= 1
                if k in CONTROLS["Right"] or k in CONTROLS["B-1"]:
                    if handcol == 0 and tab in ["Inventory", "Equipped", "Abilities", "Quest Log"]:
                        interface_sound("menu-item", SOUNDBOX)
                        handcol = 1
                        oldhandpos = handpos
                        handpos = 0
                        continue
                    elif handcol == 1 and tab in ["Inventory"]:
                        interface_sound("menu-item", SOUNDBOX)
                        invhandpos = handpos
                        handcol = 2
                        handpos = 0
                        continue
                if k in CONTROLS["Left"] or k in CONTROLS["B-2"]:
                    if handcol == 1 and tab in ["Inventory", "Equipped", "Abilities", "Quest Log"]:
                        interface_sound("menu-item", SOUNDBOX)
                        handcol = 0
                        handpos = oldhandpos
                    elif handcol == 2 and tab in ["Inventory"]:
                        interface_sound("menu-item", SOUNDBOX)
                        handcol = 1
                        handpos = invhandpos

                if k in CONTROLS["B-9"] and not renaming:
                    inmenu = False
                if k in CONTROLS["B-1"]:
                    if handcol == 1 and tab == "Abilities":
                        screen.fill((0,0,0))
                        abil_name = player.movelist[[x for x in player.combo_list if x[2] <= player.level][handpos][1]]
                        abil_surf = FONTS[14].render(abil_name, 1, (255, 255, 255))
                        abil_rect = abil_surf.get_rect()
                        abil_rect.center = (320, 50)
                        screen.blit(abil_surf, abil_rect)
                        abil_desc = ABILITY_DESC[abil_name]
                        abil_surfs = wordwrap.string_to_paragraph(abil_desc, FONTS[13], True, (255, 255, 255), 600)
                        y = 0
                        for s in abil_surfs:
                            r = s.get_rect()
                            r.midleft = (20, 150 + y*20)
                            screen.blit(s, r)
                            y += 1

                        bs = FONTS[13].render("Press " + namekey("B-1", CONTROLS) + ", " + namekey("B-2", CONTROLS) + " or " + namekey("B-9", CONTROLS) + " to return", 1, (255,255,255))
                        br = bs.get_rect()
                        br.bottomright = (635, 475)
                        screen.blit(bs, br)
                        im = True
                        myflip()
                        while im:
                            ti = pygame.time.get_ticks()
                            for e in ge():
                                if e.type == KEYDOWN:
                                    if e.key in CONTROLS["B-1"] + CONTROLS["B-2"] + CONTROLS["B-9"]:
                                        im = False
                            ti = my_raw_wait(ti, 40)
                                
                    if handcol == 0:
                        if menuitems[handpos] == "Abort level":
                            rv = -2
                            inmenu = False
                        if menuitems[handpos] == "Upload Score":
                            try:
                                uploadresult = uploadscore(game)
                            except:
                                uploadresult = ["Service unavailable, try again later or check http://jordan.trudgett.com/"]
                        if menuitems[handpos] == "Return":
                            inmenu = False
                        if menuitems[handpos] == "Main Menu":
                            if mmconfirm:
                                rv = -1
                                inmenu = False
                            else:
                                mmconfirm = True
                    if tab == "Help":
                        helping = True
                        source = open("help.txt", "r").readlines()
                        scroll = 0
                        nlines = 28
                        interface_sound("menu-item", SOUNDBOX)
                        while helping:
                            ti = pygame.time.get_ticks()
                            screen.blit(DATA.images["Not_Quite_Black.png"][0], (0,0))
                            if scroll+nlines > len(source) + 10:
                                scroll = len(source) - nlines + 10
                            # Text
                            y = 0
                            for line in source[scroll:scroll+nlines]:
                                line = line.rstrip()
                                line_s = FONTS[18].render(line, 1, (255,255,255))
                                line_r = line_s.get_rect()
                                line_r.midleft = (5, 10 + y * 17)
                                screen.blit(line_s, line_r)
                                y += 1

                            # Bottom bar
#                            screen.fill((0,0,0), Rect(0, 450, 640, 30))
                            bottombar_s = FONTS[16].render("Press " + namekey("B-2", CONTROLS) + " to exit and " +\
                                                           namekey("Up", CONTROLS) + " and " +\
                                                           namekey("Down", CONTROLS) + " to scroll", 1, (255,255,255))
                            bottombar_r = bottombar_s.get_rect()
                            bottombar_r.midright = (630, 470)
                            screen.blit(bottombar_s, bottombar_r)

                            myflip()

                            for e in ge():
                                if e.type == KEYDOWN:
                                    k = e.key
                                    if e.key == K_ESCAPE or e.key in CONTROLS["B-2"] or e.key in CONTROLS["B-9"]:
                                        helping = False
                                        interface_sound("menu-item", SOUNDBOX)
                                    elif e.key in CONTROLS["Down"]:
                                        scroll += 1
                                    elif e.key in CONTROLS["Up"]:
                                        scroll = max(0, scroll - 1)
                            
                            ti = my_raw_wait(ti, 40)
                    if tab == "Inventory":
                        if handcol == 2:
                            if handpos == 0:
                                take = False
                                if sel_obj.on_use:
                                    exec(safe(sel_obj.on_use))
                                if sel_obj.type.lower() == "consumable":
                                    take = True
                                    if sel_obj.use_sound:
                                        SOUNDBOX.PlaySound(sel_obj.use_sound)
                                if sel_obj.type.lower() == "wearable":
                                    if invlist[invhandpos].endswith("(eq.)"):
                                        if sel_obj.location == "Weapon":
                                            interface_sound("error", SOUNDBOX)
                                            continue
                                        player.inventory.append(sel_obj.name)
                                        player.wearing[sel_obj.location] = [None, None, None, None]
                                    else:
                                        interface_sound("equip", SOUNDBOX)
                                        if player.wearing[sel_obj.location][0]:
                                            player.inventory.append(player.wearing[sel_obj.location][0])
                                        player.wearing[sel_obj.location] = [sel_obj.name, sel_obj.wearable_image_prefix, [sel_obj.Warrior_Frames, sel_obj.Mage_Frames][player.classtype == 1], sel_obj]
                                        take = True
                                readd = False

                                if sel_obj.type.lower() == "accessory":
                                    if invlist[invhandpos].endswith("(eq.)"):
                                        removeme = None
                                        for x in range(len(player.wearing["Accessories"])):
                                            if player.wearing["Accessories"][x].name == sel_obj.name:
                                                removeme = x
                                                break
                                        if removeme is not None:
                                            player.wearing["Accessories"] = player.wearing["Accessories"][:removeme] + player.wearing["Accessories"][removeme+1:]
                                        player.inventory.append(sel_obj.name)
                                    elif len(player.wearing["Accessories"]) < 5:
                                        player.wearing["Accessories"].append(sel_obj)
                                        take = True

                                if take:
                                    Done = False
                                    tempinv = []
                                    for x in range(len(player.inventory)):
                                        if player.inventory[x].lower() != DATA.Itembox.GetItem(invlist[invhandpos]).name.lower() or Done == True:
                                            tempinv.append(player.inventory[x])
                                        else:
                                            Done = True

                                    player.inventory = tempinv

                            if actions[handpos] == "Discard":
                                # Get rid of item
                                if sel_obj.location == "Weapon":
                                    interface_sound("error", SOUNDBOX)
                                else:
                                    Done = False
                                    theitem = invlist[invhandpos]
                                    if theitem.endswith("(eq.)"):
                                        theitem = theitem[:-6]
                                    realname = DATA.Itembox.GetItem(theitem).name
                                    if realname in player.inventory:
                                        player.inventory.remove(realname)
                                        Done = True
                                    else:
                                        interface_sound("error", SOUNDBOX)

                            if actions[handpos] == "Examine":
                                interface_sound("menu-select", SOUNDBOX)
                                examining = True
                                copyscr = screen.copy()
                                starttick = tick
                                while examining:
                                    screen.fill((0,0,0))
                                    copyscr.set_alpha(max(255-6*(tick-starttick), 20))
                                    screen.blit(copyscr, (0,0))
                                    pic = DATA.images[sel_obj.inv_image][0]
                                    if pic:
                                        rsurf = pygame.transform.rotate(pic, tick*2)
                                        rrect = rsurf.get_rect()
                                        rrect.center = (320, 160)

                                        screen.blit(rsurf, rrect)

                                    writtendesc = sel_obj.description
                                    y = 0
                                    for line in wordwrap.string_to_paragraph(writtendesc, FONTS[13], 1, (255,255,255), 600):
                                        screen.blit(line, (20, 300 + y * 16))
                                        y += 1

                                    myflip()

                                    for e in ge():
                                        if e.type == KEYDOWN:
                                            if e.key in CONTROLS["B-1"]:
                                                examining = False
                                    
                                    ti = my_raw_wait(ti, 50)
                                    tick += 1

        if handcol == 0:
            tab = menuitems[handpos]

        # Flip
        myflip()
        if dsa < 230: dsa += 30
        if dsa > 230: dsa = 230

        # Time delay 
        ti = my_raw_wait(ti, 40)
        tick += 1

    pygame.key.set_repeat()
    SOUNDBOX.MusicVol(1)

    dsa = 230
    darksurf.set_alpha(dsa)
    for x in range(dsa / 30):
        playscreen.set_alpha(255)
        screen.blit(playscreen, (0,0))
        screen.blit(darksurf, (0,0))
        screen.blit(menusurf, (0,0))
        playscreen.set_alpha(255-dsa)
        screen.blit(playscreen, (0,0))
        dsa -= 30
        myflip()
        ti = my_raw_wait(ti, 40)
    playscreen.set_alpha(255)
    screen.blit(playscreen, (0,0))
    myflip()

    lasttick = ti
    return rv

def blit_debug_messages(screen):
    global FONTS, CSPEEDARRAY, PLAYER, PARTICLES, CAMERA_X, vpos
    # Debugging messages.

    # Player speed.
    ss = FONTS[14].render(str(abs(int(40*PLAYER.inertia[0]))) + "   pi/s", 1, (255,0,255))
    sr = ss.get_rect()
    sr.midleft = (PLAYER.x-CAMERA_X-60, PLAYER.y + 20 - vpos)
    screen.blit(ss, sr)
                 
    information = [
        "CPU Capability: " + str(int(sum(CSPEEDARRAY) / 10.0)) + "%",
        "Player Pos Rounded: " + str((int(round(PLAYER.x)),int(round(PLAYER.y)))),
        "Rain Heaviness Rounded: " + str(int(RAIN_HEAVINESS)),
        "Particles: " + str(len(PARTICLES)),
        "Groundtype: " + PLAYER.groundtype + " (" + footstep_types.get(PLAYER.groundtype, "Unknown") + ")",
        "Horizontal Speed: " + str(abs(int(40 * PLAYER.inertia[0]))) + " u"
        "Vertical Speed: " + str(abs(int(40 * PLAYER.inertia[1]))) + " u"
        ]

    for x in range(len(information)):
        infosurf = FONTS[9].render(information[x], 1, (255,255,255))
        infosurfb = FONTS[9].render(information[x], 1, (0,0,0))
        inforect = infosurf.get_rect()
        inforect.midright = (630, 10 + x * 12)
        screen.blit(infosurfb, inforect.move(1,1))
        screen.blit(infosurf, inforect)

def blit_falling_bg_objs(THISFLIP):
    global SCREEN, DATA, FALLINGBGOBJARRAY, FRAMEMOD, CAMERA_X, LEVEL
    if not FRAMEMOD%50:
        FALLINGBGOBJARRAY.append([random.randint(0,314)/100.0, random.randint(CAMERA_X-640,CAMERA_X+1280),-100, random.randint(3,10)/10.0])

    objstyle = fallingobjstylefortheme(LEVEL.theme)
    if not objstyle: return

    numframes = framesfalling(objstyle)

    if THISFLIP:
        for fallingbgobj in FALLINGBGOBJARRAY:
            lobj = DATA.images[objstyle + str(int(fallingbgobj[0]%numframes)+1) + ".png"]
            lsurf, lrect = lobj[0], lobj[1]
            lrect.center = (fallingbgobj[1] - CAMERA_X + math.sin(fallingbgobj[0])*fallingbgobj[3]*10, fallingbgobj[2])
            SCREEN.blit(lsurf, lrect)

    for x in range(len(FALLINGBGOBJARRAY)):
        FALLINGBGOBJARRAY[x][0] += FALLINGBGOBJARRAY[x][3]/6.0
        FALLINGBGOBJARRAY[x][2] += FALLINGBGOBJARRAY[x][3]*3
        if FALLINGBGOBJARRAY[x][2] > 620: # Accomodates for big snowflakes sprite
            FALLINGBGOBJARRAY[x] = None

    while None in FALLINGBGOBJARRAY:
        FALLINGBGOBJARRAY.remove(None)

def safe(s):
    #This will prevent malicious code being snuck into the scripting language
    b = ["__", "os.",
         "system", "import"]
    for x in b:
        if x.lower() in s.lower():
            return False
    return s

def check_rules(rules):
    global PLAYER, SOUNDBOX, var, RAIN_HEAVINESS, RAINING, Timegem_time, P_OPTIONS
    global LEVEL, CL_Surface, Objects, LEVELSTATUS, IN_GAME

    creplace = {
        "posx": "PLAYER.x",
        "posy": "PLAYER.y",
        "rain": "RAIN_HEAVINESS",
        "msg": "message_box",
        "ptag": "PLAYER.tags",
        "setpt": "PLAYER.tagsettrue",
        "TIME1": "Timegem_time[0]",
        "TIME2": "Timegem_time[1]",
        "TIME3": "Timegem_time[2]",
        "help": "P_OPTIONS['Help']"
        }
    
    
    for rule in rules:
        if rule[0][0] == "finished": continue
        conditionclause = rule[0][1:]
        eventclause = rule[1]
        evalcond = ""
        for condition in conditionclause:
            condition = condition.split()
            for x in range(len(condition)):
                if condition[x] in creplace.keys():
                    condition[x] = creplace[condition[x]]
                for k in creplace.keys():
                    if k in condition[x]:
                        condition[x] = condition[x].replace(k, creplace[k])
            evalcond = evalcond + " and " + " ".join(condition)
        if evalcond:
            evalcond = evalcond[5:]
        else:
            continue

        if safe(evalcond):
            if eval(safe(evalcond)):
                for event in eventclause:
                    for x in creplace.keys():
                        event = event.replace(x, creplace[x])
                    if safe(event):
                        exec(safe(event))
                    else:
                        print "Unsafe event"
                    if rule[0][0].lower() == "when":
                        rule[0][0] = "finished"

def setTreasure(id, contents):
    # Called from ArdenScrypt, sets treasurebox contents.
    global Objects
    count = 0
    for x in Objects:
        if x.id == "TreasureBox":
            count += 1
            if count == id:
                x.bounty = contents.split(",")

def process_npcs(scriptfile):
    global NPCLIST, TUT_ACTIVE
    try:
        source = open(os.path.join("Levels", scriptfile), "r").readlines()
    except:
        return
    tempNPC = None
    for line in source:
        line = line.strip()
        if not line: continue
        data = line.split()
        if data[0] == "/NPC":
            tempNPC = NPC()
            tempNPC.name = data[1]
        elif data[0] == "/set":
            exec("tempNPC." + safe(data[1]) + " = " + " ".join(data[2:]))
        elif data[0] == "/END":
            if (tempNPC.tutorial and TUT_ACTIVE) or not tempNPC.tutorial:
                NPCLIST.append(tempNPC)

def ground_at(x, f=False):
    "Finds the y co-ordinate of the ground at position x."
    global LEVEL
    ysense = 479
    sensing = True
    while sensing:
        sensetile = LEVEL.map[x/40][ysense/40]
        if not sensetile or "NONE" in sensetile.collidetype: break
        if sensetile.collidetype == "RIGHT_INCLINATION":
            if x%40 < 40-(ysense%40):
                break
        elif sensetile.collidetype == "RIGHT_HINCLINATION1":
            if x%40 < 2*(40-(ysense%40)):
                break
        elif sensetile.collidetype == "RIGHT_HINCLINATION2":
            if (x%40)+40 < 2*(40-(ysense%40)):
                break
        elif sensetile.collidetype == "LEFT_INCLINATION":
            if x%40 > ysense%40:
                break
        elif sensetile.collidetype == "LEFT_HINCLINATION1":
            if x%40 + 40 > 2*(ysense%40):
                break
        elif sensetile.collidetype == "LEFT_HINCLINATION2":
            if (x%40) > 2*(ysense%40):
                break
        ysense -= [1,10][f]
    return ysense

def NPC_Tick():
    global NPCLIST, PLAYER, DATA, SCREEN, CAMERA_X, TUT_ACTIVE

    for NPC in NPCLIST:
        if NPC.tutorial and not TUT_ACTIVE:
            NPCLIST[NPCLIST.index(NPC)] = None
    while None in NPCLIST:
        NPCLIST.remove(None)

    for NPC in NPCLIST:
        # all clocks increase once per tick.
        NPC.clock += 1

        if NPC.still:
            if not NPC.clock%6: NPC.frame += 1
            
        # depending on whether they follow the player, change vars accordingly

        if NPC.follow_player_fly:
            # NPC wishes to follow player, in a flying sense.
            NPC.x = (NPC.x * 20 + (PLAYER.x + cmp(0.5, PLAYER.direction) * 40))/21.0
            NPC.y = (NPC.y * 20 + (PLAYER.y-40))/21.0
            if abs(NPC.x - PLAYER.x) < 80:
                if NPC.first_proximity_message:
                    message_box(NPC.first_proximity_message, NPC.portrait, NPC.talksounds)
                    NPC.first_proximity_message = ""
            NPC.direction = int(NPC.x < PLAYER.x)

        if NPC.follow_player:
            # NPC wishes to follow player!
            if abs(NPC.x-PLAYER.x) > 50:
                if not NPC.unfollow:
                    if PLAYER.x > NPC.x:
                        newx = (NPC.x * 30 + (PLAYER.x-45))/31.0
                    if PLAYER.x < NPC.x:
                        newx = (NPC.x * 30 + (PLAYER.x+45))/31.0
                    speed = abs(newx-NPC.x)
                    if speed > 0.5:
                        NPC.x = newx
                        NPC.still = False
                        NPC.frame += speed/9.0
                        if NPC.animation == "Stopped":
                            NPC.frame = 0
                        NPC.animation = "Walking"
                    else:
                        NPC.animation = "Stopped"
                        if NPC.frame >= len(NPC.animations["Stopped"]):
                            NPC.frame = 0
                        NPC.still = True

                        if NPC.first_proximity_message:
                            message_box(NPC.first_proximity_message, NPC.portrait, NPC.talksounds)
                            NPC.first_proximity_message = ""

            if NPC.impervious:
                if not NPC.idirection:
                    NPC.x -= 3
                else:
                    NPC.x += 3

            gax = ground_at(int(NPC.x))
            gax2l = ground_at(int(NPC.x)-25,True)
            gax2r = ground_at(int(NPC.x)+25,True)

            if gax2l == 479 and PLAYER.x + 30 < NPC.x and NPC.y > gax-200:
                NPC.impervious = True
                NPC.idirection = NPC.direction
                NPC.fall = -6
            elif gax2r == 479 and PLAYER.x - 30 > NPC.x and NPC.y > gax-200:
                NPC.impervious = True
                NPC.idirection = NPC.direction
                NPC.fall = -6

            NPC.y += NPC.fall
            if NPC.y < gax:
                NPC.fall += 1
            elif gax >= NPC.y - 35 and gax <= NPC.y:
                NPC.y = gax
                NPC.fall = 0
                NPC.impervious = False
                NPC.unfollow = False
            elif gax < NPC.y - 35 and not NPC.impervious:
                NPC.fall = -6
                NPC.unfollow = True

            if NPC.x > PLAYER.x:
                NPC.direction = 0
            else:
                NPC.direction = 1
                
        else:
            # NPC is a rock.
            pass

        # after processing, we blit the npc, hopefully
        # as per usual, X, Y corresponds to the bottom_middle of the image.

        # firstly, get the image to blit

        if int(NPC.frame) >= len(NPC.animations[NPC.animation]):
            NPC.frame = 0

        imagename = "NPC-" + NPC.prefix + "-" + NPC.animations[NPC.animation][int(NPC.frame)]
        frame, framerect = DATA.images[imagename]
        framerect.midbottom = (NPC.x - CAMERA_X, NPC.y+5)
        if not NPC.direction: frame = pygame.transform.flip(frame, True, False)
        SCREEN.blit(frame, framerect)

def tutskip():
    global finalscreen, FONTS, DATA, CONTROLS, TUT_ACTIVE
    finalscreen.fill((0,0,0))
    myflip()
    message_box("Please follow the tutorial if this is your first time playing Ardentryst. Pay attention too, because you can only re-do this if you start the whole game again. Note: this will have no effect if you have Help messages off in the Options menu.")
    finalscreen.fill((0,0,0))
    myflip()
    ts = FONTS[17].render("Tutorial:", 1, (255,255,255))
    tr = ts.get_rect()
    tr.center = (320, 150)
    finalscreen.blit(ts, tr)

    options = ["Follow tutorial", "Skip tutorial altogether", "What now?"]

    n = 0
    for op in options:
        ops = FONTS[16].render(op, 1, (255,255,255))
        opr = ops.get_rect()
        opr.midleft = (170, 300 + n*30)
        n += 1
        finalscreen.blit(ops, opr)

    Choosing = True
    ti = 0
    c = 0
    myflip()
        
    while Choosing:
        time.sleep(0.02)
        finalscreen.fill(0)
        hs, hr = DATA.images["hand.png"]
        hs = pygame.transform.flip(hs, True, False)
        hr.midright = (150 + math.sin(ti/10.0)*10, 300 + c * 30)
        finalscreen.blit(hs, hr)

        myupdate(Rect(50,260,115,150))
        for ev in ge():
            if ev.type == KEYDOWN:
                k = ev.key
                if k == K_DOWN:
                    c = min(c + 1, 2)
                elif k == K_UP:
                    c = max(c - 1, 0)
                elif k == K_RETURN or k in CONTROLS["B-1"] and ti > 10:
                    if c == 1:
                        TUT_ACTIVE = False
                    elif c == 2:
                        tutskip()
                    Choosing = False
        ti += 1

def level_intro():
    global LEVEL, SCREEN, DATA, FONTS, PLAYER, GAME, finalscreen, Start_Level_Time
    global CONTROLS, Timegem_time
    
    SCREEN.fill((0,0,0))

    name_s = FONTS[14].render(LEVEL.name, 1, (255,255,255))
    name_r = name_s.get_rect()

    por_s, por_r = DATA.images["Portrait_"+GAME.character+".png"]
    por_r.topleft = (20, 20)

    t = pygame.time.get_ticks()
    e = t + 4000

    yts = Timegem_time[0]
    rts = Timegem_time[1]
    bts = Timegem_time[2]

    yts = str(yts/60).zfill(1) + ":" + str(yts%60).zfill(2)
    rts = str(rts/60).zfill(1) + ":" + str(rts%60).zfill(2)    
    bts = str(bts/60).zfill(1) + ":" + str(bts%60).zfill(2)

    if sum(Timegem_time) > 0:

        moardata = ["Yellow Timegem    " + yts,
                    "Red Timegem    " + rts,
                    "Blue Timegem    " + bts]
    else:
        moardata = ["No timegems",
                    "available!"]

    for x in range(len(moardata)):
        moardata[x] = FONTS[14].render(moardata[x], 1, (255-40*x%2,255-40*x%2,255-40*x%2))
        moardata[x] = [moardata[x], moardata[x].get_rect()]
    stopped = False
    while t < e:
        SCREEN.fill((0,0,0))

        sks = FONTS[17].render("Press " + namekey("B-1") + " to skip", 1, (255,255,255))
        skr = sks.get_rect()
        skr.midright = (635, 465)
        SCREEN.blit(sks, skr)

        at = e-t-1800
        t = pygame.time.get_ticks()
        name_r.topleft = (240, 150)

        n = 0
        for md in moardata:
            md[1].topleft = (280, 240 + 35 * n)
            n += 1
            SCREEN.blit(md[0], md[1])
        if not stopped:
            por_r.topleft = (math.sin(at/900.0)*140 - 150, 20)
        if math.cos(at/900.0) > 0 and at < 7000: por_r.topleft = (-10, 20); stopped = True

        SCREEN.blit(name_s, name_r)
        SCREEN.blit(por_s, por_r)

        for ev in ge():
            if ev.type == KEYDOWN:
                key = ev.key
                if key in CONTROLS["B-1"]:
                    t = e

        finalscreen.blit(SCREEN, (0,0))
        myflip()
        mywait(t)

    fade_to_black(SCREEN)
    Start_Level_Time = pygame.time.get_ticks()

def Level_Score(enemyperc, treasureperc, seconds, sd):
    global SCREEN, FONTS, finalscreen, DATA, CONTROLS, MEDAL

    enemyperc = int(enemyperc)
    treasureperc = int(treasureperc)

    info = [
        "Timegem: " + {-1: "None", 0: "Yellow (Fast)", 1: "Red (Faster)", 2: "Blue (Fastest)"}[MEDAL],
        "Enemies",
            "Treasure",
            "Level Completion",
            "Level Total",
            "",
            "Time"]

    info2 = [enemyperc,
             treasureperc,
             ["100%", "200%"][sd],
             (treasureperc+enemyperc+200)/4 +[0,100][sd],
             "",
             seconds]

    vinfo2 = [0, 0, ["100%","200%"][sd], 0, "", 0]

    blacksurf = pygame.Surface((640,480))
    blacksurf.set_alpha(100)
    SCREEN.blit(blacksurf, (0,0))

    lcr = DATA.images["LC.png"][1]
    lcr.center = (320, 112)
    SCREEN.blit(DATA.images["LC.png"][0], lcr)

    y = 0
    level_s = FONTS[17].render(LEVEL.name, 1, (255,255,255))
    level_r = level_s.get_rect()
    level_r.center = (320, 225)
    
    SCREEN.blit(level_s, level_r)

    for line in info:
        line_s = FONTS[17].render(line, 1, (255,255,255))
        line_r = line_s.get_rect()
        line_r.midleft = (100, 260 + y*30)
        SCREEN.blit(line_s, line_r)
        y += 1

    BACKSCREEN = SCREEN.convert()

    y = 0
    
    for line in vinfo2:
        if type(line) == str:
            line_s = FONTS[17].render(line, 1, (255,255,255))
        elif y == 5:
            line_s = FONTS[17].render("0:00", 1, (255,255,255))
        else:
            line_s = FONTS[17].render(str(line) + "%", 1, (255,255,255))
        line_r = line_s.get_rect()
        line_r.midright = (440, 290 + y*30)
        SCREEN.blit(line_s, line_r)
        y += 1

    finalscreen.blit(SCREEN, (0,0))
    fade_from_black(finalscreen, 50)

    Counting = True
    while Counting:
        ti = pygame.time.get_ticks()
        SCREEN.blit(BACKSCREEN, (0,0))

        y = 0
        for line in vinfo2:
            if y < 4:
                if type(line) == str:
                    line_s = FONTS[17].render(line, 1, (255,255,255))
                else:
                    line_s = FONTS[17].render(str(line) + "%", 1, (255,255,255))

                line_r = line_s.get_rect()
                line_r.midright = (440, 290 + y*30)
                SCREEN.blit(line_s, line_r)
            elif y == 5:
                line_s = FONTS[17].render(str(line/60) + ":" + str(line%60).zfill(2), 1, (255,255,255))
                line_r = line_s.get_rect()
                line_r.midright = (440, 290 + y*30)
                SCREEN.blit(line_s, line_r)

            y += 1

        Counting = False
        for x in range(len(vinfo2)):
            if type(vinfo2[x]) == int:
                if vinfo2[x] < info2[x]:
                    vinfo2[x] += 1
                    Counting = True

        ti = mywait(ti)
        finalscreen.blit(SCREEN, (0,0))
        myflip()

        for ev in ge():
            if ev.type == KEYDOWN:
                k = ev.key
                if k in CONTROLS["B-1"]:
                    Counting = False

    SCREEN.blit(BACKSCREEN, (0,0))

    y = 0
    for line in info2:
        if y < 4:
            if type(line) == str:
                line_s = FONTS[17].render(line, 1, (255,255,255))
            else:
                line_s = FONTS[17].render(str(line) + "%", 1, (255,255,255))
            line_r = line_s.get_rect()
            line_r.midright = (440, 290 + y*30)
            SCREEN.blit(line_s, line_r)
        elif y == 5:
            line_s = FONTS[17].render(str(line/60) + ":" + str(line%60).zfill(2), 1, (255,255,255))
            line_r = line_s.get_rect()
            line_r.midright = (440, 290 + y*30)
            SCREEN.blit(line_s, line_r)

        y += 1

    finalscreen.blit(SCREEN, (0,0))
    myflip()

    csleep(20)
    return info2[3]

def csleep(sec):
    global CONTROLS
    startti = pygame.time.get_ticks()
    while pygame.time.get_ticks() < startti + 1000 * sec:
        time.sleep(0.01)
        for ev in ge():
            if ev.type == KEYDOWN:
                k = ev.key
                if k in CONTROLS["B-1"]:
                    return True
    return False

def playdemo(*args):
    global PLAYDEMO, eventd, monsterd, playerd
    demofile = args[-1]
    args = args[:-1]
    dfile = open(os.path.join("Demos", demofile), "r")
    eventd, monsterd, playerd = cPickle.load(dfile)
    PLAYDEMO = True
    return playlevel(*args)

def check_tips():
    global MOUSEPOS, TOOLTIP
    regions = [
        [5  , 390, 80 , 470, "Health (HP) Bar"],
        [550, 390, 625, 470, "Mana (MP) Bar"],
        [180, 405, 250, 420, "Health (HP)"],
        [250, 405, 325, 420, "Character Level"],
        [325, 405, 470, 420, "Name Bar"],
        [180, 390, 470, 395, "Experience (Exp) Bar"],
        [180, 425, 250, 440, "Mana (MP)"],
        [250, 425, 325, 440, "Ailments"],
        [325, 425, 400, 440, "Weapon and magic combo timing bar"],
        [180, 450, 250, 465, "Silver pieces"],
        [250, 450, 325, 465, "Level playing time"],
        [325, 450, 470, 470, "Current combo"]
        ]

    for region in regions:
        if region[0] < MOUSEPOS[0] < region[2] and region[1] < MOUSEPOS[1] < region[3]:
            TOOLTIP = region[4]
        

def playlevel(player, level, scripts, screen, data, fonts, soundbox, game, options, tut_active, ovs, pl):
    # Play a level LEVEL on screen SCREEN. Returns a few values to the caller
    # to indicate information about the play.

    global LEVEL, SCREEN, DATA, FONTS, SOUNDBOX, PLAYER, PLAYER2
    global SKIPNEXT, lasttick, GAME, SCCOPY, STATUSBAR_RECT
    global DELAY, RAIN_HEAVINESS, CONTROLS, finalscreen
    global STATUSBAR_SURF, SCREENSHOT, CAMERA_X, RAINING
    global bbrect, FRAMEMOD, fsol, Time_Played, TUTBOX
    global CL_Surface, PLAYERSURF, DIGSURF, TUT_ACTIVE
    global MESSAGE_JUST_DONE, PARTICLES, Monsters, LEVELSTATUS
    global FACE_VIEW, ORBS, CONSOLE_ACTIVE, RTICK, EOLFADE
    global V_EXP, DSCREEN, POISONFACTOR, DEBUG, CSPEEDARRAY
    global FALLINGBGOBJARRAY, NPCLIST, vpos, NOTICE_VIEW, PIC_VIEW
    global Objects, TreasureCount, Treasures, Start_Level_Time
    global Timegem_time, MEDAL, PLAYDEMO, eventd, monsterd, playerd
    global simpressed, HPGLOBELIGHT, MPGLOBELIGHT, V_HP, V_MP
    global IN_GAME, ovscreen

    simpressed = [False] * 1000

    Timegem_time = [0, 0, 0]
    MEDAL = -1

    global RECORD_DEMO
    HPGLOBELIGHT, MPGLOBELIGHT = 0, 0

    # Testing
#    RECORD_DEMO = [True, {}, {}, {}, "DEMO.dem"]
    RECORD_DEMO = [False, {}, {}, {}, "DEMO2.dem"]

    global var

    global MOUSEPOS, TOOLTIP
    MOUSEPOS = 320, 240
    TOOLTIP = ""

    global G_OPTIONS, A_OPTIONS, P_OPTIONS
    logfile("Playlevel called: " + level.name)

    Start_Level_Time = pygame.time.get_ticks()

    FALLINGBGOBJARRAY = []
    for x in range(10):
        FALLINGBGOBJARRAY.append([random.randint(0,314)/100.0, random.randint(-10,1280),random.randint(-50,380), random.randint(3,10)/10.0])
    var = [0] * 100

    NPCLIST = []

    DELAY = 0
    MESSAGE_JUST_DONE = 100
    POISONFACTOR = 0

    DEBUG = False
    CSPEEDARRAY = [0, 0, 0, 0, 0]
    
    Hurtfade = 0
    ORBS = []

    PLAYER = player
    LEVEL = level
    SCREEN = pygame.Surface((640,480))
    definescreen(screen)
    DATA = data
    magic.m_init_data(DATA)
    FONTS = fonts
    SOUNDBOX = soundbox
    GAME = game

    G_OPTIONS, A_OPTIONS, P_OPTIONS, CONTROLS = options

    V_HP = 76 * PLAYER.hp[0] / float(PLAYER.hp[1])
    V_MP = 76 * PLAYER.mp[0] / float(PLAYER.mp[1])

    TUT_ACTIVE = tut_active and P_OPTIONS["Help"]
    TUTBOX = tutorial.TutBox(CONTROLS)
    if PLAYER.classtype:
        TUTBOX.Checkpoints = TUTBOX.Checkpoints2
        TUTBOX.face = TUTBOX.face2
        TUTBOX.playerclass = PLAYER.classtype
    PARTICLES = []
    FACE_VIEW = FaceViewer(550,100)
    NOTICE_VIEW = NoticeViewer(FONTS[13])
    PIC_VIEW = PicViewer()

    OBJECT_PROXIMITY_S = pygame.Surface((0,0))
    OBJECT_PROXIMITY_SB = pygame.Surface((0,0))
    OBJECT_PROXIMITY_R = Rect(0,0,0,0)
    OBJECT_CLOSEST = None

    DSCREEN = DATA.images["trans640.png"][0].convert_alpha()
    DSSCREEN = pygame.Surface((640,480))

    PLAYER.reset_for_new()
    if TUT_ACTIVE:
        PLAYER.ignore_move = True
    else:
        PLAYER.ignore_move = False
    V_EXP = PLAYER.exp

    LEVEL.endpoint = None
    LEVEL.STARTSET = False

    Make_CL_Surface(pygame.Surface((len(LEVEL.map)*40,480), SRCALPHA, 32))

    BACKGROUND = DATA.images[bgfortheme(LEVEL.theme)][0]

    PARALLAX_LAYERS_1 = pbgfortheme(LEVEL.theme)

    PXL1_DEFAULT = 1

    PARALLAX_LAYERS_2 = pfgfortheme(LEVEL.theme)

    PXL2_DEFAULT = 0

    ALAYER_1 = pygame.Surface((640, 480))
    ALAYER_2 = pygame.Surface((640, 480))
    CONSOLE_WIN = pygame.Surface((640,240))
    PAUSE_ALPHA = pygame.Surface((640,480))
    SCCOPY = pygame.Surface((640,480))
    SCCOPY.set_colorkey((0,0,0))
    SCCOPY.set_alpha(100)

#    LevelComplete, LCR = DATA.images["LC.png"]
    
    clock = pygame.time.Clock()
    lasttick = 0

    laggy = 0
    said_laggy = False
    IN_GAME = True
    CAMERA_X = 0
    CAMERA_MIDX = 320
    CAMERA_SLOWNESS = 18
    CAMVIEWDIST = 60
    CONSOLE_ACTIVE = False
    CONSOLE_ALPHA = 128
    CONSOLE_HISTORY = []
    CONSOLE_TEXT = ""
    CONSOLE_HIST_STAGE = 0
    CONSOLE_VIEW = []
    consurf = pygame.Surface((640, 240))
    consurf.blit(DATA.images["Console.png"][0], (0,0))

    finalscreen = screen
    ovscreen = pygame.transform.scale(ovs, (320, 240))

    STATUSBAR_RECT = pygame.Rect(0, 0, 640, 90)
    STATUSBAR_SURF = pygame.Surface((640,90))
    STATUSBAR_SURF.set_alpha(100)

    PLAYERSURF = pygame.Surface((400, 200))
    PLAYERSURF.set_colorkey((255,0,255))

    DIGSURF = pygame.Surface((320,100))
    DIGSURF.set_colorkey((255,0,255))

    EOLFADE = None
    EOLSURF = pygame.Surface((640,480))

    DEATHFADE = 0
    DEATHSURF = pygame.Surface((640,480))
    DEATHSURF.fill((0,0,0))

    HURTSURF = pygame.Surface((640,480))
    HURTSURF.fill((255,0,0))

    RAINING = True
    RAINSOUND = False
    RAIN_HEAVINESS = 0
    RTICK = 0
    RAIN_ARRAY = []

    FLIP_EVERY = 1
    FRAMEMOD = 0
    SKIPNEXT = 0
    SKIPWAIT = 0

    PAUSED = False

    LEVELSTATUS = "Failed"
    LEVELPERCENT = 0

    VIDEO_INFO = pygame.display.Info()

    TreasureCount = 0
    Treasures = 0
    Objects = Get_Objects(LEVEL)
    Monsters = Init_Monsters(LEVEL)
    MonsterCount = len(Monsters)

    levelscript, npcscript = scripts
    Rules = level_script.parse_scriptfile(levelscript)
    process_npcs(npcscript)

    if not LEVEL.STARTSET:
        PLAYER.x = 20; PLAYER.y = 40
    else:
        CAMERA_MIDX = PLAYER.x + CAMVIEWDIST

    # midlevel save

    if PLAYER.obelisk_save:
        if PLAYER.obelisk_save[0] == LEVEL.name:
            Monsters = cPickle.loads(PLAYER.obelisk_save[2])[:]
            Objects = PLAYER.obelisk_save[3][:]
            PLAYER.obelisk_save[1].obelisk_save = PLAYER.obelisk_save[:]
            PLAYER = copy.deepcopy(PLAYER.obelisk_save[1])
#            PLAYER.reset_for_new()
#            PLAYER.suddendeath = PLAYER.obelisk_save[1].suddendeath
            CAMERA_MIDX = PLAYER.x
            Treasures = PLAYER.obelisk_save[4]
        else:
            PLAYER.obelisk_save = None

    #debug stuff

    bounding_box = False
    bbrect = pygame.Rect(0,0,0,0)


    # first start of level
    fsol = True

    THISFLIP = True

    #end debug stuff

    uppervals = {
        "1" : "!",
        "2" : "@",
        "3" : "#",
        "4" : "$",
        "5" : "%",
        "6" : "^",
        "7" : "&",
        "8" : "*",
        "9" : "(",
        "0" : ")",
        "-" : "_",
        "=" : "+",
        ";" : ":",
        "'" : '"',
        "," : "<",
        "." : ">",
        "/" : "?",
        "[" : "{",
        "]" : "}",
        "\\" : "|",
        "`" : "~"
        }

    pygame.event.clear()

    if level.bgmusic:
        SOUNDBOX.PlaySong(level.bgmusic, -1)

    check_rules(Rules)

    level_intro()
    if PLAYER.obelisk_save:
        FRAMEMOD = PLAYER.obelisk_time

    if tut_active:
        tutskip()
        if not TUT_ACTIVE:
            PLAYER.ignore_move = False

    Time_Played = 0 # Purportedly fixes crash when level has no endpoint

    while IN_GAME:
        TOOLTIP = ""
        check_tips()
        if PLAYDEMO and FRAMEMOD in monsterd:
#            Monsters = [m for m in Monsters if m.x <= CAMERA_MIDX-500 or m.x >= CAMERA_MIDX+500]
            for x in range(len(monsterd[FRAMEMOD])):
                for key in monsterd[FRAMEMOD][x]:
                    setattr(Monsters[x], key, monsterd[FRAMEMOD][x][key])

        if PLAYDEMO and FRAMEMOD in playerd:
            for attr in playerd[FRAMEMOD]:
                setattr(PLAYER, attr, playerd[FRAMEMOD][attr])

        pl.update(locals())
        pl.update(globals())

        THISFLIP = FRAMEMOD % FLIP_EVERY == 0

        if CSPEEDARRAY.count(0) == 0:
            if int(sum(CSPEEDARRAY) / 10.0) < 70:
                laggy += 1
                if laggy == 20 and not said_laggy and not GAME.said_laggy:
                    said_laggy = True
                    GAME.said_laggy = True
                    message_box("The game seems sluggish. Tune the graphics effects to your system's capability from the Options menu in the Main Menu. Consider turning off Rain, Parallax effects and/or Moving BG Objects to increase playability before you next play Ardentryst.")
            else:
                laggy = 0

        if RAINING and not RAINSOUND and RAIN_HEAVINESS > 0:
            SOUNDBOX.SetSoundVolume("Rain_Loop.ogg", 0)
            SOUNDBOX.PlaySound("Rain_Loop.ogg", -1)
            RAINSOUND = True

        lasttick = mywait(lasttick) # Waiter
        if LEVEL.endpoint > PLAYER.x:
#            Time_Played = (pygame.time.get_ticks() - Start_Level_Time) / 1000
            Time_Played = int((FRAMEMOD*25)/1000.0)

        # Control rain sound
        if RAINING and RAIN_HEAVINESS > 0:
            if FRAMEMOD < 80:
                SOUNDBOX.SetSoundVolume("Rain_Loop.ogg", (FRAMEMOD/80.0)*RAIN_HEAVINESS/200.0)
            else:
                SOUNDBOX.SetSoundVolume("Rain_Loop.ogg", RAIN_HEAVINESS/200.0)
        else:
            SOUNDBOX.SetSoundVolume("Rain_Loop.ogg", 0)

        while CONSOLE_ACTIVE:
            lasttick = pygame.time.get_ticks()
            lasttick = mywait(lasttick)
            for event in ge():
                if event.type == KEYDOWN:
                    if event.key == K_BACKQUOTE:
                        CONSOLE_ACTIVE = False
                        CONSOLE_TEXT = ""
                        CONSOLE_HIST_STAGE = 0
                        continue
                    elif event.key == K_SPACE:
                        CONSOLE_TEXT += " "
                    elif event.key == K_RETURN:
                        logfile("Developers console: " + CONSOLE_TEXT)
                        CONSOLE_HISTORY.append(CONSOLE_TEXT)
                        CONSOLE_VIEW.append("] "+CONSOLE_TEXT)
                        try:
                            CONSOLE_VIEW.append("&" + str(eval(CONSOLE_TEXT)))
                        except Exception, e:
                            try:
                                exec(CONSOLE_TEXT) in globals()
                                CONSOLE_VIEW.append("%Successful")
                            except Exception, f:
                                CONSOLE_VIEW.append("#Couldn't evaluate because "+str(e)+".")                                
                                CONSOLE_VIEW.append("#Couldn't execute because " + str(f) + ".")
                        CONSOLE_HIST_STAGE = 0
                        CONSOLE_TEXT = ""
                    elif event.key == K_BACKSPACE:
                        CONSOLE_TEXT = CONSOLE_TEXT[:-1]
                    elif event.key == K_UP:
                        CONSOLE_HIST_STAGE += 1
                        if CONSOLE_HIST_STAGE > len(CONSOLE_HISTORY):
                            CONSOLE_HIST_STAGE = len(CONSOLE_HISTORY)
                        if len(CONSOLE_HISTORY) > 0:
                            CONSOLE_TEXT = CONSOLE_HISTORY[-CONSOLE_HIST_STAGE]
                    elif event.key == K_DOWN:
                        CONSOLE_HIST_STAGE -= 1
                        if CONSOLE_HIST_STAGE <= 0:
                            CONSOLE_TEXT = ""
                            CONSOLE_HIST_STAGE = 0
                        elif len(CONSOLE_HISTORY) > 0:
                            CONSOLE_TEXT = CONSOLE_HISTORY[-CONSOLE_HIST_STAGE]
                    keyname = pygame.key.name(event.key)
                    if len(keyname) == 1:
                        pygame.event.pump()
                        pkgp = pygame.key.get_pressed()
                        if pkgp[K_LSHIFT] or pkgp[K_RSHIFT]:
                            if uppervals.has_key(keyname):
                                CONSOLE_TEXT += uppervals[keyname]
                            else:
                                CONSOLE_TEXT += keyname.upper()
                        else:
                            CONSOLE_TEXT += keyname.lower()

            SCREEN.blit(CONSOLE_WIN, (0,0))
            ctrender = FONTS[9].render("] " + CONSOLE_TEXT, 1, (255,255,255))
            SCREEN.blit(ctrender, (10, 215))
            R_CONSOLE_VIEW = CONSOLE_VIEW[:]
            R_CONSOLE_VIEW.reverse()
            R_CONSOLE_VIEW = R_CONSOLE_VIEW[:17]
            for x in range(len(R_CONSOLE_VIEW)):
                R_CONSOLE_VIEW[x] = str(R_CONSOLE_VIEW[x])
                if R_CONSOLE_VIEW[x].startswith("]"):
                    cr, cg, cb = 180, 180, 180
                if R_CONSOLE_VIEW[x].startswith("#"):
                    R_CONSOLE_VIEW[x] = R_CONSOLE_VIEW[x][1:]
                    cr, cg, cb = 255, 50, 50
                elif R_CONSOLE_VIEW[x].startswith("&"):
                    R_CONSOLE_VIEW[x] = R_CONSOLE_VIEW[x][1:]
                    cr, cg, cb = 220, 180, 20
                elif R_CONSOLE_VIEW[x].startswith("%"):
                    R_CONSOLE_VIEW[x] = R_CONSOLE_VIEW[x][1:]
                    cr, cg, cb = 25, 200, 25
                else:
                    cr, cg, cb = 255, 255, 255
                thisline = FONTS[9].render(str(R_CONSOLE_VIEW[x]), 1, (cr,cg,cb))
                SCREEN.blit(thisline, (10, 203 - 12*x))
            finalise_screen()
            myflip()
            time.sleep(0.01)

        CAMERA_SLOWNESS = max(0, 20 - PLAYER.inertia[0])
        
        if PLAYER.direction:
            CAMERA_MIDX = slow_cam(CAMERA_MIDX, PLAYER.x + CAMVIEWDIST, CAMERA_SLOWNESS)
        else:
            CAMERA_MIDX = slow_cam(CAMERA_MIDX, PLAYER.x - CAMVIEWDIST, CAMERA_SLOWNESS)
            
        CAMERA_X = int(CAMERA_MIDX) - 320
        if PLAYER.quaking or PLAYER.bgquake:
            CAMERA_X += random.randint(-12,12)

        if CAMERA_X < 0: CAMERA_X = 0

        SCREEN.fill((25,25,25))

        SCREEN.blit(BACKGROUND, (0,0))
        # BG Plx.Layers

        if G_OPTIONS["Parallax Backgrounds"] > 0:
            for PL in PARALLAX_LAYERS_1:
                if PARALLAX_LAYERS_1.index(PL) != PXL1_DEFAULT and G_OPTIONS["Parallax Backgrounds"] == 1: continue
                x = -CAMERA_X * PL[2]
                SCREEN.blit(DATA.images[PL[0]][0], (int(x%640), 0))
                SCREEN.blit(DATA.images[PL[0]][0], (int(x%640) - 640, 0))

        PLAYER.var_tick(0)
        PLAYER.movement_run_tick()
        PLAYER.movement_jump_tick()
        PLAYER.movement_fall_tick()
        PLAYER.animation_update_tick()
        PLAYER.animation_frame_tick()
        PLAYER.arrow_tick()
        PLAYER.magic_tick()
        PLAYER.do_combo()

        if PLAYER.hp[0] <= 0 and DEATHFADE == 0:
            LEVELSTATUS = "Failed.LoseLife"
            LEVELPERCENT = 0
            DEATHFADE = 1
            if PLAYER.obelisk_save:
                PLAYER.obelisk_save[1].tags = PLAYER.tags[:]

        if G_OPTIONS["Moving BG Objects"]:
            blit_falling_bg_objs(THISFLIP)
        if THISFLIP:
            blit_map_at(CAMERA_X)

        Object_Tick(Objects, False)
        Monsters = Monster_Tick(Monsters)
        check_rules(Rules)
        NPC_Tick()

        if THISFLIP and Hurtfade == 0:
            blit_character(PLAYER, CAMERA_X)

        PLAYER.breath_tick()
        Object_Tick(Objects, True)
        Particle_Tick(PARTICLES)
        Orb_Tick(ORBS)

        # Now do object proximity stuff
        close_objects = []
        newclose = None
        for obj in Objects:
            if obj.x > PLAYER.x - [60, 20][PLAYER.direction] and obj.x < PLAYER.x + [20, 60][PLAYER.direction]:
                if obj.y > PLAYER.y - 40 and obj.y < PLAYER.y + 20:
                    if obj._activateable:
                        close_objects.append(obj)
        for npc in NPCLIST:
            if npc.x > PLAYER.x - [60, 20][PLAYER.direction] and npc.x < PLAYER.x + [20, 60][PLAYER.direction]:
                if npc.y > PLAYER.y - 40 and npc.y < PLAYER.y + 20:
                    if npc.interactive:
                        close_objects.append(npc)

        if close_objects:
            newclose = reduce(lambda a, b: [a, b][abs(b.x-PLAYER.x) < abs(a.x-PLAYER.x)], close_objects)
            if newclose != OBJECT_CLOSEST:
                OBJECT_CLOSEST = newclose
                try:
                    # obj
                    OBJECT_PROXIMITY_S = FONTS[13].render(newclose.P_id, 1, (255,255,255))
                    OBJECT_PROXIMITY_SB = FONTS[13].render(newclose.P_id, 1, (0,0,0))
                    OBJECT_PROXIMITY_R = OBJECT_PROXIMITY_S.get_rect()
                    isnpc = False
                except:
                    # npc
                    OBJECT_PROXIMITY_S = FONTS[13].render(newclose.name, 1, (255,255,255))
                    OBJECT_PROXIMITY_SB = FONTS[13].render(newclose.name, 1, (0,0,0))
                    OBJECT_PROXIMITY_R = OBJECT_PROXIMITY_S.get_rect()
                    isnpc = True

            if OBJECT_CLOSEST:
                if isnpc:
                    OBJECT_PROXIMITY_R.center = (OBJECT_CLOSEST.x, OBJECT_CLOSEST.y + 15)
                else:
                    OBJECT_PROXIMITY_R.center = (OBJECT_CLOSEST.x + 20, OBJECT_CLOSEST.y + 15)
                if hasattr(OBJECT_CLOSEST, "_wordoffset"):
                    OBJECT_PROXIMITY_R.move_ip(OBJECT_CLOSEST._wordoffset)
                for x in range(-1, 2):
                    for y in range(-1, 2):
                        SCREEN.blit(OBJECT_PROXIMITY_SB, OBJECT_PROXIMITY_R.move(x-CAMERA_X, y))
                SCREEN.blit(OBJECT_PROXIMITY_S, OBJECT_PROXIMITY_R.move(-CAMERA_X,0))
        else:
            OBJECT_CLOSEST = None

            
        # If passed endpoint, end
        if LEVEL.endpoint and PLAYER.y < 480:
            if LEVEL.endpoint <= PLAYER.x or PLAYER.iwin:
                MEDAL = -1
                for x in range(3):
                    if Time_Played <= Timegem_time[x]:
                        MEDAL = x
                PLAYER.directions[1] = True
                if EOLFADE is None:
                    EOLFADE = 255


        # If raining, draw rain
        if RAINING and G_OPTIONS["Rain"] == 1:
            RAIN_ARRAY = blit_new_rain(RAIN_HEAVINESS, RAIN_ARRAY, VIDEO_INFO)

        if RAIN_HEAVINESS < 1 and not TUTBOX.startraining: RAIN_HEAVINESS = 0


        # Parallax foregrounds after rain

        if G_OPTIONS["Parallax Foregrounds"] > 0:
            for PL in PARALLAX_LAYERS_2:
                if PARALLAX_LAYERS_2.index(PL) != PXL2_DEFAULT and G_OPTIONS["Parallax Foregrounds"] == 1: continue
                x = -CAMERA_X * PL[2]
                ALAYER_2.blit(SCREEN, (0,0))
                ALAYER_2.blit(DATA.images[PL[0]][0], (x%640, 0))
                ALAYER_2.blit(DATA.images[PL[0]][0], (x%640 - 640, 0))
                ALAYER_2.set_alpha(PL[1])
                SCREEN.blit(ALAYER_2, (0,0))


        # New: bit effects!

        if PLAYER.isbit("#regen1"):
            if not FRAMEMOD % 200 and PLAYER.hp[0] > 0: PLAYER.Take_Damage(-3)

        if PLAYER.isbit("#wings") and PLAYER.gravity > 0.85:
            PLAYER.gravity = 0.45
            PLAYER.jump_strength = 3.5
        else:
            PLAYER.gravity = 0.9
            PLAYER.jump_strength = 7

        # Hurt effects

        if PLAYER.isbit("poisoned"):
            Poison_Tick()

        if PLAYER.GOTHIT:
            PLAYER.suddendeath = False
            PLAYER.GOTHIT = False
            Hurtfade = min(Hurtfade + 15, 30)
            SOUNDBOX.PlaySound("Hit.ogg")

        if Hurtfade > 0 and DEATHFADE == 0:
            Hurtfade -= 1
            if G_OPTIONS["Tint screen"]:
                 HURTSURF.set_alpha(Hurtfade*5)
                 SCREEN.blit(HURTSURF, (0,0))

            TEMPSCREEN = SCREEN.copy()

            if G_OPTIONS["Pixellise screen"]:
                SCREEN.fill((0,0,0))
                r = ((30-Hurtfade)/30.0)
                r = int(r * 100)/100.0
                TEMPSCREEN = pygame.transform.scale(TEMPSCREEN, (int(160*r),int(120*r)))
                TEMPSCREEN = pygame.transform.scale(TEMPSCREEN, (640,480))

            if G_OPTIONS["Shake screen"]:
                nx = random.randint(-10,10)
                ny = random.randint(-10,10)
                nx *= Hurtfade/20.0
                ny *= Hurtfade/20.0
            else:
                nx, ny = 0, 0

            SCREEN.blit(TEMPSCREEN, (nx,ny))
            blit_character(PLAYER, CAMERA_X)

        if bounding_box:
            pygame.draw.rect(SCREEN, (255,255,255), bbrect, 1)
            pygame.draw.rect(SCREEN, (255,0,0), bbrect.inflate(-22,0), 1)

        if DEATHFADE > 0:
            if DEATHFADE == 1:
                DSSCREEN.blit(SCREEN, (0,0))
            PLAYER.directions = [False, False]
            DEATHSURF.set_alpha(DEATHFADE)
            DEATHFADE += 4

            stscreen = pygame.transform.scale(DSSCREEN, (800, 600))
#            stscreen = pygame.transform.scale(stscreen, (640, 480))

            stscreenr = stscreen.get_rect()
            stscreenr.center = (320,240)
            SCREEN.blit(stscreen, stscreenr)
            DSSCREEN.blit(stscreen, stscreenr)
            SCREEN.blit(DEATHSURF, (0,0))
            if DEATHFADE >= 255:
                PLAYER.hp[0] = PLAYER.hp[1]>>1 # half of max
                PLAYER.mp[0] = PLAYER.mp[1]>>1 # same.
                IN_GAME = False
                break

        # SCREEN UPDATES ->
        # Vertical scroll implementation [26-12-08]

        if THISFLIP:
            # note. our virtual screen is 640x380; in tiles; 12x9.5
            vpos = max(min(int((int(PLAYER.y)/480.0)*100),100),0) #restricted to between 0-100
            # PLAYER.vlook[0] will be -1, 0 or 1 (looking down)
            # vpos is say, 90.
            # tending to -1 -> vpos tends to 0
            # tending to 0 -> vpos tends to vpos
            # tending to 1 -> vpos tends to 100 .. 0.5 would be halfway between vpos and 100.
            avl = PLAYER.vlook[0] + 1
            if avl <= 1:
                vpos *= avl
            else:
                dif = 100 - vpos
                vpos += dif * PLAYER.vlook[0]
            vpos = min(vpos, 100)


            finalscreen.blit(SCREEN, (0, -vpos))

            #battle status window
            FACE_VIEW.blit(finalscreen)
            
            #status bar
            blit_new_status_bar(finalscreen)
            #globe lights
            if HPGLOBELIGHT:
                gs, gr = DATA.images["globelight.png"]
                gr.center = (43, 432)
                sbit = pygame.Surface(gr.size)
                sbit.blit(finalscreen, (0,0), gr)
                finalscreen.blit(gs, gr)
                sbit.set_alpha(255-HPGLOBELIGHT)
                finalscreen.blit(sbit, gr)
                HPGLOBELIGHT -= 5
            if MPGLOBELIGHT:
                gs, gr = DATA.images["globelight.png"]
                gr.center = (586, 432)
                sbit = pygame.Surface(gr.size)
                sbit.blit(finalscreen, (0,0), gr)
                finalscreen.blit(gs, gr)
                sbit.set_alpha(255-MPGLOBELIGHT)
                finalscreen.blit(sbit, gr)
                MPGLOBELIGHT -= 5
            # combo notice
            blit_combo(finalscreen, PLAYER.comboalpha)

            # end-of-level overlay and fade
            if EOLFADE is not None:
                EOLSURF.set_alpha(255-EOLFADE)
                finalscreen.blit(EOLSURF, (0,0))

                if EOLFADE <= 0:
                    IN_GAME = False
                    LEVELSTATUS = "Level_Complete"
                    if TreasureCount == 0:
                        TreasureCount = 1
                        Treasures = 1
                    if MonsterCount == 0:
                        MonsterCount = 1
                        Monsters = []
                    LEVELPERCENT = Level_Score(100-(len([x for x in Monsters if not x.isdead])*100/MonsterCount), Treasures*100/TreasureCount, Time_Played, PLAYER.suddendeath)
                EOLFADE -= 12

            # <-
        FACE_VIEW.tick()
        NOTICE_VIEW.blit_tick(finalscreen)
        PIC_VIEW.blit(finalscreen)

        # Now mouse cursor

        finalscreen.blit(DATA.images["MouseCurs2.png"][0], MOUSEPOS)
        if TOOLTIP:
            finalscreen.fill((0,0,0), Rect(0,467,640,13))
            tsurf = FONTS[23].render(TOOLTIP, 1, (255,255,255))
            trect = tsurf.get_rect()
            trect.midtop = (320, 466)
            finalscreen.blit(tsurf, trect)

        # Just before flipping, do a fade if need be
        if fsol: fade_from_black(finalscreen); fsol = False; lasttick = pygame.time.get_ticks()

        # Finally, after everything is blitted, check for messages from TutBox
        if TUT_ACTIVE:
            Tutorial_Tick(THISFLIP)
            MESSAGE_JUST_DONE += 1 # Another ticker-type object, but controls messagebox sounds
#        elif PLAYER.ignore_move:
#            PLAYER.ignore_move = False

        # DEBUG MESSAGES are on top of everything!

        if DEBUG:
            blit_debug_messages(finalscreen)

        # end debug messages

        # This is where the screen is flipped

#        if PLAYDEMO:
#            pygame.image.save(finalscreen, os.path.join("DemoScreens", str(FRAMEMOD).zfill(6)+".tga"))

        if SKIPNEXT >= 1:
            SKIPNEXT -= 1
            SKIPWAIT += 1
            if SKIPWAIT == 15:
                SKIPWAIT = 0
                myflip()
            if SKIPNEXT > 4:
                SKIPNEXT = 1
                if not said_laggy and not GAME.said_laggy:
                    message_box("The game appears too slow. You can try reducing graphics intensity in the"\
                                " Options menu via the Main Menu to increase playability. Turn off parallax layers and rain first.")
                    said_laggy = True
                    GAME.said_laggy = True
        elif THISFLIP:
            myflip()

        FRAMEMOD += 1

        if not FRAMEMOD % 75:
            if PLAYER.classtype: PLAYER.mp[0] += int(0.015 * PLAYER.mp[1]) + 1
            else: PLAYER.hp[0] += int(0.015 * PLAYER.hp[1]) + 1

        if not FRAMEMOD % 150:
            if PLAYER.classtype: PLAYER.hp[0] += int(0.015 * PLAYER.hp[1]) + 1
            else: PLAYER.mp[0] += int(0.015 * PLAYER.mp[1]) + 1

        if EOLFADE is not None: continue # Ignore events if level finishing
        if DEATHFADE is not 0: continue # likewise


        # <-
        # CONTROL STRUCTURE, controls are done here.

        if PLAYDEMO:
            ge()
            if FRAMEMOD in eventd:
                for e in eventd[FRAMEMOD]:
                    if e > 0:
                        post_e = pygame.event.Event(KEYDOWN, {"key": e})
                        simpressed[e] = True
                    else:
                        post_e = pygame.event.Event(KEYUP, {"key": -e})
                        simpressed[-e] = False
                    pygame.event.post(post_e)

        Record_Data = []
        pev = ge()[:]
        for ev in pev:
            if ev.type == KEYDOWN:
                Record_Data.append(ev.key)
            elif ev.type == KEYUP:
                Record_Data.append(-ev.key)

        if controldown("Right"): PLAYER.directions[1] = True
        else: PLAYER.directions[1] = False
        if controldown("Left"): PLAYER.directions[0] = True
        else: PLAYER.directions[0] = False
        if controldown("B-3"): PLAYER.strafing = True
        else: PLAYER.strafing = False
        if controldown("B-8"): PLAYER.looking = True
        else: PLAYER.looking = False

        if PLAYER.looking:
            if controldown("Up"):
                PLAYER.vlook[1] = -1
            elif controldown("Down"):
                PLAYER.vlook[1] = 1
            else:
                PLAYER.vlook[1] = 0
        else:
            PLAYER.vlook[1] = 0

        PLAYER.vlook[0] = (PLAYER.vlook[0]*3 + PLAYER.vlook[1])/4.0
        PLAYER.hlook[0] = (PLAYER.hlook[0]*3 + PLAYER.hlook[1])/4.0

        for event in pev:
            if event.type == MOUSEMOTION:
                MOUSEPOS = pygame.mouse.get_pos()
            if event.type == KEYDOWN:
                MOUSEPOS = -50, -50
                if RECORD_DEMO[0]: Record_Data.append(event.key)
                if event.key == K_e and DEBUG:
                    PLAYER.exp = (PLAYER.exp + PLAYER.expfor(PLAYER.level+1))/2
                if event.key == K_l and DEBUG:
                    PLAYER.exp = PLAYER.expfor(PLAYER.level+1)
                    PLAYER.possible_level_up()
                if event.key == K_x and DEBUG:
                    bounding_box = True
                if event.key == K_p and DEBUG:
                    IN_GAME = False
                    LEVELSTATUS = "Level_Complete"
                    LEVELPERCENT = 100
                    MEDAL = 2
                if event.key in CONTROLS["Up"] and not controldown("B-8"):
                    PLAYER.up_held = True
                    PLAYER.jumping = True
                if event.key in CONTROLS["Down"]:
                    PLAYER.down_held = True
                for x in range(8):
                    if event.key in CONTROLS["B-"+str(x+1)]:
                        PLAYER.add_to_combo(str(x+1))
                        break
                if event.key in CONTROLS["B-3"]:
                    try:
                        if OBJECT_CLOSEST and OBJECT_CLOSEST._activateable:
                            OBJECT_CLOSEST._activate()
                    except Exception, e:
                        if OBJECT_CLOSEST and OBJECT_CLOSEST.interactive:
                            if safe(OBJECT_CLOSEST.action):
                                exec(OBJECT_CLOSEST.action) in globals()
                if event.key in CONTROLS["B-9"]:
                    beforetick = pygame.time.get_ticks()
                    abortable = GAME.scores[GAME.location[0]-1][GAME.location[1]-1]
                    r = Ingame_Menu((finalscreen, DATA, FONTS, CONTROLS, SOUNDBOX, lasttick, GAME, PLAYER, abortable))
                    lasttick = pygame.time.get_ticks()
                    Start_Level_Time += lasttick-beforetick
                    if r:
                        if r == -1:
                            IN_GAME = False
                            LEVELSTATUS = "Quit"
                        elif r == -2:
                            IN_GAME = False
                            LEVELSTATUS = "Level_Complete"
                            LEVELPERCENT = -1
                            
                if event.key == K_BACKQUOTE and DEBUG:
                    pkgm = pygame.key.get_mods()
                    if not pkgm & KMOD_LSHIFT: continue
                    if not pkgm & KMOD_LCTRL: continue
                    PLAYER.directions = [False, False]
                    CONSOLE_ACTIVE = True
                    Ct = pygame.time.get_ticks()
                    vrender = FONTS[9].render("Developer's Console", 1, (255,255,255))
                    vrect = vrender.get_rect()
                    vrect.midright = (630, 225)
                    CONSOLE_WIN.blit(consurf, (0,0))
                    CONSOLE_WIN.blit(vrender, vrect)
                    for x in range(20):
                        SCREEN.blit(CONSOLE_WIN, (0,-228+x*12))
                        finalise_screen()
                        myupdate(Rect(0,0,640,320))
                        Ct = mswait(Ct, 10)
                if event.key == K_h and DEBUG:
                    PLAYER.Take_Damage(1)
                if event.key == K_s and DEBUG:
                    PLAYER.mp[0] -= 1
            elif event.type == KEYUP:
                if RECORD_DEMO[0]: Record_Data.append(-event.key)
                if event.key == K_x:
                    bounding_box = False
                if event.key in CONTROLS["Up"]:
                    PLAYER.up_held = False
                if event.key in CONTROLS["Down"]:
                    PLAYER.down_held = False

    if LEVELSTATUS != "Quit":
        SOUNDBOX.FadeoutMusic(1500)
        time.sleep(1.5)
    else:
        SOUNDBOX.FadeoutMusic(200)
    SOUNDBOX.FadeoutSound("Rain_Loop.ogg")
    if pygame.mixer.get_init():
        pygame.mixer.stop()
    fade_to_black(screen)
    check_rules(Rules)
    return LEVELSTATUS, LEVELPERCENT, MEDAL+1

def Particle_Spawn(sx, sy, ptype, amt):
    global G_OPTIONS, PARTICLES
    if G_OPTIONS["Particle Effects"] == 0: return
    if G_OPTIONS["Particle Effects"] == 1: amt /=2
    for x in range(amt):
        PARTICLES.append(Particle(sx, int(sy), ptype))

def blit_new_rain(r_heaviness, rain, v_info):
    global SCREEN, LEVEL, RTICK, CAMERA_X

    heaviness = int(r_heaviness/3)
    rlen = 9
    speed = 7
    trail = math.sin(RTICK/500.0)*10
    RTICK += 1
    SCCOPY = SCREEN.convert()

    rcols = ["BOX", "NONE_R"]
    mcols = ["RIGHT_INCLINATION", "LEFT_INCLINATION",
             "RIGHT_HINCLINATION1", "RIGHT_HINCLINATION2",
             "LEFT_HINCLINATION1", "LEFT_HINCLINATION2"]
    rcols += mcols
    while len(rain) < heaviness:
        rain.append([random.randint(0,640),random.randint(-60,-20), random.randint(3,10), random.randint(-5,5)])

    if len(rain) > heaviness:
        rain = rain[:heaviness]

    for x in range(len(rain)):

        if rain[x][1] > 480:
            rain[x][0] = random.randint(0,640)
            rain[x][1] = random.randint(-60,-20)

        rain[x][0] %= 640

        drop = rain[x]
        # define start and end points
        sp = (drop[0], drop[1])
        ep = (drop[0]-(trail+drop[3]), drop[1]+rlen*drop[2])
        # check if end point in map
        eptx = int((ep[0]+CAMERA_X)/40)
        epty = int(ep[1]/40)
        if 0 <= eptx <= len(LEVEL.map)-1 and 0 <= epty <= 11:
            lmexy = LEVEL.map[eptx][epty]
            if lmexy and lmexy.collidetype in rcols:
                ct = [eptx, epty]
                if ep[1]/40 != 0:
                    lmcxy = LEVEL.map[ct[0]][ct[1]]
                    while lmcxy and lmcxy.collidetype in rcols:
                        tiletype = lmcxy.collidetype
                        ct[1] -= 1
                        lmcxy = LEVEL.map[ct[0]][ct[1]]
                    px = ep[0]+CAMERA_X
                    py = ct[1]*40 + 40
                    if tiletype in mcols:
                        py += 20
                    Particle_Spawn(px, py, "PART_SPLASH", 2)
                    rain[x] = None
                else:
                    rain[x] = [random.randint(0,640),random.randint(-60,-20), random.randint(3,10), random.randint(-5,5)]

        if rain[x]:
            pygame.draw.line(SCREEN, (200, 200, 200), sp, ep, 1)
            rain[x][1] += speed * drop[2]
            rain[x][0] -= trail

    SCCOPY.set_alpha(140)
    SCREEN.blit(SCCOPY, (0,0))

    while None in rain:
        rain.remove(None)
    
    return rain

def toggle(variable):
    if variable: return False
    return True

def slow_cam(Camx, Plx, Slow):
    # Camx = Camera x (left pixel of screen)
    # Plx = Player x (middle pixel of player)
    # Slow = how slow to follow player.

    return (Camx * Slow + Plx) / float(Slow+1)

def comboname(combo):
    combos = [
        70, "Godlike!",
        60, "Mind-blowing!",
        55, "Terrifying!",
        45, "Demonic!",
        36, "Supreme!",
        28, "Awesome!",
        20, "Marvellous!",
        15, "Magnificent!",
        12, "Excellent!",
        9, "Impressive!",
        5, "Great!",
        3, "Good!",
        0, ""
        ]
    for x in range(0,len(combos),2):
        if combos[x] < combo:
            return combos[x+1]

def blit_combo(surf, alpha):
    global PLAYER, FONTS, FRAMEMOD
    if PLAYER.dcombo > 0 and PLAYER.comboalpha > 0:

        c = (0, 0, 0)
        comborender = FONTS[14].render(str(PLAYER.dcombo) + " hit" + ["s", ""][PLAYER.dcombo == 1] + "!", 1, c)
        combonamerender = FONTS[13].render(comboname(PLAYER.dcombo), 1, c) 
        damagerender = FONTS[13].render(str(int(PLAYER.dcombodamage)) + " damage", 1, c)
        comborect = comborender.get_rect()
        comborect.midleft = (10, 160)
        damagerect = damagerender.get_rect()
        damagerect.midleft = (10, 200)
        cnrect = combonamerender.get_rect()
        cnrect.midleft = (10,180)

        urect = comborect.union(damagerect).union(comborect).inflate(8,8)
        screenbit = pygame.Surface((urect[2],urect[3]))
        screenbit.blit(surf, (0,0), urect)
        screenbit.set_alpha(255-alpha)

        for x in range(-2, 3):
            for y in range(-2, 3):
                surf.blit(comborender, comborect.move(x,y))
                surf.blit(damagerender, damagerect.move(x,y))
                surf.blit(combonamerender, cnrect.move(x,y))

        c = (255, 255, 255)
        comborender = FONTS[14].render(str(PLAYER.dcombo) + " hit" + ["s", ""][PLAYER.dcombo == 1] + "!", 1, c)
        combonamerender = FONTS[13].render(comboname(PLAYER.dcombo), 1, c) 
        damagerender = FONTS[13].render(str(int(PLAYER.dcombodamage)) + " damage", 1, c)
        comborect = comborender.get_rect()
        comborect.midleft = (10, 160)
        damagerect = damagerender.get_rect()
        damagerect.midleft = (10, 200)
        cnrect = combonamerender.get_rect()
        cnrect.midleft = (10,180)

        surf.blit(comborender, comborect)
        surf.blit(damagerender, damagerect)
        surf.blit(combonamerender, cnrect)

        surf.blit(screenbit, urect)

def blit_new_status_bar(surf):
    global GAME, V_EXP, FONTS, Time_Played, DATA, CAMERA_X, vpos, PLAYER, V_HP, V_MP

    # Note to self: V_EXP means visual exp. bar. The bar that's seen
    # as opposed to the raw value which does not slide smoothly.
    # Sliding:
    V_EXP = (V_EXP * 20 + PLAYER.exp)/21.0
    exp_perc = float(V_EXP-PLAYER.expfor(PLAYER.level)) / (PLAYER.expfor(PLAYER.level+1) - PLAYER.expfor(PLAYER.level))

    # Same for HP/MP globes.
    V_HP = (V_HP * 14 + (76 * PLAYER.hp[0] / float(PLAYER.hp[1])))/15.0
    V_MP = (V_MP * 14 + (76 * PLAYER.mp[0] / float(PLAYER.mp[1])))/15.0

    # EXP BAR
    c = int(min(255, PLAYER.leveljustup*(255/100.0)))
    c = max(c, 0)
    surf.fill((c,c,c), Rect(180, 390, 290, 10))
    surf.fill((250,180,30), Rect(180, 390, exp_perc * 290, 10))

    if PLAYER.leveljustup > 0:

        if PLAYER.leveljustup >= 90:
            aura_alpha = (100 - PLAYER.leveljustup)*25
        else:
            aura_alpha = int(255 * (PLAYER.leveljustup/90.0))
        auraimg, aurarect = DATA.images["levelupaura.png"]
        aurarect.center = (PLAYER.x - CAMERA_X, PLAYER.y - 132 - vpos)
        screen_rect = pygame.Surface(aurarect.size)
        screen_rect.blit(surf, (-aurarect[0],-aurarect[1]))
        screen_rect.set_alpha(255-aura_alpha)
        surf.blit(auraimg, aurarect)
        surf.blit(screen_rect, aurarect)
        PLAYER.leveljustup -= 1
     
    if GAME.character == "Pyralis":
        surf.blit(DATA.images["Pyralis_Head.png"][0], (90,390))
    else:
        surf.blit(DATA.images["Nyx_Head.png"][0], (90,390))


    # ANGELS

    surf.blit(DATA.images["stonepiece.png"][0], (0,380))
    surf.blit(DATA.images["angelhp.png"][0], (2,348))

    surf.blit(DATA.images["stonepiece.png"][0], (542,380))
    surf.blit(DATA.images["angelmp.png"][0], (544,348))

    # hp, mp in orb

    hpsurf = pygame.Surface((90,100))
    hpsurf.set_colorkey((255,0,255))
    hpsurf.fill((255,0,255))
    mpsurf = pygame.Surface((90,100))
    mpsurf.set_colorkey((255,0,255))
    mpsurf.fill((255,0,255))

#    hpixperc = 76 * PLAYER.hp[0] / float(PLAYER.hp[1])
#    mpixperc = 76 * PLAYER.mp[0] / float(PLAYER.mp[1])
    hpsurf.fill((150,0,0), Rect(0, 19+(76-V_HP), 90, V_HP))
    hpsurf.set_alpha(160)
    mpsurf.fill((0,0,100), Rect(0, 19+(76-V_MP), 90, V_MP))
    mpsurf.set_alpha(200)
    surf.blit(hpsurf, (0,375))
    surf.blit(mpsurf, (542,375))

    # ACTUAL STATUS BAR
    surf.blit(DATA.images["statusbar.png"][0], (0, 380))
    # Re over it.
    surf.blit(DATA.images["angelhpnoorb.png"][0], (2,348))
    surf.blit(DATA.images["angelmpnoorb.png"][0], (544,348))

    # LEVEL
    lsurf = FONTS[13].render(str(PLAYER.level), 1, (255,255,255))
    lrect = lsurf.get_rect()
    lrect.center = (300, 414)
    surf.blit(lsurf, lrect)
    # TIME
    tsurf = FONTS[13].render(str(Time_Played/60).zfill(2)+":"+str(Time_Played%60).zfill(2), 1, (255,255,255))
    trect = tsurf.get_rect()
    trect.center = (300, 458)
    surf.blit(tsurf, trect)
    # HEALTH
    hsurf = FONTS[13].render(str(PLAYER.hp[0]), 1, (255,255,255))
    hrect = hsurf.get_rect()
    hrect.center = (227, 414)
    surf.blit(hsurf, hrect)
    # MANA
    msurf = FONTS[13].render(str(PLAYER.mp[0]), 1, (255,255,255))
    mrect = msurf.get_rect()
    mrect.center = (227, 434)
    surf.blit(msurf, mrect)
    # SILVER
    ssurf = FONTS[13].render(str(GAME.silver), 1, (255,255,255))
    srect = ssurf.get_rect()
    srect.center = (227, 459)
    surf.blit(ssurf, srect)

    # Name
    nsurf = FONTS[13].render(GAME.savefilename[:-4], 1, (255, 255, 255))
    if nsurf.get_width() > 120:
        nsurf = FONTS[13].render(GAME.savefilename[:6] + "...", 1, (255, 255, 255))
    nrect = nsurf.get_rect()
    nrect.center = (404, 414)
    surf.blit(nsurf, nrect)

    # Weapon break time bar

    RELOADRECT = pygame.Rect((348, 426, 0, 18))
    RELOADRECT[2] = min((PLAYER.breaktime+PLAYER.mycombotime), 49)
    c = PLAYER.breaktime * 5 + 100
    if c > 255: c = 255
    if PLAYER.breaktime > PLAYER.combotime:
        surf.fill((c,c,c), RELOADRECT)
    else:
        if PLAYER.breaktime > 0:
            surf.fill((255,255,0), RELOADRECT)
        else:
            surf.fill((0,255,0), RELOADRECT)

    # Combo text
    csurf = FONTS[13].render("-".join(PLAYER.combo_string), 1, (255,255,255))
    crect = csurf.get_rect()
    crect.center = (370, 434)
    crect.center = (404, 458)
    surf.blit(csurf, crect)

    # Ailments

    ails = ["poisoned"]
    curails = [x for x in PLAYER.bits.keys() if PLAYER.isbit(x) and x in ails]

    space = 50.0 / (len(curails) + 1)

    xp = 1

    for ail in curails:
        asurf, arect = DATA.images["ailment_" + ail + ".png"]
        arect.midtop = (273 + int(space * xp), 425)
        surf.blit(asurf, arect)
        xp += 1

def status(msg):
    global FONTS, SCREEN
    smsg = FONTS[3].render(str(msg), 1, (255,255,255))
    SCREEN.blit(smsg, (0,0))
                
def blit_character(PLAYER, CAMERA_X, in_eq = False):
    # Uses PLAYER Character instance to blit in position.
    # if in_eq is true, then we are blitting in the equip menu.

    global SCREEN, PLAYERFRAMES, DATA, bbrect, PLAYERSURF
    global DIGSURF

    playerlower = 7

    pframedata = [DATA.pframes, DATA.pframes2][PLAYER.classtype]

    #Legs
    LIMG = pframedata[PLAYERFRAMES[PLAYER.animation][int(PLAYER.frame)%len(PLAYERFRAMES[PLAYER.animation])]]
    LIMGRECT = LIMG[1][1]
    LIMGTOBLIT = LIMG[1][0]
    #Torso
    TIMG = pframedata[PLAYERFRAMES[PLAYER.torso_animation][int(PLAYER.tframe)%len(PLAYERFRAMES[PLAYER.torso_animation])]]
    TIMGRECT = TIMG[0][1]
    TIMGTOBLIT = TIMG[0][0]

    PLAYERSURF.fill((255,0,255))
    PLAYERSURF.blit(LIMGTOBLIT, (180, 100))
    PLAYERSURF.blit(TIMGTOBLIT, (180-(TIMGRECT[2]-40)/2, 100))

    if (PLAYER.nomanaicon/10) % 2:
        PLAYERSURF.blit(DATA.images["manaicon.png"][0], (190, 80))

    for wkey in PLAYER.wearing.keys():
        tf = ["Weapon", "Head", "Torso"]
        item = PLAYER.wearing[wkey]
        if wkey == "Accessories": continue
        if item:
            if item[0] and wkey not in tf:
                prefix = item[1]
                cf = int(PLAYER.frame)%len(PLAYERFRAMES[PLAYER.animation])
                frameinfo = item[2][PLAYER.animation][cf%len(item[2][PLAYER.animation])]
                surf = DATA.images[prefix + frameinfo[0] + ".png"][0]
                surf = pygame.transform.rotate(surf, frameinfo[3])
                PLAYERSURF.blit(surf, (180 + frameinfo[1], 100 + frameinfo[2]))
            elif item[0] and wkey in tf:
                # Difference: weapon/head overlays go by torso frame
                prefix = item[1]
                cf = int(PLAYER.tframe)%len(PLAYERFRAMES[PLAYER.torso_animation])
                frameinfo = item[2][PLAYER.torso_animation][cf%len(item[2][PLAYER.torso_animation])]
                surf = DATA.images[prefix + frameinfo[0] + ".png"][0]
                surf = pygame.transform.rotate(surf, frameinfo[3])
                PLAYERSURF.blit(surf, (180 + frameinfo[1], 100 + frameinfo[2]))

    if not PLAYER.direction:
        PLAYERSURF = pygame.transform.flip(PLAYERSURF, True, False)
    
    Blit_X = int(round((PLAYER.x - CAMERA_X) - TIMGRECT[2] / 2))
    Blit_Y = int(round(PLAYER.y - TIMGRECT[3] + 1))

    flimg, flrect = DATA.images["Magic_Flare.png"]
    flrect.center = (Blit_X+18, Blit_Y+52)

    if PLAYER.suddendeath:
        if PLAYER.classtype:
            if PLAYER.direction:
                PLAYERSURF.blit(DATA.images["halo.png"][0], (195, 80))
            else:
                PLAYERSURF.blit(DATA.images["halo.png"][0], (188, 80))
        else:
            PLAYERSURF.blit(DATA.images["halo.png"][0], (190, 80))

    makeupx = (TIMGRECT[2]-40)/2
    SCREEN.blit(PLAYERSURF, (Blit_X - 180 + makeupx, Blit_Y - 100 + playerlower))
    if PLAYER.flare > 0:
        scover = pygame.Surface((flrect[2],flrect[3]))
        scover.blit(SCREEN, (0,0), flrect)
        SCREEN.blit(flimg, flrect)
        PLAYER.flare -= 20
        if PLAYER.flare < 0: PLAYER.flare = 0
        scover.set_alpha(255-PLAYER.flare)
        SCREEN.blit(scover, flrect)

    if len(PLAYER.numbers) > 0:
        for number in PLAYER.numbers:
            curative = number[0]
            ntype = number[1]
            digits = number[2:]
            if sum([int(x[0]) for x in digits]) == 0: continue
            cd = 1
            DIGSURF.fill((255,0,255))
            for digit in digits:
                digpair = DATA.images[digit[0] + ntype  + ".png"]
                dr = digpair[1]
                rs = 18*len(digits)
                bx = 100 -(rs-40)/2 + int((float(rs)/(len(digits)+1)) * cd) - dr[2]/2
                bounce = 500.0/(digit[1]+5)
                if digit[1] > 32: bounce = 0
                if not curative:
                    by = 60 - abs(int((math.sin(digit[1]/5.0)*bounce)))
                else:
                    by = 60 - digit[1]/2.0
                DIGSURF.blit(digpair[0], (bx, by))
                cd += 1
            dsa = 340-digit[1]*4
            if dsa > 255: dsa = 255
            DIGSURF.set_alpha(dsa)

            nx = PLAYERSURF.get_rect()[2]/2+Blit_X - 300 + makeupx
            SCREEN.blit(DIGSURF, (nx,Blit_Y-65))

    PLAYER.Advance_Numbers()

    bbrect = pygame.Rect(Blit_X, Blit_Y, 40, 80)

def Make_CL_Surface(surf):
    global LEVEL, DATA, CL_Surface

    for x in range(len(LEVEL.map)):
        for y in range(12):
            ct = LEVEL.map[x][y]
            if ct:
                CTRECT = DATA.images[LEVEL.tiledef[ct.type]][1]
                TX = (x * 40) - (CTRECT[2]-40) / 2
                TY = y * 40 - CTRECT[3] + 40
                surf.blit(DATA.images[LEVEL.tiledef[ct.type]][0], (TX, TY))

    CL_Surface = surf
#    CL_Surface.set_colorkey((255,0,255))

def blit_map_at(CAMERA_X):
    # Blits the map of LEVEL onto the screen, using CAMERA_X to decide what
    # tiles to blit and where.

    global LEVEL, SCREEN, DATA

    global CL_Surface

    SCREEN.blit(CL_Surface, (0,0), Rect(CAMERA_X, 0, 640,480))

class Hourglass:
    def __init__(self, ttime):
        global DATA
        self.ttime = ttime
        self.real_angle = 360
        self.angle = 360
        self.pic, self.rect = DATA.images["hourglass.png"]
        self.tick()
    def update(self, percent):
        self.angle = percent * 3.6
    def tick(self):
        self.real_angle = (self.real_angle * self.ttime + self.angle)/float(self.ttime+1)
        if self.real_angle < 0.01: self.real_angle = 0
        self.image = pygame.transform.rotate(self.pic, self.real_angle)
        self.rect = self.image.get_rect()

class PicViewer:
    def __init__(self):
        self.x = 10
        self.y = 10
        self.pics = []
    def blit(self, screen):
        global DATA
        sbit = pygame.Surface((130,130))
        for x in range(len(self.pics)):
            img, alpha = self.pics[x]
            slide = ((255 - min(255, alpha))/255.0 * 20) ** 1.65
            sbit.blit(screen, (int(-self.x+slide), -self.y))
            screen.blit(pygame.transform.scale(DATA.images[img][0], (int(100-slide/2), int(100-slide/2))), (int(self.x-slide), self.y))
            sbit.set_alpha(max(0, 255-alpha))
            screen.blit(sbit, (int(self.x-slide), self.y))
            self.pics[x][1] -= 2

        self.pics = [xp for xp in self.pics if xp[1] > 0]
            

class NoticeViewer:
    def __init__(self, font):
        self.notices = []
        self.font = font
        self.extra = 0
        self.mas = math.asin(0.92)*15
    def blit_tick(self, surf):
        global DATA
        y = 0
        for noticeinfo in self.notices:
            notice, stage, realstage = noticeinfo
            pre_x = 640-(math.sin(stage/15.0)*300)
            surf.blit(DATA.images["notice.png"][0], (pre_x-10,y*30+self.extra))
            name_s = self.font.render(notice, 1, (0,0,0))
            name_sw = self.font.render(notice, 1, (255,255,255))
            name_r = name_s.get_rect()
            for x in range(-1,1):
                for z in range(-1,1):
                    name_r.midleft = (pre_x+x,15+y*30+z+self.extra)
                    surf.blit(name_s, name_r)
            name_r.midleft = (pre_x,15+y*30+self.extra)
            surf.blit(name_sw, name_r)

            y += 1

        self.extra *= 0.9

        for x in range(len(self.notices)):
            mssn = math.sin(self.notices[x][1]/15.0)
            if mssn < 0.92 or self.notices[x][2] > 300:
                self.notices[x][1] += 1
            if mssn >= 0.92 and self.notices[x][2] <= 300:
                self.notices[x][1] = self.mas
            self.notices[x][2] += 1
            if mssn < 0:
                self.notices[x] = None

        while None in self.notices:
            self.notices.remove(None)
            self.extra += 30

    def add(self, notice):
        self.notices.append([notice, 0, 0])

class Orb:
    def __init__(self, orbtype, x, y, value = 0):
        self.type = orbtype
        self.x = x
        self.y = y
        self.value = value
        self.ticker = int(random.randint(0, int(3.141*300))/10.0)
        self.reachpoint = 0
        self.removeme = False
        self.inertia = [0,0]
        self.gravitational = False

        if self.type == "Health":
            r = min(value * 2, 100)
            self.image = pygame.transform.scale(DATA.images["ORB_Health.png"][0], (10+r,10+r))
            self.rect = self.image.get_rect()
            self.reachpoint = 700
            self.inertia[0] = random.randint(-90,90)/10.0
            self.inertia[1] = random.randint(-20,20)/10.0

        if self.type == "Mana":
            r = min(value * 2, 100)
            self.image = pygame.transform.scale(DATA.images["ORB_Mana.png"][0], (10+r,10+r))
            self.rect = self.image.get_rect()
            self.reachpoint = 700
            self.inertia[0] = random.randint(-90,90)/10.0
            self.inertia[1] = random.randint(-20,20)/10.0

    def tick(self, Player = None):
        global SOUNDBOX, HPGLOBELIGHT, MPGLOBELIGHT
        self.ticker += 1
        self.x += self.inertia[0]
        self.inertia[0] *= 0.9
        self.y += self.inertia[1]
        self.inertia[1] *= 0.9

#        if self.type == "Health": self.gravitational = Player.hp[0] < Player.hp[1]
#        if self.type == "Mana": self.gravitational = Player.mp[0] < Player.mp[1]
        if self.type == "Health": self.gravitational = True
        if self.type == "Mana": self.gravitational = True


        if Player != None:
            if (self.type == "Health" or self.type == "Mana") and self.gravitational:
                self.y = ((Player.y-40) + self.y*10)/11.0
            dist = abs(Player.x - self.x)
            if dist < self.reachpoint and self.gravitational:
                power = (dist/18.0)+7
                if power > dist: power = dist
                if Player.x > self.x:
                    self.x += power
                else:
                    self.x -= power

            dist = abs(Player.x - self.x)

            if dist < 10 and abs(self.y -(Player.y-40))<30 and self.gravitational:
                SOUNDBOX.PlaySound("orb.ogg")
                self.removeme = True
                if self.type == "Health":
                    Player.Take_Damage(-self.value)
                    HPGLOBELIGHT = 255
                elif self.type == "Mana":
                    Player.mp[0] += self.value
                    MPGLOBELIGHT = 255
                    if Player.mp[0] > Player.mp[1]:
                        Player.mp[0] = Player.mp[1]

        self.rect.center = (self.x, self.y + math.sin(self.ticker/30.0) * 10)

    def blit(self, frame, ALT_X = 0, ALT_Y = 0):

        self.rect.move_ip(ALT_X, ALT_Y)
        if self.rect.right < 0 or self.rect.left > 640: return

        frame.blit(self.image, self.rect)

class FaceViewer:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alpha = 0
        self.maxalpha = 210
        self.facesurf = pygame.Surface((80,120))
        self.facesurf.fill((255,0,255))
        self.facesurf.set_colorkey((255,0,255))
        self.alphastep = 0
        self.hp = [1,1]
        self.name = "?????"
        self.wait_tick = 0
        self.vhp = -10 # Viewed HP
        self.bordersurf = pygame.Surface((82,82))
        self.bordersurf.fill((255,0,255), self.bordersurf.get_rect().inflate(-2,-2))
        self.bordersurf.set_colorkey((255,0,255))
        self.target = None
        self.btick = 0
        self.lockedon = False

        self.shakesurf = pygame.Surface((82,120))
        self.shakesurf.set_colorkey((255,0,255))
        self.shakesurf.fill((255,0,255))

        self.shake = 0
        self.monobj = None
    def update_name(self, name):
        self.name = name
    def update_maxhp(self, hp):
        self.hp[1] = hp
        if self.vhp == -10: self.vhp = hp
    def update_curhp(self, hp):
        if hp < 0: hp = 0
        self.hp[0] = hp
    def appear(self, image, monnew = None, damage = 0):
        if monnew != self.target: self.vhp = self.hp[0]
        if damage > self.hp[1]: damage = self.hp[1]
        self.facesurf.blit(image, (0,0))
        self.alphastep = 16
        self.wait_tick = 0
        self.shake = [-1,1,-1,1][random.randint(0,3)] * (damage/float(self.hp[1])) * 50
        if monnew: self.monobj = monnew
    def disappear(self):
        self.alphastep = -2
    def tick(self):
        if self.monobj:
            self.hp[0] = self.monobj.hp

        if not self.target:
            self.lockedon = False
        self.wait_tick += 1
        self.alpha += self.alphastep
        if self.alpha > self.maxalpha: self.alpha = self.maxalpha; self.alphastep = 0
        if self.alpha < 0: self.alpha = 0; self.alphastep = 0

        if self.wait_tick >= 300 and self.alpha > 0: self.disappear()

        self.vhp = (self.hp[0] + 8 * self.vhp)/9.0
    def blit(self, canvas):
        global FONTS, G_OPTIONS, CAMERA_X, DATA, vpos, PLAYER
        self.btick += 1
        self.lockedon = False

        if self.target and self.target.BOSS:
            canvas.blit(DATA.images[self.target.BOSSFACE][0], (2, 2))
            fhprect = Rect(0, 0, 200, 15)
            hprect = Rect(0, 0, 200 * self.target.hp / float(self.target.maxhp), 15)
            fhprect.topleft = (84, 2)
            hprect.topleft = (84, 2)
            canvas.fill((100, 20, 2), fhprect)
            canvas.fill((200, 40, 10), hprect)

        if PLAYER.wearing["Weapon"][3].bow:
            if self.target: self.alpha = self.maxalpha
            if not self.target or ((self.target.x > PLAYER.x and PLAYER.direction == 0) or (self.target.x < PLAYER.x and PLAYER.direction == 1)):
                global Monsters
                if PLAYER.direction == 0:
                    posmons = [mon for mon in Monsters if mon.x < PLAYER.x and not mon.isdead and abs(mon.x-PLAYER.x) < 500]
                else:
                    posmons = [mon for mon in Monsters if mon.x > PLAYER.x and not mon.isdead and abs(mon.x-PLAYER.x) < 500]

                if posmons:
                    self.target = reduce(lambda x, y: [x, y][abs(PLAYER.x-y.x) < abs(PLAYER.x-x.x)], posmons)
                    FACE_VIEW.update_curhp(self.target.hp)
                    FACE_VIEW.update_maxhp(self.target.maxhp)
                    self.vhp = self.hp[0]
                    if not self.target.isdead:
                        FACE_VIEW.update_name(self.target.presentable_name)
                    self.appear(DATA.mimages[self.target.name]["face.png"][0], self.target)

        if self.alpha == 0: return

        if self.target:
            targetpic = "target.png"
            if PLAYER.wearing["Weapon"][3].bow:
                tgy = self.target.y - self.target.collision_hdist/2
                tgx = self.target.x
                if tgx != PLAYER.x:
                    theta = math.degrees(math.atan((tgy-(PLAYER.y-40))/(tgx-PLAYER.x)))

                    if -50 < theta < 50 and ((PLAYER.direction == 1 and PLAYER.x < tgx) or (PLAYER.direction == 0 and PLAYER.x > tgx)):
                        targetpic = "target2.png"
                        self.lockedon = True
                
            if self.target.isdead: self.target = None
            else:
                ts, tr = DATA.images[targetpic]
                ts = pygame.transform.rotate(ts, self.btick*3)
                tr = ts.get_rect()
                tr.center = (self.target.x - CAMERA_X, self.target.y - vpos - self.target.collision_hdist/2)
                canvas.blit(ts, tr)

        alo255 = int((self.alpha/float(self.maxalpha))*255)
        c1, c2, c3 = alo255, alo255, alo255
        if self.name.endswith("Exp."): c1 = 0; c3 = 0
        namesurf = FONTS[15].render(self.name, 1, (c1,c2,c3))
        namerect = namesurf.get_rect()
        namerect.center = (40, 97)

        namebitrect = pygame.Rect(40 - alo255 * (40/255.0), 88, alo255 * (80/255.0), 20)
        nameleftrect = pygame.Rect(0, 88, 40 - alo255 * (40/255.0), 20)
        namerightrect = pygame.Rect(40 + alo255*(40/255.0)-1, 88, 40 - alo255 * (40/255.0)+2, 20)
        namemaskrect = pygame.Rect(40 - alo255 * (40/255.0), 0, alo255 * (80/255.0), 20)
        self.facesurf.fill((0,0,0), namebitrect)
        self.facesurf.fill((25,25,25), namebitrect.inflate(-4,-4))

        hprect = pygame.Rect(0, 110, 80, 10)
        self.facesurf.fill((0,0,0), hprect)
        self.facesurf.fill((75,0,0), hprect.inflate(-2,-2))

        if self.vhp < 0: self.vhp = 0
        if self.vhp > self.hp[1]: self.vhp = self.hp[1]

        hps = self.vhp / float(self.hp[1]) * 255
        hpbs = self.vhp / float(self.hp[1]) * 78
        
        self.facesurf.fill((255-hps,hps,0), pygame.Rect(1,111, hpbs, 8))
        
        self.facesurf.blit(namesurf, namerect)

        self.facesurf.fill((255,0,255), nameleftrect)
        self.facesurf.fill((255,0,255), namerightrect)
        self.shakesurf.fill((255,0,255))


        self.bordersurf.fill((0,0,0))
        self.bordersurf.fill((255,0,255), self.bordersurf.get_rect().inflate(-2,-2))

        self.shakesurf.blit(self.bordersurf, (0,0))
        self.shakesurf.blit(self.facesurf, (1,1))

        oldcenter = self.shakesurf.get_rect().move(self.x-1, self.y-1)
        oldcenter = oldcenter.center
        
        if G_OPTIONS["Shake battle window"]:
            rotsurf = pygame.transform.rotate(self.shakesurf, self.shake)
        else:
            rotsurf = self.shakesurf
        rotrect = rotsurf.get_rect()
        rotrect.center = oldcenter
        rotsurf.set_alpha(self.alpha)
        canvas.blit(rotsurf, rotrect)

        self.shake *= 0.8

class Particle:
    def __init__(self, x, y, ptype):
        self.x = x
        self.y = y
        self.type = ptype
        self.colour = (255,0,255)
        self.colour2 = (255,0,255)
        self.inertia = [0,0]
        self.lifespan = 0
        self.lifetime = 0
        self.removeme = False
        self.size = 1

        # Custom initialisations

        if ptype == "PART_NOMANA":
            s = random.randint(50, 120)/100.0
            self.colour = (int(30 * s), int(10 * s), int(200 * s))
            self.size = 2
            self.lifespan = 30
            self.inertia[0] = random.randint(-4, 4)
            self.inertia[1] = random.randint(-8, -2)

        if ptype == "PART_SPARK":
            b = random.randint(50,100)/100.0
            self.colour = (int(255*b),int(200*b),int(70*b))
            self.inertia[1] = random.randint(-4,0)
            self.inertia[0] = random.randint(-5,5)
            self.lifespan = 60
            self.size = random.randint(1,5)

        if ptype == "PART_CRITICAL":
            b = random.randint(50,100)/100.0
            c = random.randint(180,255)
            self.colour = [(c,c,c), (int(255*b),int(200*b),int(70*b))][random.randint(0,1)]
            self.size = random.randint(2,4)
            self.angle = random.randint(0,62830)/10000.0
            self.lifespan = 40

        if ptype == "PART_BUBBLE":
            b = random.randint(40,100)/100.0
            self.colour = (int(b*120),int(b*216),int(b*252))
            self.size = random.randint(1,4)
            self.inertia[0] = random.randint(-8,8)
            self.inertia[1] = random.randint(-2,4)
            self.lifespan = 70

        if ptype == "PART_SPLASH":
            b = random.randint(60,100)/100.0
            self.colour = (int(b*120),int(b*216),int(b*252))
            self.size = 1
            self.inertia[0] = random.randint(-8,8)
            self.inertia[1] = random.randint(-9,-1)
            self.lifespan = 10

        if ptype == "PART_HIT":
            c = random.randint(50,255)
            self.colour = (c,c,c)
            self.size = 1
            self.inertia[0] = random.randint(-10,10)
            self.inertia[1] = random.randint(-6,2)
            self.lifespan = 25

        if ptype == "PART_LEVELUP":
            v = random.randint(300,1100)/1000.0
            self.colour = (int(230*v), int(200*v), int(75*v))
            self.size = random.randint(2,4)
            self.lifespan = 45
            self.inertia[0] = random.randint(-350,350)/100.0
            self.inertia[1] = random.randint(-80,0)/10.0
            self.y -= random.randint(0,400)/10.0
       

        self.image = pygame.Surface((int(self.size*3), int(self.size*3)))
        self.image.set_colorkey((255,0,255))
        self.image.fill((255,0,255))
            
    def tick(self):
        global PLAYER
        self.lifetime += 1
        if self.lifespan != None and self.lifespan <= self.lifetime:
            self.removeme = True

        if self.type == "PART_SPARK":
            self.inertia[1] += 0.2
            self.y += self.inertia[1]
            self.x += self.inertia[0]
        elif self.type == "PART_NOMANA":
            self.inertia[1] += 0.6
            self.y += self.inertia[1]
            self.x += self.inertia[0]
        elif self.type == "PART_CRITICAL":
            self.x += 10 * math.cos(self.angle)
            self.y += 10 * math.sin(self.angle)
            self.inertia[1] += 0.7
            self.y += self.inertia[1]
        elif self.type == "PART_BUBBLE":
            self.y += self.inertia[1]
            self.x += self.inertia[0]
            self.inertia[0] = self.inertia[0]*0.95
            self.inertia[1] -= 0.2
        elif self.type == "PART_SPLASH":
            self.y += self.inertia[1]
            self.x += self.inertia[0]
            self.inertia[1] += 0.8
        elif self.type == "PART_HIT":
            self.y += self.inertia[1]
            self.x += self.inertia[0]
            self.inertia[1] += 0.8
        elif self.type == "PART_LEVELUP":
            self.y -= self.inertia[1]
            self.inertia[1] += 0.4
            self.x += self.inertia[0]
            self.x += PLAYER.inertia[0]

    def blit(self, frame, ALT_X = 0, ALT_Y = 0):

        if self.x+ALT_X < -5 or self.x+ALT_X > 645 or self.y+ALT_Y < -5 or self.y+ALT_Y > 485:
            self.removeme = True

        # Above statement removes particles that have moved past edges of screen

        mid = int(round((self.image.get_width()-1) / 2.0))
        if self.type != "PART_SPLASH":
            pygame.draw.circle(self.image, self.colour, (mid, mid), self.size, 0)
        else:
            self.image.set_at((mid,mid), self.colour)
        sir = self.image.get_rect()
        sir.center = (self.x, self.y)
        sir.move_ip(ALT_X,ALT_Y)

        if sir.left > 640 or sir.right < 0: return

        ao255 = ( self.lifetime / float(self.lifespan) ) * 255
        self.image.set_alpha(255 - ao255)
        
        frame.blit(self.image, sir)

class Arrow:
    def __init__(self, x, y, d, a, dm, endloc = None, hcd = 0):
        self.x = x
        self.y = y
        self.d = d
        self.a = a
        self.broken = False
        self.r = 0
        self.g = 0
        self.remove = False
        self.dmg = dm
        if endloc is not None:
            yd = endloc[1] - self.y # How much i need to go down
            xd = abs(endloc[0] - self.x) # How far away it is
            xd -= hcd/2 # Because in reality, it hits the side of it. This will bring the arrow's flight path up.
            steps = xd/3.0 # How many steps are required to get there
            self.dy = yd/steps
            self.r = -math.degrees(math.atan(yd/xd))
        else:
            self.dy = 0
    def tick(self):
        if self.broken:
            # Broken flight
            self.r += 1

            if self.d:
                self.x -= 0.3
            else:
                self.x += 0.3

            self.y += self.g
            self.g += 0.03

        else:
            # Straight/angled flight
            self.y += self.dy
            if self.d:
                self.x += 3
            else:
                self.x -= 3
        if self.y >= 480 or self.x <= 0 or self.x >= (128*40 - 1):
            self.remove = True
            self.y = min(self.y, 480)
            self.x = max(self.x, 0)
            self.x = min(self.x, 128*40-1)

class Character:
    def __init__(self):
        # Core and Platform Elements
        self.relics = 0
        self.suddendeath = True
        self.speedrecord = 0
        self.iwin = False
        self.nomanaicon = 0
        self.quaking = False
        self.bgquake = False
        self.chainmove = [None, None]
        self.bound = -1000
        self.stepc = 0
        self.groundtype = "None"
        self.laststep = 0
        self.start = (20,440)
        self.casting = False
        self.shooting = False
        self.arrows = []
        self.animation = "Stopped"
        self.torso_animation = "Stopped"
        self.frame = 0
        self.tframe = 0
        self.ptframe = 0
        self.x = 20 # these are now replaced by start obj.; arbitrary value
        self.y = 440 # these are now replaced by start obj.; arbitrary value
        self.directions = [False, False]
        self.direction = 1
        self.cold = False
        self.maxspeed = 3
        self.speed = self.maxspeed
        self.acceleration = .8
        self.deceleration = 0.6
        self.air_fric = 0.6
        self.jump_strength = 7
        self.gravity = 0.9
        self.inertia = [0, 0]
        self.jumping = False
        self.in_air = False
        self.jump_able = False
        self.up_held = False
        self.down_held = False
        self.running = True
        self.on_ramp = False
        self.combo = 0
        self.dcombo = 0
        self.comboalpha = 0
        self.combodamage = 0
        self.dcombodamage = 0

        self.landedsound = True

        self.obelisk_save = None # [levelname, self object, monsters, objects, TC]
        self.obelisk_time = 9001 # Time of save

        self.looking = False
        self.vlook = [0, 0]
        self.hlook = [0, 0]

        self.bonus_air_jump = 5

        self.bonus_air = self.bonus_air_jump
        self.bonus_enabled = True
        self.bonus_tick = 0

        self.ignore_move = False

        # Graphics variables
        # self.numbers is a list of numbers to display above head, and
        # information about how they are to be displayed
        self.numbers = []
        self.GOTHIT = False
        self.flare = 0 # magic flare effect
        self.breath = [] # Cold breath

        # RPG Elements
        self.level = 1
        self.leveljustup = 0
        self.exp = 0
        self.quests = {}
                    # Each quest should have a value of a list, where the first value is Boolean to indicate
                    # if the quest is complete, then a string for the quest log, then any amount of variables
                    # for the quest to use.
        

        self.slayer = {}

        self.strength = [0, 0]
        self.endurance = [0, 0]
        self.magic = [0, 0]
        self.luck = [0, 0]

        self.bonuses = {}
        self.protection = 0

        self.hp = [0, 0]
        self.mp = [0, 0]

        self.wearing = {
            "Legs"        : [None, None, None, None],
            "Torso"       : [None, None, None, None],
            "Head"        : [None, None, None, None], # Name, Prefix, Framelist, ItemObj
            "Accessories" : [], # <item>, <item>, ...
            "Gloves"      : [None, None, None, None],
            "Boots"       : [None, None, None, None],
            "Weapon"      : [None, None, None, None],
                        }

        self.inventory = []

        self.classtype = 0 # A name independent variable of which character was chosen

        self.speedbonus = 0
        self.scale_vitals = False

        # Combo Elements

        self.combotime = 10 # Max. Frames between consecutive combo buttons
        self.mycombotime = 0
        self.combo_string = ""
        self.oldcombostr = "A non-blank string"
        self.lastmovelen = 1
        self.buttonbuffer = ""

        self.attackat = None, None, None
        self.p_attack = None
        self.p_asound = None

        self.slow_attack = False
        self.lunging = False
        self.magic_immobile = False

        self.md = 0

        self.breaktime = 0 # Frames to rest for next attack
        self.mbreaktime = 0 # Frames to rest for magic attack
        self.spells = [] # Active spells

        # Combos

        self.combo_list = [

            [
            ("1", "singleattack", 1),
            ("12", "lungeattack", 1),
            ("4", "magic_power", 1),
            ("45", "fire_1", 1),
            ("17", "uppercut", 2),
            ("15", "spinslash", 3),
            ("46", "fire_2", 4),
            ("41", "quake", 7),
            ],

            [
            ("1", "singleattack", 1),
            ("4", "magic_power", 1),
            ("44", "burst", 1),
            ("45", "ice_1", 1),
            ("43", "teleport", 3),
            ("46", "ice_2", 5),
            ("48", "implosion_1", 10),
            ("7", "summon", 12),
            ("71", "maea", 12),
            ]

            ]
        # NOTE in ardentryst.py, it selects the appropriate
        # sub-combo-list, warrior/mage, thats why there are two
        # combo lists, yet later on we iterate through it as if
        # going through individual moves (we move in a degree)

        # Name of moves
        self.movelist = {
            "singleattack": "Attack",
            "lungeattack": "Lunge",
            "uppercut": "Uppercut",
            "spinslash": "Spin-slash",
            "magic_power": "Focus Magic",
            "summon": "Focus Summon",
            "maea": "Summon Maea",
            "fire_1": "Fire",
            "fire_2": "Blaze",
            "burst": "Burst",
            "ice_1": "Ice",
            "teleport": "Teleport",
            "ice_2": "Frost",
            "implosion_1": "Implosion",
            "quake": "Quake",
            }

        # Animation statics

        self.SPEEDS = {
            "Stopped": 80,
            "Walking": 65,
            "Jumping": 30
            }

        self.WARRIOR_BASE = [15, 14, 8, 0]
        self.MAGE_BASE = [6, 13, 18, 0]

        # bits
        self.bits = dict.fromkeys(
            ["poisoned"],
            False
            )

        self.tags = [0] * 999
        # Tag information
        # 0 - Learning to Strafe: Pyralis
        # 1 - Learning to Look: Pyralis
        # 2 - Learning about mdrain
        # 3 - Obelisks
        # 4 - Levers
        # 5 - Timegems
        # 6 - Learning to Strafe: Nyx
        # 7 - Learning to Look: Nyx
        # 8 - Quest get: Nyx
        # 9 - Quest get: Pyralis

        # 10 - Killed Radkelu?

    def questsdone(self):
        d = 0
        for key in self.quests.keys():
            if self.quests[key][0]:
                d += 1
        return d

    def tagsettrue(self, tag):
        self.tags[tag] = True

    def breath_tick(self):
        global FRAMEMOD, SCREEN, CAMERA_X, DATA
        if not self.cold: return
        if (FRAMEMOD%130)-10 <= 0:
            d = (self.direction*2)-1
            h = [7,0][self.classtype] # Makes breath higher for Pyralis
            xd = [8,15][self.classtype] # Pyralis' breath comes from closer to the centre of his sprite
            self.breath.append([self.x+xd*d, self.y-45-h, d*(random.randint(80,180)/100.0), (random.randint(-40,40)/10.0), 5])
            self.breath.append([self.x+xd*d, self.y-45-h, d*(random.randint(80,180)/100.0), (random.randint(-40,40)/10.0), 5])
            self.breath.append([self.x+xd*d, self.y-45-h, d*(random.randint(80,180)/100.0), (random.randint(-40,40)/10.0), 5])

        for x in range(len(self.breath)):
            breath = self.breath[x]
            b, br = DATA.images["breath.png"]
            b = pygame.transform.scale(b, (int(breath[4]), int(breath[4])))
            br = b.get_rect()
            br.center = (int(breath[0])-CAMERA_X, int(breath[1]))
            screenbit = pygame.Surface(br.size)
            screenbit.blit(SCREEN, (0,0), br)
            screenbit.set_alpha(breath[4]*9)
            if breath[4] * 9 >= 255:
                self.breath[x] = None
                continue
            SCREEN.blit(b, br)
            SCREEN.blit(screenbit, br)
            self.breath[x][0] += breath[2]
            self.breath[x][1] -= (breath[3]/35.0)
            self.breath[x][3] += random.randint(-8,16)/8.0
            if self.breath[x][2] > 0:
                self.breath[x][2] -= 0.035
            elif self.breath[x][2] < 0:
                self.breath[x][2] += 0.035
            self.breath[x][4] += 0.5

        while None in self.breath:
            self.breath.remove(None)

    def statsfor(self, level):
        x = level - 1
        strength = 0
        endurance = 0
        magic = 0
        luck = 0
        if not self.classtype:
            # Warrior (Level 100: 255, 255, 180, 255)
            strength = int(self.WARRIOR_BASE[0] + x**1.193)
            endurance = int(self.WARRIOR_BASE[1] + x**1.194)
            magic = int(self.WARRIOR_BASE[2] + x**1.121)
            luck = int(self.WARRIOR_BASE[3] + x**1.206)
        else:
            # Mage (Level 100: 180, 255, 255, 255)
            strength = int(self.MAGE_BASE[0] + x**1.123)
            endurance = int(self.MAGE_BASE[1] + x**1.195)
            magic = int(self.MAGE_BASE[2] + x**1.19)
            luck = int(self.MAGE_BASE[3] + x**1.206)
        return strength, endurance, magic, luck

    def var_tick(self, mode):
        global Objects, GAME
        try:
            # Stop cheaters on Frosty Frolic
            if GAME.location == [3, 4] and Objects[3].state == 0 and PLAYER.x > 4220 and mode == 0:
                message_box("The gods do not like it when you try to cheat!")
                PLAYER.x = 4220
                PLAYER.inertia[0] = -1
                PLAYER.hp[0] = 0
        except:
            pass
        
        self.speedrecord = max(self.speedrecord, abs(int(40 * self.inertia[0])))
        for key in self.bits:
            if key[0] == "#":
                # Is an item-induced bit, therefore we must remove it in case the item has been removed.
                # It will be re-applied later in this function if it is still worn.
                self.bits[key] = False

        self.possible_level_up()

        while self.expfor(self.level) > self.exp:
            self.level -= 1

        self.strength[1], self.endurance[1], self.magic[1], self.luck[1] = self.statsfor(self.level)

        self.protection = 0

        self.endurance[0] = max(1, self.endurance[0])

        if self.scale_vitals and self.hp[0] and self.mp[0]:
            hpratio = self.hp[1]/float(self.hp[0])
            mpratio = self.mp[1]/float(self.mp[0])

        self.hp[1] = int(self.endurance[0]**1.4452)
        self.mp[1] = int(self.magic[0]**1.4452)

        if self.scale_vitals and self.hp[0] and self.mp[0]:
            self.hp[0] = int(self.hp[1] / hpratio)
            self.mp[0] = int(self.mp[1] / mpratio)
            self.scale_vitals = False

        self.hp[0] = min(self.hp[0], self.hp[1])
        self.mp[0] = min(self.mp[0], self.mp[1])

        bonuses = {
            "strength"  : 0,
            "endurance" : 0,
            "magic"     : 0,
            "luck"      : 0
            }

        for item in self.wearing["Accessories"]:
            tempitem = item_module.Item("")
            for att in dir(tempitem):
                if not hasattr(item, att):
                    setattr(item, att, getattr(tempitem, att))

            ub = item.usage_bonus
            if item.protection:
                self.protection += item.protection
            for key in ub.keys():
                bonuses[key] += ub[key]

            for bit in item.bits:
                if not self.isbit(bit):
                    self.bits[bit] = True

        for placeloc in ["Legs", "Torso", "Head", "Gloves", "Boots", "Weapon"]:
            item = self.wearing[placeloc][3]

            if not item: continue

            tempitem = item_module.Item("")
            for att in dir(tempitem):
                if not hasattr(item, att):
                    gia = getattr(tempitem, att)
                    setattr(item, att, gia)

            if item.protection:
                self.protection += item.protection
            ub = item.usage_bonus
            for key in ub.keys():
                bonuses[key] += ub[key]

            for bit in item.bits:
                if not self.isbit(bit):
                    self.bits[bit] = True


        # Strength
        self.strength[0] = self.strength[1] + bonuses["strength"]

        # Magic
        self.magic[0] = self.magic[1] + bonuses["magic"]

        # Endurance
        self.endurance[0] = self.endurance[1] + bonuses["endurance"]

        # Luck
        self.luck[0] = self.luck[1] + bonuses["luck"]
        self.bonuses = bonuses

    def isbit(self, bit):
        if self.bits.has_key(bit):
            return self.bits[bit]
        return False

    def expfor(self, l):
        return int((((l-1)*6)**2.7)/((l+0.00001)*2))

    def possible_level_up(self):
        global NOTICE_VIEW, lasttick
        if self.exp >= self.expfor(self.level+1):
            self.level += 1
            self.leveljustup = 100
            Particle_Spawn(self.x, self.y, "PART_LEVELUP", 80)
            NOTICE_VIEW.add("Congratulations! You levelled up!")
            self.scale_vitals = True
            Level_Up_Screen()
            lasttick = pygame.time.get_ticks()
            self.possible_level_up()

    def add_to_combo(self, button):
        if self.chainmove[0]: return
        if self.combotime > self.breaktime > 0: self.buttonbuffer = button
        if self.combotime > self.mbreaktime > 0: self.buttonbuffer = button
        if self.breaktime > 0: return
        if self.mbreaktime > 0: return
        self.combo_string += button
        self.lunging = False
        self.slow_attack = False
        for move in self.combo_list:
            if move[0].startswith(button):
                self.mycombotime = self.combotime
                break

    def do_combo(self):

        self.breaktime -= 1
        if self.breaktime < 0:
            self.breaktime = 0
            self.shooting = False
            if self.torso_animation == "Attack":
                self.torso_animation = "Stopped"
        self.mbreaktime -= 1
        if self.isbit("#haste1"):
            self.mbreaktime -= 0.6
        if self.mbreaktime < 0: self.mbreaktime = 0; self.casting = False

        if self.combo != 0: self.dcombo = self.combo; self.dcombodamage = self.combodamage
        self.comboalpha -= 5
        if self.comboalpha <= 0:
            self.comboalpha = 0
            self.combo = 0
            self.combodamage = 0

        # IF BREAKING (weapon rest), we cannot execute the next attack
        # Also, we don't want the combo timer running while
        # the attack is recovering, it's opportunity time
        # not absolute time. (hence, only tick when player CAN
        # execute the combo.)

        if self.breaktime == 0 and self.mbreaktime == 0:
            self.mycombotime -= 1
            if self.chainmove[1] > 0:
                self.chainmove[1] -= 1
            if self.chainmove[1] == 0:
                cm = self.chainmove[:]
                self.chainmove = [None, None]
                getattr(self, cm[0])()
            elif self.buttonbuffer:
                self.combo_string += self.buttonbuffer
                self.buttonbuffer = ""

        if self.mycombotime <= 0: self.combo_string = ""; self.lastmovelen = 1
        toexec = [None, None]
        
        combostr = self.combo_string
        if self.oldcombostr == combostr:
            return
        self.oldcombostr = combostr
        for move in self.combo_list:
            if move[2] > self.level: continue
            if combostr == move[0] and (len(move[0]) > toexec[1] or toexec[1] is None):
                toexec = [move[1], len(move[0])]

        
        if toexec[0]:
            execfunc = getattr(self, toexec[0])
            execfunc()
            self.lastmovelen = toexec[1]
            self.mycombotime = self.combotime
        else:
            self.combo_string = self.combo_string[self.lastmovelen:]
            self.lunging = False
            self.slow_attack = False

    def prep_attack(self, wrange, wdamagebase):
        self.md = self.wearing["Weapon"][3].magic_drain
        self.hitsound = self.wearing["Weapon"][3].hit_sound

        damage = wdamagebase * (random.randint(70,130)/100.0)
        if self.wearing["Weapon"][3].magic_drain:
            damage *= (self.magic[0] + self.strength[0])/2.0
        else:
            damage *= self.strength[0]
        damage = int(damage/10.0)
        critical = self.luck[0]>random.randint(0,300)
        if damage < 0: damage = 0
        self.p_attack = wrange, damage, critical

    def magic_power(self):
        global SOUNDBOX
        self.mbreaktime = 5
        SOUNDBOX.PlaySound("Magicpower.ogg")
        self.flare = 255

    def burst(self):
        global SOUNDBOX
        self.animation = "Stopped"
        self.torso_animation = "Cast"
        self.frame = 0
        self.tframe = 0
        self.casting = True
        self.spells.append(magic.Burst(self, self.x, self.y-40))
        SOUNDBOX.PlaySound("Burst.ogg")

    def summon(self):
        global SOUNDBOX
        self.spells.append(magic.Summon(self, self.x, self.y))

    def maea(self):
        global SOUNDBOX
        self.spells.append(magic.Summon_Maea(self, self.x, self.y))
        if not self.spells[-1].finished:
            SOUNDBOX.PlaySound("Maea.ogg")
        else:
            # No mana
            Particle_Spawn(self.x, self.y-40, "PART_NOMANA", 15)
            self.nomanaicon = 59

    def fire_1(self):
        global SOUNDBOX
        self.spells.append(magic.Fire_1(self, self.x, self.y-25))
        if not self.spells[-1].finished:
            SOUNDBOX.PlaySound("flame_whoosh.ogg")
        else:
            # No mana
            Particle_Spawn(self.x, self.y-40, "PART_NOMANA", 15)
            self.nomanaicon = 59

    def quake(self):
        global SOUNDBOX
        self.spells.append(magic.Quake(self, self.x, self.y-25))
        if not self.spells[-1].finished:
            SOUNDBOX.PlaySound("quake.ogg")
        else:
            # No mana
            Particle_Spawn(self.x, self.y-40, "PART_NOMANA", 15)
            self.nomanaicon = 59

    def ice_1(self):
        self.spells.append(magic.Ice_1(self, self.x, self.y))
        if self.spells[-1].cant:
            # No mana
            Particle_Spawn(self.x, self.y-40, "PART_NOMANA", 15)
            self.nomanaicon = 59
            
    def implosion_1(self):
        self.spells.append(magic.Implosion_1(self, self.x, self.y))
        if self.spells[-1].cant:
            # No mana
            Particle_Spawn(self.x, self.y-40, "PART_NOMANA", 15)
            self.nomanaicon = 59
            

    def ice_2(self):
        self.spells.append(magic.Ice_2(self, self.x, self.y))
        if self.spells[-1].cant:
            # No mana
            Particle_Spawn(self.x, self.y-40, "PART_NOMANA", 15)
            self.nomanaicon = 59

    def teleport(self):
        global SOUNDBOX, GAME
        if GAME.location in [[3, 4], [3, 10]]:
            message_box("That spell cannot be used here.")
            return
        if self.mp[0] < 10:
            # No mana
            Particle_Spawn(self.x, self.y-40, "PART_NOMANA", 15)
            self.nomanaicon = 59
            return
        self.mp[0] -= 10
        self.x, self.y = self.start
        self.torso_animation = "Cast"
        self.animation = "Stopped"
        self.frame, self.tframe = 0, 0
        self.casting = True
        SOUNDBOX.PlaySound("Burst.ogg")

    def fire_2(self):
        global SOUNDBOX
        self.spells.append(magic.Fire_2(self, self.x, self.y-25))
        if not self.spells[-1].finished:
            SOUNDBOX.PlaySound("flame_whoosh.ogg")
        if self.spells[-1].finished:
            # No mana
            Particle_Spawn(self.x, self.y-40, "PART_NOMANA", 15)
            self.nomanaicon = 59

    def singleattack(self):
        global SOUNDBOX
        if self.wearing["Weapon"][3].bow:
            # The weapon I'm using is a *EDIT: MAGIC* bow
            md = self.wearing["Weapon"][3].magic_drain
            if md <= self.mp[0]:
                self.breaktime = self.wearing["Weapon"][3].time
                self.shooting = True
                SOUNDBOX.PlaySound("magicbow.ogg")
                dmg = self.wearing["Weapon"][3].damage
                dmg *= random.randint(80,120)/100.0
                dmg *= self.magic[0]/20.0
                dmg = int(dmg)

                # Targeting System

                global FACE_VIEW
                if FACE_VIEW.lockedon and FACE_VIEW.target:
                    self.arrows.append(Arrow(self.x - 40 + self.direction*80, self.y-30, self.direction, self.wearing["Weapon"][3].arrow, dmg, (FACE_VIEW.target.x, FACE_VIEW.target.y - FACE_VIEW.target.collision_hdist/2), FACE_VIEW.target.collision_dist))
                else:
                    self.arrows.append(Arrow(self.x - 40 + self.direction*80, self.y-30, self.direction, self.wearing["Weapon"][3].arrow, dmg)) # Straight arrow
                self.mp[0] -= md
            else:
                # No mana
                Particle_Spawn(self.x, self.y-40, "PART_NOMANA", 15)
                self.nomanaicon = 59
            return
        self.breaktime = self.wearing["Weapon"][3].time
        self.tframe = 0
        self.ptframe = 0
        self.torso_animation = "Attack"
        self.attackat = "WeaponSwingHigh.ogg", 1, 3
        self.p_asound = True
        self.prep_attack((self.wearing["Weapon"][3].range,self.wearing["Weapon"][3].minrange), self.wearing["Weapon"][3].damage)

    def uppercut(self):
        self.breaktime = self.wearing["Weapon"][3].time*3
        self.tframe = 1
        self.ptframe = 1
        self.torso_animation = "Attack"
        self.attackat = "WeaponSwing.ogg", 2, 2
        self.inertia[0] *= 1.7
        if self.jump_able:
            self.inertia[1] -= 9
            self.y -= 24

        self.prep_attack((self.wearing["Weapon"][3].range, self.wearing["Weapon"][3].minrange), self.wearing["Weapon"][3].damage*3)

    def spinslash(self):
        self.ignore_move = True
        self.breaktime = self.wearing["Weapon"][3].time/2
        self.tframe = 3
        self.ptframe = 3
        self.torso_animation = "Attack"
        self.attackat = "WeaponSwing.ogg", 3, 3

        self.prep_attack((self.wearing["Weapon"][3].range, self.wearing["Weapon"][3].minrange), self.wearing["Weapon"][3].damage)
        self.chainmove = ["spinslash2", 1]

    def spinslash2(self):
        self.direction = int(not self.direction)
        self.breaktime = self.wearing["Weapon"][3].time/2
        self.tframe = 3
        self.ptframe = 3
        self.torso_animation = "Attack"
        self.attackat = "WeaponSwing.ogg", 3, 3

        self.prep_attack((self.wearing["Weapon"][3].range, self.wearing["Weapon"][3].minrange), self.wearing["Weapon"][3].damage*1.1)
        self.chainmove = ["spinslash3", 1]
        
    def spinslash3(self):
        self.direction = int(not self.direction)
        self.breaktime = self.wearing["Weapon"][3].time/2
        self.tframe = 3
        self.ptframe = 3
        self.torso_animation = "Attack"
        self.attackat = "WeaponSwing.ogg", 3, 3

        self.prep_attack((self.wearing["Weapon"][3].range, self.wearing["Weapon"][3].minrange), self.wearing["Weapon"][3].damage*1.2)
        self.chainmove = ["spinslash4", 1]
        
    def spinslash4(self):
        self.direction = int(not self.direction)
        self.breaktime = self.wearing["Weapon"][3].time/2
        self.tframe = 3
        self.ptframe = 3
        self.torso_animation = "Attack"
        self.attackat = "WeaponSwing.ogg", 3, 3

        self.prep_attack((self.wearing["Weapon"][3].range, self.wearing["Weapon"][3].minrange), self.wearing["Weapon"][3].damage*1.3)
        self.ignore_move = False
        

    def lungeattack(self):
        self.breaktime = self.wearing["Weapon"][3].time * 1.5
        self.tframe = 3
        self.ptframe = 3
        self.torso_animation = "Attack"
        self.attackat = "WeaponSwing.ogg", 3, 3
        self.p_asound = True

        if abs(self.inertia[0]) > 0:
            self.inertia[0] = max(min(8, self.inertia[0] * (1+self.sense_friction())), -8)

        self.prep_attack((self.wearing["Weapon"][3].range,self.wearing["Weapon"][3].minrange),self.wearing["Weapon"][3].damage*(abs(self.inertia[0])+6)/6)

        self.slow_attack = True
        self.lunging = True

    def reset_for_new(self):
        self.suddendeath = True
        self.bits["poisoned"] = False
        self.bound = -1000
        self.iwin = False
        self.quaking = False
        self.bgquake = False
        self.chainmove = None, None
        self.stepc = 0
        self.laststep = 0
        self.landedsound = True
        self.cold = False
        self.casting = False
        self.shooting = False
        self.leveljustup = 0
        self.directions = [False, False]
        self.direction = 1
        self.animation = "Stopped"
        self.torso_animation = "Stopped"
        self.frame = 0
        self.tframe = 0
        self.ptframe = 0
        self.inertia = [0, 0]
        self.jumping = False
        self.in_air = False
        self.jump_able = True
        self.up_held = False
        self.running = True
        self.on_ramp = False
        self.flare = 0
        self.mycombotime = 0
        self.lastmovelen = 1
        self.bonus_air_jump = 5
        self.dcombo = 0
        self.dcombodamage = 0
        self.comboalpha = 0
        self.strafing = False
        self.breath = []

        self.looking = False
        self.vlook = [0, 0]
        self.hlook = [0, 0]

        self.bonus_air = self.bonus_air_jump
        self.bonus_enabled = True
        self.bonus_tick = 0
        self.numbers = []
        self.GOTHIT = False

        self.attackat = None, None, None
        self.p_attack = None
        self.p_asound = None

        self.slow_attack = False
        self.lunging = False
        self.magic_immobile = False

        self.md = 0

        self.breaktime = 0 # Frames to rest for next attack
        self.mbreaktime = 0 # Frames to rest for magic attack
        self.spells = [] # Active spells


    def Advance_Numbers(self):
        for i in range(len(self.numbers)):
            for j in range(len(self.numbers[i])):
                if j <= 1: continue
                self.numbers[i][j][1] += 1.5
                if self.numbers[i][j][1] >= 84:
                    self.numbers[i] = None
                    break

        while None in self.numbers:
            self.numbers.remove(None)

    def painsound(self, damage):
        global SOUNDBOX, A_OPTIONS        
        if max(0, int(round(damage))-self.protection):
            # i.e. it hurts
            if self.classtype:
                SOUNDBOX.PlaySound("NYX_PAIN" + str(random.randint(1, 10)) + ".ogg")
            else:
                SOUNDBOX.PlaySound("PYR_PAIN" + str(random.randint(1, 7)) + ".ogg")

    def raw_hit(self, damage):
        global PLAYDEMO
        self.painsound(damage)
        if not PLAYDEMO:
            self.Take_Damage(max(0, int(round(damage))-self.protection))

    def Take_Damage(self, damage, hiteffect = True, ntype = "b"):
        curative = False
        if damage < 0:
            curative = True

            ntype = "d"

        damage = [str(damage),str(damage)[1:]][curative]
        damage = str(int(round(float(damage))))

        if not curative:
            if int(damage) >= self.hp[0] and self.hp[0] > 1:
                if random.randint(0, 255) <= self.luck[0]:
                    damage = str(self.hp[0]-1)

        if not damage.isdigit():
            return

        num_info = [curative, ntype]

        phase = 0
        bounce_height = 40

        for digit in damage:
            num_info.append(
                [digit, phase, bounce_height]
                )
            phase += 1

        if not curative:
            self.numbers.append(num_info)
            self.hp[0] -= int(damage)
            if int(damage) > 0:
                self.GOTHIT = hiteffect
        else:
            self.hp[0] += int(damage)
            self.numbers.append(num_info)

        if self.hp[0] < 0: self.hp[0] = 0
        if self.hp[0] > self.hp[1]: self.hp[0] = self.hp[1]

    def Init_RPG_Elements(self, Distribution, Abilities):
        base = Distribution
        if self.classtype:
            self.MAGE_BASE = base[:]
        else:
            self.WARRIOR_BASE = base[:]
        self.strength = [base[0],base[0]]
        self.endurance = [base[1],base[1]]
        self.magic = [base[2],base[2]]
        self.luck = [base[3],base[3]]

        self.hp = [int(base[1]**1.4452)-10, int(base[1]**1.4452)]
        self.mp = [int(base[2]**1.4452)-10, int(base[2]**1.4452)]

        self.Abilities = Abilities

    def Init_Items(self, DATA, equipped, bagged):
        WOM = [7,8][self.classtype]
        for item in equipped:
            iteminfo = DATA.Itembox.ItemInfo(item)
            realitem = DATA.Itembox.GetItem(item)
            self.wearing[iteminfo[1]] = [item, iteminfo[6], iteminfo[WOM], realitem]

        for item in bagged:
            self.inventory.append(item)

    def animation_frame_tick(self):
        global SOUNDBOX

        if self.nomanaicon:
            self.nomanaicon -= 1
        
        if self.shooting:
            self.torso_animation = "Attack"
            self.animation = "Stopped"
            self.frame = 0
            self.tframe = 3
            return
        
        if self.animation == "Stopped":
            if not (self.directions[0] and self.directions[1]):
                self.frame += (self.SPEEDS["Stopped"]) / 1000.0
                if self.torso_animation == "Stopped":
                    self.tframe = self.frame
        if self.animation == "Walking":
            if not (self.directions[0] and self.directions[1]):
                timser = 1
                if self.directions[0] and self.direction or self.directions[1] and not self.direction:
                    timser = -1
                self.frame += timser * (abs(self.inertia[0]) * self.SPEEDS["Walking"]) / 1000.0
                if self.torso_animation == "Walking":
                    self.tframe = self.frame
        if self.animation == "Jumping":
            if not (self.directions[0] and self.directions[1]):
                self.frame += (abs(self.inertia[0]) * self.SPEEDS["Jumping"]) / 1000.0
                self.frame = 4
                if self.torso_animation == "Jumping":
                    self.tframe = self.frame
        if self.torso_animation == "Attack":
            wt = 0.4
            if self.slow_attack:
                self.ptframe += wt/4.0
            else:
                self.ptframe += wt

            self.tframe = min(3, self.ptframe)
            if self.ptframe >= self.wearing["Weapon"][3].time/4.0 and self.ptframe >= 4:
                self.torso_animation = self.animation
                self.slow_attack = False
                self.lunging = False
            if abs(self.attackat[1] - self.tframe) < wt*0.6:
                if self.p_asound:
                    SOUNDBOX.PlaySound(self.attackat[0])
                    self.p_asound = None
            if abs(self.attackat[2] - self.tframe) < wt*0.6 or self.lunging:
                if self.p_attack:
                    wrange, dmg, crit = self.p_attack
                    self.deal_damage(wrange, dmg, crit)
                    if not self.lunging:
                        self.p_attack = None

    def deal_damage(self, rng, dmg, crit):
        global LEVEL, TUTBOX, Monsters, FACE_VIEW, DATA, SOUNDBOX
        # rng = [max, min]
        Reactants = []
        for Monster in Monsters:
            if Monster.isdead or Monster.hp <= 0 or Monster.ghost: continue
            if abs(Monster.y - (self.y - 20)) < self.wearing["Weapon"][3].range*0.5 + Monster.collision_hdist/2 + 20:
                if self.direction:
                    if Monster.x+Monster.collision_dist >= self.x + rng[0] >= Monster.x-Monster.collision_dist \
                    or Monster.x+Monster.collision_dist >= self.x + rng[1] >= Monster.x-Monster.collision_dist \
                    or (self.x + rng[1] <= Monster.x-Monster.collision_dist and self.x + rng[0] >= Monster.x+Monster.collision_dist):
                        Reactants.append(Monster)
                else:
                    if Monster.x-Monster.collision_dist <= self.x - rng[0] <= Monster.x+Monster.collision_dist \
                    or Monster.x-Monster.collision_dist <= self.x - rng[1] <= Monster.x+Monster.collision_dist \
                    or (self.x - rng[1] >= Monster.x-Monster.collision_dist and self.x - rng[0] <= Monster.x+Monster.collision_dist):
                        Reactants.append(Monster)
        if Reactants:
            if self.md > self.mp[0]:
                dmg /= 2; crit = 0
            elif self.md > 0:
                self.mp[0] -= self.md
                SOUNDBOX.PlaySound("mdrain.ogg")
                if not PLAYER.tags[2]:
                    message_box("The magic sound your weapon makes indicates that it is drawing mana from you.")
                    PLAYER.tags[2] = 1
        self.md = 0

        for Reactant in Reactants:
            Particle_Spawn(Reactant.x, Reactant.y-30, "PART_HIT", 6)
            dodamage = int(dmg*[1,2][crit]*random.randint(75,125)*0.01)
            self.combodamage += min(dodamage, Reactant.hp)
            Reactant.react_to_damage(dodamage)
            self.combo += 1
            if Reactant.name == "pod":
                TUTBOX.playeraction("pod_hit")
                if Reactant.hp <= 0: TUTBOX.playeraction("pod_death")
            elif Reactant.name == "cspider":
                TUTBOX.playeraction("cspider_hit")
                if Reactant.hp <= 0: TUTBOX.playeraction("cspider_death")
                
            if crit:
                Particle_Spawn(Reactant.x, self.y - 40, "PART_CRITICAL", 15)

        if Reactants:
            self.comboalpha = 255
            self.inertia[0] *= 0.5
            self.lunging = False
            self.slow_attack = False
            if self.hitsound:
                SOUNDBOX.PlaySound(self.hitsound)
                self.hitsound = ""
            if Reactant.hp <= 0:
                if hasattr(Reactant, "reward_exp"):
                    if Reactant.reward_exp > 0:
                        FACE_VIEW.update_name("+"+str(Reactant.reward_exp)+" Exp.")
                        SOUNDBOX.PlaySound("ChimeGliss.ogg")
                        Particle_Spawn(self.x, self.y - 40, "PART_SPARK", 15)
                    FACE_VIEW.appear(DATA.mimages[Reactant.name]["face.png"][0], Reactant)
                    FACE_VIEW.target = Reactant

                if len(Reactants) == 1: return

##             for Reactant in Reactants:
##                 if Reactant.isdead:
##                     continue
            FACE_VIEW.appear(DATA.mimages[Reactant.name]["face.png"][0], Reactant, dmg*[1,2][crit])
            FACE_VIEW.update_curhp(Reactant.hp)
            FACE_VIEW.update_maxhp(Reactant.maxhp)
            FACE_VIEW.update_name(Reactant.presentable_name)
            FACE_VIEW.target = Reactant


    def animation_update_tick(self):
        global PLAYERFRAMES
        if self.ignore_move: return
        if self.in_air == True:
            self.animation = "Jumping"
            if self.torso_animation != "Attack":
                self.torso_animation = "Jumping"
        elif (self.directions[0] or self.directions[1] and self.in_air == False) and not self.casting:
            self.animation = "Walking"
            if self.torso_animation != "Attack":
                self.torso_animation = "Walking"
        elif (not self.in_air and not self.inertia[0]) and not self.casting:
            self.animation = "Stopped"
            if self.torso_animation != "Attack":
                self.torso_animation = "Stopped"
            self.frame %= len(PLAYERFRAMES["Stopped"])

    def arrow_tick(self):
        global SCREEN, DATA, CAMERA_X, LEVEL, Monsters

        
        for arrow in self.arrows:
            if arrow.x > CAMERA_X + 640 or arrow.x < CAMERA_X - 640:
                arrow.remove = True
            if arrow.y < 0 or arrow.y > 480:
                arrow.remove = True
            for x in range(10):
                arrow.tick()
                if arrow.remove: continue
                if not arrow.broken:
                    for monster in Monsters:
                        if abs(monster.x - arrow.x) < monster.collision_dist:
                            if abs(monster.y-30-arrow.y) < monster.collision_hdist:
                                dmg = arrow.dmg
                                self.combodamage += min(monster.hp, dmg)
                                monster.react_to_damage(dmg)
                                self.combo += 1
                                arrow.broken = True
                                self.comboalpha = 255
                                if monster.hp <= 0:
                                    if hasattr(monster, "reward_exp"):
                                        if monster.reward_exp > 0:
                                            FACE_VIEW.update_name("+"+str(monster.reward_exp)+" Exp.")
                                            SOUNDBOX.PlaySound("ChimeGliss.ogg")
                                            Particle_Spawn(self.x, self.y - 40, "PART_SPARK", 15)
                                        FACE_VIEW.appear(DATA.mimages[monster.name]["face.png"][0], monster)
                                        FACE_VIEW.target = monster
                                else:
                                    FACE_VIEW.appear(DATA.mimages[monster.name]["face.png"][0], monster, dmg)
                                    FACE_VIEW.update_curhp(monster.hp)
                                    FACE_VIEW.update_maxhp(monster.maxhp)
                                    FACE_VIEW.update_name(monster.presentable_name)
                                    FACE_VIEW.target = monster


                lm = LEVEL.map[int(arrow.x/40)][int(arrow.y/40)]
                if lm:
                    if lm.collidetype == "BOX" and not arrow.broken:
                        arrow.broken = True
                        arrow.g = -2
                    if "INCLINATION" in lm.collidetype and "RIGHT" in lm.collidetype and arrow.x%40 > 15 and not arrow.broken:
                        arrow.broken = True
                        arrow.g = -2
                    if "INCLINATION" in lm.collidetype and "LEFT" in lm.collidetype and arrow.x%40 < 25 and not arrow.broken:
                        arrow.broken = True
                        arrow.g = -2
                
            img, rect = DATA.images[arrow.a]
            img = pygame.transform.rotate(img, arrow.r)
            rect = img.get_rect()
            rect.center = (arrow.x-CAMERA_X, arrow.y)
            if arrow.d == 0: img = pygame.transform.flip(img, True, False)

            SCREEN.blit(img, rect)

        self.arrows = [x for x in self.arrows if not x.remove]

    def magic_tick(self):
        global LEVEL, SCREEN, CAMERA_X, Monsters, RAIN_HEAVINESS, SOUNDBOX
        for spell in self.spells:
            spell.tick(LEVEL, [x for x in Monsters if not x.ghost], self, RAIN_HEAVINESS)
            if spell.fvm:
                self.comboalpha = 255
                if spell.fvm.hp <= 0:
                    if spell.fvm.reward_exp > 0 and not spell.fvm.chimed:
                        FACE_VIEW.update_name("+"+str(spell.fvm.reward_exp)+" Exp.")
                        SOUNDBOX.PlaySound("ChimeGliss.ogg")
                        Particle_Spawn(self.x, self.y - 40, "PART_SPARK", 15)
                        spell.fvm.chimed = True
                    FACE_VIEW.appear(DATA.mimages[spell.fvm.name]["face.png"][0], spell.fvm)
                    FACE_VIEW.target = spell.fvm
                else:
                    FACE_VIEW.appear(DATA.mimages[spell.fvm.name]["face.png"][0], spell.fvm, spell.fvd)
                    FACE_VIEW.update_name(spell.fvm.presentable_name)
                    FACE_VIEW.update_curhp(spell.fvm.hp)
                    FACE_VIEW.update_maxhp(spell.fvm.maxhp)
                    FACE_VIEW.target = spell.fvm
                spell.fvd = 0
            if spell.SOUND:
                SOUNDBOX.PlaySound(spell.SOUND)
                spell.SOUND = ""
            spell.blit(SCREEN, -CAMERA_X)
            if spell.finished == True:
                self.spells[self.spells.index(spell)] = None
        while None in self.spells:
            self.spells.remove(None)

    def movement_run_tick(self):
        if self.y > 600: self.inertia[0] = 0
        if self.ignore_move: return
        # if going both ways.. do nothing!
        both = False
        if self.directions[0] and self.directions[1]:
            both = True

        # if casting a spell, or shooting, stay still
        if self.mbreaktime or self.shooting:
            both = True # a bit of a hack but oh well

        if self.x < 20: self.x = 20

        # if running, extend self.speed
        if self.running:
            self.speed = self.maxspeed * 1.6 + self.speedbonus
        # likewise, restrain it if not running
        else:
            self.speed = self.maxspeed

        # get direction

        if not self.strafing:
            if self.directions[0]: self.direction = 0
            if self.directions[1]: self.direction = 1
        
        # Alter inertia if I am holding down the key
        # Also check for walls before doing this

        floor_friction = self.sense_friction()
        if floor_friction == -1:
            affected_acceleration = self.acceleration * self.air_fric
            affected_deceleration = max(0, (abs(self.inertia[0])-6)/100.0)
        else:
            affected_acceleration = self.acceleration * floor_friction
            affected_deceleration = self.deceleration * floor_friction

        if not both:
            if self.directions[0] and not self.sense(self.inertia[0], -10):
                if self.inertia[0] > -self.speed:
                    self.inertia[0] -= affected_acceleration
            elif self.directions[1] and not self.sense(self.inertia[0], -10):
                if self.inertia[0] < self.speed:
                    self.inertia[0] += affected_acceleration

        if self.inertia[0] > self.speed:
            self.inertia[0] -= affected_deceleration
            if self.inertia[0] < self.speed:
                self.inertia[0] = self.speed
        elif self.inertia[0] < -self.speed:
            self.inertia[0] += affected_deceleration
            if self.inertia[0] > -self.speed:
                self.inertia[0] = -self.speed

        # Alter my X value so long as I don't hit anything

        if self.sense(self.inertia[0], -10):
            if self.inertia[0] < 0:
                temp_x = 0
                while True:
                    temp_x += 0.2
                    if not self.sense(self.inertia[0] + temp_x, -10):
                        self.x += (self.inertia[0] + temp_x)
                        break
            elif self.inertia[0] > 0:
                temp_x = 0
                while True:
                    temp_x += 0.2
                    if not self.sense(self.inertia[0] - temp_x, -10):
                        self.x += (self.inertia[0] - temp_x)
                        break
            self.inertia[0] = 0
        elif self.inertia[0]:
            self.x += self.inertia[0]

        # Using a deceleration that does not go evenly
        # into acceleration (including floating point round-offs
        # will cause a zig-zag stopping effect. This stops it.
        # (it also puts deceleration into effect)

        # If both arrows are held down, it allows the character to slow/stop
        # rather than be frozen, and rather than keep running. It's probably what
        # the player wants.

        if not self.directions[1] and self.inertia[0] > 0 or both and self.inertia[0] > 0:
            if self.inertia[0] < affected_deceleration:
                self.inertia[0] = 0
            else:
                if self.in_air:
                    self.inertia[0] -= (affected_deceleration/6.0)
                else:
                    self.inertia[0] -= affected_deceleration

        if not self.directions[0] and self.inertia[0] < 0 or both and self.inertia[0] < 0:
            if self.inertia[0] > -affected_deceleration:
                self.inertia[0] = 0
            else:
                if self.in_air:
                    self.inertia[0] += (affected_deceleration/6.0)
                else:
                    self.inertia[0] += affected_deceleration
        if self.x < 0:
            self.x = 0

        # Finally apply footstep sounds

        aniframe = int(self.frame % len(PLAYERFRAMES[self.animation]))

        if self.animation == "Walking"  and aniframe in [2, 6] and self.laststep != aniframe:
            try:
                if self.classtype:
                    SOUNDBOX.PlaySound("NYX_STEP_" + footstep_types[self.groundtype] + str(self.stepc+1) + ".ogg")
                else:
                    SOUNDBOX.PlaySound("PYR_STEP_" + footstep_types[self.groundtype] + str(self.stepc+1) + ".ogg")
                self.laststep = aniframe
                self.stepc += random.randint(1, 3)
                self.stepc %= 4
            except:
                # No such ground step sound
                pass

    def movement_jump_tick(self):
        global SOUNDBOX, A_OPTIONS
        if self.senseabove(): self.inertia[1] = max(0, self.inertia[1])

        # fall death handling
        if self.y > 550:
            self.y = 550
            self.hp[0] = 0
        
        if self.mbreaktime: return
        if self.up_held: self.bonus_tick += 1
        if self.jump_able:
            self.bonus_enabled = True
        if self.jumping or self.y - self.bound < 40:
            if self.jump_able or self.on_ramp:
                self.bound = -1000
                self.inertia[1] = -self.jump_strength
                self.jump_able = False
                self.in_air = True
                self.inertia[0] *= 1.25
                if self.classtype:
                    SOUNDBOX.PlaySound("NYX_JUMP" + str(random.randint(1, 6)) + ".ogg")
                else:
                    SOUNDBOX.PlaySound("PYR_JUMP" + str(random.randint(1, 5)) + ".ogg")
            elif not self.jump_able and self.bound == -1000 and self.inertia[1] > 0:
                self.bound = self.y
            self.jumping = False
            self.on_ramp = False
            self.landedsound = False
        self.y += self.inertia[1]
        if not self.jump_able and self.in_air and self.up_held and self.bonus_enabled:
            if self.bonus_tick > 1:
                self.inertia[1] -= self.bonus_air/4.0
                self.bonus_air /= 1.3
        else:
            self.bonus_air = self.bonus_air_jump
            self.bonus_enabled = False
            self.bonus_tick = 0

    def movement_fall_tick(self):
        global SOUNDBOX
        if self.y >= 479: self.on_ramp = False
        if self.on_ramp and not self.jumping:
            ga = ground_at(int(self.x))
            if abs(ga-self.y) < 30 and self.inertia[1] < 2:
                self.y = ga
                self.inertia[1] = 0
                self.jump_able = True
                self.in_air = False
                if not self.landedsound:
                    self.landedsound = True
                    if self.classtype:
                        SOUNDBOX.PlaySound("NYX_LAND" + str(random.randint(1, 3)) + ".ogg")
                    else:
                        SOUNDBOX.PlaySound("PYR_LAND" + str(random.randint(1, 4)) + ".ogg")
                self.bound = -1000
                # bounding is pressing jump before landing, 'buffering' a jump
        if not self.sensebelow(self.inertia[1]):
            self.y += self.inertia[1]
            self.inertia[1] += self.gravity
            if self.inertia[1] > 1:
                if not self.on_ramp:
                    self.in_air = True
                    self.jump_able = False
            if self.inertia[1] > 2 and self.on_ramp:
                self.on_ramp = False
                for x in range(30):
                    for y in range(20):
                        ss =  self.sense(str(5+x), y)
                        if type(ss) != bool:
                            if "INCLINATION" in ss.collidetype:
                                self.on_ramp = True
        else:
            temp_y = 0
            while temp_y < 480:
                temp_y += 0.5
                try:
                    sb = self.sensebelow(self.inertia[1] - temp_y)
                    if not sb:
                        self.y += (self.inertia[1] - temp_y)
                        break
                    elif type(sb) != bool:
                        if "INCLINATION" in sb.collidetype:
                            self.on_ramp = True
                        
                except Exception, e:
                    raise
            if self.inertia[1] > 13:
                # Impact of land
                self.inertia[0] /= (self.inertia[1]/3.0)
            if self.inertia[1] > 0:
                self.jump_able = True
                self.in_air = False
                self.inertia[1] = 0

    def senseabove(self):
        s1 = self.sense("10", -60)
        s2 = self.sense("30", -60)
        if s1 or s2:
            return True
        return False
            
    def sensebelow(self, y_rel):
        for y in range(20):#CHANGE from 5,8
            for x in range(0,23,3): #MIDCHANGE from 18
                s = self.sense(str(x+11), y_rel-y)
                if s:
                    if y > 0:
                        if type(s) != bool:
                            if "INCLINATION" in s.collidetype:
                                self.on_ramp = True
                                self.y -= y
                                return True
                            else:
                                self.on_ramp = False
                        else:
                            self.on_ramp = False
                    elif y == 0:
                        self.on_ramp = True
                        if type(s) != bool:
                            pass
                        else:
                            self.on_ramp = False
                        return True
#Downwards
        if self.in_air and self.on_ramp:
            for y in range(7):
                for x in range(1):
                    s = self.sense(str(33-x), y_rel+y)
                    if s:
                        if y > 0:
                            if type(s) != bool:
                                if "INCLINATION" in s.collidetype:
                                    self.in_air = False
                                    self.y += y
                                    return True
        return False

    def sense_friction(self):
        bl = self.sense("LEFTEDGE", 1)
        br = self.sense("RIGHTEDGE", 1)

        try:
            bl.friction = getalt_fric(bl.type)
        except:
            pass
        try:
            br.friction = getalt_fric(br.type)
        except:
            pass


        if not bl and not br:
            self.groundtype = "Air"
            return -1
        elif type(bl) != bool and type(br) != bool:
            self.groundtype = br.type
            if self.isbit("#grip"): return 2
            return (bl.friction + br.friction) / 2.0
        elif not bl:
            self.groundtype = br.type
            if self.isbit("#grip"): return 2
            return br.friction
        elif not br:
            self.groundtype = bl.type
            if self.isbit("#grip"): return 2
            return bl.friction
        else:
            self.groundtype = "Unknown"
            return 1

    def sense(self, x_rel, y_rel):
        global LEVEL

        if type(x_rel) == str:
            if x_rel.isdigit(): xedge = int(x_rel) - 20
            
            elif x_rel == "LEFTEDGE": xedge = -20
            elif x_rel == "RIGHTEDGE": xedge = 19
            elif x_rel == "LEFTEDGEIN": xedge = -7
            elif x_rel == "RIGHTEDGEIN": xedge = 6
            elif x_rel == "CENTER": xedge = -1

            x_rel = 0
        else:
            if x_rel < 0: xedge = -13
            elif x_rel > 0: xedge = 12
            else: xedge = 0

        abs_x = int(round(self.x + xedge + x_rel))
        abs_y = int(round(self.y + y_rel))
        if abs_x <= -2:
            return True
        if abs_y >= 480:
            return False
        looktile = LEVEL.map[abs_x/40][abs_y/40]
        if looktile:
            if looktile.collidetype == "RIGHT_INCLINATION":
                # is a 45 degree ramp with peak at right
                if abs_x%40 > 40-(abs_y%40):
                    return looktile
            if looktile.collidetype == "RIGHT_HINCLINATION1":
                # is a 22.5 degree ramp with half-peak at right
                if (abs_x%40) > 2*(40-(abs_y%40)):
                    return looktile
            if looktile.collidetype == "RIGHT_HINCLINATION2":
                # is a 22.5 degree ramp with peak at right
                if (abs_x%40)+40 > 2*(40-(abs_y%40)):
                    return looktile
            if looktile.collidetype == "LEFT_INCLINATION":
                # is a 45 degree ramp with peak at left
                if abs_x%40 < (abs_y%40):
                    return looktile
            if looktile.collidetype == "LEFT_HINCLINATION1":
                # is a 22.5 degree ramp with half-peak at left
                if (abs_x%40)+40 < 2*((abs_y%40)):
                    return looktile
            if looktile.collidetype == "LEFT_HINCLINATION2":
                # is a 22.5 degree ramp with peak at left
                if (abs_x%40) < 2*((abs_y%40)):
                    return looktile
            if looktile.collidetype == "BOX":
                return looktile

        return False

class NPC:
    def __init__(self):
        self.x = 0
        self.y = 0

        self.portrait = ["Nobody_Head.png"]
        self.name = "Nobody"

        self.message = "Hello, there."
        self.follow_player = False
        self.follow_player_fly = False

        self.tutorial = False

        self.impervious = False
        self.idirection = 0
        self.unfollow = True

        self.prefix = ""
        self.animations = {
            "Stopped": [""],
            "Walking": [""],
            "Jumping": [""]
            }

        self.still = True

        # "Animation name": ["frame", "frame2"]

        self.fall = 0
        self.animation = "Stopped"
        self.direction = 1 # 1 = right. 0 = left.
        self.frame = 0

        self.clock = 0

        self.talksounds = []

        # MISC. INTERACTION VARIABLES

        self.interactive = False
        self.action = ""
        self.first_proximity_message = ""

######                  ######
###     Object Classes     ###
######                  ######

# Required for each object:
# local variable _needinfo: True/False
# local variable _runtime: "All" or "InScreen"
# local variable _infront: Whether to blit in front of player
# local variable _activateable: Whether it can be activated
# function _activate(): what to do when activated
# function _inscreen(CX): return True/False
# function _giveinfo(player)
# function _poll(): return image to blit and absolute location
# function _tick(): what to do in one tick

# self.P_id: Public identification
# self.id: Intrinsic identification

class FallingRock:
    def __init__(self, tx, ty):
        self._needinfo = True
        self._runtime = "InScreen"
        self._infront = True
        self.id = "FallingRock"
        self.P_id = ""
        self._activateable = False

        self.x = tx * 40 + 20
        self.y = ty * 40 + 40
        self.ga = ground_at(self.x)
        if self.ga == 479: self.ga = 550
        self.inert = 0
        self.xinert = 0
        self.falling = False
        self.pstate = None
        self.hurt = False

        self.frame = "Rock.png"
    def _inscreen(self, CX):
        if CX - 100 <= self.x <= CX + 740:
            return True
        return False
    def _giveinfo(self, player):
        self.pstate = player
    def _poll(self):
        return self.frame, self.x-20, self.y - 20
    def _tick(self):
        global SOUNDBOX
        if abs(self.pstate.x - self.x) < 100:
            self.falling = True
        if self.falling:
            self.x += self.xinert
            self.inert += 0.55
            self.y += self.inert
            if self.y >= 530:
                self.y = 530
                return
            if self.y >= self.ga:
                self.y = self.ga
                self.inert *= -0.6
                self.xinert = random.randint(-10,10)/10.0
                self.ga = 530
                SOUNDBOX.PlaySound("Rock.ogg")

        if abs(self.x-self.pstate.x) < 18 and abs(self.y-(self.pstate.y-40))<30 and not self.hurt:
            self.hurt = True
            self.pstate.raw_hit(random.randint(6,12))

class StaticObj:
    def __init__(self, name, frame, tx, ty):
        self._needinfo = False
        self._runtime = "InScreen"
        self._infront = False
        self.id = name,
        self.P_id = ""
        self._activateable = False

        self.x = tx*40+20
        self.y = ty*40+20

        self.frame = frame

    def _inscreen(self, CX):
        if CX - 100 <= self.x <= CX + 740:
            return True
        return False
    def _poll(self):
        return self.frame, self.x-20, self.y - 20
    def _tick(self):
        pass

class Gas:
    def __init__(self, x, y):
        global DATA
        self.id = "Gas"
        self._needinfo = True
        self._runtime = "All"
        self._infront = True
        self._activateable = False
        self.x = x
        self.y = y
        self.gaspic = DATA.images["poisongas.png"][0]
        self.rect = self.gaspic.get_rect()
        self.xsize, self.ysize = self.rect.size
        self.ticker = 0
        self._alpha = 255
        self.pstate = None
        self.frame = pygame.Surface((0,0))

        self.poison = True
    
    def _giveinfo(self, player):
        self.pstate = player
    def _inscreen(self, CX):
        if CX - 100 <= self.x <= CX + 740: return True
        else: return False
    def _poll(self):
        self.rect = self.frame.get_rect()
        self.rect.center = (self.x, self.y)
        return self.frame, self.x, self.y, self.rect
    def _tick(self):
        self.ticker += 1
        self._alpha -= 5
        self.y -= 2
        gsize = (int(self.xsize * math.log(self.ticker) * 0.15), int(self.ysize * math.sin(self.ticker/50.0) * 1.5))
        self.frame = pygame.transform.scale(self.gaspic, gsize)

        if self._alpha <= 0:
            global Objects
            Objects = [x for x in Objects if x is not self]

        if self._alpha < 120:
            self.poison = False

        if self.poison and self.pstate.bits["poisoned"] == False:
            if abs(self.pstate.x - self.x) < gsize[0]/2 + 15:
                if abs((self.pstate.y-40) - self.y) < gsize[1]/2:
                    self.pstate.Take_Damage(1)
                    self.pstate.bits["poisoned"] = True
                    self.poison = False
        

class Walltorch:
    def __init__(self, tx, ty):
        self._needinfo = False
        self._runtime = "InScreen"
        self._infront = False
        self.id = "Walltorch",
        self.P_id = ""
        self._activateable = False

        self.x = tx*40+20
        self.y = ty*40+20

        self.frame = ["Walltorch.png", "Walltorch2.png", "Walltorch3.png", "Walltorch2.png"]
        self.state = 0
        self.tick = 0
    def _inscreen(self, CX):
        if CX - 100 <= self.x <= CX + 740:
            return True
        return False
    def _poll(self):
        return self.frame[self.state], self.x-20, self.y - 20
    def _tick(self):
        self.tick +=1
        if not self.tick%3:
            self.state = (self.state + 1) % 4

class Torchref:
    def __init__(self, tx, ty):
        self._needinfo = False
        self._runtime = "InScreen"
        self._infront = False
        self.id = "Torchref",
        self.P_id = ""
        self._activateable = False

        self.x = tx*40+20
        self.y = ty*40+20

        self.frame = ["Torchref.png", "Torchref3.png", "Torchref2.png", "Torchref3.png"]
        self.state = 0
        self.tick = 0
    def _inscreen(self, CX):
        if CX - 100 <= self.x <= CX + 740:
            return True
        return False
    def _poll(self):
        return self.frame[self.state], self.x-20, self.y - 20
    def _tick(self):
        self.tick +=1
        if not self.tick%3:
            self.state = (self.state + 1) % 4

class Firepit:
    def __init__(self, tx, ty):
        global DATA
        self._needinfo = False
        self._runtime = "InScreen"
        self._infront = False
        self.id = "Firepit"
        self.P_id = "Firepit"
        self._activateable = False
        self._wordoffset = (-20, 0)
        self.ticker = 0
        self._ambsound = "fire_loop.ogg"
        self.soundplaying = False

        self.x = tx * 40 + 20
        self.y = ty * 40 + 40

        self.state = 1
        self.fireballs = []

    def _inscreen(self, CX):
        if CX - 100 <= self.x <= CX + 740:
            return True
        return False
    def _giveinfo(self, info):
        return
    def _poll(self):
        return "Pit.png", self.x-20, self.y - 40
    def _tick(self):
        global SCREEN, DATA, CAMERA_X, PLAYER, SOUNDBOX, Objects

        ambvol = 0
        for ob in [o for o in Objects if o.id == "Firepit" and o.state == 1]:
            vol = ((300 - abs(ob.x - PLAYER.x))/3)/100.0
            if vol > ambvol:
                ambvol = vol
        if self._ambsound in SOUNDBOX.sounds and not SOUNDBOX.sounds[self._ambsound].get_num_channels():
            SOUNDBOX.SetSoundVolume(self._ambsound, ambvol)
            SOUNDBOX.PlaySound(self._ambsound, -1)
        else:
            SOUNDBOX.SetSoundVolume(self._ambsound, ambvol)
        
        self.ticker += 1
        HitTick = False
        if self.state:
            if not self.ticker%5:
                x = random.randint(-10,10)/30.0
                y = random.randint(-40,-12)/10.0
                self.fireballs.append([random.randint(-3,3),-3,x,y,0])

        for fireball in self.fireballs:
            fb = DATA.images["Fireball.png"][0]
            s = int(10 + fireball[4]/5.0)
            fb = pygame.transform.scale(fb, (s, s))
            fbr = fb.get_rect()
            fbr.center = (self.x + fireball[0]-CAMERA_X, self.y+fireball[1])
            fbri = fbr.inflate(20, 20)
            screenbit = pygame.Surface(fbr.size)

            screenbit.blit(SCREEN, (0,0), fbr)
            screenbit.set_alpha(fireball[4]>>1)

            if G_OPTIONS["Heat Shimmer"]:
                screenbit2 = pygame.Surface(fbri.size)
                screenbit2.blit(SCREEN, (0,0), fbri.move(0,random.randint(-1,1)))
                screenbit2.set_alpha(fireball[4]>>1)


            SCREEN.blit(fb, fbr)
            SCREEN.blit(screenbit, fbr)

            if G_OPTIONS["Heat Shimmer"]:
                SCREEN.blit(screenbit2, fbri)

            if fbr.inflate(10,20).collidepoint((PLAYER.x-CAMERA_X, PLAYER.y-40)) and not self.ticker%3 and PLAYER.hp[0] > 0 and not HitTick:
                PLAYER.Take_Damage(random.randint(5,10))
                HitTick = True

        for x in range(len(self.fireballs)):
            self.fireballs[x][4] += 5
            self.fireballs[x][0] += self.fireballs[x][2]
            self.fireballs[x][1] += self.fireballs[x][3]
            if self.fireballs[x][4] >= 270:
                self.fireballs[x] = None

        while None in self.fireballs:
            self.fireballs.remove(None)
            
    def _activate(self):
        pass

class Lever:
    def __init__(self, tx, ty):
        global DATA
        self._needinfo = False
        self._runtime = "InScreen"
        self._infront = False
        self.id = "Lever"
        self.P_id = "Lever"
        self._activateable = True
        self._wordoffset = (-20, 0)

        self.x = tx * 40 + 20
        self.y = ty * 40 + 40
        self.command = ""

        self.frame = ["Lever1.png", "Lever2.png"]
        self.state = 0

    def _inscreen(self, CX):
        if CX - 100 <= self.x <= CX + 740:
            return True
        return False
    def _giveinfo(self, info):
        return
    def _poll(self):
        return self.frame[self.state], self.x-40, self.y - 40
    def _tick(self):
        pass
    def _activate(self):
        global PLAYER, NOTICE_VIEW, SOUNDBOX

        self.state = 1
        self._activateable = False
        if safe(self.command):
            thread.start_new_thread(self.run, ())
        SOUNDBOX.PlaySound("stone.ogg")
    def run(self):
        global PLAYER, EOLFADE
        exec(self.command)

class Obelisk:
    def __init__(self, tx, ty, otype = ''):
        global DATA
        self._needinfo = False
        self._runtime = "InScreen"
        self._infront = False
        self.id = "Obelisk"
        self.P_id = "Obelisk"
        self._activateable = True
        self._wordoffset = (-17, -4)

        self.x = tx * 40 + 20
        self.y = ty * 40 + 40
        self.otype = otype

        self.frame = [x + ["_"+otype, ""][otype == ""] + ".png" for x in ['Obelisk', 'Obelisk2']]
        self.state = 0

    def _inscreen(self, CX):
        if CX - 100 <= self.x <= CX + 740:
            return True
        return False
    def _giveinfo(self, info):
        return
    def _poll(self):
        return self.frame[self.state], self.x-20, self.y - 200
    def _tick(self):
        pass
    def _activate(self):
        global PLAYER, NOTICE_VIEW, SOUNDBOX, LEVEL, Monsters, Objects, FRAMEMOD, Treasures

        NOTICE_VIEW.add("Obelisk activated!")
        self.state = 1
        self._activateable = False
        PLAYER.obelisk_time = FRAMEMOD
        PLAYER.obelisk_save = [LEVEL.name, copy.deepcopy(PLAYER), cPickle.dumps(copy.deepcopy(Monsters)), Objects[:], Treasures]

        PLAYER.obelisk_save[1].inventory = PLAYER.inventory

        SOUNDBOX.PlaySound("Obelisk.ogg")

class Sign:
    def __init__(self, tx, ty):
        global DATA
        self._needinfo = False
        self._runtime = "InScreen"
        self._infront = False
        self.id = "Sign"
        self.P_id = "Sign"
        self._activateable = True
        self._wordoffset = (0, -25)

        self.x = tx * 40
        self.y = ty * 40 

        self.frame = "Sign.png"
        self.message = ""
    def _inscreen(self, CX):
        if CX - 100 <= self.x <= CX + 740:
            return True
        return False
    def _giveinfo(self, info):
        return
    def _poll(self):
        return self.frame, self.x, self.y
    def _tick(self):
        pass
    def _activate(self):
        message_box(self.message)

class TreasureBox:
    def __init__(self, tx, ty):
        global DATA
        self._needinfo = False
        self._runtime = "InScreen"
        self._infront = False
        self.id = "TreasureBox"
        self.P_id = "Treasure box"
        self._activateable = True

        self.x = tx * 40 + 20
        self.y = ty * 40 + 40 

        self.frame = ["Treasure_Closed.png", "Treasure_Open.png"]
        self.state = 0
        self.bounty = []
    def _inscreen(self, CX):
        if CX - 100 <= self.x <= CX + 740:
            return True
        return False
    def _giveinfo(self, info):
        return
    def _poll(self):
        return self.frame[self.state], self.x-20, self.y - 57
    def _tick(self):
        pass
    def _activate(self):
        global PLAYER, NOTICE_VIEW, SOUNDBOX, Treasures, GAME, DATA, PIC_VIEW
        Treasures += 1
        if random.randint(1,30) == 1:
            NOTICE_VIEW.add("Found *RELIC*!")
            PIC_VIEW.pics.append(["ring6.png", 400])
            PLAYER.relics += 1
        else:
            for item in self.bounty:
                if item.isdigit():
                    NOTICE_VIEW.add("Found " + item + " silver pieces!")
                    item = int(item)
                    GAME.silver += item
                    PIC_VIEW.pics.append(["silverpouch.png", 400])
                else:
                    NOTICE_VIEW.add("Found " + DATA.Itembox.GetItem(item).display + "!")
                    PLAYER.inventory.append(item)
                    PIC_VIEW.pics.append([DATA.Itembox.GetItem(item).inv_image, 400])
        self.state = 1
        self._activateable = False
        SOUNDBOX.PlaySound("Treasure.ogg")

class TreasureBoxB(TreasureBox):
    def __init__(self, tx, ty):
        global DATA
        self._needinfo = False
        self._runtime = "InScreen"
        self._infront = False
        self.id = "TreasureBox"
        self.P_id = "Treasure box"
        self._activateable = True

        self.x = tx * 40 + 20
        self.y = ty * 40 + 40 

        self.frame = ["TreasureB_Closed.png", "TreasureB_Open.png"]
        self.state = 0
        self.bounty = []

class TreasureBoxC(TreasureBox):
    def __init__(self, tx, ty):
        global DATA
        self._needinfo = False
        self._runtime = "InScreen"
        self._infront = False
        self.id = "TreasureBox"
        self.P_id = "Treasure box"
        self._activateable = True

        self.x = tx * 40 + 20
        self.y = ty * 40 + 40 

        self.frame = ["TreasureC_Closed.png", "TreasureC_Open.png"]
        self.state = 0
        self.bounty = []

class Butterfly:
    def __init__(self, tx, ty):
        global DATA
        self._needinfo = False
        self._runtime = "InScreen"
        self._infront = True
        self.id = "Butterfly"
        self._activateable = False
        
        self.st = (tx, ty) # Start tile

        self.x = tx * 40
        self.y = ty * 40

        self.dir = False
        self.ticker = 0
        self.frame = ["Butterfly.png","Butterfly2.png"]
        self.phase = True
        self.phase2 = True
    def _inscreen(self, CX):
        if CX - 100 <= self.x <= CX + 740:
            return True
        return False
    def _giveinfo(self, *args):
        return
    def _poll(self):
        return self.frame[self.dir], self.x, self.y    
    def _tick(self):
        if self.ticker%2:self.ticker += 1;return
        self.dir = [True, False][self.dir]
        self.x += random.randint(-2,2)
        self.y += random.randint(-2,2)
        self.ticker +=1

class ButterflyB(Butterfly):
    def __init__(self, tx, ty):
        global DATA
        self._needinfo = False
        self._runtime = "InScreen"
        self._infront = True
        self.id = "ButterflyB"
        self._activateable = False
        
        self.st = (tx, ty) # Start tile

        self.x = tx * 40
        self.y = ty * 40

        self.dir = False
        self.ticker = 0
        self.frame = ["ButterflyB.png","ButterflyB2.png"]
        self.phase = True
        self.phase2 = True

class ButterflyC(Butterfly):
    def __init__(self, tx, ty):
        global DATA
        self._needinfo = False
        self._runtime = "InScreen"
        self._infront = True
        self.id = "ButterflyC"
        self._activateable = False
        
        self.st = (tx, ty) # Start tile

        self.x = tx * 40
        self.y = ty * 40

        self.dir = False
        self.ticker = 0
        self.frame = ["ButterflyC.png","ButterflyC2.png"]
        self.phase = True
        self.phase2 = True
