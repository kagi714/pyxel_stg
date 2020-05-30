from random import randint
import math
import pyxel

#[[img, u, v, w, h, colkey], ...]
BULLET_IMGS  = [[ 0,  0,  8,  2,  2,  0],[ 0,  4,  8,  2,  2,  0]]
BULLET_TIMS  = [6,6]
SHIP_IMGS    = [[ 0,  0,  0,  7,  7,  0]]
SHIP_TIMS    = [10]
EXPLODE_IMGS = [
                [ 0,  16,  8,  8,  8,  0],[ 0,  24,  8,  8,  8,  0],
                [ 0,  32,  8,  8,  8,  0],[ 0,  40,  8,  8,  8,  0]
               ]
EXPLODE_TIMS = [3, 3, 3, 3]

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

    def distance(self, vec):
        return math.sqrt((self.x-vec.x)**2+(self.y-vec.y)**2)

class Collision():
    def __init__(self, siz=0.0, type=0x00, onhit_func=None):
        self.size = siz
        self.type = type
        self.__onhit = onhit_func

    def update(self, objs, pos):
        for o in objs:
            opos, ocol = o.get_hitbox()
            if self.__is_hit( pos, opos, ocol):
                self.__onhit(o)

    def __is_hit(self, selfpos, objpos, objcol):
        if self.type & objcol.type:
            if selfpos.distance(objpos) < (self.size+objcol.size):
                return True
        return False


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
    def __init__(self, app, pos, rot, anim):
        self.__app = app
        self.__pos = pos
        self.__rot = rot
        self.__anim = anim

        self.__col = Collision(2.0, 0x01, self.__on_hit)
        self.__vel = Vector(0.0,1.3)

    def update(self):
        self.__go_forward(self.__rot)
        self.__pos.update(self.__vel)

    def draw(self):
        self.__anim.draw(self.__pos)

    def get_hitbox(self):
        return self.__pos, self.__col

    def __on_hit(self, obj):
        pass

    def __go_forward(self, theta):
        self.__vel.x = 0
        self.__vel.y = 0.3
        self.__vel.rotate(theta)

class Player():
    def __init__(self, app, pos, rot, anim):
        self.__app = app
        self.__pos = pos
        self.__rot = rot
        self.__anim = anim

        self.__col = Collision(7.0, 0x0F, self.__on_hit)
        self.__vel = Vector(0.0,0.0)

    def update(self):
        self.__control()
        self.__pos.update(self.__vel)
        self.__col.update(self.__app.get_hitobjects(self), self.__pos)

    def draw(self):
        self.__anim.draw(self.__pos)
        
    def get_hitbox(self):
        return self.__pos, self.__col

    def __on_hit(self, obj):
        print("hit")

    def __control(self):
        vx, vy = 0.0, 0.0
        if pyxel.btn(pyxel.KEY_A) : vx = -1.0
        if pyxel.btn(pyxel.KEY_D) : vx =  1.0
        if pyxel.btn(pyxel.KEY_W) : vy = -1.0
        if pyxel.btn(pyxel.KEY_S) : vy =  1.0
        self.__vel.x = vx
        self.__vel.y = vy

class App():
    def __init__(self):
        pyxel.init(80, 60, fps=60, quit_key=pyxel.KEY_ESCAPE)
        pyxel.load("my_resource.pyxres")

        self.objs = []
        pos = Vector(5.0, 10.0)
        self.objs.append(self.new_object("Player",pos))

        pos = Vector(20.0, 10.0)
        self.objs.append(self.new_object("Bullet",pos,math.pi/6.0))

        pyxel.run(self.update, self.draw)

    def update(self):
        for o in self.objs :
            o.update()

    def draw(self):
        pyxel.cls(0)
        for o in self.objs :
            o.draw()

    def new_object(self, type, vec = None ,theta = None):
        pos = vec if vec is not None else Vector(0.0,0.0)
        rot = theta if theta is not None else 0

        if type == "Player":
            anim = Anim(SHIP_IMGS, SHIP_TIMS)
            return Player(self ,pos, rot, anim)
        elif type == "Bullet":
            anim = Anim(BULLET_IMGS, BULLET_TIMS)
            return Bullet(self, pos, rot, anim)
        else:
            raise

    def get_hitobjects(self, obj):
        exclude_self  = lambda o : o is not obj
        is_has_hitbox = lambda o : o.get_hitbox() is not None

        return filter(lambda o : exclude_self(o) & is_has_hitbox(o), self.objs)

App()