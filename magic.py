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

import pygame, math, random
from pygame.locals import *

def ground_at(LEVEL, x, f=False):
    "Finds the y co-ordinate of the ground at position x."
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
        if ysense <= 0: return 479
    return ysense

def m_init_data(data):
    global DATA
    DATA = data

class Spell: # Spell is a class that (basically) all spells are based on
    def __init__(self, caster, x, y):
        self.cost = 0
        self.x = x
        self.y = y
        self.caster = caster
        self.a_step = 0
        self.ticker = 0
        self.LEVELSTATE = None
        self.MONSTERSTATE = None
        self.RAIN_H = False
        self.finished = False

        self.SOUND = ""
        self.fvm = None # Faceview monster
        self.fvd = 0 # faceview damage

        self.s_init()

    def s_init(self):
        pass

    def blit(self, surf, ALT_X = 0, ALT_Y = 0):
        if not self.finished: self.s_blit(surf, ALT_X, ALT_Y)

    def tick(self, LEVEL, MONSTERS, CASTER, RAIN = False):
        if self.finished: return
        self.RAIN_H = RAIN
        self.LEVELSTATE = LEVEL
        self.MONSTERSTATE = MONSTERS
        self.ticker += 1
        self.caster = CASTER
        self.stick()

class Fire_1(Spell):
    def s_init(self):
        self.cost = 4
        if self.caster.mp[0] < self.cost: self.finished = True; return
        self.frames = ["m_fire1_" + str(x) + ".png" for x in range(1,6)]
        self.flame_entities = []
        self.caster.mbreaktime = 16
        self.caster.mp[0] -= self.cost
        self.mydir = self.caster.direction * 2 - 1
        self.unchdir = self.caster.direction
        self.x += self.mydir * 10
        self.rise = 0

    def s_blit(self, surf, ALT_X, ALT_Y):
        c = 0
        for flame in self.flame_entities:
            if flame == -40: continue
            gimg, grect = DATA.mag_images["m_fire1_glow.png"]
            img, rect = DATA.mag_images[self.frames[flame%5]]
            rect.midbottom = (self.x + flame*8, self.y-math.sin(flame/2.0)*5.0+c*self.rise+((c+0.001)**(abs(self.rise)+1))*[1,-1][self.rise<0])
            rect.move_ip(ALT_X, ALT_Y)
            grect.midbottom = (self.x + flame*8, self.y-math.sin(flame/2.0)*5.0+c*self.rise+((c+0.001)**(abs(self.rise)+1))*[1,-1][self.rise<0])
            grect.move_ip(ALT_X, ALT_Y+3)
            surf.blit(img, rect)
            surf.blit(gimg, grect)
            c += 1

    def stick(self):

        self.y = self.caster.y - 25
        self.x = self.caster.x
        self.caster.jumping = False
        if len(self.flame_entities) < 8:
            self.caster.direction = self.unchdir

        if not self.ticker % 2:
            if len(self.flame_entities) < 8:
                self.flame_entities = [0] + self.flame_entities

        self.flame_entities = [[x + self.mydir,-40][[x<-35 or x>0,x>35 or x<0][self.unchdir]] for x in self.flame_entities]
            

        if self.caster.up_held: self.rise -= 0.05
        if self.caster.down_held: self.rise += 0.05

        # Collision detections

        c = 0
        for flame in self.flame_entities:

            if flame == -40: continue
            img, rect = DATA.mag_images[self.frames[flame%5]]
            rect.midbottom = (self.x + flame*8, self.y-math.sin(flame/2.0)*5.0+c*self.rise+((c+0.001)**(abs(self.rise)+1))*[1,-1][self.rise<0])

            if self.check_collide(rect):
                self.flame_entities[c] = -40

            c += 1

        if sum(self.flame_entities) == 8 * -40:
            self.finished = True

    def check_collide(self, crect):
        for monster in self.MONSTERSTATE:
            monsterrect = pygame.rect.Rect((0,0,monster.collision_dist*2,monster.collision_hdist*2))
            monsterrect.center = monster.x, monster.y
            if crect.colliderect(monsterrect):
                damage = (self.caster.magic[0] * 3)/15.0
                self.caster.combodamage += min(damage, monster.hp)
                monster.react_to_magic(damage)
                self.fvm = monster
                self.fvd = damage
                self.caster.combo += 1
                return True
        return False

