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

# By the way the code below is REALLY messy. Haha. Avert your eyes..

import pygame, os, time, random
from wordwrap import string_to_paragraph
from pygame.locals import *
from helpers import myflip, ge
pygame.font.init()

finalstage = 200
mytext = ""
mytext2 = ""
myfont = pygame.font.Font(os.path.join("Fonts","FreeSerif.ttf"), 15)

quotes = [
    [
    # Nyx
    "With each new horizon and each new day that springs forth, so too springs the opportunity to write history.",
    "With courage we will slay all evil. With swords and magic we will dispatch them.",
    "The icy winds of Snodom are delightful; but those pesky Gelatice always block the view.",
    "The two greatest warriors in the fight for freedom are patience and time.",
    "We shall quest, day and night, until the Nightbringers receive their due punishment.",
    "My home has been destroyed. My town of half-heritage; under a catastrophic spell.",
    ],
    [
    # Pyralis
    "The butterflies in Sempridge are as big as your hand!",
    "As long as I am present, I will bring justice to the innocent.",
    "Ardentrystrians all over shall rejoice for our victories... or mourn our defeat.",
    "I will save those Kiripians... every last one of them!",
    "Through strength and wisdom we can accomplish our greatest dreams.",
    "This is going to be a piece of cake. A ... rather ... large cake."
    ]
    ]

def dofinal(f):
    global finalstage
    finalstage = f

def Loading_Screen(scr, loading_image, myfont, acc):
    "Initialise loading screen."
    global loading_img, bar_grad, screen, lb, lbr
    screen = scr
    loading_img = loading_image[0]
    screensize = screen.get_size()
    screen.blit(loading_img, (0,0))

def Update_Loading(stage, text, *args):
    global finalstage, loading_img, bar_grad, screen, mytext, myfont, mytext2, lb, lbr
    screen.fill((0,0,0))
    screen.blit(loading_img, (0,0))
    y = 0

    if stage == -1:
        stage = finalstage

    text += " / " + str(int(100*stage/float(finalstage))) + "%"
    Loading_Bar(stage, text)
    myflip()
    ge()

def Loading_Bar(stage, text):
    global finalstage, loading_img, bar_grad, screen, mytext, myfont, mytext2, lb, lbr
    barrect = Rect(0,0,600,2)
    barrect.center = (320,470)
    screen.fill((0,0,0), barrect)
    barrect[2] = int(stage * (600.0 / finalstage))
    screen.fill((220,190,30), barrect)

    text = myfont.render(text, True, (255, 255, 255))
    textrect = text.get_rect()
    textrect.bottomright = (637, 469)

    screen.blit(text, textrect)

def Update_Loading_Old(stage, mytext3, finish = False):
    global finalstage, loading_img, bar_grad, screen, mytext, myfont, mytext2, lb, lbr
    screen.fill((0, 0, 0), pygame.rect.Rect(0, 370, 640, 140))

    #pygame.display.update(updr.inflate(160, 10))

    mytext = "Precaching Game Data:"

    mytext2 = str(int((100.0/finalstage)*stage))+"%"
    if mytext2 == "100%": mytext2 = "Please wait- Precaching Audio (through Conch) ..."; mytext = ""; mytext3 = "One moment..."

    if finish: mytext = "Precaching complete!"; mytext2 = ""; stage = finalstage

    cstage = stage * (255.0 / finalstage)
    b = int(cstage)
    
    tb = myfont.render(mytext + " "+mytext2, 1, (255,255,255))
    tb2 = myfont.render(mytext3, 1, (255,255,255))
    tr = tb.get_rect()
    tr2 = tb2.get_rect()

    tr.center = (320,430)
    tr2.center = (320, 460)

    lbr.midright = ((503.0/finalstage)*stage + 100,404)

    screen.blit(lb, lbr)
    screen.blit(loading_img[0], (0,0))
    screen.blit(bar_grad[0], (69,399))
    screen.blit(tb, tr)
    screen.blit(tb2,tr2)
    myflip()
