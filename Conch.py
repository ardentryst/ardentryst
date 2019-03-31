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

"""
Conch.py, a music toolkit.
By Kris Schnee, borrowing heavily from Pygame's docs and examples.
 
License: Free software; use as you please. Credit appreciated.
Requirements: Just Python and Pygame. Put all sound and music files
in subdirectories called "sound" and "music".
Notes: These are easy functions for using music and sound in Python/Pygame,
just wrappers around Pygame's functions. The Jukebox class keeps track of a
set of loaded sound effects and paths for songs, with keys so you can just
call 'j.PlaySong("Battle Music")' to access an obscurely named song file
neatly stored in a subdirectory. So, to use this code you just LoadSong for
whatever songs you like, giving the filename and a nickname, then PlaySong
to play. Same for sound effects, though behind the scenes the sounds are
actually loaded once and kept in memory instead of just the paths.
 
Example:
j = Jukebox()
j.LoadSong("battle00.mid","Battle Music")
j.PlaySong("Battle Music")
j.StopMusic()
"""
 
 
import pygame ## Pygame toolkit for sound (and many other things); pygame.org
import os     ## File system
import time

def conchinit(HZ):
    Hz = HZ
    try:
    #    pygame.mixer.pre_init(44100,-16,2, 8)
        if Hz == None:
            pygame.mixer.init(44100, -16, 2, 2**10)
        else:
            pygame.mixer.init(Hz)

        i = list(pygame.mixer.get_init())
        if i[1] < 0: i[1] = "16, signed"
        else: i[1] = "16, unsigned"
    except Exception as e:
        print("Warning: Sound disabled! ("+str(e)+")")
        print("Is your sound in use?")

MODULE_NAME = "Conch Sound System (Conch.py)"
MODULE_VERSION = "2006.8.9"
 
DEFAULT_MUSIC_EXTENSION = ".mp3"
DEFAULT_SOUND_EXTENSION = ".wav"
SOUND_DIRECTORY = "Sounds"
MUSIC_DIRECTORY = "Music"
 
JUKEBOX_COMMENTS = False
 
## You can change these options to have sound/music muted by default.
MUSIC_ON = True
SOUND_ON = True
 
 
class Jukebox:
    def __init__(self,dir=MUSIC_DIRECTORY):
        """Load and play sounds and music, referenced by name.
        Create one of these to put audio in your game.
        One is created automatically when the module loads, so
        there's not really a need to make another."""
        self.name = "Conch Audio Module"
        self.comments = JUKEBOX_COMMENTS
 
        self.music_on = MUSIC_ON
        self.sound_on = SOUND_ON
 
        self.songs = {} ## eg. {"Battle Theme":"battle01.ogg"}
 
        self.music_directory = MUSIC_DIRECTORY
        self.sound_directory = SOUND_DIRECTORY
 
        self.sounds = {}

        self.music_volume = 1
        self.sound_volume = 1
 
    def Comment(self,what):
        if self.comments:
            print("["+self.name+"] " + str(what))
 
    def ToggleMusic(self,on=True):
        self.music_on = on
 
    def ToggleSound(self,on=True):
        self.sound_on = on
 
    def StopMusic(self):
        """Stops music without turning it off; another song may get cued."""
        if not pygame.mixer.get_init():
            return
        pygame.mixer.music.stop()
 
    def QuitMusic(self):
        """Shuts off Pygame's music code.
        This probably isn't necessary."""
        pygame.mixer.music.stop()
        pygame.mixer.quit()

    def MusicGetPos(self):
        if pygame.mixer.get_init():
            return pygame.mixer.music.get_pos()
        return 0

    def MusicVol(self, vol):
        try:
            pygame.mixer.music.set_volume(vol * self.music_volume)
        except:
            pass

    def pause(self):
        try:
            pygame.mixer.music.pause()
        except:
            pass

    def unpause(self):
        try:
            pygame.mixer.music.unpause()
        except:
            pass
 
    def LoadSong(self,songname,key=""):
        """Add name, including directory location, to songlist.
        You can give the song a key, too, for easy reference.
        Note that rather than actually loading the song, we store only
        the path to it. Contrast with sound loading."""
        new_song_path = os.path.join(self.music_directory,songname)
        if key:
            self.songs[ key ] = new_song_path

    def ResetSongData(self):
        self.songs = {}

    def fadein(self):
        for x in range(20):
            self.MusicVol(x/20.0)
            time.sleep(0.03)
 
    def PlaySong(self,cue_name,loops = 0, vol= 1.0, interrupt=False):
        """Cue this song. If interrupt, the song will start even
        if one is already playing."""
        if not pygame.mixer.get_init():
            return
        path = self.songs.get( cue_name )
        if path:
            if not self.music_on:
                return ## Never mind.
            if not interrupt:
                if pygame.mixer.music.get_busy():
                    for x in range(20):
                        self.MusicVol(1-x/20.0)
                        time.sleep(0.03)
                    pygame.mixer.music.stop()
 
