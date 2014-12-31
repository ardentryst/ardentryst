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

import pygame, time, md5, random
from helpers import ge, myflip
from pygame.locals import *
from fade import *
import wordwrap
from math import radians, sin

    #1st slide(bg,(txtlines),spch,alt.len,(prespeech,prescr,extrascr,endw),amb)

script = {

    "End": [

    "theme1.ogg",

    ("End.png",
     ("After Radkelu's evil power over Kiripan had been dispelled,", "Kiripan returned to the ground safely...", "and Ardentryst was saved from the clutches of despair!"),
     None,
     None,
     (1, 25, 0, 2),
     None
     ),

    ("End.png#",
     ("", "THE END"),
     None,
     None,
     (3, 15, 0, 999),
     None
     ),


    ("black.png",
     ("",""),
     None,
     1,
     (0, 0, 0, 0),
     "continue",
     )

    ],

    "Introduction": [

    "Story.ogg",

    ("Intro_Kiripan_Village.png",
     ("When I was a child, I knew bright, blue days when",
      "The heat was blaring, and the gulls were soaring."),
     "VOI_Intro_1.ogg",
     None,
     (2, 1, 6, 1),
     "AMB_Intro_1.ogg"
     ),

    ("Intro_Kiripan_Beach.png",
     ("I ... guess time escaped us....",
      "We'd sit at the beach, watching the water come in, and leave;",
      "Over and over."),
     "VOI_Intro_2.ogg",
     8,
     (1, 0, 0, 0),
     "AMB_Intro_2.ogg"
     ),

    ("Intro_Kiripan_Beach_Fade.png",
     ("", "Summer began to fade...."),
     "VOI_Intro_3.ogg",
     4,
     (1, 0, 0, 1),
     "AMB_Intro_3.ogg"
     ),

    ("black.png",
     ("I remember....",
      "A huge tremor rumbled beneath us....",
      "Chasms tore us apart."),
     "VOI_Intro_4.ogg",
     8,
     (1, 0, 1, 0),
     "continue"
     ),

    ("black.png#",
     ("Then suddenly,",
      "Kiripan rose into the sky, high above the clouds...."),
     "VOI_Intro_5.ogg",
     5,
     (1, 0, 0, 2),
     "continue"
     ),

    ("Intro_Newspaper.png#",
     ("", "Day ... has turned to night."),
     "VOI_Intro_6.ogg",
     6,
     (2, 0, 0, 3),
     "AMB_Intro_6.ogg"
     ),

    ("black.png",
     ("",""),
     None,
     1,
     (0, 0, 0, 0),
     "continue",
     )

    ],



}


def Wait_10_ms(t):
    timebeen = (pygame.time.get_ticks() - t)
    if timebeen < 10:
        time.sleep((10 - timebeen) / 1000.0)
    return

def r_wait(sec):
    ft = pygame.time.get_ticks()
    while pygame.time.get_ticks() < ft + sec*1000:
        time.sleep(0.001)
        for e in ge():
            if e.type == KEYDOWN:
                if e.key == K_ESCAPE or e.key == K_RETURN: return True
    return False

