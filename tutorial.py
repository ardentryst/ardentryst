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

import pygame

def key(action):
    global CONTROLS
    return pygame.key.name(CONTROLS[action][0]).upper()

class TutBox:
    def __init__(self, controls):
        global CONTROLS

        # Links to outside
        self.Text = ""
        self.RAIN = 0
        self.playerclass = 0

        # End links

        self.startraining = False
        
        self.cpt = None

        self.Narrator = "<Narrator Name>"
        self.face = ["Pyralis_Mentor.png", "Pyralis_Mentor2.png", "Pyralis_Mentor3.png"]
        self.face2 = ["Nyx_Mentor.png", "Nyx_Mentor2.png", "Nyx_Mentor3.png", "Nyx_Mentor4.png"]

        CONTROLS = controls

        self.Checkpoints = [
            (0,
             "Hey, you there! Wait up!*2"),
            (500,
             "That's it! You're doing well. Okay, keep going!*1"),
            (900,
             ["Carefully jump over this chasm.", "#Use " + key("Up") +" to jump. Hold this key down while you are running for the best results!"]),
            (1300,
             "#This is a monster. To attack, press " + key("B-1") + ". This is your Attack 1 button. Go up to it now, and keep attacking it!"),
            (2000,
             "#To do advanced attacks, you'll need to input more buttons. After using " + key("B-1") + " which is your Attack 1 button,"
             " use " + key("B-2") + ". If you time it right, you'll joust with your weapon. Do this whilst running for best results!"),
            (2300,
             "You're doing great. Make sure you know how to handle your weapons. Check the weapon timing bar out.. this is vital!$430,410$*1"),
            (2740,
             "#This is your first treasurebox... It can be activated. Walking up to it shows its name."),
            (2865,
             "#Since this name is shown, you can activate this object. Press " + key("B-3") + " to open it! Check the top of the screen to see"
             " what you got."),
            (2900,
             "#Hopefully you got the potion. You can get to the status menu by pressing " + key("B-9") + ". Do this to"
             " drink the potion! This menu is also available outside of levels!"),
            (3000,
             "#Using magic is a valid way of getting enemies out of your way. Pressing your Attack 4 button, " + key("B-4") + ", you will"
             " focus your thoughts. This is how any magical spell starts. Try pressing " + key("B-4") + " now, after this box."),
            (3250,
             "#When the aura is visible, if you press Button 5, " + key("B-5") + ", you will unleash your basic magic (Fire)"
             " attack. Use up/down to make it wave! This will consume mana (see the blue bar in the bottom right!)$490,410$&"),
            (3600,
             "Defeat this next monster with fire. Remember, press " + key("B-4") + ", then quickly " + key("B-5") + "!"),
            (4500,
             "This is all I have time for. Go now, and save the world!")
             ]

        self.Checkpoints2 = [
             (0,
              "Huff, puff!*3"),
             (315,
              "Hey, Nyx! Check out this treasurebox. Why isn't that in the treasure room? I guess you better help the queen collect her treasure, then!"),
             (315,
              "#Press " + key("B-3") + " to open it, making sure you're just next to it."),
             (445,
              "Now, I hope you got whatever was inside the treasurebox!*1"),
             (445,
              "#It tells you what you got in the top right of the screen."),
             (445,
              "Oh no! It looks like the castle's floor has been broken and shifted by the earthquake! I need you to make a big leap up here.*2"),
             (445,
              "#Press and hold " + key("Up") + " to make the jump. It's done best whilst running."),
             (860,
              "Oh, I fear it is worse than I expected! The castle is ruined! We should get out of here!*2"),
             (1185,
              "#Sometimes treasure boxes are empty. You'll still need to open them all for a 100% Treasure rating."),
             (1385,
              ["Ooh, a potion! Let's drink it.", "#Bring up the in-game menu with " + key("B-9") + " and drink the potion if you got it. You can also"
               " use this menu from outside of levels!"
               ]),
             (1490,
              "Oh dear, the Arexes have made a new home out of our hallways. You will have to dispose of them... Either attack them with " + key("B-1") + " or"
              " use some of your icy magic by pressing " + key("B-4") + ", " + key("B-5") + "! You might like to"
              " see what abilities you have. You can find out from the menu (press " + key("B-9") + ".)*2"),
             (1550,
              "#When the aura is visible, if you press Button 5, " + key("B-5") + ", you will unleash your basic magic (ice)"
              " attack. This will consume mana (see the blue bar in the bottom right!)$490,410$&"),
             (2865,
              "Alright, that was good. Now keep on the lookout for bits of the castle ceiling that might give way. To look up, hold " + key("B-8") + " and"
              " then use " + key("Up") + ".")
             ]

        for i in range(len(self.Checkpoints)):
            self.Checkpoints[i] = [self.Checkpoints[i], 0]

        for i in range(len(self.Checkpoints2)):
            self.Checkpoints2[i] = [self.Checkpoints2[i], 0]


        # Flags for tutorial


        self.FlagMessages = {
            "pod_hit": "#The number that appears above its head is the damage that you dealt. After this message box,"
                       " look for a status window towards the right. It will give you information about the enemy you"
                       " last attacked. You'll also notice these pods regenerate health.",
            "pod_death": ["#You recieve a bit of experience for each monster you slay,"
                         " and accumulating this experience allows you to become more powerful. To see how much you got,"
                         " look in the battle status window. Your experience bar will fill up.$475,370$",
                          "Hey, it left behind some life and mana force. These green and blue orbs regenerate your health and mana."],
            "pod_collide": ["Ouch! You lost some health!*2",
                            "#The number over your head"
                            " tells you how much. You can see the health you have in the bottom left.$100,410$"],

            "cspider_hit": "#The number that appears above its head is the damage that you dealt. After this message box,"
                       " look for a status window towards the right. It will give you information about the enemy you"
                       " last attacked.",
            "cspider_death": ["#You recieve a bit of experience for each monster you slay,"
                         " and accumulating this experience allows you to become more powerful. To see how much you got,"
                         " look in the battle status window. Your experience bar will fill up.$475,370$",
                          "Hey, it left behind some life and mana force. These green and blue orbs regenerate your health and mana."],
            "cspider_collide": ["Oops! You took some damage!*2",
                            "#The number over your head"
                            " tells you how much. You can see the health you have in the bottom left.$100,410$"]
            }

        self.ExtraFlags = []

        self.AlwaysFlag = []

        self.Flags = dict.fromkeys(
            self.FlagMessages.keys() + self.ExtraFlags,
            False)


    def playerat(self, x):
        for i in range(len(self.Checkpoints)):
            if self.Checkpoints[i][1] > 0: self.Checkpoints[i][1] += 1; continue
            if x > self.Checkpoints[i][0][0]:
                self.Checkpoints[i][1] = 1
                self.Text = self.Checkpoints[i][0][1]
                self.cpt = self.Checkpoints[i][0][0]
                break

        if 2500 > x > 700 and not self.playerclass:
            self.startraining = True
        if x > 2500 and not self.playerclass:
            self.startraining = False

    def tick(self):
        if self.startraining:
            self.RAIN += 0.2
            if self.RAIN > 100:
                self.RAIN = 100
        else:
            self.RAIN -= 0.6
            if self.RAIN < 0:
                self.RAIN = 0

    def poll(self):
        r = self.Text
        self.Text = ""
        return r, self.cpt, self.face

    def playeraction(self, action):
        if self.Flags.has_key(action):
            if not self.Flags[action] or action in self.AlwaysFlag:
                self.Text = self.FlagMessages[action]
            self.Flags[action] = True