class Summon(Spell):
    def s_init(self):
        self.caster.mbreaktime = 20
        self.rays = []
        self.alphamod = 0.0
    def s_blit(self, surf, ALT_X, ALT_Y):
        global DATA
        alphamult = self.alphamod / 100.0
        if alphamult > 0:
            for width, phase, magnitude in self.rays:
                rayrect = Rect(0, 0, width, 480)
                variance = math.sin(phase) * magnitude
                rayrect.midbottom = self.caster.x + variance, self.caster.y
                raysurf = pygame.Surface(rayrect.size)
                colour = (int(20 + magnitude * 2.5), 50 + width * 3, int(220 - phase * 10))
                raysurf.fill(colour)
                relalpha = max(0, min(255, 255 - (abs(variance)) * (255/100.0))) * 0.3
                raysurf.set_alpha(alphamult * relalpha)
                surf.blit(raysurf, rayrect.move(ALT_X, ALT_Y))
                
    def stick(self):
        ri = random.randint
        if self.alphamod and self.caster.mbreaktime:
            self.caster.animation = "Stopped"
            self.caster.torso_animation = "Cast"


        if self.ticker < 25:
            # Creation of rays phase
            if not self.ticker % 3:
                self.rays.append([ri(5,35), ri(-30,30)/10.0, ri(5, 30)]) # Width, phase, magntd

            self.alphamod = min(self.alphamod + 7.5, 100)

        if self.ticker > 25:
            self.alphamod -= 10
            if self.alphamod < 0: self.alphamod = 0; self.finished = True

        for r in range(len(self.rays)):
            ray = self.rays[r]
            self.rays[r][1] += ray[2]/300.0

class Burst(Spell):
    def s_init(self):
        global DATA
        self.caster.mbreaktime = 30
    def s_blit(self, surf, ALT_X, ALT_Y):
        global DATA
        self.mticker = -abs(self.ticker-15)+15
        pic = DATA.mag_images["Burst.png"][0]
        msurf = pygame.transform.scale(pic, (max(5, min(185, self.mticker**3))+15, max(5, min(185, self.mticker**3))+15))
        msurf = pygame.transform.rotate(msurf, self.ticker**1.8)
        rect = msurf.get_rect()
        rect.center = (self.x + ALT_X, self.y + ALT_Y)
        surf.blit(msurf, rect)
        if self.ticker >= 30:
            self.finished = True
    def stick(self):
        self.x, self.y = self.caster.x, self.caster.y - 40
        if self.ticker%3: return
        for monster in self.MONSTERSTATE:
            dist = abs(monster.x - self.x) + abs(monster.y - self.y)
            if dist > 110:
                continue
            monster.react_to_magic(0)

class Ice_1(Spell):
    def s_init(self):
        global DATA
        self.affected = []
        self.cant = self.caster.mp < 4
    def s_blit(self, surf, ALT_X, ALT_Y):
        global DATA
        if not self.affected:
            if self.ticker >= 0: self.finished = True
            return
        self.mticker = -abs(self.ticker-15)+15
        msurf = pygame.transform.scale(DATA.mag_images["ice.png"][0], (max(5, min(125, self.mticker**2))+15, max(5, min(125, self.mticker**2))+15))
        msurf = pygame.transform.rotate(msurf, self.ticker**1.7)
        rect = msurf.get_rect()
        for mon in self.affected:
            rect.center = (mon.x + ALT_X, mon.y-40 + ALT_Y)
            surf.blit(msurf, rect)
            if self.ticker == 10:
                dmg = int(random.randint(80,120)/100.0 * self.caster.magic[0] * 0.6)
                self.caster.combodamage += min(dmg, mon.hp)
                mon.react_to_magic(dmg)
                self.fvm = mon
                self.fvd = dmg
                self.caster.combo += 1

        if self.ticker >= 30:
            self.finished = True

    def stick(self):
        if self.affected == []:
            for monster in self.MONSTERSTATE:
                xdist = abs(monster.x-self.caster.x)
                if xdist < 300 and not monster.isdead:
                    if self.caster.mp[0] >= 4:
                        self.affected.append(monster)
                        self.caster.mp[0] -= 4
            if len(self.affected):
                self.SOUND = "Ice.ogg"
                self.caster.animation = "Stopped"
                self.caster.torso_animation = "Cast"
                self.caster.frame = 0
                self.caster.tframe = 0
                self.caster.casting = True
                self.caster.mbreaktime = 30

