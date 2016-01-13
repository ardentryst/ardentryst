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

import random, pygame, math

def monster_ground_at(x, l, f=1):
    "Finds the y co-ordinate of the ground at position x. For monsters."
    x = int(x)
    LEVEL = l
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
        ysense -= f
    if ysense == 479: return 666 # Has to be greater than 500
    return ysense

class Monster:
    def __init__(self):

        # Vitals
        self.name = "?????"
        self.presentable_name = "?????"
        self.x = 0
        self.y = 0
        self.a_prefix = ""
        self.a_frame = 1
        self.ticker = 0
        self.diedyet = False
        self.isdead = False
        self.collision_dist = 30
        self.collision_hdist = 40 #height

        self.active = False
        self.PLAYDEMO = False

        # Self's stats
        self.hp = 0
        self.maxhp = 0
        self.projectile_damage = 5
        self.ghost = False
        self.affected = {"quake": False}

        # Rewards
        self.reward_exp = 0
        self.reward_hp = [0]
        self.reward_items = []

        # Visuals
        self.numbers = []
        self.projectiles = []

        # Contact to the outside world
        self.chimed = False
        self.useprojectilecollision = True
        self.SOUND = ""
        self.SOUNDTIME = 0
        self.AFTERSOUND = 5
        self.REMOVEME = False
        self.SPAWN_GOODIES = False
        self.ALPHA = 255
        self.FLIPME = False
        self.EXECUTE = ""
        self.BOSS = False

        self.slayercount = False

        self.PLAYERSTATE = None
        self.LEVELSTATE = None

    def inscreen(self, CX):
        if CX - 50 <= self.x <= CX + 690:
            return True
        return False

    def update(self, x, y):
        self.x = x
        self.y = y

    def info(self, pl, lv):
        self.PLAYERSTATE = pl
        self.LEVELSTATE = lv

    def step(self):
        return

    def die(self):
        return

    def tick(self):
        if self.SOUNDTIME > 0: self.SOUNDTIME -= 1
        self.ticker += 1
        if self.hp <= 0:
            if not self.diedyet:
                self.die()
                self.diedyet = True
        self.step()

    def damage(self):
        return

    def collision(self, entity):
        return

    def react_to_damage(self, damage):
        if damage > self.maxhp:
            damage = self.maxhp
        if damage > self.hp:
            damage = self.hp
        if self.isdead: return
        curative = False
        if damage < 0:
            curative = True
        damage = [str(damage),str(damage)[1:]][curative]
        damage = str(int(round(float(damage))))
        if not damage.isdigit():
            print "Damage was not a digit!"
            return

        num_info = [curative]

        phase = 0
        bounce_height = 40

        for digit in damage:
            num_info.append(
                [digit, phase, bounce_height]
                )
            phase += 1

        if not self.PLAYDEMO:
            self.numbers.append(num_info)

            self.hp -= int(float(damage))

        if self.hp > 0:
            self.damage()

    def react_to_magic(self, damage):

        if damage > self.maxhp:
            damage = self.maxhp
        if damage > self.hp:
            damage = self.hp
        if self.isdead: return
        curative = False
        if damage < 0:
            curative = True
        damage = [str(damage),str(damage)[1:]][curative]
        damage = str(int(round(float(damage))))
        if not damage.isdigit():
            print "Damage was not a digit!"
            return

        num_info = [curative]

        phase = 0
        bounce_height = 40

        for digit in damage:
            num_info.append(
                [digit, phase, bounce_height]
                )
            phase += 1

        self.numbers.append(num_info)

        self.hp -= int(float(damage))
        if self.hp > 0:
            self.damage()

    def Advance_Numbers(self):
        for i in range(len(self.numbers)):
            for j in range(len(self.numbers[i])):
                if j == 0: continue
                self.numbers[i][j][1] += 1.5
                if self.numbers[i][j][1] >= 84:
                    self.numbers[i] = None
                    break

        while None in self.numbers:
            self.numbers.remove(None)


