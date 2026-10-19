# 大砲打靶：調整速度與角度，讓砲彈落進紅色目標。
# 執行 python GUI.py，不需要額外安裝套件。
import math
import random
import time
import tkinter as tk
from tkinter import ttk
from pathlib import Path


class CannonGame:
    def __init__(self, root):
        self.root = root
        root.title("大砲打靶｜拋射小遊戲")
        root.geometry("1050x700")
        root.minsize(760, 580)
        root.configure(bg="#f1f5f9")
        source = tk.PhotoImage(file=str(Path(__file__).parent / "assets" / "cannon_display.png"))
        self.cannon = source.subsample(max(1, (source.width() + 119) // 120))
        self.timer = None
        self.flying = False
        self.trail = []
        self.ball = None
        self.velocity = tk.DoubleVar(value=27)
        self.angle = tk.DoubleVar(value=45)
        self.message = tk.StringVar()
        self.score_text = tk.StringVar()
        self.settings = tk.StringVar()
        style = ttk.Style(root)
        style.configure("TButton", font=("Microsoft JhengHei", 11), padding=8)
        style.configure("TLabel", font=("Microsoft JhengHei", 11))
        ttk.Label(root, text="大砲打靶", font=("Microsoft JhengHei", 23, "bold"), background="#f1f5f9").pack(anchor="w", padx=24, pady=(16, 3))
        ttk.Label(root, text="5 發挑戰 · 調整力道與角度，讓砲彈落進紅色靶區！", background="#f1f5f9").pack(anchor="w", padx=24)
        panel = ttk.Frame(root, padding=12)
        panel.pack(fill="x", padx=20, pady=12)
        panel.columnconfigure(1, weight=1)
        ttk.Label(panel, text="初速度").grid(row=0, column=0, padx=8)
        self.speed_scale = ttk.Scale(panel, from_=10, to=36, variable=self.velocity, command=self.update_settings)
        self.speed_scale.grid(row=0, column=1, sticky="ew", padx=10)
        ttk.Label(panel, text="發射角度").grid(row=1, column=0, padx=8)
        self.angle_scale = ttk.Scale(panel, from_=10, to=80, variable=self.angle, command=self.update_settings)
        self.angle_scale.grid(row=1, column=1, sticky="ew", padx=10, pady=10)
        ttk.Label(panel, textvariable=self.settings, width=23).grid(row=0, column=2, rowspan=2, padx=10)
        self.fire_button = ttk.Button(panel, text="發射！ Space", command=self.fire)
        self.fire_button.grid(row=0, column=3, padx=6)
        ttk.Button(panel, text="重新開始", command=self.restart).grid(row=1, column=3, padx=6)
        self.canvas = tk.Canvas(root, bg="#eaf4fb", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=20)
        self.canvas.bind("<Configure>", lambda event: self.draw())
        footer = ttk.Frame(root, padding=14)
        footer.pack(fill="x", padx=10)
        ttk.Label(footer, textvariable=self.score_text, foreground="#1e3a5f").pack(side="right")
        ttk.Label(footer, textvariable=self.message, wraplength=540).pack(side="left")
        root.bind("<space>", lambda event: self.fire())
        root.protocol("WM_DELETE_WINDOW", self.close)
        self.restart()

    def update_settings(self, value=None):
        # get 讀取滑桿的數值，set 更新顯示文字。
        self.settings.set(f"速度：{self.velocity.get():.1f} m/s\n角度：{self.angle.get():.0f} 度")
        if hasattr(self, "target"):
            self.draw()  # 調整角度時，方向箭頭也跟著改變。

    def cancel_animation(self):
        if self.timer is not None:
            self.root.after_cancel(self.timer)
            self.timer = None

    def restart(self):
        self.cancel_animation()
        self.score, self.shots = 0, 5
        self.flying = False
        self.ball, self.trail = None, []
        self.velocity.set(27)
        self.angle.set(45)
        self.target = random.randint(38, 103)
        self.message.set("先調整滑桿，再按「發射」或空白鍵。")
        self.set_controls(True)
        self.update_settings()
        self.update_score()
        self.draw()

    def set_controls(self, enabled):
        # 飛行時鎖住滑桿，避免中途改變這一發的參數。
        state = "normal" if enabled else "disabled"
        for widget in (self.fire_button, self.speed_scale, self.angle_scale):
            widget.configure(state=state)

    def update_score(self):
        self.score_text.set(f"命中 {self.score} 次  /  剩餘 {self.shots} 發")

    def fire(self):
        if self.flying or self.shots == 0:
            return
        self.cancel_animation()
        # sin、cos 要用弧度；將初速度拆成水平與垂直速度。
        theta = math.radians(self.angle.get())
        velocity = self.velocity.get()
        self.vx = velocity * math.cos(theta)
        self.vy = velocity * math.sin(theta)
        self.duration = 2 * self.vy / 9.81
        self.range = self.vx * self.duration
        self.start_time = time.perf_counter()
        self.flying = True
        self.shots -= 1
        self.trail = [(0, 0)]
        self.ball = (0, 0)
        self.message.set("砲彈飛行中……")
        self.update_score()
        self.set_controls(False)
        self.tick()

    def tick(self):
        self.timer = None
        # 用真實經過時間計算位置，視窗更新較慢也不會讓動畫變慢。
        elapsed = min((time.perf_counter() - self.start_time) * 2, self.duration)
        x = self.vx * elapsed
        y = max(0, self.vy * elapsed - 0.5 * 9.81 * elapsed ** 2)
        self.ball = (x, y)
        self.trail.append(self.ball)
        self.draw()
        if elapsed >= self.duration:
            self.resolve_shot()
        else:
            self.timer = self.root.after(16, self.tick)  # 每次只排程一小步，不用 sleep。

    def resolve_shot(self):
        self.flying = False
        # 砲彈落在靶心左右 4 公尺以內就算命中。
        hit = abs(self.range - self.target) <= 4
        if hit:
            self.score += 1
            self.message.set("命中！+1 分，下一個目標出現了。")
        else:
            direction = "太近" if self.range < self.target else "太遠"
            self.message.set(f"{direction}了！落點 {self.range:.1f} m，差 {abs(self.range - self.target):.1f} m；再調整一下。")
        if self.shots == 0:
            self.message.set(f"挑戰結束！5 發命中 {self.score} 次。按「重新開始」再挑戰。")
        elif hit:
            # 下一個目標至少移動 12 公尺，方便看出位置改變。
            options = [x for x in range(38, 104) if abs(x - self.target) >= 12]
            self.target = random.choice(options)
        self.set_controls(self.shots > 0)
        self.update_score()
        self.draw()

    def draw(self):
        c = self.canvas
        c.delete("all")
        width, height = c.winfo_width(), c.winfo_height()
        if width < 100 or height < 100:
            return
        origin_x, ground = 120, height - 96
        # 所有回合固定比例，調整速度時才能比較飛得多遠。
        scale = min((width - 155) / 140, max(1, (height - 130)) / 72)

        def point(x, y):
            return origin_x + x * scale, ground - y * scale

        c.create_rectangle(0, ground, width, height, fill="#dbe8cc", outline="")
        c.create_line(0, ground, width, ground, fill="#8b9c6c", width=2)
        # 地面尺規與距離標籤。
        for distance in range(0, 141, 20):
            x, _ = point(distance, 0)
            c.create_line(x, ground, x, ground + 6, fill="#64748b")
            c.create_text(x, ground + 21, text=f"{distance} m", fill="#475569")
        c.create_text(18, 18, anchor="nw", text="重力 9.81 m/s²  ·  無風  ·  紅色區域 ±4 m", fill="#475569")
        # 靶區以公尺寬度繪製，判定範圍和畫面一致。
        target_x, _ = point(self.target, 0)
        c.create_rectangle(target_x - 4 * scale, ground - 6,
                           target_x + 4 * scale, ground + 5, fill="#ef4444", outline="")
        c.create_line(target_x, ground, target_x, ground - 55, fill="#7f1d1d", width=3)
        c.create_polygon(target_x, ground - 55, target_x + 26, ground - 46,
                         target_x, ground - 36, fill="#ef4444", outline="")
        c.create_text(target_x, ground - 74, text=f"目標 {self.target} m", fill="#991b1b", font=("Microsoft JhengHei", 11, "bold"))
        if len(self.trail) > 1:
            coords = [coordinate for x, y in self.trail for coordinate in point(x, y)]
            c.create_line(*coords, fill="#94a3b8", width=2, dash=(4, 4))
        # 對準圖片砲口，底座留在地面下方的裝飾區。
        c.create_image(origin_x - self.cannon.width() * .86,
                       ground - self.cannon.height() * .34, image=self.cannon, anchor="nw", tags="cannon")
        theta = math.radians(self.angle.get())
        c.create_line(origin_x, ground, origin_x + 50 * math.cos(theta),
                      ground - 50 * math.sin(theta), fill="#e49a22", width=2, arrow="last")
        c.create_arc(origin_x - 32, ground - 32, origin_x + 32, ground + 32,
                     start=0, extent=self.angle.get(), style="arc", outline="#e49a22", width=2)
        if self.ball:
            x, y = point(*self.ball)
            c.create_oval(x-6, y-6, x+6, y+6, fill="#737b86", outline="#303740", width=2, tags="ball")
            c.create_oval(x-3, y-3, x-1, y-1, fill="#d4d9df", outline="", tags="ball")

    def close(self):
        self.cancel_animation()
        self.root.destroy()


def main():
    root = tk.Tk()
    CannonGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