class Ice_2(Ice_1):
    def s_init(self):
        global DATA
        self.affected = []
        self.cant = self.caster.mp[0] < 8
    def s_blit(self, surf, ALT_X, ALT_Y):
        global DATA
        if not self.affected:
            if self.ticker >= 0: self.finished = True
            return
        self.mticker = -abs(self.ticker-15)+15
        msurf = pygame.transform.scale(DATA.mag_images["ice2.png"][0], (max(5, min(125, self.mticker**2))+15, max(5, min(125, self.mticker**2))+15))
        msurf = pygame.transform.rotate(msurf, self.ticker**1.7)
        rect = msurf.get_rect()
        for mon in self.affected:
            rect.center = (mon.x + ALT_X, mon.y-40 + ALT_Y)
            surf.blit(msurf, rect)
            if self.ticker == 10:
                dmg = int(random.randint(80,120)/100.0 * self.caster.magic[0] * 1.1)
                self.caster.combodamage += min(dmg, mon.hp)
                mon.react_to_magic(dmg)
                self.fvm = mon
                self.fvd = dmg
                self.caster.combo += 1


        if self.ticker >= 30:
            self.finished = True

    def stick(self):
        if self.affected == []:
            for monster in self.MONSTERSTATE:
                xdist = abs(monster.x-self.caster.x)
                if xdist < 300 and not monster.isdead:
                    if self.caster.mp[0] >= 8:
                        self.affected.append(monster)
                        self.caster.mp[0] -= 8
            if len(self.affected):
#                self.affected = reduce(lambda m1,m2:[m1,m2][abs(m2.x-self.caster.x)<abs(m1.x-self.caster.x)], self.affected)
#                attacks (1) closest enemy ^ ^ ^ ^ ^ ^ ^
                self.SOUND = "Ice.ogg"
                self.caster.animation = "Stopped"
                self.caster.torso_animation = "Cast"
                self.caster.frame = 0
                self.caster.tframe = 0
                self.caster.casting = True
                self.caster.mbreaktime = 45

class Fire_2(Spell):
    def s_init(self):
        self.cost = 12
        if self.caster.mp[0] < self.cost: self.finished = True; return
        self.frames = ["m_fire1_" + str(x) + ".png" for x in range(1,6)]
        self.flame_entities = []
        self.caster.mbreaktime = 40
        self.caster.mp[0] -= self.cost
        self.mydir = self.caster.direction * 2 - 1
        self.unchdir = self.caster.direction
        self.x += self.mydir * 10
        self.rise = 0

    def s_blit(self, surf, ALT_X, ALT_Y):
        c = 0
        for flame in self.flame_entities:
            if flame == -666: continue
            gimg, grect = DATA.mag_images["m_fire1_glow.png"]
            img, rect = DATA.mag_images[self.frames[flame%5]]
            rect.midbottom = (self.x + flame*4, self.y-math.sin(flame/2.0)*5.0+c*self.rise+((c+0.001)**(abs(self.rise)+1))*[1,-1][self.rise<0])
            rect.move_ip(ALT_X, ALT_Y)
            grect.midbottom = (self.x + flame*4, self.y-math.sin(flame/2.0)*5.0+c*self.rise+((c+0.001)**(abs(self.rise)+1))*[1,-1][self.rise<0])
            grect.move_ip(ALT_X, ALT_Y+3)
            for y in range(-1,2):
                surf.blit(img, rect.move(0,y*flame))
                surf.blit(gimg, grect.move(0, y*flame))
            c += 1

    def stick(self):

        self.y = self.caster.y - 25
        self.x = self.caster.x
        self.caster.jumping = False
        if len(self.flame_entities) < 8:
            self.caster.direction = self.unchdir

        if not self.ticker % 2:
            if len(self.flame_entities) < 8:
                self.flame_entities = [0] + self.flame_entities

        self.flame_entities = [[x + self.mydir,-666][[x<-65 or x>0,x>65 or x<0][self.unchdir]] for x in self.flame_entities]
            

        if self.caster.up_held: self.rise -= 0.05
        if self.caster.down_held: self.rise += 0.05

        # Collision detections

        c = 0
        for flame in self.flame_entities:

            if flame == -666: continue
            img, rect = DATA.mag_images[self.frames[flame%5]]
            rect.midbottom = (self.x + flame*4, self.y-math.sin(flame/2.0)*5.0+c*self.rise+((c+0.001)**(abs(self.rise)+1))*[1,-1][self.rise<0])

            for y in range(-1,2):
                if self.check_collide(rect.move(0, y*flame)):
                    self.flame_entities[c] = -666

            c += 1

        if sum(self.flame_entities) == 8 * -666:
            self.finished = True

    def check_collide(self, crect):
        for monster in self.MONSTERSTATE:
            monsterrect = pygame.rect.Rect((0,0,monster.collision_dist*2,monster.collision_hdist*2))
            monsterrect.center = monster.x, monster.y
            if crect.colliderect(monsterrect):
                damage = (self.caster.magic[0] * 8)/60.0
                self.caster.combodamage += min(monster.hp, damage)
                monster.react_to_magic(damage)
                self.fvm = monster
                self.fvd = damage
                self.caster.combo += 1
                return True
        return False

