from random import randint
import math
import copy
import pyxel

import params as p

#[[img, u, v, w, h, colkey], ...]
BULLET_IMGS  = [[ 0,  0,  8,  2,  2,  0],[ 0,  4,  8,  2,  2,  0]]
BULLET_TIMS  = [6,6]
SHIP_IMGS    = [[ 0,  0, 16,  7,  7,  0]]
SHIP_TIMS    = [10]
SHOT_IMGS    = [[ 0, 32, 16,  3,  3,  0]]
SHOT_TIMS    = [10]
EXPLODE_IMGS = [
                [ 0,  16,  8,  8,  8,  0],[ 0,  24,  8,  8,  8,  0],
                [ 0,  32,  8,  8,  8,  0],[ 0,  40,  8,  8,  8,  0]
               ]
EXPLODE_TIMS = [2, 2, 2, 2]
ENEMY_IMGS   = [[ 0,  8, 56,  7,  7,  0]]
ENEMY_TIMS   = [10]

class Vector():
    """
    ２次元ベクトルクラス
    位置や速度を表すために使用する
    """

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
    """
    当たり判定用クラス
    """

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
        self._pos = pos   # 位置
        self._rot = rot   # 角度
        self._anim = anim # アニメーション
        self._col = None  # 当たり判定
        self._vel = None  # 速度
        self._time = 0    # 時間

    def update(self):
        self._control()
        self._pos.update(self._vel)
        self._time += 1

    def draw(self):
        self._anim.draw(self._pos)
        
    def get_hitbox(self):
        """
        当たり判定情報を返す
        """
        return self._col

    def _on_hit(self, obj):
        """
        何かに衝突した時の処理

        obj : 衝突したオブジェクト
        """
        pass

    def _control(self):
        """
        毎フレーム行う処理
        """
        pass

class Bullet(GameObject):
    def __init__(self, app, pos, rot, anim):
        super().__init__(app, pos, rot, anim)
        self._col = Collision(self._pos, 2.0, 0x01, self._on_hit)
        self._vel = Vector(0.0,1.3)

    def _control(self):
        self.__go_forward(self._rot)
        if self.__is_outofbound(): self._app.remove_object(self)
        if self._time > 300: self._app.remove_object(self)

    def __go_forward(self, theta):
        self._vel.x = 0
        self._vel.y = 0.3
        self._vel.rotate(theta)

    def __is_outofbound(self):
        return not self._pos.is_in(0, 0, 80, 60)

class Explode(GameObject):
    def __init__(self, app, pos, rot, anim):
        super().__init__(app, pos, rot, anim)
        self._col = None
        self._vel = Vector(0.0,0.0)

    def _control(self):
        if self._time > 12: self._app.remove_object(self)

class Shot(GameObject):
    def __init__(self, app, pos, rot, anim):
        super().__init__(app, pos, rot, anim)
        self._col = Collision(self._pos, 2.0, 0xF0, self._on_hit)
        self._vel = Vector(0.0,0.0)

    def _control(self):
        self.__go_forward(self._rot)
        if self.__is_outofbound(): self._app.remove_object(self)
        if self._time > 300: self._app.remove_object(self)

    def __go_forward(self, theta):
        self._vel.x = 0
        self._vel.y = -1.5
        self._vel.rotate(theta)

    def __is_outofbound(self):
        return not self._pos.is_in(0, 0, 80, 60)

class EnemyZako(GameObject):
    def __init__(self, app, pos, rot, anim):
        super().__init__(app, pos, rot, anim)
        self._col = Collision(self._pos, 4.0, 0x22, self._on_hit)
        self._vel = Vector(0.0,0.0)

        self.__is_muteki = False
        self.__is_alive = True
        self.__hp = 5

    def update(self):
        self._control()
        self._col.update(self._app.get_hitobjects(self))
        self._pos.update(self._vel)
        self._time += 1

    def _on_hit(self, obj):
        if self.__is_alive:
            if obj.get_hitbox().type != 0x22:
                self.damage(1)
                self._app.remove_object(obj)

    def damage(self, dmg):
        self.__hp -= dmg
        if self.__hp <= 0:
            self._app.new_object("Explode", self._pos, self._rot)
            self._app.remove_object(self)
            self.__is_alive = False

    def _control(self):
        self.__go_forward(self._rot)
        if self.__is_outofbound(): self._app.remove_object(self)
        if self._time > 600: self._app.remove_object(self)
        if self._time % 90 == 0:
            self.__shot(copy.copy(self._pos), self._rot)

    def __go_forward(self, theta):
        self._vel.x = 0
        self._vel.y = 0.1
        self._vel.rotate(theta)

    def __is_outofbound(self):
        return not self._pos.is_in(0, 0, 80, 60)

    def __shot(self, pos, rot):
        pos.y -= 2
        self._app.new_object("Bullet", pos, rot)