class pod(Monster):
    def m_init(self):
        self.name = "pod"
        self.presentable_name = "Nepthene"
        self.hp = 40
        self.maxhp = self.hp
        self.reward_exp = 5
        self.reward_hp = [6, 2, 3, 5,
                          1, 3, 10]
        self.reward_mp = [2, 2, 4,
                          ]
        self.reward_items = [
            (55, "Nepthene tongue"),
            (1, "Nepthene fibre leggings")]
                             
        self.a_prefix = "rest"
        self.a_frame = 1
        self.barb_pain = 4
        self.collision_dist = 25
        self.barbtime = 0
        self.rechargehp = 0
        self.affected["quake"] = True
    def step(self):
        if self.isdead:
            self.a_prefix = "hurt"
            self.a_frame = 1
            self.ticker = 0
            self.ALPHA -= 8
            if self.ALPHA <= 0: self.ALPHA = 0; self.REMOVEME = True
        else:

            self.rechargehp += 0.08
            if self.rechargehp >= 1:
                self.rechargehp = 0
                self.hp += 1
                if self.hp > self.maxhp:
                    self.hp = self.maxhp
            if self.barbtime: self.barbtime -= 1

            if not self.ticker%16:
                self.a_prefix = "rest"
                self.a_frame += 1
                if self.a_frame >= 3:
                    self.a_frame = 1
    def die(self):
        self.SOUND = "death"
        self.isdead = True
        self.SPAWN_GOODIES = True
    def damage(self):
        self.a_frame = 1
        self.a_prefix = "hurt"
        self.ticker = 8
        self.SOUND = "hurt"
        self.AFTERSOUND = 6
    def collision(self, entity):
        if entity.x > self.x: entity.inertia[0] = random.randint(3,6)
        else: entity.inertia[0] = random.randint(-6,-3)
        if not self.barbtime:
            entity.raw_hit(self.barb_pain * (random.randint(60,140)/100.0))
            self.barbtime = 20
            self.SOUND = "barb"

class poispod(Monster):
    def m_init(self):
        self.name = "poispod"
        self.presentable_name = "Venom Nepthene"
        self.hp = 85
        self.maxhp = self.hp
        self.reward_exp = 18
        self.reward_hp = [7, 9, 8, 10,
                          5, 7, 14, 0]
        self.reward_mp = [4, 7, 6, 0, 0
                          ]
        self.reward_items = [(50, "Nepthene tongue")]
        self.a_prefix = "rest"
        self.a_frame = 1
        self.barb_pain = 10
        self.collision_dist = 25
        self.barbtime = 0
        self.rechargehp = 0
        self.affected["quake"] = True
        self.gasdown = 0
    def step(self):
        if self.isdead:
            self.a_prefix = "hurt"
            self.a_frame = 1
            self.ticker = 0
            self.ALPHA -= 8
            if self.ALPHA <= 0: self.ALPHA = 0; self.REMOVEME = True
        else:

            if self.gasdown:
                self.gasdown -= 1

            if self.gasdown == 1:
                self.EXECUTE = "Objects.append(Gas(" + str(self.x) + "," + str(self.y - 6) + "))"

            self.rechargehp += 0.16
            if self.rechargehp >= 1:
                self.rechargehp = 0
                self.hp += 1
                if self.hp > self.maxhp:
                    self.hp = self.maxhp
            if self.barbtime: self.barbtime -= 1

            if not self.ticker%120:
                self.gasdown = 25

            if self.gasdown > 0:
                self.a_prefix = "rest"
                self.a_frame = 3

            elif not self.ticker%16:
                self.a_prefix = "rest"
                self.a_frame += 1
                if self.a_frame >= 3:
                    self.a_frame = 1

    def die(self):
        self.SOUND = "death"
        self.isdead = True
        self.SPAWN_GOODIES = True
    def damage(self):
        self.a_frame = 1
        self.a_prefix = "hurt"
        self.ticker = 8
        self.SOUND = "hurt"
        self.AFTERSOUND = 6
    def collision(self, entity):
        if random.randint(0, 4) == 0: entity.bits["poisoned"] = True
        if entity.x > self.x: entity.inertia[0] = random.randint(3,6)
        else: entity.inertia[0] = random.randint(-6,-3)
        if not self.barbtime:
            entity.raw_hit(self.barb_pain * (random.randint(60,140)/100.0))
            self.barbtime = 30
            self.SOUND = "barb"


