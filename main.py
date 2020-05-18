from random import randint
import pyxel

#[[img, u, v, w, h, colkey], ...]
BULLET_IMGS = [[ 0,  0,  8,  2,  2,  0],[ 0,  4,  8,  2,  2,  0]]
BULLET_TIMS = [6,6]
SHIP_IMGS   = [[ 0,  0,  0,  7,  7,  0]]
SHIP_TIMS   = [10]

class Position():
    def __init__(self, x=0, y=0, r=0):
        self.__px = x
        self.__py = y
        self.__angle = r

    def move(self, x=0, y=0, r=0):
        self.__px += x
        self.__py += y
        self.__angle += r

    def data(self):
        return self.__px, self.__py, self.__angle

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
        self.__position = pos
        self.__anim = anim

    def update(self):
        pass

    def draw(self):
        self.__anim.draw(self.__position)

class Player():
    def __init__(self, pos, anim):
        self.__position = pos
        self.__anim = anim

    def update(self):
        self.__control()

    def draw(self):
        self.__anim.draw(self.__position)

    def __control(self):
        pass

class App():
    def __init__(self):
        pyxel.init(80, 60, fps=60, quit_key=pyxel.KEY_ESCAPE)
        pyxel.load("my_resource.pyxres")

        self.objs = []
        pos = Position(5, 10)
        anim = Anim(SHIP_IMGS, SHIP_TIMS)
        self.objs.append(Player(pos, anim))

        pos = Position(20, 10)
        anim = Anim(BULLET_IMGS, BULLET_TIMS)
        self.objs.append(Bullet(pos, anim))

        pyxel.run(self.update, self.draw)

    def update(self):
        for o in self.objs :
            o.update()

    def draw(self):
        for o in self.objs :
            o.draw()

App()