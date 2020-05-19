from random import randint
import pyxel

#[[img, u, v, w, h, colkey], ...]
BULLET_IMGS = [[ 0,  0,  8,  2,  2,  0],[ 0,  4,  8,  2,  2,  0]]
BULLET_TIMS = [6,6]
SHIP_IMGS   = [[ 0,  0,  0,  7,  7,  0]]
SHIP_TIMS   = [10]

class Vector():
    def __init__(self, x=0.0, y=0.0, r=0.0):
        self.set(x,y,r)

    def add(self, x=0.0, y=0.0, r=0.0):
        self.__x += x
        self.__y += y
        self.__angle += r

    def set(self, x=0.0, y=0.0, r=0.0):
        self.__x = x
        self.__y = y
        self.__angle = r

    def update(self, vel):
        self.__x += vel.__x
        self.__y += vel.__y
        self.__angle += vel.__angle

    def data(self):
        return self.__x, self.__y, self.__angle

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

        px, py, _ = pos.data()
        x = px + (img[3]/2)
        y = py + (img[4]/2)

        pyxel.blt(x ,y ,img[0], img[1], img[2], img[3], img[4], img[5])

        self.__time_count += 1
        if self.__time_count == self.__times[self.__index]:
            self.__time_count = 0
            if self.__index == self.__max_index:
                self.__index = 0
            else:
                self.__index += 1

class Bullet():
    def __init__(self, pos, anim):
        self.__pos = pos
        self.__anim = anim
        self.__vel = Vector(0.0,1.3,0.0)

    def update(self):
        self.__pos.update(self.__vel)

    def draw(self):
        self.__anim.draw(self.__pos)

class Player():
    def __init__(self, pos, anim):
        self.__pos = pos
        self.__anim = anim
        self.__vel = Vector(0.0,0.0,0.0)

    def update(self):
        self.__control()
        self.__pos.update(self.__vel)

    def draw(self):
        self.__anim.draw(self.__pos)

    def __control(self):
        vx, vy = 0.0, 0.0
        if pyxel.btn(pyxel.KEY_W) :
            vy = -2.0
        self.__vel.set(vx, vy)

class App():
    def __init__(self):
        pyxel.init(80, 60, fps=60, quit_key=pyxel.KEY_ESCAPE)
        pyxel.load("my_resource.pyxres")

        self.objs = []
        pos = Vector(5.0, 10.0)
        anim = Anim(SHIP_IMGS, SHIP_TIMS)
        self.objs.append(Player(pos, anim))

        pos = Vector(20.0, 10.0)
        anim = Anim(BULLET_IMGS, BULLET_TIMS)
        self.objs.append(Bullet(pos, anim))

        pyxel.run(self.update, self.draw)

    def update(self):
        for o in self.objs :
            o.update()

    def draw(self):
        pyxel.cls(0)
        for o in self.objs :
            o.draw()

App()