class spider(Monster):
    def m_init(self):
        self.name = "spider"
        self.presentable_name = "Forest Arex"
        self.hp = 20
        self.maxhp = self.hp
        self.reward_exp = 3
        self.reward_hp = [2, 1, 3, 2,
                          0, 0, 0]
        self.reward_mp = [1, 0, 0,
                          ]
        self.reward_items = []
        self.a_prefix = "rest"
        self.a_frame = 1
        self.collision_dist = 20
        self.collision_hdist = 40

        self.hittime = 0
        self.upjump = 0

        self.basex = 0
        self.basey = 0

        self.angle = 1.5 * math.pi
        self.swing = 0

    def step(self):
        if self.isdead:
            self.ticker = 1
            self.ALPHA -= 8
            if self.ALPHA <= 0: self.ALPHA = 0; self.REMOVEME = True
        else:

            if self.basey == 0: self.basey = self.y
            if self.basex == 0: self.basex = self.x
            
            if self.upjump > 1:
                self.basey -= self.upjump
                self.upjump *= 0.9
            else:
                self.upjump = 0
            if self.hittime > 0: self.hittime -= 1
            if self.basey < self.PLAYERSTATE.y:
                self.basey += 2
            elif self.y - 5 > self.PLAYERSTATE.y:
                if self.upjump == 0:
                    self.upjump = 7


        mga = monster_ground_at(self.x, self.LEVELSTATE, 8)
        if mga > self.y - 20:
            self.y = min(-(math.sin(self.angle) * self.basey), mga-10)
            self.x = self.basex + math.cos(self.angle) * self.basey

        if abs(self.swing) > 0.01:
            self.angle += 0.01*self.swing
            self.swing *= 0.8
        else:
            self.swing = 0

        if self.angle > 1.53*math.pi:
            self.swing -= 0.11
        elif self.angle < 1.47*math.pi:
            self.swing += 0.11

        if not self.ticker%16:
            self.a_frame +=1
            if self.a_frame == 3:
                self.a_frame = 1

    def die(self):
        self.isdead = True
        self.SPAWN_GOODIES = True
        self.swing = cmp(self.x, self.PLAYERSTATE.x) * (480-self.basey)/40
        self.SOUND = "squeak"

    def damage(self):
        self.AFTERSOUND = 6
        self.swing = cmp(self.x, self.PLAYERSTATE.x) * (480-self.basey)/40
        self.SOUND = "squeak"

    def collision(self, entity):
        self.swing = cmp(self.x, self.PLAYERSTATE.x) * (480-self.basey)/40
        if not self.hittime:
            entity.raw_hit(random.randint(1,2))
            self.hittime = 24
            self.swing = cmp(self.x, self.PLAYERSTATE.x) * (480-self.basey)/24

class cspider(Monster):
    def m_init(self):
        self.name = "cspider"
        self.presentable_name = "Arex"
        self.hp = 20
        self.maxhp = self.hp
        self.reward_exp = 3
        self.reward_hp = [3, 3, 5, 3,
                          1, 1, 1]
        self.reward_mp = [3, 1, 1,
                          ]
        self.reward_items = []
        self.a_prefix = "rest"
        self.a_frame = 1
        self.collision_dist = 20
        self.collision_hdist = 40

        self.hittime = 0
        self.upjump = 0

        self.basex = 0
        self.basey = 0

        self.angle = 1.5 * math.pi
        self.swing = 0

    def step(self):
        if self.isdead:
            self.ticker = 1
            self.ALPHA -= 8
            if self.ALPHA <= 0: self.ALPHA = 0; self.REMOVEME = True
        else:

            if self.basey == 0: self.basey = self.y
            if self.basex == 0: self.basex = self.x
            
            if self.upjump > 1:
                self.basey -= self.upjump
                self.upjump *= 0.9
            else:
                self.upjump = 0
            if self.hittime > 0: self.hittime -= 1
            if self.basey < self.PLAYERSTATE.y:
                self.basey += 2
            elif self.y - 5 > self.PLAYERSTATE.y:
                if self.upjump == 0:
                    self.upjump = 7


        mga = monster_ground_at(self.x, self.LEVELSTATE, 8)
        if mga > self.y - 20:
            self.y = min(-(math.sin(self.angle) * self.basey), mga-10)
            self.x = self.basex + math.cos(self.angle) * self.basey

        if abs(self.swing) > 0.01:
            self.angle += 0.01*self.swing
            self.swing *= 0.8
        else:
            self.swing = 0

        if self.angle > 1.53*math.pi:
            self.swing -= 0.11
        elif self.angle < 1.47*math.pi:
            self.swing += 0.11

        if not self.ticker%16:
            self.a_frame +=1
            if self.a_frame == 3:
                self.a_frame = 1

    def die(self):
        self.isdead = True
        self.SPAWN_GOODIES = True
        self.swing = cmp(self.x, self.PLAYERSTATE.x) * (480-self.basey)/40
        self.SOUND = "squeak"

    def damage(self):
        self.AFTERSOUND = 6
        self.swing = cmp(self.x, self.PLAYERSTATE.x) * (480-self.basey)/40
        self.SOUND = "squeak"

    def collision(self, entity):
        self.swing = cmp(self.x, self.PLAYERSTATE.x) * (480-self.basey)/40
        if not self.hittime:
            entity.raw_hit(random.randint(1,3))
            self.hittime = 24
            self.swing = cmp(self.x, self.PLAYERSTATE.x) * (480-self.basey)/24

class giantjelly(Monster):
    def m_init(self):
        self.name = "giantjelly"
        self.presentable_name = "Gelatice"
        self.hp = 200
        self.maxhp = self.hp
        self.reward_exp = 25
        self.reward_hp = [9, 11, 11, 6,
                          12, 4, 12, 0, 0]
        self.reward_mp = [7, 7, 4, 0, 0
                          ]
        self.reward_items = [(50, "Potion2"),
                             (40, "Mana potion"),
                             (5, "Haste ring")]
        self.a_prefix = "move"
        self.a_frame = 1

        self.pain = 8
        self.inert = 0
        self.fall = 0
        self.collision_dist = 50
        self.collision_hdist = 70

        self.hittime = 0
        self.sling = True
        self.slingt = 0
