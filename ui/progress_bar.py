import tkinter as tk
from tkinter import ttk

class ProgressBar:
    def __init__(self, parent, total_steps: int):
        """
        初始化进度条组件。
        :param parent: 父容器
        :param total_steps: 总步数
        """
        self.total_steps = total_steps
        self.current_step = 0

        # 创建进度条容器
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.X, pady=10)

        # 创建进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.frame,
            variable=self.progress_var,
            maximum=100,
            length=400,
            mode="determinate",
        )
        self.progress_bar.pack(fill=tk.X, padx=10)

        # 设置绿色样式
        style = ttk.Style()
        style.configure("green.Horizontal.TProgressbar", troughcolor="#2e2e2e", background="#00ff88")
        self.progress_bar.configure(style="green.Horizontal.TProgressbar")

    def update(self, step: int = 1):
        """
        更新进度条。
        :param step: 增加的步数，默认为 1
        """
        self.current_step += step
        progress_percentage = (self.current_step / self.total_steps) * 100
        self.progress_var.set(progress_percentage)

    def reset(self):
        """
        重置进度条。
        """
        self.current_step = 0
        self.progress_var.set(0)
