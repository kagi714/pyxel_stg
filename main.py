from random import randint
import math
import copy
import pyxel

#[[img, u, v, w, h, colkey], ...]
BULLET_IMGS  = [[ 0,  0,  8,  2,  2,  0],[ 0,  4,  8,  2,  2,  0]]
BULLET_TIMS  = [6,6]
SHIP_IMGS    = [[ 0,  0, 16,  7,  7,  0]]
SHIP_TIMS    = [10]
SHOT_IMGS    = [[ 0,  8, 12,  2,  4,  0],[ 0, 12, 12,  2,  4,  0]]
SHOT_TIMS    = [3,3]
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

    def is_in(self, x1, y1, x2, y2):
        return (x1 < self.x < x2)and(y1 < self.y < y2)

class Collision():
    def __init__(self, pos = None, siz=0.0, type=0x00, onhit_func=None):
        self.pos = pos
        self.size = siz
        self.type = type
        self.__onhit = onhit_func

    def update(self, objs):
        for o in objs:
            if self.__is_hit(o.get_hitbox()):
                self.__onhit(o)

    def __is_hit(self, objcol):
        if self.type & objcol.type:
            if self.pos.distance(objcol.pos) < (self.size + objcol.size):
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

        x = pos.x - (img[3]/2)
        y = pos.y - (img[4]/2)

        pyxel.blt(x ,y ,img[0], img[1], img[2], img[3], img[4], img[5])

        self.__time_count += 1
        if self.__time_count == self.__times[self.__index]:
            self.__time_count = 0
            if self.__index == self.__max_index:
                self.__index = 0
            else:
                self.__index += 1

class GameObject():
    def __init__(self, app, pos, rot, anim):
        self._app = app
        self._pos = pos
        self._rot = rot
        self._anim = anim
        self._col = None
        self._vel = None

    def update(self):
        self._control()
        self._pos.update(self._vel)

    def draw(self):
        self._anim.draw(self._pos)
        
    def get_hitbox(self):
        return self._col

    def _on_hit(self, obj):
        pass

    def _control(self):
        pass

class Bullet(GameObject):
    def __init__(self, app, pos, rot, anim):
        super().__init__(app, pos, rot, anim)
        self._col = Collision(self._pos, 2.0, 0x01, self._on_hit)
        self._vel = Vector(0.0,1.3)

        self.__time = 0

    def _control(self):
        self.__go_forward(self._rot)
        if self.__is_outofbound(): self._app.remove_object(self)
        if self.__time > 300: self._app.remove_object(self)
        self.__time += 1

    def __go_forward(self, theta):
        self._vel.x = 0
        self._vel.y = 0.3
        self._vel.rotate(theta)

    def __is_outofbound(self):
        return not self._pos.is_in(0, 0, 80, 60)

class Explode():
    def __init__(self, app, pos, rot, anim):
        self.__app = app
        self.__pos = pos
        self.__rot = rot
        self.__anim = anim

        self.__col = None
        self.__vel = Vector(0.0,0.0)
        self.__time = 0

    def update(self):
        self.__pos.update(self.__vel)
        if self.__time > 12: self.__app.remove_object(self)
        self.__time += 1

    def draw(self):
        self.__anim.draw(self.__pos)

    def get_hitbox(self):
        return None

    def __on_hit(self, obj):
        pass

class Shot():
    def __init__(self, app, pos, rot, anim):
        self.__app = app
        self.__pos = pos
        self.__rot = rot
        self.__anim = anim

        self.__col = Collision(self.__pos, 2.0, 0xF0, self.__on_hit)
        self.__vel = Vector(0.0,0.0)
        self.__time = 0

    def update(self):
        self.__go_forward(self.__rot)
        self.__pos.update(self.__vel)
        if self.__is_outofbound(): self.__app.remove_object(self)
        if self.__time > 300: self.__app.remove_object(self)
        self.__time += 1

    def draw(self):
        self.__anim.draw(self.__pos)

    def get_hitbox(self):
        return self.__col

    def __on_hit(self, obj):
        pass

    def __go_forward(self, theta):
        self.__vel.x = 0
        self.__vel.y = -1.5
        self.__vel.rotate(theta)

    def __is_outofbound(self):
        return not self.__pos.is_in(0, 0, 80, 60)

class Player(GameObject):
    def __init__(self, app, pos, rot, anim):
        super().__init__(app, pos, rot, anim)
        self._col = Collision(self._pos, 7.0, 0x0F, self._on_hit)
        self._vel = Vector(0.0,0.0)

        self.__is_muteki = False
        self.__is_alive = True
        self.__time = 0

    def update(self):
        self._control()
        self._col.update(self._app.get_hitobjects(self))
        self._pos.update(self._vel)
        self.__time += 1

    def draw(self):
        self._anim.draw(self._pos)
        
    def get_hitbox(self):
        return self._col

    def _on_hit(self, obj):
        self._app.new_object("Explode", self._pos, self._rot)
        self._app.remove_object(self)

    def _control(self):
        if self.__is_alive :
            vx, vy = 0.0, 0.0
            if pyxel.btn(pyxel.KEY_A) : vx = -1.0
            if pyxel.btn(pyxel.KEY_D) : vx =  1.0
            if pyxel.btn(pyxel.KEY_W) : vy = -1.0
            if pyxel.btn(pyxel.KEY_S) : vy =  1.0
            self._vel.x = vx
            self._vel.y = vy

            if pyxel.btnp(pyxel.KEY_ENTER):
                self.__shot(copy.copy(self._pos), self._rot)

    def __shot(self, pos, rot):
        pos.y -= 2
        self._app.new_object("Shot", pos, rot)

class App():
    def __init__(self):
        pyxel.init(80, 60, fps=60, quit_key=pyxel.KEY_ESCAPE)
        pyxel.load("my_resource.pyxres")

        self.objs = []
        self.new_object("Player", Vector(0.0, 0.0))
        self.new_object("Bullet", Vector(20.0, 10.0), math.pi/6.0)

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
        obj = None

        if type == "Player":
            anim = Anim(SHIP_IMGS, SHIP_TIMS)
            obj = Player(self ,pos, rot, anim)
        elif type == "Bullet":
            anim = Anim(BULLET_IMGS, BULLET_TIMS)
            obj = Bullet(self, pos, rot, anim)
        elif type == "Explode":
            anim = Anim(EXPLODE_IMGS, EXPLODE_TIMS)
            obj = Explode(self, pos, rot, anim)
        elif type == "Shot":
            anim = Anim(SHOT_IMGS, SHOT_TIMS)
            obj = Shot(self, pos, rot, anim)
        
        if obj is not None :
            self.objs.append(obj)
        return obj

    def remove_object(self, obj):
        self.objs.remove(obj)

    def get_hitobjects(self, obj):
        exclude_self  = lambda o : o is not obj
        is_has_hitbox = lambda o : o.get_hitbox() is not None

        return filter(lambda o : exclude_self(o) & is_has_hitbox(o), self.objs)

App()