#        self.imgheight = 40
        self.affected["quake"] = True

    def step(self):
        if self.isdead:
            self.a_prefix = "hurt"
            self.a_frame = 1
            self.ticker = 0
            self.ALPHA -= 6
            if self.ALPHA <= 0: self.ALPHA = 0; self.REMOVEME = True
        else:
            p = self.PLAYERSTATE
            if p.x - self.x < 700 and self.sling:
                if p.x < self.x and self.inert > -3:
                    self.inert -= 0.5
                elif p.x > self.x and self.inert < 3:
                    self.inert += 0.5

            self.slingt += 1

            if self.slingt >= 40 and self.sling or self.slingt >= 10 and not self.sling:
                self.slingt = 0
                self.sling = not self.sling
                self.a_prefix = "move"
                self.a_frame = self.sling + 1

        self.y += self.fall

        self.FLIPME = self.PLAYERSTATE.x > self.x
        mga = monster_ground_at(self.x+self.inert, self.LEVELSTATE, 2)
        mgaf = monster_ground_at(self.x+15*cmp(self.inert, 0), self.LEVELSTATE, 3)

        if mga > self.y - 5:
            if mgaf > self.y - 25:
                self.x += self.inert
            if abs(mga - self.y) < 6:
                self.y = mga+2
                self.fall = 0
            else:
                self.fall = min(5, self.fall + 0.5)
        if mgaf < self.y - 25:
            self.inert = 0
            
        self.inert *= 0.85

        if self.hittime:
            self.hittime -= 1

        if self.y > 500:
            self.hp = 0

    def die(self):
        self.SOUND = "hurt"
        self.isdead = True
        self.SPAWN_GOODIES = True
    def damage(self):
        self.a_frame = 1
        self.a_prefix = "hurt"
        self.ticker = 8
        self.SOUND = "hurt"
        self.AFTERSOUND = 6
        if self.PLAYERSTATE.x < self.x:
            self.inert += 2
        else:
            self.inert -= 2
    def collision(self, entity):
        if entity.x > self.x: entity.inertia[0] = random.randint(4,8); self.inert -= .5
        else: entity.inertia[0] = random.randint(-8,-4); self.inert += .5
        if not self.hittime:
            entity.raw_hit(self.pain * (random.randint(60,140)/100.0))
            self.hittime = 10
            self.SOUND = "collide"

class worm(Monster):
    def m_init(self):
        self.name = "worm"
        self.presentable_name = "Anneludine"
        self.hp = 70
        self.maxhp = self.hp
        self.reward_exp = 10
        self.reward_hp = [6, 8, 3, 6,
                          1, 3, 12, 0, 0, 0, 0]
        self.reward_mp = [5, 5, 4,
                          ]
        self.reward_items = [(60, "Anneludine shell"),
                             (42, "Potion"),
                             (26, "Mana potion"),
                             (2, "Silver ring")]
        self.a_prefix = "move"
        self.a_frame = 1

        self.pain = 6
        self.inert = 0
        self.fall = 0

        self.hittime = 0
        self.affected["quake"] = True

    def step(self):
        if self.isdead:
            self.a_prefix = "hurt"
            self.a_frame = 1
            self.ticker = 0
            self.ALPHA -= 8
            if self.ALPHA <= 0: self.ALPHA = 0; self.REMOVEME = True
        else:
            p = self.PLAYERSTATE
            if p.x - self.x < 700:
                if p.x < self.x and self.inert > -1.5:
                    self.inert -= 0.05
                elif p.x > self.x and self.inert < 1.5:
                    self.inert += 0.05

            if not self.ticker%14:
                self.a_prefix = "move"
                self.a_frame = (self.a_frame % 2) + 1

        self.y += self.fall

        self.FLIPME = self.PLAYERSTATE.x > self.x
        mga = monster_ground_at(self.x+self.inert, self.LEVELSTATE, 2)
        mgaf = monster_ground_at(self.x+15*cmp(self.inert, 0), self.LEVELSTATE, 3)

        if mga > self.y - 5:
            if mgaf > self.y - 25:
                self.x += self.inert
            if abs(mga - self.y) < 6:
                self.y = mga+2
                self.fall = 0
            else:
                self.fall = min(5, self.fall + 0.5)
        if mgaf < self.y - 25:
            self.inert = 0
            
        self.inert *= 0.96

        if self.hittime:
            self.hittime -= 1

        if self.y > 500:
            self.hp = 0

    def die(self):
        self.SOUND = "hurt"
        self.isdead = True
        self.SPAWN_GOODIES = True
    def damage(self):
        self.a_frame = 1
        self.a_prefix = "hurt"
        self.ticker = 8
        self.SOUND = "hurt"
        self.AFTERSOUND = 6
        if self.PLAYERSTATE.x < self.x:
            self.inert += 4
        else:
            self.inert -= 4
    def collision(self, entity):
        if entity.x > self.x: entity.inertia[0] = random.randint(2,4); self.inert -= 2
        else: entity.inertia[0] = random.randint(-4,-2); self.inert += 2
        if not self.hittime:
            entity.raw_hit(self.pain * (random.randint(60,140)/100.0))
            self.hittime = 20
            self.SOUND = "collide"