#            pygame.mixer.music.stop()
 
            ## Now load and play.
            try:
                pygame.mixer.music.load(path)
            except:
                print("Couldn't load song '"+cue_name+"'.")
                return
            try:
                self.MusicVol(0)
                pygame.mixer.music.play(loops)
                self.fadein()
                self.Comment("Cue music: '"+cue_name+"'")
            except:
                print("Couldn't play song '"+cue_name+"'.")

    def set_svol(self, svol):
        self.sound_volume = svol/3.0

    def set_mvol(self, mvol):
        self.music_volume = mvol/3.0
        self.MusicVol(1)
 
    def FadeoutMusic(self, time):
        if not pygame.mixer.get_init():
            return
        pygame.mixer.music.fadeout(time)
    def LoadSound(self,filename,cue_name=None):
        """Load a sound into memory, not just its name, for quick use."""
        if not pygame.mixer.get_init():
            return
        if not "." in filename:
            filename += DEFAULT_SOUND_EXTENSION
        new_sound = pygame.mixer.Sound( os.path.join(SOUND_DIRECTORY,filename) )
        if not cue_name:
            cue_name = filename
        self.sounds[ cue_name ] = new_sound

    def SoundLength(self, cue_name):
        if cue_name in self.sounds:
            return self.sounds[cue_name].get_length()
        return 5

    def FadeoutSound(self, cue_name):
        if not pygame.mixer.get_init(): return
        if cue_name in self.sounds:
            vol = self.sounds[cue_name].get_volume()
            while vol > 0:
                self.sounds[cue_name].set_volume(vol-0.1)
                vol -= 0.1
                time.sleep(0.05)
            self.sounds[cue_name].stop()

    def FadeoutSoundSlow(self, cue_name):
        if not pygame.mixer.get_init(): return
        if cue_name in self.sounds:
            vol = self.sounds[cue_name].get_volume()
            while vol > 0:
                self.sounds[cue_name].set_volume(vol-0.1)
                vol -= 0.1
                time.sleep(0.1)

    def SetSoundVolume(self, cue_name, vol):
        if not pygame.mixer.get_init(): return
        if cue_name in self.sounds:
            self.sounds[cue_name].set_volume(vol)

    def PlaySound(self,cue_name, loops=0):
        ## How to check whether sound player is busy?
        if not pygame.mixer.get_init():
            return

        if cue_name in self.sounds:
            self.sounds[cue_name].set_volume(self.sound_volume)
            a =  self.sounds[ cue_name ].play(loops)
        else:
            self.Comment("Tried to play sound '"+cue_name+"' without loading it.")
            pass

    def StopSound(self,cue_name):
        if cue_name in self.sounds:
            self.sounds[ cue_name ].stop()
 
 
##### AUTORUN #####
if __name__ == '__main__':
    ## This code runs if this file is run by itself.
    print("Running "+MODULE_NAME+", v"+MODULE_VERSION+".")
 
else:
    soundbox = Jukebox() ## You can now just refer to "soundbox" in your own program.
                          # Oh. Now you tell me. I might rewrite some parts to make
                          # better use of this. Later. :)
