# GUI.py：Tkinter 常用元件教學，執行 python GUI.py 開啟。
# tk 是基本元件；ttk 是外觀較現代的元件。
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser, simpledialog


def main():
    root = tk.Tk()  # 建立主視窗，一個程式通常只建立一個 Tk。
    root.title("Tkinter 常用範例")
    # 依螢幕大小設定視窗，避免視窗超出畫面。
    寬 = min(960, root.winfo_screenwidth() - 80)
    高 = min(760, root.winfo_screenheight() - 100)
    left = (root.winfo_screenwidth() - 寬) // 2
    top = (root.winfo_screenheight() - 高) // 2
    root.geometry(f"{寬}x{高}+{left}+{top}")  # x 分隔寬高，+ 後面是位置。

    status = tk.StringVar(value="歡迎！請切換分頁試用元件。")
    ttk.Label(root, text="Tkinter 元件練習", font=("Microsoft JhengHei", 18)).pack(pady=10)
    notebook = ttk.Notebook(root)  # Notebook：分頁容器。
    notebook.pack(fill="both", expand=True, padx=12, pady=5)

    def page(title):
        frame = ttk.Frame(notebook, padding=12)
        notebook.add(frame, text=title)
        return frame

    # ===== 1. 基本輸入 =====
    basic = page("基本輸入")
    # StringVar、BooleanVar、IntVar 可以讓變數與畫面連動。
    name = tk.StringVar(value="小明")
    greeting = tk.StringVar(value="你好！")
    subscribed = tk.BooleanVar(value=True)
    language = tk.StringVar(value="Python")
    ttk.Label(basic, text="Label：顯示文字").grid(row=0, column=0, sticky="w", pady=6)
    ttk.Label(basic, textvariable=greeting).grid(row=0, column=1, sticky="w")
    ttk.Label(basic, text="Entry：單行輸入").grid(row=1, column=0, sticky="w", pady=6)
    entry = ttk.Entry(basic, textvariable=name)
    entry.grid(row=1, column=1, sticky="ew")

    def say_hello():
        greeting.set(f"你好，{name.get().strip() or '訪客'}！")  # get 讀取，set 修改。

    # command 傳入函式名稱，不加 ()，按下時才執行。
    ttk.Button(basic, text="Button：打招呼", command=say_hello).grid(row=1, column=2, padx=8)
    entry.bind("<Return>", lambda event: say_hello())  # bind 函式會收到 event。
    ttk.Checkbutton(basic, text="Checkbutton：接收通知", variable=subscribed).grid(row=2, column=1, sticky="w", pady=8)
    ttk.Label(basic, text="Radiobutton：單選").grid(row=3, column=0, sticky="w")
    choices = ttk.Frame(basic)
    choices.grid(row=3, column=1, sticky="w")
    for text in ("Python", "Java", "C++"):
        ttk.Radiobutton(choices, text=text, variable=language, value=text).pack(side="left")
    ttk.Label(basic, text="Combobox：下拉選單").grid(row=4, column=0, sticky="w", pady=10)
    combo = ttk.Combobox(basic, values=["台北", "台中", "高雄"], state="readonly")
    combo.current(0)
    combo.grid(row=4, column=1, sticky="ew")
    combo.bind("<<ComboboxSelected>>", lambda event: status.set(f"選擇城市：{combo.get()}"))
    ttk.Label(basic, text="Spinbox：數字選擇").grid(row=5, column=0, sticky="w")
    ttk.Spinbox(basic, from_=1, to=100).grid(row=5, column=1, sticky="ew")
    ttk.Button(basic, text="讀取選項", command=lambda: status.set(
        f"通知：{subscribed.get()}；語言：{language.get()}；城市：{combo.get()}"
    )).grid(row=6, column=1, sticky="w", pady=12)
    basic.columnconfigure(1, weight=1)  # weight 讓這一欄隨視窗伸展。

    # ===== 2. 文字區與清單 =====
    lists = page("文字與清單")
    panes = ttk.Panedwindow(lists, orient="horizontal")  # 可拖曳中間分隔線。
    panes.pack(fill="both", expand=True)
    editor_frame = ttk.LabelFrame(panes, text="Text + Scrollbar：多行文字", padding=8)
    list_frame = ttk.LabelFrame(panes, text="Listbox：清單", padding=8)
    panes.add(editor_frame, weight=3)
    panes.add(list_frame, weight=2)
    editor = tk.Text(editor_frame, wrap="word", undo=True, width=35, height=10)
    scrollbar = ttk.Scrollbar(editor_frame, orient="vertical", command=editor.yview)
    editor.configure(yscrollcommand=scrollbar.set)  # 文字與捲軸雙向連接。
    scrollbar.pack(side="right", fill="y")
    editor.pack(fill="both", expand=True)
    editor.insert("1.0", "在這裡輸入文字。\n可以使用上方選單開啟或儲存 UTF-8 文字檔。")
    item_name = tk.StringVar()
    ttk.Entry(list_frame, textvariable=item_name).pack(fill="x", pady=4)
    item_list = tk.Listbox(list_frame, height=8, exportselection=False)
    item_list.pack(fill="both", expand=True)
    for fruit in ("蘋果", "香蕉", "橘子"):
        item_list.insert("end", fruit)

    def add_item():
        text = item_name.get().strip()
        if text:
            item_list.insert("end", text)
            item_name.set("")

    def delete_item():
        for index in reversed(item_list.curselection()):
            item_list.delete(index)

    ttk.Button(list_frame, text="新增項目", command=add_item).pack(fill="x", pady=4)
    ttk.Button(list_frame, text="刪除選取", command=delete_item).pack(fill="x")

    # ===== 3. 表格、滑桿、進度條 =====
    data = page("表格與進度")
    tree = ttk.Treeview(data, columns=("name", "score"), show="headings", height=5)
    tree.heading("name", text="姓名")
    tree.heading("score", text="分數")
    tree.column("score", width=100, anchor="center")
    tree.pack(fill="x")
    for row in (("小明", 90), ("小華", 85), ("小美", 95)):
        tree.insert("", "end", values=row)

    def select_row(event):
        selected = tree.selection()
        if selected:
            status.set(f"選取資料：{tree.item(selected[0], 'values')}")

    tree.bind("<<TreeviewSelect>>", select_row)
    ttk.Separator(data).pack(fill="x", pady=15)  # 分隔線。
    amount = tk.DoubleVar(value=30)
    amount_text = tk.StringVar(value="進度：30%")

    def update_amount(value):
        amount_text.set(f"進度：{float(value):.0f}%")

    ttk.Label(data, text="Scale：拖曳滑桿調整進度").pack(anchor="w")
    ttk.Scale(data, from_=0, to=100, variable=amount, command=update_amount).pack(fill="x", pady=8)
    ttk.Progressbar(data, maximum=100, variable=amount).pack(fill="x")
    ttk.Label(data, textvariable=amount_text).pack(pady=6)
    busy = ttk.Progressbar(data, mode="indeterminate")  # 不確定完成時間的進度條。
    busy.pack(fill="x", pady=8)
    ttk.Button(data, text="開始等待動畫", command=lambda: busy.start(12)).pack(side="left")
    ttk.Button(data, text="停止動畫", command=busy.stop).pack(side="left", padx=8)

    # ===== 4. Canvas 與滑鼠事件 =====
    drawing = page("畫布與事件")
    ttk.Label(drawing, text="在畫布按住滑鼠左鍵畫線；移動滑鼠可看到座標。").pack(anchor="w")
    canvas = tk.Canvas(drawing, bg="white", height=340, highlightthickness=1)
    canvas.pack(fill="both", expand=True, pady=8)
    canvas.create_rectangle(30, 30, 150, 100, fill="#bfdbfe", outline="#2563eb")
    ball = canvas.create_oval(180, 30, 250, 100, fill="#fbbf24")
    canvas.create_line(30, 140, 250, 140, fill="#16a34a", width=4)
    canvas.create_text(140, 180, text="Canvas 可以畫圖形、文字與線條")
    previous = [None]

    def start_draw(event):
        previous[0] = (event.x, event.y)

    def draw(event):
        if previous[0] is not None:
            x, y = previous[0]
            canvas.create_line(x, y, event.x, event.y, width=3, fill="#334155")
        previous[0] = (event.x, event.y)

    canvas.bind("<Button-1>", start_draw)
    canvas.bind("<B1-Motion>", draw)
    canvas.bind("<ButtonRelease-1>", lambda event: previous.__setitem__(0, None))
    canvas.bind("<Motion>", lambda event: status.set(f"滑鼠座標：x={event.x}，y={event.y}"))
    ttk.Button(drawing, text="移動黃色圓形", command=lambda: canvas.move(ball, 15, 0)).pack(side="left")
    ttk.Button(drawing, text="清空畫布", command=lambda: canvas.delete("all")).pack(side="left", padx=8)

    # ===== 5. 對話框、子視窗、計時器 =====
    dialogs = page("對話框與計時")

    def open_file():
        path = filedialog.askopenfilename(parent=root, filetypes=[("文字檔", "*.txt"), ("全部檔案", "*.*")])
        if not path:  # 按取消時不處理。
            return
        try:
            with open(path, encoding="utf-8") as file:
                content = file.read()
        except (OSError, UnicodeError) as error:
            messagebox.showerror("開啟失敗", str(error), parent=root)
            return
        editor.delete("1.0", "end")
        editor.insert("1.0", content)
        notebook.select(lists)
        status.set(f"已開啟：{path}")

    def save_file():
        path = filedialog.asksaveasfilename(parent=root, defaultextension=".txt", filetypes=[("文字檔", "*.txt")])
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as file:
                file.write(editor.get("1.0", "end-1c"))  # 排除 Text 自動加入的最後換行。
        except OSError as error:
            messagebox.showerror("儲存失敗", str(error), parent=root)
            return
        status.set(f"已儲存：{path}")

    def choose_color():
        color = colorchooser.askcolor(parent=root, title="選擇畫布背景")[1]
        if color:
            canvas.configure(bg=color)
            notebook.select(drawing)

    def ask_name():
        answer = simpledialog.askstring("輸入", "你叫什麼名字？", parent=root)
        if answer is not None:
            name.set(answer)
            say_hello()
            status.set(greeting.get())

    def confirm():
        answer = messagebox.askyesno("確認", "你喜歡 Python 嗎？", parent=root)
        status.set(f"確認結果：{'是' if answer else '否'}")

    def child_window():
        child = tk.Toplevel(root)  # 子視窗使用 Toplevel，不再建立 Tk。
        child.title("子視窗")
        child.geometry("320x180")
        child.transient(root)
        ttk.Label(child, text="這是另一個視窗！").pack(pady=25)
        ttk.Button(child, text="關閉", command=child.destroy).pack()

    for text, callback in (
        ("訊息框", lambda: messagebox.showinfo("提示", "這是提示訊息。", parent=root)),
        ("確認框", confirm), ("輸入框", ask_name), ("選擇顏色", choose_color),
        ("開啟文字檔", open_file), ("儲存文字檔", save_file), ("開啟子視窗", child_window),
    ):
        ttk.Button(dialogs, text=text, command=callback).pack(anchor="w", pady=3)
    seconds = tk.IntVar(value=0)
    ttk.Label(dialogs, text="程式啟動秒數（after 示範）").pack(anchor="w", pady=(12, 0))
    ttk.Label(dialogs, textvariable=seconds).pack(anchor="w")

    def tick():
        seconds.set(seconds.get() + 1)
        root.after(1000, tick)  # 排程下一次執行；不使用 sleep 卡住畫面。

    timer = root.after(1000, tick)

    # ===== 6. 三種排版 =====
    layout = page("排版")
    ttk.Label(layout, text="同一個容器內不要混用 pack 與 grid；不同 Frame 可以各用各的。").pack(anchor="w", pady=8)
    pack_box = ttk.LabelFrame(layout, text="pack：依序排列", padding=10)
    pack_box.pack(fill="x", pady=8)
    for text in ("左邊", "中間", "右邊"):
        ttk.Label(pack_box, text=text, relief="solid", padding=10).pack(side="left", padx=5)
    grid_box = ttk.LabelFrame(layout, text="grid：像表格一樣指定列與欄", padding=10)
    grid_box.pack(fill="x", pady=8)
    for row in range(2):
        for column in range(3):
            ttk.Label(grid_box, text=f"列 {row}，欄 {column}", relief="solid", padding=8).grid(row=row, column=column, padx=4, pady=4, sticky="ew")
    place_box = ttk.LabelFrame(layout, text="place：指定位置或比例", height=110)
    place_box.pack(fill="x", pady=8)
    ttk.Label(place_box, text="x=15, y=15").place(x=15, y=15)
    ttk.Button(place_box, text="置中按鈕").place(relx=0.5, rely=0.5, anchor="center")

    # Menu：視窗上方選單；右鍵選單也能使用 Menu。
    menu = tk.Menu(root)
    file_menu = tk.Menu(menu, tearoff=False)
    file_menu.add_command(label="開啟文字檔", command=open_file)
    file_menu.add_command(label="儲存文字檔", command=save_file)
    file_menu.add_separator()
    file_menu.add_command(label="離開", command=root.destroy)
    menu.add_cascade(label="檔案", menu=file_menu)
    menu.add_command(label="關於", command=lambda: messagebox.showinfo("關於", "Tkinter 常用範例\n使用 Python 內建套件。", parent=root))
    root.configure(menu=menu)
    # 快捷鍵同樣透過 bind 綁定。
    root.bind("<Control-o>", lambda event: open_file())
    root.bind("<Control-s>", lambda event: save_file())
    ttk.Label(root, textvariable=status, relief="sunken", padding=5).pack(fill="x", padx=12, pady=8)
    root.mainloop()  # 持續接收按鈕、鍵盤與滑鼠事件。


if __name__ == "__main__":
    main()  # 直接執行檔案時才開啟視窗。
