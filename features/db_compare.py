from ui.components import create_result_area, show_toast
from modules.file_utils import get_all_files, get_file_size
from models.zidian import check_kvalue_exists, insert_zidian_record, get_db_session
import tkinter as tk
from tkinter import ttk, filedialog
import os

def build_db_compare_panel(parent, target_path_var, root):
    ttk.Label(parent, text="📂 数据库比对工具", font=("Microsoft YaHei UI", 14, "bold")).pack(anchor=tk.W, pady=(0, 20))

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

    create_path_selector("目标文件夹：", target_path_var)

    button_frame = ttk.Frame(parent)
    button_frame.pack(fill=tk.X, pady=10)

    canvas, result_inner = create_result_area(parent)

    def compare_with_db():
        global redundant_files
        redundant_files = []  # 用于存储重复文件的全局列表
        for widget in result_inner.winfo_children():
            widget.destroy()

        target = target_path_var.get()
        if not os.path.exists(target):
            show_toast(root, "路径无效，请检查输入")
            return

        target_files = get_all_files(target)
        has_result = False

        with get_db_session() as db:
            for file in target_files:
                file_size = str(get_file_size(file))  # 转换为字符串以匹配数据库字段类型
                if check_kvalue_exists(db, file_size):
                    has_result = True
                    redundant_files.append(file)  # 将重复文件添加到列表
                    add_result_row(result_inner, f"重复文件：{file}", "red")
                else:
                    # 插入新记录
                    insert_zidian_record(db, kname=os.path.basename(file), kvalue=file_size, ktype="1", ktypech="1024zip文件标记")
                    add_result_row(result_inner, f"新增记录：{file}", "green")

        if not has_result:
            ttk.Label(result_inner, text="✅ 未发现重复文件，所有记录已插入数据库。", foreground="#00ff88", font=("Microsoft YaHei UI", 12, "bold")).pack(pady=20)

    def delete_all_redundant_files():
        """
        删除所有标记为重复的文件。
        """
        global redundant_files
        deleted = 0
        failed = 0
        failed_files = []

        for file in list(redundant_files):
            try:
                os.remove(file)
                redundant_files.remove(file)
                deleted += 1
            except Exception as e:
                failed += 1
                failed_files.append(file)
                print(f"删除失败：{file}，错误：{e}")

        # 清空结果区域
        for widget in result_inner.winfo_children():
            widget.destroy()

        # 显示删除结果
        if failed > 0:
            show_toast(root, f"已删除 {deleted} 个文件，{failed} 个文件删除失败\n失败文件：{', '.join(failed_files)}")
        else:
            show_toast(root, f"已删除 {deleted} 个文件，全部删除成功！")

    def add_result_row(parent, text, color):
        ttk.Label(parent, text=text, wraplength=900, foreground=color).pack(anchor="w", padx=20)

    ttk.Button(button_frame, text="开始比对", command=compare_with_db).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="删除全部", command=delete_all_redundant_files).pack(side=tk.LEFT, padx=5)