class Game_Object:
    def __init__(self):
        self.savefilename = ""
        self.character = "Nobody"
        self.location = [1, 0] # [World, Level]
                               # since level is 0, we're on the world map
        self.said_laggy = False
        self.silver = 0
        self.ENDSCENE = 0
        self.startdate = ""
        self.version = ""
        self.world_tut = 0
        self.game_tut = 0

        self.ac_code = "".join([chr(97 + random.randint(0,25)) for x in range(4)]).upper()

        self.playerobject = None
        self.password = ""

        self.Accessible = [
            [1],          # Worlds on world map that are accessible by default
            [1],          # Levels in semp. that are accessible by default
            [1],          # Levels in ent. that are accessible by default
            [1, 2],       # Levels in sno. that are accessible by default
            ]

        self.scores = [
            ]

        self.timegems = []
        self.GID = md5.new(str(random.randint(0, 9999999)).zfill(7)+time.ctime()).hexdigest()
        self.KIRI_HEIGHT = 1 # How high kiripan is levitated.

        #1st slide(bg,(txtlines),spch,alt.len,(prespeech,prescr,extrascr,endw),amb)
        self.hc = False

        self.storyline = "When one of Ardentryst's Mages of Balance is struck by greed for power and becomes corrupt, the story of the small coastal town of Kiripan is changed forever... Nyx, the descendent and only daughter of the Entaryan Queen Amee, is an apprentice mage when she hears the news. Simultaneously, in the forest town Sempridge, Pyralis hears of the news from the local storyteller. When the evil mage Radkelu turned against the good mages, turning them to stone, he summoned a horde of creatures which came out of portals all throughout the land. They crawled the cities and the villagers fled. Rumour has it that Radkelu is hiding out in a cave atop the snowy mountain range Snodom. It is now up to the bravest souls of Entarya and Sempridge to rescue Kiripan from Radkelu's clutches..."

    def text_intro(self, screen, data, fonts, soundbox):
        soundbox.PlaySong("castle2.ogg", -1)
        Quitsurfw = fonts[9].render("Hit ESC or RETURN to skip", 1, (255,255,255))
        Quitrect = Quitsurfw.get_rect()
        storysurfs = wordwrap.string_to_paragraph(self.storyline, fonts[22], 1, (220, 230, 255), 620)
        h = 250
        for s in storysurfs:
            h += s.get_height()
        bigsurf = pygame.Surface((640, h), SRCALPHA, 32)
        ch = 0
        bigsurf.blit(data.SSI["part1.png"][0], (61, 20))
        for s in storysurfs:
            r = s.get_rect()
            r.midtop = (320, 215 + ch)
            ch += r.height
            bigsurf.blit(s, r)

        # Now bigsurf is made.

        height = 100
        bigsurfheight = bigsurf.get_height()
        tick = -bigsurfheight + height + 100
        while tick < 500:
            screen.blit(data.SSI["Kiripan_dark.png"][0], (0,0))

            for ly in range(1, 850):
                row = pygame.Surface((640, 1), SRCALPHA, 32)
                # At ly = 1, the angle will be a little declining.
                
                exte = ly / 20.0
                inte = 90 - exte
                dist = height * sin(radians(inte)) / sin(radians(exte))
                imy = bigsurfheight - dist + tick
                row.blit(bigsurf, (0, -imy))
                w = ly * 1.5
                row = pygame.transform.scale(row, (int(w/4.0)*4, 1))
                rowr = row.get_rect()
                rowr.midtop = (320, ly)
                screen.blit(row, rowr)


            tick += 1
            Quitrect.bottomright = (635, 475)
            screen.blit(Quitsurfw, Quitrect)
            myflip()
            if r_wait(0.01):return


    def story_scene(self, scene, screen, d, f, s):
        Scene_Info = script[scene]
        Scene_Music = Scene_Info[0]
        Old_Slide_Amb = None
        Slide_Amb = None
        Slide = 1
        Showing = True

        lh = 25

        this_slide = pygame.Surface((640,480))

        if Scene_Music:
            s.PlaySong(Scene_Music, -1)

        Quitsurfw = f[9].render("Hit ESC or RETURN to skip", 1, (255,255,255))
        Quitsurfb = f[9].render("Hit ESC or RETURN to skip", 1, (0,0,0))
        Quitrect = Quitsurfw.get_rect()


        while Showing:

            Amb_Cont = False
            if Slide_Amb:
                Old_Slide_Amb = Slide_Amb

            Camera_X = 0
            CUT = False
            
            Slide_Info = Scene_Info[Slide]
            Slide_Amb = Slide_Info[5]

            if Slide_Amb == "continue": Slide_Amb = Old_Slide_Amb; Amb_Cont = True

            if Slide_Amb and not Amb_Cont: s.PlaySound(Slide_Amb)
            if Slide_Info[0][-1] == "#": CUT = True
            if CUT:
                Slide_Img, Slide_Rect = d.SSI[Slide_Info[0][:-1]]
            else:
                Slide_Img, Slide_Rect = d.SSI[Slide_Info[0]]
            this_slide.blit(Slide_Img, (0,0))

            if not CUT: fade_screens(screen, this_slide, 25)
            else: screen.blit(this_slide, (0,0))

            for x in range(-1,2):
                for y in range(-1,2):
                    Quitrect.bottomright = (635+x, 475+y)
                    screen.blit(Quitsurfb, Quitrect)

            Quitrect.bottomright = (635, 475)
            screen.blit(Quitsurfw, Quitrect)
            
            myflip()

            Subtitles = Slide_Info[1]
            Speech = Slide_Info[2]
            Time_Wait = Slide_Info[4]

            if Time_Wait[0]:
                if r_wait(Time_Wait[0]):
                    break

            if Old_Slide_Amb and not Amb_Cont:
                s.FadeoutSoundSlow(Old_Slide_Amb)

            if Speech: s.PlaySound(Speech); SlideLength = s.SoundLength(Speech)

            SlideLength = 0.1
            if Slide_Info[3]: SlideLength = Slide_Info[3]

            if Subtitles:
                for i in range(len(Subtitles)):
                    Sub_Img = f[12].render(Subtitles[i], 1, (0,0,0))
                    Sub_Rct = Sub_Img.get_rect()
                    Sub_Rct.centerx = 321
                    Sub_Rct.bottom = 475 - ((len(Subtitles)-i-1) * lh)
                    for x in range(-1, 2):
                        for y in range(-1, 2):
                            this_slide.blit(Sub_Img, Sub_Rct.move(x,y))

                    Sub_Img = f[12].render(Subtitles[i], 1, (255,255,255))
                    Sub_Rct = Sub_Img.get_rect()
                    Sub_Rct.centerx = 320
                    Sub_Rct.bottom = 475 - ((len(Subtitles)-i-1) * lh)
                    this_slide.blit(Sub_Img, Sub_Rct)
            fade_screens(screen, this_slide, 10)

            Extra_Space = Slide_Rect[2] - 640
            Slide_Factor = Extra_Space / float((SlideLength-Time_Wait[1]+Time_Wait[2])*100)

            Sliding = False
            if Extra_Space:
                Sliding = True

            if not Sliding:
                if r_wait(SlideLength):
                    break

            if Time_Wait[1]:
                if r_wait(Time_Wait[1]):
                    break

            while Sliding:
                t = pygame.time.get_ticks()
                Camera_X += Slide_Factor
                screen.blit(Slide_Img, (-Camera_X, 0))
                if Subtitles:
                    for i in range(len(Subtitles)):
                        Sub_Img = f[12].render(Subtitles[i], 1, (0,0,0))
                        Sub_Rct = Sub_Img.get_rect()
                        Sub_Rct.centerx = 321
                        Sub_Rct.bottom = 475 - ((len(Subtitles)-i-1) * lh)
                        for x in range(-1,2):
                            for y in range(-1, 2):
                                screen.blit(Sub_Img, Sub_Rct.move(x,y))
                        Sub_Img = f[12].render(Subtitles[i], 1, (255,255,255))
                        Sub_Rct = Sub_Img.get_rect()
                        Sub_Rct.centerx = 320
                        Sub_Rct.bottom = 475 - ((len(Subtitles)-i-1) * lh)
                        screen.blit(Sub_Img, Sub_Rct)
                    
                myflip()
                Wait_10_ms(t)
                if r_wait(0.001): Showing = False

                if Camera_X >= Extra_Space: Sliding = False

                if not Showing: break

            Slide += 1

            if Slide == len(Scene_Info):
                Showing = False

            this_slide.blit(Slide_Img, (-Camera_X,0))
            fade_screens(screen, this_slide, 10)
            if not Showing: break
            if Time_Wait[3]:
                if r_wait(Time_Wait[3]):
                    break

        fade_to_black(screen, 8)
        s.FadeoutMusic(4000)
        if Slide_Amb:
            s.FadeoutSound(Slide_Amb)
        if Speech:
            s.FadeoutSound(Speech)