class wasp(Monster):
    def m_init(self):
        self.name = "wasp"
        self.presentable_name = "Wasp"
        self.hp = 50
        self.maxhp = self.hp
        self.reward_exp = 7
        self.reward_hp = [6, 4, 0, 0]
        self.reward_mp = [2, 0, 0]
        self.reward_items = []
        self.a_prefix = "fly"
        self.a_frame = 1
        self.collision_dist = 20
        self.collision_hdist = 20
        self.pain = 5
        self.sx = self.x-20
        self.sy = self.y
        self.hittime = 0
        self.fall = 0
        self.xdash = 0
        self.pause = 0
        
    def step(self):
        if self.isdead:
            self.a_prefix = "dead"
            self.a_frame = 1
            self.ticker = 0
            self.fall += 0.5
            self.y += self.fall
            self.x += self.xdash
            if self.y >= 500: self.REMOVEME = True
        else:
            if self.pause: self.ticker -= 1; self.pause -= 1
            ox = self.x
            self.FLIPME = self.PLAYERSTATE.x > self.x
            self.x = int(self.sx + 40 * math.cos(self.ticker/11.0))
            self.xdash = self.x-ox
            self.y = int(self.sy + 30 * math.sin(self.ticker/11.0))
            if not self.ticker%4 or self.pause:
                self.a_prefix = "fly"
                self.a_frame += 1
                if self.a_frame >= 5:
                    self.a_frame = 1
            if self.hittime:
                self.hittime -= 1
    def die(self):
        self.SOUND = "dead"
        self.isdead = True
        self.SPAWN_GOODIES = True
    def damage(self):
        self.a_frame = 1
        self.SOUND = "hurt"
        self.AFTERSOUND = 6
        self.pause = 12
    def collision(self, entity):
        if entity.x > self.x: entity.inertia[0] = random.randint(1,2)
        else: entity.inertia[0] = random.randint(-2,-1)
        if not self.hittime:
            entity.raw_hit(self.pain * (random.randint(60,140)/100.0))
            self.hittime = 12
            self.SOUND = "hurt"

class giantworm(Monster):
    def m_init(self):
        self.name = "giantworm"
        self.presentable_name = "Mega Annelud."
        self.hp = 450
        self.maxhp = self.hp
        self.reward_exp = 50
        self.reward_hp = [30, 24, 20, 26,
                          19, 23, 17]
        self.reward_mp = [30, 33, 24,
                          ]
        self.reward_items = [(80, "Mega anneludine skull"),
                             (10, "Regen ring"),
                             (5, "Haste ring"),
                             (4, "Nature pendant"),
                             (1, "Ancient pendant")]
        self.a_prefix = "move"
        self.a_frame = 1

        self.projectile_damage = 12
        self.pain = 20
        self.inert = 0
        self.collision_dist = 100
        self.collision_hdist = 120
        self.Active = False

        self.hittime = 0
        self.affected["quake"] = True
        self.lasty = None

    def step(self):
        if self.isdead:
            self.a_frame = 1
            self.ticker = 0
            self.ALPHA -= 2
            if self.ALPHA <= 0: self.ALPHA = 0; self.REMOVEME = True
        else:
            p = self.PLAYERSTATE
            if p.x - self.x < 700:
                if p.x < self.x and self.inert > -1:
                    self.inert -= 0.05

            if not self.ticker%24:
                self.a_prefix = "move"
                self.a_frame = (self.a_frame % 2) + 1

            if not self.ticker%120:
                self.projectiles.append(["slimeball.png", self.x-70, self.y-60, 100])
                self.SOUND = "belch"

            for p in range(len(self.projectiles)):
                if self.projectiles[p] is None: continue
                self.projectiles[p][3] -= 1
                self.projectiles[p][1] -= 3
                theg = monster_ground_at(self.projectiles[p][1], self.LEVELSTATE)
                if self.projectiles[p][2] - (theg-25) > 40:
                    self.projectiles[p] = None
                else:
                    self.projectiles[p][2] = min(self.projectiles[p][2] + 2, theg-25)

            while None in self.projectiles:
                self.projectiles.remove(None)

        self.FLIPME = self.PLAYERSTATE.x > self.x
            
        self.inert *= 0.99
        newy = monster_ground_at(self.x, self.LEVELSTATE)
        if self.lasty:
            if abs(self.lasty-newy) < 40:
                self.y = newy
                self.x += self.inert
            else:
                self.inert = 0
        else:
            self.y = newy
        if not self.lasty:
            self.lasty = self.y

        if self.hittime:
            self.hittime -= 1

    def die(self):
        self.SOUND = "dead"
        self.isdead = True
        self.SPAWN_GOODIES = True
    def damage(self):
        self.a_frame = 1
        self.ticker = 8
        self.SOUND = "hurt"
        self.AFTERSOUND = 24
    def collision(self, entity):
        if entity.x > self.x: entity.inertia[0] = random.randint(10,16); self.inert = 0
        else: entity.inertia[0] = random.randint(-16,-10); self.inert = 0
        if not self.hittime:
            entity.raw_hit(self.pain * (random.randint(60,140)/100.0))
            self.hittime = 30
            self.SOUND = "collide"

    def inscreen(self, CX):
        if self.x <= CX + 900: self.Active = True
        return self.Active

