import os
import re
from ui.components import create_result_area, show_toast
import tkinter as tk
from tkinter import ttk, filedialog

def build_tv_rename_panel(parent, default_folder_var, root):
    ttk.Label(parent, text="📺 电视剧名称专用工具", font=("Microsoft YaHei UI", 14, "bold")).pack(anchor=tk.W, pady=(0, 20))

    def create_path_selector(label_text, var):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=6)
        ttk.Label(frame, text=label_text, width=12).pack(side=tk.LEFT)
        entry = ttk.Entry(frame, textvariable=var, width=70)
        entry.pack(side=tk.LEFT, padx=5)
        entry.configure(foreground="black")
        ttk.Button(frame, text="浏览", command=lambda: browse_folder(var)).pack(side=tk.LEFT)

    def browse_folder(var):
        path = filedialog.askdirectory()
        if path:
            var.set(os.path.normpath(path))

    create_path_selector("目标文件夹：", default_folder_var)

    # 输入框：电视剧名称
    name_frame = ttk.Frame(parent)
    name_frame.pack(fill=tk.X, pady=6)
    ttk.Label(name_frame, text="电视剧名称：", width=12).pack(side=tk.LEFT)
    tv_name_var = tk.StringVar()
    ttk.Entry(name_frame, textvariable=tv_name_var, width=70).pack(side=tk.LEFT, padx=5)

    # 输入框：第几季
    season_frame = ttk.Frame(parent)
    season_frame.pack(fill=tk.X, pady=6)
    ttk.Label(season_frame, text="第几季：", width=12).pack(side=tk.LEFT)
    season_var = tk.StringVar()
    ttk.Entry(season_frame, textvariable=season_var, width=70).pack(side=tk.LEFT, padx=5)

    # 结果展示区域
    canvas, result_inner = create_result_area(parent)

    def extract_episode_number(filename):
        """
        从文件名中提取集数（如 03、3 或 332）。
        """
        # 修改正则表达式，匹配连续的数字（1-3 位），并排除文件扩展名部分
        match = re.search(r'(?<!\d)(\d{1,3})(?=\D|$)', filename)
        return match.group(1) if match else None

    def preview_rename():
        """
        预览批量重命名的效果。
        """
        folder = default_folder_var.get()
        if not os.path.exists(folder):
            show_toast(root, "路径无效，请检查输入")
            return

        tv_name = tv_name_var.get().strip()
        season = season_var.get().strip()
        if not tv_name or not season:
            show_toast(root, "请输入电视剧名称和第几季")
            return

        # 清空旧内容
        for widget in result_inner.winfo_children():
            widget.destroy()

        files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
        if not files:
            ttk.Label(result_inner, text="✅ 文件夹中没有文件。", foreground="#00ff88", font=("Microsoft YaHei UI", 12, "bold")).pack(pady=20)
            return

        for file in files:
            episode = extract_episode_number(file)
            if episode:
                file_name, file_ext = os.path.splitext(file)  # 分离文件名和后缀
                new_name = f"{tv_name}S{season.zfill(2)}E{episode.zfill(2)}{file_ext}"  # 保留后缀
                ttk.Label(result_inner, text=f"{file} → {new_name}", wraplength=900, foreground="#bbbbbb").pack(anchor="w", padx=20)
            else:
                ttk.Label(result_inner, text=f"无法识别集数：{file}", wraplength=900, foreground="yellow").pack(anchor="w", padx=20)

    def execute_rename():
        """
        执行批量重命名操作。
        """
        folder = default_folder_var.get()
        if not os.path.exists(folder):
            show_toast(root, "路径无效，请检查输入")
            return

        tv_name = tv_name_var.get().strip()
        season = season_var.get().strip()
        if not tv_name or not season:
            show_toast(root, "请输入电视剧名称和第几季")
            return

        # 清空旧内容
        for widget in result_inner.winfo_children():
            widget.destroy()

        files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
        if not files:
            ttk.Label(result_inner, text="✅ 文件夹中没有文件。", foreground="#00ff88", font=("Microsoft YaHei UI", 12, "bold")).pack(pady=20)
            return

        success_count = 0
        failed_count = 0

        for file in files:
            episode = extract_episode_number(file)
            if episode:
                old_path = os.path.join(folder, file)
                file_name, file_ext = os.path.splitext(file)  # 分离文件名和后缀
                new_name = f"{tv_name}S{season.zfill(2)}E{episode.zfill(2)}{file_ext}"  # 保留后缀
                new_path = os.path.join(folder, new_name)

                try:
                    os.rename(old_path, new_path)
                    success_count += 1
                    ttk.Label(result_inner, text=f"成功重命名：{file} → {new_name}", wraplength=900, foreground="green").pack(anchor="w", padx=20)
                except Exception as e:
                    failed_count += 1
                    ttk.Label(result_inner, text=f"重命名失败：{file}，错误：{e}", wraplength=900, foreground="red").pack(anchor="w", padx=20)
            else:
                ttk.Label(result_inner, text=f"无法识别集数：{file}", wraplength=900, foreground="yellow").pack(anchor="w", padx=20)

        show_toast(root, f"重命名完成：成功 {success_count} 个，失败 {failed_count} 个")

    # 操作按钮区域
    button_frame = ttk.Frame(parent)
    button_frame.pack(pady=10)
    ttk.Button(button_frame, text="预览", command=preview_rename).pack(side=tk.LEFT, padx=10)
    ttk.Button(button_frame, text="执行", command=execute_rename).pack(side=tk.LEFT, padx=10)

from . import register_feature
from config.settings import DEFAULT_FOLDER

def _init_feature(parent, root):
    default_folder_var = tk.StringVar(value=DEFAULT_FOLDER)
    build_tv_rename_panel(parent, default_folder_var, root)

register_feature("电视剧名称专用")(_init_feature)