class Player(GameObject):
    def __init__(self, app, pos, rot, anim):
        super().__init__(app, pos, rot, anim)
        self._col = Collision(self._pos, 3.0, 0x0F, self._on_hit)
        self._vel = Vector(0.0,0.0)

        self.__is_muteki = False
        self.__is_alive = True

    def update(self):
        self._control()
        self._col.update(self._app.get_hitobjects(self))
        self._pos.update(self._vel)
        self._time += 1

    def _on_hit(self, obj):
        if self.__is_alive :
            self._app.new_object("Explode", self._pos, self._rot)
            self._app.remove_object(self)
            self.__is_alive = False

    def _control(self):
        if self.__is_alive :
            vx, vy = 0.0, 0.0
            if pyxel.btn(pyxel.KEY_A) : vx = -p.PLAYER_SPD
            if pyxel.btn(pyxel.KEY_D) : vx =  p.PLAYER_SPD
            if pyxel.btn(pyxel.KEY_W) : vy = -p.PLAYER_SPD
            if pyxel.btn(pyxel.KEY_S) : vy =  p.PLAYER_SPD
            self._vel.x = vx
            self._vel.y = vy

            if pyxel.btnp(pyxel.KEY_ENTER):
                self.__shot(copy.copy(self._pos), self._rot)

    def __shot(self, pos, rot):
        pos.y -= 2
        self._app.new_object("Shot", pos, rot)

class ObjectGenerator():
    def __init__(self,):
        self.__obj_dict = {}
        self.__obj_dict["Player"] = Player
        self.__obj_dict["Bullet"] = Bullet
        self.__obj_dict["Shot"] = Shot
        self.__obj_dict["Explode"] = Explode
        self.__obj_dict["EnemyZako"] = EnemyZako
        
        self.__anim_dict = {}
        self.__anim_dict["Player"] = Anim(SHIP_IMGS, SHIP_TIMS)
        self.__anim_dict["Bullet"] = Anim(BULLET_IMGS, BULLET_TIMS)
        self.__anim_dict["Shot"] = Anim(SHOT_IMGS, SHOT_TIMS)
        self.__anim_dict["Explode"] = Anim(EXPLODE_IMGS, EXPLODE_TIMS)
        self.__anim_dict["EnemyZako"] = Anim(ENEMY_IMGS, ENEMY_TIMS)


    def generate(self, app, type, vec = Vector(0.0,0.0) ,theta = 0):
        obj = None

        if type in self.__obj_dict:
            anim = self.__anim_dict[type]
            obj = self.__obj_dict[type](app, vec, theta, anim)

        return obj

class App():
    def __init__(self):
        pyxel.init(80, 60, fps=60, quit_key=pyxel.KEY_ESCAPE)
        pyxel.load("my_resource.pyxres")

        self.__obj_generator = ObjectGenerator()
        self.objs = []

        self.__game_init()

        pyxel.run(self.__update, self.__draw)

    def __game_init(self):
        self.new_object("Player", Vector(0.0, 0.0))
        self.new_object("EnemyZako", Vector(40.0, 10.0))
        self.new_object("EnemyZako", Vector(40.0, 10.0), -math.pi/6.0)

    def __update(self):
        for o in self.objs :
            o.update()

    def __draw(self):
        pyxel.cls(0)
        for o in self.objs :
            o.draw()

    def new_object(self, type, vec = Vector(0.0,0.0) ,theta = 0):
        """
        オブジェクトを生成する

        type  : オブジェクトの種類(string型)
        vec   : オブジェクトの初期位置
        theta : オブジェクトの初期角度
        """
        obj = self.__obj_generator.generate(self, type, vec, theta)
        if obj is not None : self.objs.append(obj)
        return obj

    def remove_object(self, obj):
        """
        オブジェクトを削除する
        """
        self.objs.remove(obj)

    def get_hitobjects(self, obj):
        """
        当たり判定の処理に必要なオブジェクトのリストを得る
        """
        exclude_self  = lambda o : o is not obj
        is_has_hitbox = lambda o : o.get_hitbox() is not None

        return filter(lambda o : exclude_self(o) & is_has_hitbox(o), self.objs)

App()