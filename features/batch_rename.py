from ui.components import create_result_area, show_toast
import tkinter as tk
from tkinter import ttk, filedialog
import os

def build_batch_rename_panel(parent, default_folder_var, root):
    ttk.Label(parent, text="🛠 文件名批量修改工具", font=("Microsoft YaHei UI", 14, "bold")).pack(anchor=tk.W, pady=(0, 20))

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

    # 输入框：待删除的字符
    char_frame = ttk.Frame(parent)
    char_frame.pack(fill=tk.X, pady=6)
    ttk.Label(char_frame, text="删除字符：", width=12).pack(side=tk.LEFT)
    char_var = tk.StringVar()
    ttk.Entry(char_frame, textvariable=char_var, width=70).pack(side=tk.LEFT, padx=5)

    # 输入框：字符替换功能
    replace_frame = ttk.Frame(parent)
    replace_frame.pack(fill=tk.X, pady=6)
    ttk.Label(replace_frame, text="替换字符：", width=12).pack(side=tk.LEFT)
    replace_from_var = tk.StringVar()
    ttk.Entry(replace_frame, textvariable=replace_from_var, width=30).pack(side=tk.LEFT, padx=5)
    ttk.Label(replace_frame, text="替换为：", width=8).pack(side=tk.LEFT)
    replace_to_var = tk.StringVar()
    ttk.Entry(replace_frame, textvariable=replace_to_var, width=30).pack(side=tk.LEFT, padx=5)

    # 结果展示区域
    canvas, result_inner = create_result_area(parent)

    def preview_rename():
        """
        预览批量删除和替换字符的效果。
        """
        folder = default_folder_var.get()
        if not os.path.exists(folder):
            show_toast(root, "路径无效，请检查输入")
            return

        char_to_remove = char_var.get().strip()
        replace_from = replace_from_var.get().strip()
        replace_to = replace_to_var.get().strip()

        # 清空旧内容
        for widget in result_inner.winfo_children():
            widget.destroy()

        files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
        if not files:
            ttk.Label(result_inner, text="✅ 文件夹中没有文件。", foreground="#00ff88", font=("Microsoft YaHei UI", 12, "bold")).pack(pady=20)
            return

        for file in files:
            new_name = file
            if char_to_remove and char_to_remove in file:
                new_name = new_name.replace(char_to_remove, "")
            if replace_from and replace_from in new_name:
                new_name = new_name.replace(replace_from, replace_to)
            if new_name != file:
                ttk.Label(result_inner, text=f"{file} → {new_name}", wraplength=900, foreground="#bbbbbb").pack(anchor="w", padx=20)
            else:
                ttk.Label(result_inner, text=f"无需修改：{file}", wraplength=900, foreground="yellow").pack(anchor="w", padx=20)

    def execute_rename():
        """
        执行批量删除和替换字符操作。
        """
        folder = default_folder_var.get()
        if not os.path.exists(folder):
            show_toast(root, "路径无效，请检查输入")
            return

        char_to_remove = char_var.get().strip()
        replace_from = replace_from_var.get().strip()
        replace_to = replace_to_var.get().strip()

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
            old_path = os.path.join(folder, file)
            new_name = file
            if char_to_remove and char_to_remove in file:
                new_name = new_name.replace(char_to_remove, "")
            if replace_from and replace_from in new_name:
                new_name = new_name.replace(replace_from, replace_to)
            new_path = os.path.join(folder, new_name)

            if new_name != file:
                try:
                    os.rename(old_path, new_path)
                    success_count += 1
                    ttk.Label(result_inner, text=f"成功重命名：{file} → {new_name}", wraplength=900, foreground="green").pack(anchor="w", padx=20)
                except Exception as e:
                    failed_count += 1
                    ttk.Label(result_inner, text=f"重命名失败：{file}，错误：{e}", wraplength=900, foreground="red").pack(anchor="w", padx=20)
            else:
                ttk.Label(result_inner, text=f"无需修改：{file}", wraplength=900, foreground="yellow").pack(anchor="w", padx=20)

        show_toast(root, f"重命名完成：成功 {success_count} 个，失败 {failed_count} 个")

    # 操作按钮区域
    button_frame = ttk.Frame(parent)
    button_frame.pack(pady=10)
    ttk.Button(button_frame, text="预览", command=preview_rename).pack(side=tk.LEFT, padx=10)
    ttk.Button(button_frame, text="执行", command=execute_rename).pack(side=tk.LEFT, padx=10)