# Snodom

class snowogre(Monster):
    def m_init(self):
        self.name = "snowogre"
        self.presentable_name = "Snought"
        self.hp = 130
        self.maxhp = self.hp
        self.reward_exp = 20
        self.reward_hp = [11, 10, 8, 10,
                          1, 3, 22, 0, 0, 0, 0]
        self.reward_mp = [0, 0, 7,
                          ]
        self.reward_items = [(90, "Potion"),
                             (40, "Mana potion"),
                             (2, "Regen ring")]
        self.a_prefix = "rest"
        self.a_frame = 1
        self.ghost = True

        self.pain = 8
        self.inert = 0
        self.fall = 0
        self.collision_hdist = 60

        self.hittime = 0

        self.state = 0 #0:rest, 1:walking, 2:charging, 3:lunging
        self.rising = False
        self.charging = 0
        self.lunged = False
        self.affected["quake"] = True

    def step(self):
        if self.isdead:
            self.a_frame = 5
            self.a_prefix = "walk"
            self.ticker = 0
            self.ALPHA -= 6
            if self.ALPHA <= 0: self.ALPHA = 0; self.REMOVEME = True
        else:
            p = self.PLAYERSTATE
            if p.x > self.x + 80 and not self.rising:
                self.rising = True

            if self.rising and not self.ticker%4 and self.a_prefix == "rest":
                if self.a_frame == 4:
                    self.rising = False
                    self.a_prefix = "walk"
                    self.a_frame = 1
                    self.state = 1
                    self.ghost = False
                else:
                    self.a_frame += 1

            if self.state == 1:
                if p.x - self.x < 700:
                    if p.x < self.x and self.inert > -4:
                        self.inert -= 0.25
                    elif p.x > self.x and self.inert < 4:
                        self.inert += 0.25

                if not self.ticker%7:
                    self.a_prefix = "walk"
                    self.a_frame = (self.a_frame % 6) + 1

                if abs(p.x - self.x) < 250:
                    self.state = 2
                    self.charging = 0
            if self.state == 2:
                self.charging += 1
                self.a_prefix = "attack"
                self.a_frame = 1
                self.FLIPME = self.PLAYERSTATE.x > self.x
                if self.charging >= 30:
                    self.state = 3
                    self.FLIPME = self.PLAYERSTATE.x > self.x

            if self.state == 3:
                if self.lunged == False:
                    self.lunged = True
                    self.a_prefix = "attack"
                    self.a_frame = 2
                    if self.FLIPME:
                        self.inert = 8
                    else:
                        self.inert = -8
                

        if abs(self.inert) < 4 and self.state == 3: self.lunged = False; self.state = 1

        self.y += self.fall

        if self.state == 1: self.FLIPME = self.PLAYERSTATE.x > self.x
        mga = monster_ground_at(self.x+self.inert, self.LEVELSTATE, 2)
        mgaf = monster_ground_at(self.x+15*cmp(self.inert, 0), self.LEVELSTATE, 3)

        if mga > self.y - 15:
            if mgaf > self.y - 25:
                self.x += self.inert
            if abs(mga - self.y) < 15:
                self.y = mga+2
                self.fall = 0
            else:
                self.fall = min(5, self.fall + 0.5)
        if mgaf < self.y - 25:
            self.inert = 0
            
        self.inert *= 0.98

        if self.hittime:
            self.hittime -= 1

        if self.y > 500:
            self.hp = 0

    def react_to_damage(self, damage):
        if self.state == 0: return
        if damage > self.maxhp:
            damage = self.maxhp
        if damage > self.hp:
            damage = self.hp
        if self.isdead: return
        curative = False
        if damage < 0:
            curative = True
        damage = [str(damage),str(damage)[1:]][curative]
        damage = str(int(round(float(damage))))
        if not damage.isdigit():
            print "Damage was not a digit!"
            return

        num_info = [curative]

        phase = 0
        bounce_height = 40

        for digit in damage:
            num_info.append(
                [digit, phase, bounce_height]
                )
            phase += 1

        self.numbers.append(num_info)

        self.hp -= int(float(damage))
        if self.hp > 0:
            self.damage()

        self.SOUND = "hurt"

    def react_to_magic(self, damage):
        if self.state == 0: return

        if damage > self.maxhp:
            damage = self.maxhp
        if damage > self.hp:
            damage = self.hp
        if self.isdead: return
        curative = False
        if damage < 0:
            curative = True
        damage = [str(damage),str(damage)[1:]][curative]
        damage = str(int(round(float(damage))))
        if not damage.isdigit():
            print "Damage was not a digit!"
            return

        num_info = [curative]

        phase = 0
        bounce_height = 40

        for digit in damage:
            num_info.append(
                [digit, phase, bounce_height]
                )
            phase += 1

        self.numbers.append(num_info)

        self.hp -= int(float(damage))
        if self.hp > 0:
            self.damage()

        self.SOUND = "hurt"

    def die(self):
