from ui.components import create_result_area, show_toast
import tkinter as tk
from tkinter import ttk, filedialog
import os
import shutil

# 引入规则配置
from config.settings import FILE_EXTENSIONS, FOLDER_NAMES, SPECIFIC_FILE_NAMES, DEFAULT_FOLDER

# 初始化扫描结果与标签
scan_results = []
scan_labels = {}
clean_inner = None  # ✅ 统一的结果容器，保证每次只更新一个区域


def build_clean_panel(parent, clean_path_var, root):
    global clean_inner  # 设置为全局，便于更新内容

    ttk.Label(parent, text="🧹 违规文件清理工具", font=("Microsoft YaHei UI", 14, "bold")).pack(anchor=tk.W, pady=(0, 20))

    # 路径选择区域
    path_frame = ttk.Frame(parent)
    path_frame.pack(fill=tk.X, pady=6)
    ttk.Label(path_frame, text="清理路径：", width=10).pack(side=tk.LEFT)

    entry = ttk.Entry(path_frame, textvariable=clean_path_var, width=70)
    entry.pack(side=tk.LEFT, padx=5)
    entry.configure(foreground="black")

    ttk.Button(path_frame, text="浏览", command=lambda: browse_folder(clean_path_var)).pack(side=tk.LEFT)
    clean_path_var.set(DEFAULT_FOLDER)

    def browse_folder(var):
        path = filedialog.askdirectory()
        if path:
            var.set(os.path.normpath(path))

    # ✅ 只创建一次结果显示区域
    canvas, clean_inner_ref = create_result_area(parent)
    clean_inner = clean_inner_ref  # 绑定为全局 clean_inner

    def scan_folder():
        global scan_results, scan_labels, clean_inner

        folder = clean_path_var.get()
        if not os.path.exists(folder):
            show_toast(root, "路径无效，请检查输入")
            return

        # ✅ 清空旧内容
        for widget in clean_inner.winfo_children():
            widget.destroy()
        scan_labels.clear()
        scan_results.clear()

        found_items = []

        for root_dir, dirs, files in os.walk(folder, topdown=False):
            for name in files:
                file_path = os.path.join(root_dir, name)
                file_lower = name.lower()
                if any(file_lower.endswith(ext) for ext in FILE_EXTENSIONS) or any(keyword in name for keyword in SPECIFIC_FILE_NAMES):
                    found_items.append(file_path)
            for name in dirs:
                dir_path = os.path.join(root_dir, name)
                if name in FOLDER_NAMES:
                    found_items.append(dir_path)

        if found_items:
            for item in found_items:
                label = ttk.Label(clean_inner, text=f"发现违规项：{item}", wraplength=900, foreground="#bbbbbb")
                label.pack(anchor="w", padx=20)
                scan_labels[item] = label
        else:
            ttk.Label(clean_inner, text="✅ 未发现违规文件或文件夹。", foreground="#00ff88",
                      font=("Microsoft YaHei UI", 12, "bold")).pack(pady=20)

        scan_results.extend(found_items)

    def clean_folder():
        global scan_results, scan_labels

        if not scan_results:
            show_toast(root, "未发现违规项，请先扫描")
            return

        deleted_items = []
        failed_items = []

        for item in scan_results:
            try:
                if os.path.isfile(item):
                    os.remove(item)
                elif os.path.isdir(item):
                    shutil.rmtree(item)
                deleted_items.append(item)
                label = scan_labels[item]
                label.config(foreground="green", font=("Microsoft YaHei UI", 10, "overstrike"))
            except Exception as e:
                failed_items.append(item)
                label = scan_labels[item]
                label.config(foreground="red")
                print(f"删除失败：{item}，错误：{e}")

        scan_results.clear()
        show_toast(root, f"清理完成：已删除 {len(deleted_items)} 项，失败 {len(failed_items)} 项")

    # 操作按钮区域
    button_frame = ttk.Frame(parent)
    button_frame.pack(pady=10)
    ttk.Button(button_frame, text="扫描", command=scan_folder).pack(side=tk.LEFT, padx=10)
    ttk.Button(button_frame, text="清理", command=clean_folder).pack(side=tk.LEFT, padx=10)
