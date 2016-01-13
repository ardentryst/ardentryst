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

import pygame, time
from pygame.locals import *
from helpers import myflip, ge

FADES = True
SKIPWAIT = False

def fade_set_slow():
    # Ironically, this tells the fades to go FAST. (-q option activates)
    global SKIPWAIT
    SKIPWAIT = True

def tick_wait(ms, d):
    global SKIPWAIT
    ge()
    if SKIPWAIT: return False
    if ms < d:
        time.sleep(0.001 * (d - ms))
        return True
    return False

def NOFADES():
    global FADES
    FADES = False

def FADE_DOUBLESIZE():
    "Deprecated"
    global DOUBLESIZE
    DOUBLESIZE = True

def INIT_FADES(realscr, scr):
    "Deprecated"
    global REAL, SCREEN
    REAL = realscr
    SCREEN = scr

def flip():
    myflip()

def fade_screens(screen, screen2, delay = 2):
    global FADES
    if not FADES:
        screen.blit(screen2, (0,0))
        flip()
        return

    orig_screen = pygame.Surface((640, 480))
    orig_screen.blit(screen, (0,0))
    skipnext = False
    for x in range(41):
        ms = pygame.time.get_ticks()
        screen.blit(screen2, (0,0))
        orig_screen.set_alpha(255 - int(x * (255/40.0)))
        screen.blit(orig_screen, (0,0))
        flip()
        ms = pygame.time.get_ticks() - ms
        tickw = tick_wait(ms, delay)
        if type(tickw) == str: break
        if not tickw: skipnext = True

def fade_to_black(screen, delay = 2):
    global FADES
    if not FADES:
        screen.fill((0,0,0))
        flip()
        return

    orig_screen = pygame.Surface((640, 480))
    orig_screen.blit(screen, (0,0))
    skipnext = False
    for x in range(41):
        if skipnext: skipnext = False; continue
        ms = pygame.time.get_ticks()
        screen.fill((0, 0, 0))
        orig_screen.set_alpha(255 - int(x * (255/40.0)))
        screen.blit(orig_screen, (0,0))
        flip()
        ms = pygame.time.get_ticks() - ms
        tickw = tick_wait(ms, delay)
        if type(tickw) == str: break
        if not tickw: skipnext = True
    screen.fill((0, 0, 0))
    flip()


def fade_to_white(screen, delay = 2):
    global FADES
    if not FADES:
        screen.fill((255,255,255))
        flip()
        return

    orig_screen = pygame.Surface((640, 480))
    orig_screen.blit(screen, (0,0))
    skipnext = False
    for x in range(41):
        ms = pygame.time.get_ticks()
        screen.fill((255, 255, 255))
        orig_screen.set_alpha(255 - int(x * (255/40.0)))
        screen.blit(orig_screen, (0,0))
        flip()
        ms = pygame.time.get_ticks() - ms
        tickw = tick_wait(ms, delay)
        if type(tickw) == str: break
        if not tickw: skipnext = True
    
def fade_from_black(screen, delay = 2):
    global FADES
    if not FADES:
        flip()
        return

    orig_screen = pygame.Surface((640, 480))
    orig_screen.blit(screen, (0,0))
    skipnext = False
    for x in range(41):
        if skipnext: skipnext = False; continue
        ms = pygame.time.get_ticks()
        screen.fill((0, 0, 0))
        orig_screen.set_alpha(int(x * (255/40.0)))
        screen.blit(orig_screen, (0,0))
        flip()
        ms = pygame.time.get_ticks() - ms
        tickw = tick_wait(ms, delay)
        if type(tickw) == str: break
        if not tickw: skipnext = True

def fade_from_white(screen, delay = 2):
    global FADES
    if not FADES:
        flip()
        return

    orig_screen = pygame.Surface((640, 480))
    orig_screen.blit(screen, (0,0))
    skipnext = False
    for x in range(41):
        ms = pygame.time.get_ticks()
        screen.fill((255, 255, 255))
        orig_screen.set_alpha(int(x * (255/40.0)))
        screen.blit(orig_screen, (0,0))
        flip()
        ms = pygame.time.get_ticks() - ms
        tickw = tick_wait(ms, delay)
        if type(tickw) == str: break
        if not tickw: skipnext = True
