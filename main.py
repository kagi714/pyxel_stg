from random import randint
import math
import pyxel

#[[img, u, v, w, h, colkey], ...]
BULLET_IMGS = [[ 0,  0,  8,  2,  2,  0],[ 0,  4,  8,  2,  2,  0]]
BULLET_TIMS = [6,6]
SHIP_IMGS   = [[ 0,  0,  0,  7,  7,  0]]
SHIP_TIMS   = [10]

class Vector():
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

    def update(self, vel):
        self.x += vel.x
        self.y += vel.y

    def rotate(self, theta):
        x, y = self.x, self.y
        self.x = x * math.cos(theta) - y * math.sin(theta)
        self.y = x * math.sin(theta) + y * math.cos(theta)

class Anim():
    def __init__(self, imgs, tims):
        if len(imgs) > 0 :
            self.__images = imgs
        if len(tims) > 0 :
            self.__times = tims
        self.__index = 0
        self.__time_count = 0
        self.__max_index = min(len(self.__images),len(self.__times))-1

    def draw(self, pos):
        img = self.__images[self.__index]

        x = pos.x + (img[3]/2)
        y = pos.y + (img[4]/2)

        pyxel.blt(x ,y ,img[0], img[1], img[2], img[3], img[4], img[5])

        self.__time_count += 1
        if self.__time_count == self.__times[self.__index]:
            self.__time_count = 0
            if self.__index == self.__max_index:
                self.__index = 0
            else:
                self.__index += 1

class Bullet():
    def __init__(self, pos, rot, anim):
        self.__pos = pos
        self.__rot = rot
        self.__anim = anim
        self.__vel = Vector(0.0,1.3)

    def update(self):
        self.__go_forward(self.__rot)
        self.__pos.update(self.__vel)

    def draw(self):
        self.__anim.draw(self.__pos)

    def __go_forward(self, theta):
        self.__vel.x = 0
        self.__vel.y = 1.3
        self.__vel.rotate(theta)

class Player():
    def __init__(self, pos, rot, anim):
        self.__pos = pos
        self.__rot = rot
        self.__anim = anim
        self.__vel = Vector(0.0,0.0)

    def update(self):
        self.__control()
        self.__pos.update(self.__vel)

    def draw(self):
        self.__anim.draw(self.__pos)

    def __control(self):
        vx, vy = 0.0, 0.0
        if pyxel.btn(pyxel.KEY_A) : vx = -1.0
        if pyxel.btn(pyxel.KEY_D) : vx =  1.0
        if pyxel.btn(pyxel.KEY_W) : vy = -1.0
        if pyxel.btn(pyxel.KEY_S) : vy =  1.0
        self.__vel.x = vx
        self.__vel.y = vy

def new_object(type, vec = None ,theta = None):
    pos = vec if vec is not None else Vector(0.0,0.0)
    rot = theta if theta is not None else 0

    if type == "Player":
        anim = Anim(SHIP_IMGS, SHIP_TIMS)
        return Player(pos, rot, anim)
    elif type == "Bullet":
        anim = Anim(BULLET_IMGS, BULLET_TIMS)
        return Bullet(pos, rot, anim)
    else:
        raise

class App():
    def __init__(self):
        pyxel.init(80, 60, fps=60, quit_key=pyxel.KEY_ESCAPE)
        pyxel.load("my_resource.pyxres")

        self.objs = []
        pos = Vector(5.0, 10.0)
        self.objs.append(new_object("Player",pos))

        pos = Vector(20.0, 10.0)
        self.objs.append(new_object("Bullet",pos,math.pi/6.0))

        pyxel.run(self.update, self.draw)

    def update(self):
        for o in self.objs :
            o.update()

    def draw(self):
        pyxel.cls(0)
        for o in self.objs :
            o.draw()

App()