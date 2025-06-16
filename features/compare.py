from ui.components import create_result_area, show_toast
from modules.file_utils import get_all_files, get_file_size
import tkinter as tk
from tkinter import ttk, filedialog
import os
from concurrent.futures import ThreadPoolExecutor

redundant_files = []

def build_compare_panel(parent, left_path_var, right_path_var, root):
    ttk.Label(parent, text="📁 文件夹对比工具", font=("Microsoft YaHei UI", 14, "bold")).pack(anchor=tk.W, pady=(0, 20))

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

    create_path_selector("源文件夹：", left_path_var)
    create_path_selector("目标文件夹：", right_path_var)

    button_frame = ttk.Frame(parent)
    button_frame.pack(fill=tk.X, pady=10)

    canvas, result_inner = create_result_area(parent)

    def compare_folders():
        global redundant_files
        redundant_files.clear()
        for widget in result_inner.winfo_children():
            widget.destroy()

        source = left_path_var.get()
        target = right_path_var.get()
        if not os.path.exists(source) or not os.path.exists(target):
            show_toast(root, "路径无效，请检查输入")
            return

        source_files = get_all_files(source)
        target_files = get_all_files(target)

        size_map_source = {}
        size_map_target = {}

        def map_worker(file_path):
            return file_path, get_file_size(file_path)

        with ThreadPoolExecutor(max_workers=6) as executor:
            for path, size in executor.map(map_worker, source_files):
                size_map_source.setdefault(size, []).append(path)
            for path, size in executor.map(map_worker, target_files):
                size_map_target.setdefault(size, []).append(path)

        has_result = False

        if os.path.abspath(source) == os.path.abspath(target):
            for size, files in size_map_source.items():
                if len(files) > 1:
                    has_result = True
                    add_result_group(result_inner, f"🔁 重复组：{size:,} B", files, allow_delete=files[1:])  # 保留第一个
        else:
            for size in size_map_source:
                if size in size_map_target:
                    has_result = True
                    src_files = size_map_source[size]
                    tgt_files = size_map_target[size]
                    all_files = src_files + tgt_files
                    add_result_group(result_inner, f"🔁 大小匹配：{size:,} B", all_files, allow_delete=tgt_files)  # 只允许删除目标文件夹文件

        if has_result:
            delete_all_button.config(state=tk.NORMAL)
        else:
            ttk.Label(result_inner, text="✅ 未发现重复文件。", foreground="#00ff88", font=("Microsoft YaHei UI", 12, "bold")).pack(pady=20)

    def add_result_group(parent, title, files, allow_delete=None):
        group = ttk.LabelFrame(parent, text=title, padding=10)
        group.pack(fill=tk.X, expand=True, padx=10, pady=8)

        for file in files:
            can_delete = allow_delete and file in allow_delete
            row = ttk.Frame(group)
            row.pack(fill=tk.X, pady=4)

            ttk.Label(row, text=f"📄 {os.path.basename(file)}").pack(side=tk.LEFT, padx=10)
            ttk.Label(row, text=f"路径: {file}", wraplength=900, foreground="#bbbbbb").pack(side=tk.LEFT, padx=10)

            if can_delete:
                redundant_files.append(file)
                ttk.Button(row, text="删除", command=lambda f=file, r=row, g=group, fs=files: delete_one_file(f, r, g, fs)).pack(side=tk.RIGHT)

    def delete_one_file(file_path, row_widget, group_widget, files):
        try:
            os.remove(file_path)
            row_widget.destroy()
            if file_path in redundant_files:
                redundant_files.remove(file_path)
            show_toast(root, f"已删除：{file_path}")
            files.remove(file_path)
            remaining = [f for f in files if f in redundant_files]
            if len(remaining) <= 1:
                group_widget.destroy()
        except FileNotFoundError:
            show_toast(root, f"删除失败：文件未找到\n路径：{file_path}")
        except PermissionError:
            show_toast(root, f"删除失败：权限不足\n路径：{file_path}")
        except Exception as e:
            show_toast(root, f"删除失败：{file_path}\n错误：{e}")

    def delete_all_files():
        deleted = 0
        failed = 0
        failed_files = []

        for file in list(redundant_files):
            try:
                os.remove(file)
                redundant_files.remove(file)
                deleted += 1
            except Exception:
                failed += 1
                failed_files.append(file)

        for widget in result_inner.winfo_children():
            widget.destroy()

        if failed > 0:
            show_toast(root, f"已删除 {deleted} 个文件，{failed} 个文件删除失败\n失败文件：{', '.join(failed_files)}")
        else:
            show_toast(root, f"已删除 {deleted} 个文件，全部删除成功！")
        delete_all_button.config(state=tk.DISABLED)

    ttk.Button(button_frame, text="开始比对", command=compare_folders).pack(side=tk.LEFT, padx=5)
    delete_all_button = ttk.Button(button_frame, text="删除全部", command=delete_all_files, state=tk.DISABLED)
    delete_all_button.pack(side=tk.LEFT, padx=5)

from . import register_feature
from config.settings import DEFAULT_FOLDER

def _init_feature(parent, root):
    left_var = tk.StringVar(value=DEFAULT_FOLDER)
    right_var = tk.StringVar(value=DEFAULT_FOLDER)
    build_compare_panel(parent, left_var, right_var, root)

register_feature("文件夹对比")(_init_feature)