class Quake(Spell):
    def s_init(self):
        self.cost = 15
        if self.caster.mp[0] < self.cost: self.finished = True; return
        self.caster.mbreaktime = 26
        self.caster.mp[0] -= self.cost
        self.ticker = 0
        self.px = 0
        self.py = 0

    def s_blit(self, surf, ALT_X, ALT_Y):
        self.caster.quaking = True

    def stick(self):
        self.ticker += 1
        hitlist = []
        if not self.ticker%20:
            for mon in self.MONSTERSTATE:
                if mon.x > self.caster.x - 350 and mon.x < self.caster.x + 350:
                    if mon.affected["quake"]:
                        hitlist.append(mon)
            for monster in hitlist:
                damage = self.caster.magic[0] * 0.8
                damage *= random.randint(75, 125)/100.0
                self.caster.combodamage += min(damage, monster.hp)
                monster.react_to_damage(int(damage))
                self.caster.combo += 1


        if self.ticker == 100:
            self.finished = True
            self.caster.quaking = False


class Implosion_1(Spell):
    def s_init(self):
        global DATA
        self.affected = []
        self.cant = self.caster.mp < 15
    def s_blit(self, surf, ALT_X, ALT_Y):
        global DATA
        pic = DATA.mag_images["bubble.png"][0]
        if not self.affected:
            if self.ticker >= 0: self.finished = True
            return

        for mon in self.affected:
            moncentre = (mon.x + ALT_X, mon.y-40 + ALT_Y)
            eachang = (math.pi/4)
            r = max(0, 300 - self.ticker*15)
            turn = self.ticker / 5.0
            sp = max(4, 20-self.ticker/2)
            for x in range(8):
                for c in range(10):
                    xp = math.cos(x * eachang + turn + (c * 0.15)*(-1**c)) * (r + c * sp)
                    yp = math.sin(x * eachang + turn + (c * 0.15)*(-1**c)) * (r + c * sp)
                    rect = pic.get_rect()
                    rect.center = moncentre
                    rect.move_ip(xp, yp)
                    surf.blit(pic, rect)

    def stick(self):
        if self.affected == []:
            for monster in self.MONSTERSTATE:
                xdist = abs(monster.x-self.caster.x)
                if xdist < 400 and not monster.isdead:
                    if self.caster.mp[0] >= 15:
                        self.affected.append(monster)

            self.affected.sort(lambda x, y: cmp(y.maxhp, x.maxhp))

            if len(self.affected):
                self.affected = self.affected[:1]
                self.caster.mp[0] -= 15
                self.SOUND = "Implosion.ogg"
                self.caster.animation = "Stopped"
                self.caster.torso_animation = "Cast"
                self.caster.frame = 0
                self.caster.tframe = 0
                self.caster.casting = True
                self.caster.mbreaktime = 25

        for mon in self.affected:
            if self.ticker >= 20 and not self.ticker%5:
                dmg = int(random.randint(90,155)/100.0 * self.caster.magic[0] * 0.8)
                self.caster.combodamage += min(dmg, mon.hp)
                mon.react_to_magic(dmg)
                self.fvm = mon
                self.fvd = dmg
                self.caster.combo += 1

        if self.ticker >= 31:
            self.finished = True


