import tkinter as tk
from tkinter import ttk, filedialog
from ui.components import create_sidebar
from features import load_features

class AppLayout:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("文件对比工具")
        self.root.geometry("1000x650")
        self.root.configure(bg="#2e2e2e")

        # Load feature registry
        self.features = load_features()

        self._apply_dark_theme()
        self._build_ui()

    def _apply_dark_theme(self):
        style = ttk.Style(self.root)
        style.theme_use("default")

        self.base_font = ("Microsoft YaHei UI", 11)

        style.configure(".", background="#2e2e2e", foreground="#ffffff", font=self.base_font)
        style.configure("TLabel", background="#2e2e2e", foreground="#ffffff", font=self.base_font)
        style.configure("TButton", background="#3c3c3c", foreground="#ffffff", padding=6, relief="flat", font=self.base_font)
        style.map("TButton", background=[("active", "#555"), ("pressed", "#666")])
        style.configure("TCombobox", fieldbackground="#3a3a3a", background="#3a3a3a", foreground="#ffffff", padding=4, font=self.base_font)

        # 默认输入框文字颜色为黑色
        style.configure("TEntry", foreground="black")
        style.configure("TText", foreground="black")

    def _build_ui(self):
        main_pane = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg="#2e2e2e")
        main_pane.pack(fill=tk.BOTH, expand=True)

        menu_items = list(self.features.keys())
        menu_frame, self.menu_listbox = create_sidebar(main_pane, menu_items, self._on_menu_select)
        main_pane.add(menu_frame)

        self.main_frame = ttk.Frame(main_pane, padding=20)
        main_pane.add(self.main_frame, stretch="always")

        if menu_items:
            self._on_menu_select(menu_items[0])  # 默认加载第一个功能

    def _on_menu_select(self, selection):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        builder = self.features.get(selection)
        if builder:
            builder(self.main_frame, self.root)

    def run(self):
        self.root.mainloop()
