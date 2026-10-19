# 單機回合制砲戰：方向鍵瞄準，A/D 移動，長按空白鍵蓄力、放開發射。
# 只使用 Python 內建套件，不需要網路或 API token。
import math
import random
import time
import tkinter as tk
from tkinter import ttk
from pathlib import Path


GRAVITY = 15.0
WORLD_WIDTH = 180


def terrain_height(terrain, x):
    return terrain[max(0, min(WORLD_WIDTH, int(x)))]


def position(x, y, vx, vy, wind, t):
    # 水平受風力加速，垂直受重力影響。
    return x + vx*t + wind*t*t/2, y + vy*t - GRAVITY*t*t/2


def predict(terrain, x, direction, angle, power, wind):
    theta = math.radians(angle)
    y = terrain_height(terrain, x) + 8
    vx, vy = direction*power*math.cos(theta), power*math.sin(theta)
    for step in range(1, 2001):
        px, py = position(x, y, vx, vy, wind, step*.025)
        if px < 0 or px > WORLD_WIDTH or py <= terrain_height(terrain, px):
            return px, py
    return px, py


class BattleGame:
    def __init__(self, root):
        self.root = root
        root.title("砲砲對決｜單機回合戰")
        root.geometry('1120x780')
        root.minsize(850, 680)
        root.configure(bg='#eff3f8')
        source = tk.PhotoImage(file=str(Path(__file__).parent/'assets'/'cannon_display.png'))
        self.image = source.subsample(max(1, (source.width()+99)//100))
        self.enemy_image = tk.PhotoImage(width=self.image.width(), height=self.image.height())
        # 負的縮放方向可水平翻轉圖片，讓敵方砲口朝左。
        self.enemy_image.tk.call(str(self.enemy_image), 'copy', str(self.image), '-subsample', -1, 1)
        self.pending = None
        self.angle = tk.DoubleVar(value=45)
        self.power = tk.DoubleVar(value=32)
        self.info = tk.StringVar()
        self.hint = tk.StringVar()
        self.readout = tk.StringVar()
        self.keys = set()
        style = ttk.Style(root)
        style.configure('TLabel', font=('Microsoft JhengHei', 11))
        style.configure('TButton', font=('Microsoft JhengHei', 11), padding=7)
        header = ttk.Frame(root, padding=14)
        header.pack(fill='x')
        ttk.Label(header, text='砲砲對決', font=('Microsoft JhengHei', 21, 'bold')).pack(side='left')
        ttk.Label(header, textvariable=self.info).pack(side='left', padx=24)
        ttk.Button(header, text='重新對戰', command=self.restart).pack(side='right')
        self.canvas = tk.Canvas(root, bg='#dceefb', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True, padx=16)
        panel = ttk.Frame(root, padding=12)
        panel.pack(fill='x', padx=8)
        panel.columnconfigure(1, weight=1)
        ttk.Label(panel, text='仰角').grid(row=0, column=0, padx=8)
        self.angle_scale = ttk.Scale(panel, from_=10, to=80, variable=self.angle, command=self.adjust)
        self.angle_scale.grid(row=0, column=1, sticky='ew', padx=8)
        ttk.Label(panel, text='力道').grid(row=1, column=0, padx=8)
        self.power_scale = ttk.Scale(panel, from_=15, to=65, variable=self.power, command=self.adjust)
        self.power_scale.grid(row=1, column=1, sticky='ew', padx=8, pady=8)
        ttk.Label(panel, textvariable=self.readout, width=23).grid(row=0, column=2, rowspan=2, padx=8)
        self.fire_button = ttk.Button(panel, text='直接發射', command=self.fire)
        self.fire_button.grid(row=0, column=3, padx=6)
        self.charge_button = ttk.Button(panel, text='按住蓄力／放開發射')
        self.charge_button.grid(row=1, column=3, padx=6)
        self.charge_button.bind('<ButtonPress-1>', self.begin_charge)
        self.charge_button.bind('<ButtonRelease-1>', self.end_charge)
        ttk.Label(root, textvariable=self.hint, wraplength=1000).pack(anchor='w', padx=24, pady=(0, 5))
        ttk.Label(root, text='A / D 移動（每回合 12 m）  ·  ↑ / ↓ 調角度  ·  按住空白鍵蓄力，放開發射  ·  爆炸可破壞地形',
                  background='#eff3f8').pack(anchor='w', padx=24, pady=(0, 12))
        root.bind('<KeyPress>', self.key_down)
        root.bind('<KeyRelease>', self.key_up)
        root.bind('<FocusOut>', self.focus_out)
        self.canvas.bind('<Button-1>', lambda event: root.focus_set())
        self.canvas.bind('<Configure>', lambda event: self.draw())
        root.protocol('WM_DELETE_WINDOW', self.close)
        self.restart()

    def cancel(self):
        if self.pending is not None:
            self.root.after_cancel(self.pending)
            self.pending = None

    def schedule(self, delay, callback):
        self.cancel()
        self.pending = self.root.after(delay, callback)

    def restart(self):
        self.cancel()
        self.keys.clear()
        self.terrain = [8 + 3*math.sin(x/23) + 2*math.sin(x/11) for x in range(181)]
        self.players = [{'x': 23., 'hp': 100}, {'x': 154., 'hp': 100}]
        self.round = 0
        self.trace, self.ball, self.blast = [], None, None
        self.angle.set(45)
        self.power.set(32)
        self.start_turn(0)

    def controls(self, enabled):
        state = 'normal' if enabled else 'disabled'
        for widget in (self.angle_scale, self.power_scale, self.fire_button, self.charge_button):
            widget.configure(state=state)

    def start_turn(self, who):
        self.pending = None
        self.turn = who
        self.phase = 'aim'
        self.fuel = 12.
        self.wind = random.choice([-3., -2., -1., 0., 1., 2., 3.])
        self.round += 1
        self.blast = None
        self.controls(who == 0)
        self.hint.set('輪到你！留意風向，移動或調整角度後發射。' if who == 0 else '電腦正在瞄準……')
        self.adjust()
        if who == 1:
            self.schedule(900, self.computer_fire)

    def adjust(self, value=None):
        self.readout.set(f'角度 {self.angle.get():.0f}°  /  力道 {self.power.get():.1f}\n移動額度 {getattr(self, "fuel", 12):.0f} m')
        if hasattr(self, 'terrain'):
            self.draw()

    def key_down(self, event):
        key = event.keysym.lower()
        if key == 'space':
            self.begin_charge()
            return 'break'
        if self.turn != 0 or self.phase != 'aim':
            return
        if key in ('a', 'd') and self.fuel >= 1:
            player = self.players[0]
            x = player['x'] + (-1 if key == 'a' else 1)
            if 8 <= x <= self.players[1]['x'] - 25:
                player['x'] = x
                self.fuel -= 1
        elif key in ('up', 'down'):
            self.angle.set(max(10, min(80, self.angle.get() + (1 if key == 'up' else -1))))
        self.adjust()

    def key_up(self, event):
        if event.keysym.lower() == 'space':
            self.end_charge()
            return 'break'

    def focus_out(self, event):
        # 切到其他程式時取消蓄力，避免放開按鍵後還一直充能。
        if self.root.focus_displayof() is None and self.phase == 'charge':
            self.cancel()
            self.phase = 'aim'
            self.hint.set('蓄力已取消，重新按住空白鍵即可。')

    def begin_charge(self, event=None):
        if self.turn != 0 or self.phase != 'aim':
            return
        self.phase = 'charge'
        self.charge_started = time.perf_counter()
        self.power.set(15)
        self.charge_tick()

    def charge_tick(self):
        self.pending = None
        if self.phase != 'charge':
            return
        # 約兩秒蓄滿；滿格後維持，不會自動發射。
        self.power.set(min(65, 15+(time.perf_counter()-self.charge_started)*25))
        self.hint.set('蓄力中……放開空白鍵或滑鼠即可發射！')
        self.adjust()
        self.schedule(20, self.charge_tick)

    def end_charge(self, event=None):
        if self.phase == 'charge':
            self.cancel()
            self.phase = 'aim'
            self.fire()

    def fire(self):
        if self.turn != 0 or self.phase != 'aim':
            return
        self.launch(self.angle.get(), self.power.get())

    def computer_fire(self):
        self.pending = None
        if self.turn != 1 or self.phase != 'aim':
            return
        # 電腦用相同物理公式試算，再加入些微誤差。
        enemy, target = self.players[1], self.players[0]
        candidates = []
        for angle in (30, 40, 50, 60, 70):
            for power in range(22, 66):
                x, _ = predict(self.terrain, enemy['x'], -1, angle, power, self.wind)
                candidates.append((abs(x-target['x']), angle, power))
        _, angle, power = min(candidates)
        self.launch(angle + random.uniform(-2, 2), power + random.uniform(-2, 2))

    def launch(self, angle, power):
        self.cancel()
        self.phase = 'flight'
        self.controls(False)
        player = self.players[self.turn]
        theta = math.radians(angle)
        self.launch_x = player['x']
        self.launch_y = terrain_height(self.terrain, player['x'])+8
        self.vx = (1 if self.turn == 0 else -1)*power*math.cos(theta)
        self.vy = power*math.sin(theta)
        self.shot_started = time.perf_counter()
        self.last_t = 0.
        self.trace = [(self.launch_x, self.launch_y)]
        self.ball = self.trace[0]
        self.hint.set('你的砲彈飛行中……' if self.turn == 0 else '敵方砲彈飛行中……')
        self.flight_tick()

    def flight_tick(self):
        self.pending = None
        elapsed = min(30., (time.perf_counter()-self.shot_started)*2)
        # 補算中間步驟，避免畫面延遲時砲彈穿過山坡。
        while self.last_t < elapsed:
            self.last_t = min(elapsed, self.last_t+.025)
            x, y = position(self.launch_x, self.launch_y, self.vx, self.vy, self.wind, self.last_t)
            self.ball = x, y
            self.trace.append(self.ball)
            if x < 0 or x > WORLD_WIDTH:
                self.finish_turn('砲彈飛出場外，這回合沒有造成傷害。')
                return
            if y <= terrain_height(self.terrain, x):
                self.explode(x, terrain_height(self.terrain, x))
                return
        self.draw()
        if elapsed >= 30:
            self.finish_turn('砲彈飛出戰場。')
        else:
            self.schedule(16, self.flight_tick)

    def explode(self, x, y):
        self.ball = None
        self.blast = x, y
        damage = []
        for index, player in enumerate(self.players):
            distance = math.hypot(player['x']-x, terrain_height(self.terrain, player['x'])+3-y)
            amount = max(0, round(48*(1-distance/20)))
            player['hp'] = max(0, player['hp']-amount)
            if amount:
                damage.append(f'{"你" if index == 0 else "電腦"}受到 {amount} 傷害')
        # 爆炸挖出小坑，角色會落到新的地面高度。
        for i in range(max(0, int(x)-11), min(181, int(x)+12)):
            dent = max(0, 1-abs(i-x)/11)*6
            self.terrain[i] = max(1, self.terrain[i]-dent)
        self.finish_turn('；'.join(damage) if damage else '差一點！爆炸沒有傷到任何一方。')

    def finish_turn(self, message):
        self.cancel()
        self.ball = None
        self.phase = 'settle'
        dead = [player['hp'] <= 0 for player in self.players]
        if any(dead):
            self.phase = 'over'
            result = '雙方同時倒下，平手！' if all(dead) else ('你贏了！' if dead[1] else '電腦獲勝，再挑戰一次吧！')
            self.hint.set(result + ' 按「重新對戰」再玩一局。')
        else:
            self.hint.set(message)
            self.schedule(1300, lambda: self.start_turn(1-self.turn))
        self.draw()

    def draw(self):
        if not hasattr(self, 'terrain'):
            return
        c = self.canvas
        c.delete('all')
        w, h = c.winfo_width(), c.winfo_height()
        if w < 100 or h < 100:
            return
        scale = min((w-70)/180, (h-100)/105)
        baseline = h-55
        def point(x, y):
            return 35+x*scale, baseline-y*scale
        # 天空與遠山純粹是裝飾，不影響碰撞。
        c.create_oval(w-150, 30, w-90, 90, fill='#fff2b2', outline='')
        c.create_polygon(0, baseline, w*.3, h*.4, w*.6, baseline, fill='#ccdfdd', outline='')
        coords = [0, h]
        for x in range(181):
            coords.extend(point(x, self.terrain[x]))
        coords.extend((w, h))
        c.create_polygon(*coords, fill='#947453', outline='#75583f', width=2, tags='terrain')
        for x in range(0,181,30):
            px, py = point(x, terrain_height(self.terrain,x))
            c.create_text(px, baseline+26, text=f'{x} m', fill='#ffffff')
        for index, player in enumerate(self.players):
            px, py = point(player['x'], terrain_height(self.terrain,player['x'])+8)
            image = self.image if index == 0 else self.enemy_image
            muzzle_x = .86 if index == 0 else .14
            c.create_image(px-image.width()*muzzle_x, py-image.height()*.34,
                           image=image, anchor='nw', tags='cannon')
            # 血條置於角色上方，顏色區分雙方。
            bar_y = py-50
            c.create_rectangle(px-38,bar_y,px+38,bar_y+9,fill='#d4dce5',outline='')
            c.create_rectangle(px-38,bar_y,px-38+76*player['hp']/100,bar_y+9,
                               fill='#16a37b' if index==0 else '#e75a5a',outline='')
            c.create_text(px,bar_y-13,text=f'{"玩家" if index==0 else "電腦"}  {player["hp"]} HP',fill='#24354b')
            if index == 0 and self.turn == 0 and self.phase in ('aim','charge'):
                theta=math.radians(self.angle.get())
                c.create_line(px,py,px+55*math.cos(theta),py-55*math.sin(theta),
                              arrow='last',fill='#e09b22',width=3)
        if len(self.trace)>1:
            coords=[n for x,y in self.trace for n in point(x,y)]
            c.create_line(*coords,fill='#6b829d',dash=(3,4),width=2)
        if self.ball:
            px,py=point(*self.ball)
            c.create_oval(px-6,py-6,px+6,py+6,fill='#737b86',outline='#303740',width=2,tags='ball')
        if self.blast:
            px,py=point(*self.blast)
            radius=20*scale
            c.create_oval(px-radius,py-radius,px+radius,py+radius,outline='#f19d38',width=3,dash=(5,3))
            c.create_oval(px-12,py-12,px+12,py+12,fill='#ffd47a',outline='#f97316',width=2)
        wind_text='無風' if self.wind == 0 else f'{"向右 →" if self.wind>0 else "← 向左"} {abs(self.wind):g}'
        turn_text='對戰結束' if self.phase=='over' else ('你的回合' if self.turn==0 else '電腦回合')
        self.info.set(f'第 {self.round} 回合  ·  {turn_text}  ·  風力 {wind_text}')
        if self.phase=='over':
            c.create_rectangle(w/2-150,35,w/2+150,86,fill='#fff8e8',outline='#e7c788')
            c.create_text(w/2,60,text='對戰結束｜重新對戰再挑戰',font=('Microsoft JhengHei',14,'bold'),fill='#674d2e')

    def close(self):
        self.cancel()
        self.root.destroy()


def main():
    root = tk.Tk()
    BattleGame(root)
    root.mainloop()


if __name__ == '__main__':
    main()
