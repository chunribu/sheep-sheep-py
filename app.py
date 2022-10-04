import pyxel
import random
import sheepsheep

class Element:
    def __init__(self, x, y, w=15, h=15, img=0, u=19, v=0):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.img = img
        self.u = u
        self.v = v
    def draw(self):
        pyxel.blt(self.x, self.y, self.img, self.u, self.v, self.w, self.h)

uv_list = random.sample(
    [
        (19,0),  (0,125),  (16,59),  (19,21),  (35,0),
        (108,120),(47,124),(66,0),   (61,31),  (88,77),
        (75,79), (76,95),  (77,110), (81,136), (76,62),
        (98,14), (92,107), (106,106),(119,89), (118,42),
    ],20)

ele_cover = {
    'img': 1,
    'w': 17,
    'h': 17,
    'u': 0,
    'v': 0,
}
ele_placeholder = {
    'img': 0,
    'w': 17,
    'h': 17,
    'u': 0,
    'v': 0,
}

class RandomArea:
    def __init__(self, x, data):
        self.l_x = x
        self.r_x= x + 18
        self.data = data
    def draw(self):
        l_list, r_list = self.data
        l_len, r_len = len(l_list), len(r_list)
        for i, l in enumerate(l_list):
            if i < l_len - 1:
                pyxel.blt(self.l_x, i*8, **ele_cover)
            else:
                u, v = uv_list[l['type']]
                Element(self.l_x+1, i*8, u=u, v=v).draw()
        for i, r in enumerate(r_list):
            if i < r_len - 1:
                pyxel.blt(self.r_x, i*8, **ele_cover)
            else:
                u, v = uv_list[r['type']]
                Element(self.r_x+1, i*8, u=u, v=v).draw()

class SlotArea:
    def __init__(self, x, y, data):
        self.x = x 
        self.y = y 
        self.data = data 
    def draw(self):
        for i, b in enumerate(self.data):
            x = self.x
            y = self.y + i * 16
            pyxel.blt(x, y, **ele_placeholder)
            if b:
                u, v = uv_list[b['type']]
                Element(x+1, y+1, u=u, v=v).draw()

class App:
    def __init__(self):
        self._scale = 5
        self.w = 15
        self.h = 15
        pyxel.init(40*self._scale, 24*self._scale, "羊了个羊-单机复古版-github.com/chunribu", display_scale=3)
        pyxel.load('assets/sheepgame.pyxres')
        pyxel.mouse(True)
        self.backend = sheepsheep
        self.clickables = []
        self.framekeeping = 0
        self.curr_game_level = 0
        self.game_level_num = 3
        self.start_game()
        pyxel.run(self.update, self.draw)
    def start_game(self):
        self.framekeeping = 0
        if self.curr_game_level < self.game_level_num:
            pyxel.playm(0, loop=True)
            try:
                self.backend.do_start(self.curr_game_level)
            except:
                self.backend.do_start(self.curr_game_level)
            self.curr_game_level += 1
            self._randint = [random.randint(20,30) for i in range(10)]
    def update(self):
        self.game_status = self.backend.game_status
        # 游戏状态：进行中
        if self.game_status == 1:
            prev_slot_num = self.backend.curr_slot_num
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                for b in self.clickables:
                    dx = pyxel.mouse_x - b['x']
                    dy = pyxel.mouse_y - b['y']
                    if dx >= 0 and dy >= 0:
                        if dx < self.w and dy < self.h:
                            pyxel.play(3,4)
                            self.backend.do_click_block(b['id'])
                            break
                if pyxel.mouse_x >= 26 * self._scale:
                    if pyxel.mouse_x <= 29*self._scale+2:
                        # click random area 0
                        lrb = [b for b in self.random_blocks[0] if b['status']==0]
                        if len(lrb):
                            pyxel.play(3,4)
                            self.backend.do_click_block(lrb[-1]['id'])
                    elif pyxel.mouse_x < 32*self._scale+5:
                        # click random area 1
                        rrb = [b for b in self.random_blocks[1] if b['status']==0]
                        if len(rrb):
                            pyxel.play(3,4)
                            self.backend.do_click_block(rrb[-1]['id'])
                    elif pyxel.mouse_x >= 36*self._scale:
                        # click slot area
                        self.backend.do_undo()
                curr_slot_num = self.backend.curr_slot_num
                if curr_slot_num != prev_slot_num + 1:
                    pyxel.play(3,3)
        # 失败
        elif self.game_status == 2:
            if pyxel.btnp(pyxel.KEY_SPACE):
                self.curr_game_level -= 1
                self.start_game()
        # 胜利
        elif self.game_status == 3:
            self.framekeeping += 1
            if self.framekeeping > 60:
                self.start_game()
    def draw(self):
        self.game_status = self.backend.game_status
        if self.game_status == 1:
            self.level_blocks = self.backend.level_blocks_val
            self.random_blocks = self.backend.random_blocks_val
            self.slot_blocks = self.backend.slot_area_val
            # background
            idx = 0
            pyxel.cls(11)
            for i in range(10):
                for j in range(1,8):
                    _rand = self._randint[idx%10] - 30
                    if idx % 3 > 0:
                        pyxel.bltm(i*30+_rand,j*30+_rand,0,0,0,16,16)
                    idx += 1
            # game info
            pyxel.text(26*self._scale, 21*self._scale, f"TIME: {pyxel.frame_count // 30} S", 7)
            pyxel.text(26*self._scale, 22.5*self._scale, f"LEVEL: {self.curr_game_level}/{self.game_level_num}", 7)
            # level area
            self.clickables.clear()
            for block in self.level_blocks:
                if block['status'] == 0:
                    x = block['x'] * self._scale
                    y = block['y'] * self._scale
                    u, v = uv_list[block['type']]
                    higher_block_num = len(set([i['id'] for i in block['higher_level_blocks'] if i['status']==0]))
                    if higher_block_num == 0:
                        img = 0
                        self.clickables.append({
                            'id': block['id'],
                            'x': x,
                            'y': y,
                        })
                    elif higher_block_num == 1: 
                        img = 1
                    else:
                        img = 2
                    Element(x, y, w=self.w, h=self.h, img=img, u=u, v=v).draw()
            # random area
            lrb = [b for b in self.random_blocks[0] if b['status']==0]
            rrb = [b for b in self.random_blocks[1] if b['status']==0]
            RandomArea(26*self._scale, [lrb, rrb]).draw()
            # slot area
            SlotArea(36*self._scale, .5*self._scale, self.slot_blocks).draw()
        elif self.game_status == 2:
            pyxel.cls(8)
            pyxel.text(16*self._scale, 10*self._scale, "GAME OVER", 7)
            pyxel.text(11*self._scale, 16*self._scale, 'PRESS SPACE TO TRY AGAIN', pyxel.frame_count % 16)
            pyxel.stop()
        elif self.game_status == 3:
            if self.curr_game_level == self.game_level_num:
                pyxel.cls(15 - (pyxel.frame_count % 16))
                pyxel.text(16*self._scale, 10*self._scale, "YOU WIN!!!", pyxel.frame_count % 16)
            else: 
                pyxel.cls(10)
                pyxel.text(16*self._scale, 10*self._scale, "GREEEEAT!", 7)
                pyxel.text(11*self._scale, 16*self._scale, 'GAME IS GETTING HADER...', pyxel.frame_count % 16)
            pyxel.stop()
App()