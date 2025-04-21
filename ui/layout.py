import tkinter as tk
from tkinter import ttk, filedialog
from ui.components import create_sidebar
from features.compare import build_compare_panel
from features.clean import build_clean_panel
from config.settings import DEFAULT_FOLDER
import os  # 添加 os 模块
from features.db_compare import build_db_compare_panel  # 导入数据库比对功能
from features.download711url import build_download711url_panel  # 导入下载 711 URL 功能

class AppLayout:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("文件对比工具")
        self.root.geometry("1000x650")
        self.root.configure(bg="#2e2e2e")

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

        menu_items = ["文件夹对比", "违规文件清理", "数据库比对", "下载 711 URL"]  # 添加下载 711 URL 菜单项
        menu_frame, self.menu_listbox = create_sidebar(main_pane, menu_items, self._on_menu_select)
        main_pane.add(menu_frame)

        self.main_frame = ttk.Frame(main_pane, padding=20)
        main_pane.add(self.main_frame, stretch="always")

        self._on_menu_select(menu_items[0])  # 默认加载第一个功能

    def _on_menu_select(self, selection):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        if selection == "文件夹对比":
            left_path_var = tk.StringVar(value=DEFAULT_FOLDER)
            right_path_var = tk.StringVar(value=DEFAULT_FOLDER)
            build_compare_panel(self.main_frame, left_path_var, right_path_var, self.root)
        elif selection == "违规文件清理":
            clean_path_var = tk.StringVar(value=DEFAULT_FOLDER)
            build_clean_panel(self.main_frame, clean_path_var, self.root)
        elif selection == "数据库比对":
            target_path_var = tk.StringVar(value=DEFAULT_FOLDER)
            build_db_compare_panel(self.main_frame, target_path_var, self.root)
        elif selection == "下载 711 URL":  # 添加下载 711 URL 功能的调用
            build_download711url_panel(self.main_frame, self.root)

    def run(self):
        self.root.mainloop()
