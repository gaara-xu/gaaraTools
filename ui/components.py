import tkinter as tk
from tkinter import ttk

def create_sidebar(parent, menu_items, on_select):
    menu_frame = tk.Frame(parent, width=180, bg="#1e1e1e")
    ttk.Label(menu_frame, text="功能菜单", background="#1e1e1e", foreground="white", font=("Microsoft YaHei UI", 12, "bold")).pack(pady=10)
    menu_listbox = tk.Listbox(menu_frame, bg="#1e1e1e", fg="white", font=("Microsoft YaHei UI", 11), selectbackground="#444")
    menu_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    for item in menu_items:
        menu_listbox.insert(tk.END, item)
    menu_listbox.select_set(0)
    menu_listbox.bind("<<ListboxSelect>>", lambda event: on_select(menu_listbox.get(menu_listbox.curselection())))
    return menu_frame, menu_listbox

def create_result_area(parent):
    container = ttk.Frame(parent)
    container.pack(fill=tk.BOTH, expand=True)

    canvas = tk.Canvas(container, bg="#2e2e2e", highlightthickness=0)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.configure(yscrollcommand=scrollbar.set)

    inner_frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=inner_frame, anchor="nw", width=960)

    def _on_mousewheel(event, canvas):
        """
        处理鼠标滚轮事件，滚动 Canvas。
        """
        if canvas.winfo_exists():  # 检查 Canvas 是否仍然存在
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", lambda event: _on_mousewheel(event, canvas))
    inner_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    return canvas, inner_frame

def show_toast(root, message, duration=2500):
    toast_label = ttk.Label(root, text=message, background="#444", foreground="#fff", font=("Microsoft YaHei UI", 11))
    toast_label.place(relx=0.5, rely=0.95, anchor="s")
    root.after(duration, lambda: toast_label.place_forget())