class Summon_Maea(Spell):
    def s_init(self):
        global DATA
        self.cost = 80
        if self.caster.mp[0] < self.cost: self.finished = True; return
        self.caster.mbreaktime = 50
        self.caster.mp[0] -= self.cost
        self.dir = self.caster.direction
        self.x = [640, -262][self.dir]
        self.inertia = [-10, 10][self.dir]
        self.bubbles = []
        self.bombs = []
        self.y = 50
        self.inertia2 = 0

        self.mouthpos = (130, 50)

    def s_blit(self, surf, ALT_X, ALT_Y):
        global DATA

        darkness = pygame.Surface((640, 480))
        if self.ticker < 120:
            darkness.set_alpha(7 * min(30, self.ticker))
        else:
            darkness.set_alpha(max(0, 1050 - self.ticker*7))

        surf.blit(darkness, (0,0))

        if self.dir:
            surf.blit(DATA.images["Summon1.png"][0], (self.x, self.y))
        else:
            surf.blit(pygame.transform.flip(DATA.images["Summon1.png"][0], True, False), (self.x, self.y))

        for x, y, p in self.bombs:
            bfs, bfr = DATA.images["bluefire.png"]
            nbfs = pygame.transform.scale(bfs, (int(math.cos(-p/2) * 240), int(math.sin(p) * 250)))
            nbfr = nbfs.get_rect()
            nbfr.midbottom = (x, y + 5)
            nbfr.move_ip(ALT_X, ALT_Y)
            surf.blit(nbfs, nbfr)

        for x, y, a in self.bubbles:
            bs, br = DATA.mag_images["bubble.png"]
            surf.blit(bs, br.move(self.mouthpos).move(x,y))

    def stick(self):
        self.x += self.inertia
        if self.dir:
            self.inertia -= 0.1
        else:
            self.inertia += 0.1

        self.inertia2 += 0.01
        self.y += self.inertia2

        if self.x < -280 or self.x > 658: self.finished = True

        if self.ticker <= 100 and not self.ticker%9:
            if self.dir:
                sp = int(self.caster.x - 300)
            else:
                sp = int(self.caster.x + 300)

            cx = [sp - self.ticker * 8, sp + self.ticker * 8][self.dir]
            self.bombs.append([cx, ground_at(self.LEVELSTATE, cx, True), 0])

        # We want angle to swing like a pendulum between 45 and 135 degrees
        degree_variance = math.sin(self.ticker/6.0) * 80
        bdv = -degree_variance
        degree = degree_variance + 90
        angle = math.radians(degree)
        self.bubbles.append([self.x, self.y, angle])
        degree = bdv + 90
        angle = math.radians(degree)
        self.bubbles.append([self.x, self.y, angle])

        for b in range(len(self.bubbles)):
            self.bubbles[b][0] += math.cos(self.bubbles[b][2]) * 10
            self.bubbles[b][1] += math.sin(self.bubbles[b][2]) * 10

        for z in range(len(self.bombs)):
            self.bombs[z][2] += 0.1
            if self.bombs[z][2] > 3:
                self.bombs[z] = None
                continue

            hitlist = []
            if abs(self.bombs[z][2] - 1.1) < 0.0000001:
                for monster in self.MONSTERSTATE:
                    if abs(monster.x - self.bombs[z][0]) < 100:
                        if monster.y > self.bombs[z][1] - 220:
                            hitlist.append(monster)

            for monster in hitlist:
                damage = self.caster.magic[0] * random.randint(8, 12) / 20.0
                monster.react_to_damage(int(damage))
                self.fvm = monster
                self.fvd = damage

                self.caster.Take_Damage(-1)

        biggerhitlist = []
        for monster in self.MONSTERSTATE:
            if abs(monster.x - self.x) < 400:
                if monster not in biggerhitlist:
                    biggerhitlist.append(monster)
        for monster in biggerhitlist:
            damage = 1
            monster.react_to_damage(int(damage))
            self.fvm = monster
            self.fvd = damage
                

        while None in self.bombs:
            self.bombs.remove(None)