#        self.SOUND = "hurt"
        self.isdead = True
        self.SPAWN_GOODIES = True
    def damage(self):
        self.a_frame = 1
        self.a_prefix = "walk"
        self.ticker = 0
#        self.SOUND = "hurt"
#        self.AFTERSOUND = 6
        self.inert = 0
    def collision(self, entity):
        if self.state == 0: return
        if self.state == 1 or self.state == 2: entity.inertia[0] = (((int(entity.x>self.x))*2)-1)*3; self.inert = 0; return

        # is lunging
        if entity.x > self.x: entity.inertia[0] = random.randint(2,4)
        else: entity.inertia[0] = random.randint(-4,-2)
        if not self.hittime:
            entity.raw_hit(self.pain * (random.randint(60,140)/100.0))
            self.hittime = 20
#            self.SOUND = "collide"

        self.state = 1
        self.lunged = False


class snowbat(Monster):
    def m_init(self):
        self.name = "snowbat"
        self.presentable_name = "Flust"
        self.hp = 80
        self.maxhp = self.hp
        self.reward_exp = 15
        self.reward_hp = [5, 9, 3, 5,
                          1, 3, 2, 0]
        self.reward_mp = [2, 0
                          ]
        self.reward_items = [(20, "Potion")]
        self.a_prefix = "fly"
        self.a_frame = 1
        self.collision_dist = 20
        self.collision_hdist = 25
        self.hittime = 0

        self.pain = 2
        self.inert = [0, 0]
    def step(self):
        pl = self.PLAYERSTATE
        rt, rt2 = random.randint(-20, 20), random.randint(-20, 20)
        if pl.x + rt > self.x:
            self.inert[0] += 0.2
            self.FLIPME = True
        elif pl.x + rt < self.x:
            self.inert[0] -= 0.2
        if pl.y-35 + rt2 > self.y:
            self.inert[1] += 0.2
        elif pl.y-35 + rt2 < self.y:
            self.inert[1] -= 0.2

        self.inert[0] *= 0.96
        self.inert[1] *= 0.96

        self.x += self.inert[0]
        self.y += self.inert[1]

        if self.isdead:
            self.a_frame = 1
            self.ticker = 0
            self.ALPHA -= 8
            if self.ALPHA <= 0: self.ALPHA = 0; self.REMOVEME = True
        else:
            if self.hittime:
                self.hittime -= 1

            self.a_frame = abs(((self.ticker/3)%4)-2) + 1
            self.FLIPME = self.PLAYERSTATE.x > self.x

    def die(self):
        self.isdead = True
        self.SPAWN_GOODIES = True
    def damage(self):
        self.inert[1] += self.PLAYERSTATE.inertia[1]*0.4
        self.SOUND = "squeak"
        if self.PLAYERSTATE.direction:
            self.inert[0] += 15
        else:
            self.inert[0] -= 15
        
    def collision(self, entity):
        if not self.hittime:
            entity.raw_hit(self.pain * (random.randint(60,140)/100.0))
            self.hittime = 25


# Bosses

