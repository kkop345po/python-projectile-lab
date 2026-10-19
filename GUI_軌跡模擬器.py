# 執行 python GUI.py：左邊輸入參數，右邊顯示斜向拋射軌跡。
import tkinter as tk
from tkinter import ttk
from math import radians, sin, cos
from pathlib import Path
from test import calculate_projectile


class ProjectileApp:
    def __init__(self, root):
        self.root = root
        # 使用檔案所在位置找圖片，從其他資料夾執行也能載入。
        # 使用重新編碼的 PNG，避免 Tk 誤讀圖片中附帶的預覽圖示。
        source = tk.PhotoImage(file=str(Path(__file__).parent / "assets" / "cannon_display.png"))
        self.cannon_image = source.subsample(max(1, (source.width() + 139) // 140))
        root.title("斜向拋射｜軌跡模擬器")
        width = min(1100, root.winfo_screenwidth() - 80)
        height = min(720, root.winfo_screenheight() - 100)
        root.geometry(f"{width}x{height}")
        root.minsize(680, 480)
        root.configure(bg="#eef2f7")
        self.result = None  # 儲存上一次成功計算的參數。
        self.animation = None  # 儲存 after 的編號，方便取消動畫。
        self.frame = 0
        self.playing = False
        style = ttk.Style(root)
        style.configure("TLabel", font=("Microsoft JhengHei", 11))
        style.configure("TButton", font=("Microsoft JhengHei", 11), padding=8)
        style.configure("TEntry", padding=7)
        ttk.Label(root, text="斜向拋射軌跡", font=("Microsoft JhengHei", 20, "bold"),
                  background="#eef2f7").pack(anchor="w", padx=22, pady=(18, 4))
        ttk.Label(root, text="輸入參數，觀察拋物線與發射角度", background="#eef2f7").pack(anchor="w", padx=22)
        body = ttk.Frame(root, padding=16)
        body.pack(fill="both", expand=True, padx=12, pady=12)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)
        controls = ttk.Frame(body, padding=(0, 0, 20, 0))
        controls.grid(row=0, column=0, sticky="ns")
        self.inputs = {}
        # 每個 Label 旁邊放一個 Entry，對應草圖的標籤與輸入框。
        for row, (key, label, default) in enumerate((
            ("velocity", "初速度（m/s）", "30"),
            ("angle", "發射角度（度）", "45"),
            ("gravity", "重力加速度（m/s^2）", "9.81"),
        )):
            ttk.Label(controls, text=label).grid(row=row * 2, column=0, sticky="w", pady=(10, 5))
            value = tk.StringVar(value=default)
            self.inputs[key] = value
            ttk.Entry(controls, textvariable=value, width=23).grid(row=row * 2 + 1, column=0, sticky="ew")
        ttk.Button(controls, text="計算並畫圖（Enter）", command=self.calculate).grid(row=6, column=0, sticky="ew", pady=(18, 6))
        ttk.Button(controls, text="播放飛行動畫", command=self.play).grid(row=7, column=0, sticky="ew", pady=4)
        ttk.Button(controls, text="恢復預設值", command=self.reset).grid(row=8, column=0, sticky="ew", pady=4)
        self.message = tk.StringVar()
        ttk.Label(controls, textvariable=self.message, foreground="#b42318", wraplength=225).grid(row=9, column=0, sticky="w", pady=8)
        self.summary = tk.StringVar()
        ttk.Label(controls, textvariable=self.summary, justify="left", wraplength=225).grid(row=10, column=0, sticky="w", pady=8)
        self.canvas = tk.Canvas(body, bg="#ffffff", highlightthickness=1, highlightbackground="#cbd5e1")
        self.canvas.grid(row=0, column=1, sticky="nsew")
        # 視窗大小改變時，重新計算畫布座標。
        self.canvas.bind("<Configure>", lambda event: self.draw())
        root.bind("<Return>", lambda event: self.calculate())
        ttk.Label(root, text="模型：忽略空氣阻力，起點與落點等高。角度可輸入 0～90 度。",
                  background="#eef2f7").pack(anchor="w", padx=22, pady=(0, 14))
        self.calculate()

    def stop(self):
        if self.animation is not None:
            self.root.after_cancel(self.animation)
            self.animation = None
        self.playing = False

    def calculate(self):
        try:
            velocity, angle, gravity = (float(self.inputs[key].get()) for key in ("velocity", "angle", "gravity"))
            height, distance, duration = calculate_projectile(velocity, angle, gravity)
        except ValueError as error:
            self.message.set(f"請檢查輸入：{error}")
            return  # 保留前一次成功的圖，不讓錯誤輸入造成閃退。
        self.stop()
        self.result = velocity, angle, gravity, height, distance, duration
        self.frame = 0
        self.message.set("")
        self.summary.set(f"最大高度 H：{self.number(height)} m\n\n水平射程 R：{self.number(distance)} m\n\n飛行時間 T：{self.number(duration)} s\n\n角度轉弧度：{radians(angle):.4f} rad")
        self.draw()

    def reset(self):
        for key, value in (("velocity", "30"), ("angle", "45"), ("gravity", "9.81")):
            self.inputs[key].set(value)
        self.calculate()

    @staticmethod
    def number(value):
        # 大數字用科學記號，避免文字太長換行。
        return f"{value:.3e}" if abs(value) >= 1_000_000 else f"{value:.3f}"

    def draw(self):
        if self.result is None:
            return
        c = self.canvas
        c.delete("all")
        width, height_px = c.winfo_width(), c.winfo_height()
        if width < 150 or height_px < 150:
            return
        velocity, angle, gravity, height, distance, duration = self.result
        theta = radians(angle)  # sin 和 cos 使用弧度。
        vertical = velocity * sin(theta)
        horizontal = 0.0 if angle == 90 else velocity * cos(theta)
        # 左側與下方預留大砲空間，原點對準砲口。
        left, bottom = 128, height_px - 120
        plot_width, plot_height = max(40, width - 164), max(40, height_px - 185)
        # x、y 使用相同比例，保留軌跡的真實形狀。
        extent = max(distance, height)
        scale = min(plot_width / (distance / extent if distance else 1),
                    plot_height / (height / extent if height else 1)) if extent else 1

        def point(fraction):
            # 使用時間比例計算位置，避免極大初速度造成中間運算溢位。
            x = distance * fraction
            y = height * (4 * fraction * (1 - fraction))
            return left + (x / extent * scale if extent else 0), bottom - (y / extent * scale if extent else 0)

        self.point = point
        # 座標軸與格線。
        for index in range(1, 5):
            x = left + plot_width * index / 4
            y = bottom - plot_height * index / 4
            c.create_line(x, bottom, x, bottom - plot_height, fill="#edf1f6")
            c.create_line(left, y, left + plot_width, y, fill="#edf1f6")
            c.create_text(x, bottom + 17, text=f"{extent * (plot_width * index / 4 / scale):.3g}", fill="#64748b")
            c.create_text(left - 8, y, text=f"{extent * (plot_height * index / 4 / scale):.3g}", anchor="e", fill="#64748b")
        c.create_line(left, bottom, width - 20, bottom, arrow="last", fill="#64748b", width=2)
        c.create_line(left, bottom, left, 24, arrow="last", fill="#64748b", width=2)
        c.create_text(width - 22, bottom + 72, text="水平距離（m）", anchor="e", tags="x_title")
        c.create_text(left, 16, text="高度（m）", anchor="w")
        c.create_text(left - 8, bottom + 16, text="0")
        # 用許多時間點連成平滑拋物線。
        points = [coordinate for i in range(201) for coordinate in point(i / 200)]
        c.create_line(*points, fill="#2563eb", width=3, tags="trajectory")
        peak_x, peak_y = point(0.5)
        c.create_oval(peak_x - 4, peak_y - 4, peak_x + 4, peak_y + 4, fill="#2563eb", outline="")
        c.create_text(peak_x, peak_y - 18, text=f"H = {height:.3g} m", fill="#1d4ed8")
        end_x, end_y = point(1)
        # 射程放在落點上方，靠右對齊以免超出畫布。
        c.create_text(end_x - 8, end_y - 20, text=f"R = {distance:.3g} m",
                      anchor="e", fill="#1d4ed8", tags="range_label")
        # 圖片的砲口約在寬 86%、高 34% 的位置。
        c.create_image(left - self.cannon_image.width() * 0.86,
                       bottom - self.cannon_image.height() * 0.34,
                       image=self.cannon_image, anchor="nw", tags="cannon")
        # 額外畫小角度弧線與方向箭頭，標示發射仰角。
        radius = 42
        if angle > 0:
            c.create_arc(left - radius, bottom - radius, left + radius, bottom + radius,
                         start=0, extent=angle, style="arc", outline="#f59e0b", width=2)
        c.create_line(left, bottom, left + 72 * cos(theta), bottom - 72 * sin(theta),
                      arrow="last", fill="#f59e0b", width=2)
        c.create_text(left + 88, bottom - 30, text=f"θ = {angle:g}°", fill="#a16207")
        self.draw_ball()

    def draw_ball(self):
        if not hasattr(self, "point"):
            return
        c = self.canvas
        c.delete("ball")
        c.delete("time")
        x, y = self.point(self.frame / 120)
        # 灰色砲彈加深色外框與小反光，搭配金屬砲管。
        c.create_oval(x - 7, y - 7, x + 7, y + 7, fill="#707780", outline="#303740", width=2, tags="ball")
        c.create_oval(x - 4, y - 4, x - 1, y - 1, fill="#cbd0d6", outline="", tags="ball")
        c.create_text(c.winfo_width() - 18, 18, anchor="ne", tags="time",
                      text=f"t = {self.number(self.result[5] * self.frame / 120)} s", fill="#475569")

    def play(self):
        self.calculate()  # 播放前先套用目前輸入。
        if self.message.get():
            return
        self.playing = True
        self.step()

    def step(self):
        self.animation = None
        self.draw_ball()
        if self.frame < 120:
            self.frame += 1
            self.animation = self.root.after(25, self.step)  # 三秒示範動畫，不阻塞視窗。
        else:
            self.playing = False


def main():
    root = tk.Tk()
    app = ProjectileApp(root)
    def close():
        app.stop()
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", close)
    root.mainloop()


if __name__ == "__main__":
    main()