class boss_radkelu(Monster):
    def m_init(self):
        self.name = "boss_radkelu"
        self.presentable_name = "Radkelu"
        self.hp = 20000
        self.maxhp = self.hp
        self.reward_exp = 200
        self.reward_hp = [248, 155, 339, 462]
        self.reward_mp = [129, 350, 238]
        self.reward_items = []
        self.a_prefix = "stopped"
        self.a_frame = 1
        self.collision_dist = 20
        self.collision_hdist = 100
        self.pain = 5
        self.phase = 0
        self.ptick = 0
        self.f1 = []
        self.useprojectilecollision = False
        self.fphase = 0
        self.fphase2 = 0
        self.BOSS = True
        self.BOSSFACE = "Radkeluface.png"
        
    def step(self):
        if self.isdead:
            self.ALPHA -= 5
            if self.ALPHA <= 0:
                self.PLAYERSTATE.iwin = True
                self.REMOVEME = True
        else:
            if self.phase == 0:
                # Not active yet.
                self.cx = self.x
                self.cy = self.y
                if self.PLAYERSTATE.x > 1050 or self.hp < self.maxhp:
                    self.phase = 1
                    self.hp = self.maxhp
            elif self.phase == 1 or self.phase == 6:
                # Sweep left to right, shooting fireballs from hands
                self.x = self.cx - math.sin(self.ptick/70.0) * 250
                
                self.ptick += 1

                if not self.ptick%8:
                    if self.fphase == 0:
                        self.f1.append([self.x - 32, self.y - 68, -3, 6])
                        self.f1.append([self.x + 28, self.y - 68, 3, 6])
                        self.fphase = 1
                    elif self.fphase == 1:
                        self.f1.append([self.x - 32, self.y - 68, -6, 6])
                        self.f1.append([self.x + 28, self.y - 68, 6, 6])
                        self.fphase = 2
                    elif self.fphase == 2:
                        self.f1.append([self.x - 32, self.y - 68, -1, 6])
                        self.f1.append([self.x + 28, self.y - 68, 1, 6])
                        self.fphase = 0

                if self.ptick >= 400:
                    self.phase = 2
                    self.ptick = 0
            elif self.phase == 2:
                # Coming from phase 1, centring for phase 3
                self.x = (self.x * 19 + self.cx) / 20.0
                self.ptick += 1
                if self.ptick >= 100:
                    self.phase = 3
                    self.ptick = 0

            elif self.phase == 3:
                #levitate to centre and shoot fireballs
                self.x = self.cx
                ra = math.sin(self.ptick/20.0) * 45
                langle = math.radians(ra)
                rangle = math.radians(-ra)

                if not self.ptick%3 and not (self.ptick/8)%3:
                    self.f1.append([self.x - 32, self.y - 68, 6 * math.sin(langle), 6 * math.cos(langle)])
                    self.f1.append([self.x + 28, self.y - 68, 6 * math.sin(rangle), 6 * math.cos(rangle)])

                self.ptick += 1
                if self.ptick >= 600:
                    self.ptick = 0
                    self.phase = 4
                    self.fphase2 = 0

            elif self.phase == 4:
                self.y = min(int(self.cy + self.ptick*2), 380)

                if not self.ptick%5 and not (self.ptick/20)%4:
                    if self.fphase2 == 0:
                        self.f1.append([self.x - 32, self.y - 68, -5, 6])
                        self.f1.append([self.x + 28, self.y - 68,  5, 6])
                        self.fphase2 = 1
                    elif self.fphase2 == 1:
                        self.f1.append([self.x - 32, self.y - 68, -7, 6])
                        self.f1.append([self.x + 28, self.y - 68,  7, 6])
                        self.fphase2 = 2
                    elif self.fphase2 == 2:
                        self.f1.append([self.x - 32, self.y - 68, -7, 4])
                        self.f1.append([self.x + 28, self.y - 68,  7, 4])
                        self.fphase2 = 3
                    elif self.fphase2 == 3:
                        self.f1.append([self.x - 32, self.y - 68, -9, 4])
                        self.f1.append([self.x + 28, self.y - 68,  9, 4])
                        self.fphase2 = 0
                    

                self.ptick += 1
                if self.ptick >= 200:
                    self.ptick = 0
                    self.phase = 5

            elif self.phase == 5:
                self.y = max(380 - self.ptick * 2, self.cy)

                self.ptick += 1
                if self.ptick >= 100:
                    self.ptick = 0
                    self.fphase = 0
                    self.phase = 1

            if self.hp < self.maxhp / 2:
                if not self.ptick % 4:
                    self.f1.append([self.x - 1000, self.cy+100, 10, 0])
                    self.f1.append([self.x + 1000, self.cy+100, -10, 0])

            # Tick fireballs
            for x in range(len(self.f1)):
                self.f1[x][0] += self.f1[x][2]
                self.f1[x][1] += self.f1[x][3]

                if self.f1[x][1] > 500 or self.f1[x][0] < 0 or self.f1[x][0] > 2560:
                    self.f1[x] = None

            for f in range(len(self.f1)):
                if not self.f1[f]: continue
                px, py, i1, i2 = self.f1[f]
                if abs(px - self.PLAYERSTATE.x) < 12 and abs(py - (self.PLAYERSTATE.y-40)) < 25:
                    self.f1[f] = None
                    self.PLAYERSTATE.raw_hit(random.randint(6, 12))

            while None in self.f1:
                self.f1.remove(None)



            # Create projectile array
            self.projectiles = []
            for x, y, dx, dy in self.f1:
                self.projectiles.append(["rfireball.png", x, y])

            
    def die(self):
        self.isdead = True
        self.SPAWN_GOODIES = True
    def damage(self):
        pass
    def collision(self, entity):
        pass

    def inscreen(self, x):
        return True
