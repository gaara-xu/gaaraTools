import os
import subprocess
from ui.components import create_result_area, show_toast
import tkinter as tk
from tkinter import ttk, filedialog
from ui.progress_bar import ProgressBar  # 导入进度条组件
import sys

# 设置 ffmpeg 和 ffprobe 的路径
if getattr(sys, 'frozen', False):  # 如果是打包后的环境
    BASE_DIR = sys._MEIPASS
else:  # 开发环境
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))  # 项目根目录

FFMPEG_PATH = os.path.join(BASE_DIR, "bin", "ffmpeg.exe")
FFPROBE_PATH = os.path.join(BASE_DIR, "bin", "ffprobe.exe")

def build_trim_video_panel(parent, default_folder_var, root):
    ttk.Label(parent, text="✂️ 电视剧去片头片尾工具", font=("Microsoft YaHei UI", 14, "bold")).pack(anchor=tk.W, pady=(0, 20))

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

    # 输入框：片头时长
    head_frame = ttk.Frame(parent)
    head_frame.pack(fill=tk.X, pady=6)
    ttk.Label(head_frame, text="片头时长（秒）：", width=12).pack(side=tk.LEFT)
    head_duration_var = tk.StringVar()
    ttk.Entry(head_frame, textvariable=head_duration_var, width=70).pack(side=tk.LEFT, padx=5)

    # 输入框：片尾时长
    tail_frame = ttk.Frame(parent)
    tail_frame.pack(fill=tk.X, pady=6)
    ttk.Label(tail_frame, text="片尾时长（秒）：", width=12).pack(side=tk.LEFT)
    tail_duration_var = tk.StringVar()
    ttk.Entry(tail_frame, textvariable=tail_duration_var, width=70).pack(side=tk.LEFT, padx=5)

    # 结果展示区域（可复制）
    result_inner = tk.Text(parent, wrap="word", height=15, bg="#2e2e2e", fg="#ffffff", font=("Microsoft YaHei UI", 10))
    result_inner.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    result_inner.config(state="disabled")

    def append_to_result(text, color="white"):
        """
        在结果区域中追加文本。
        """
        result_inner.config(state="normal")
        result_inner.insert(tk.END, text + "\n")
        result_inner.tag_add(color, "end-1l", "end")
        result_inner.tag_config(color, foreground=color)
        result_inner.config(state="disabled")

    # 初始化进度条
    progress_bar = ProgressBar(parent, total_steps=1)  # 默认步数为 1，稍后更新

    def get_video_duration(file_path):
        """
        使用 ffprobe 获取视频总时长。
        """
        try:
            cmd = [
                FFPROBE_PATH, "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", file_path
            ]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            return float(result.stdout.strip())
        except Exception as e:
            raise RuntimeError(f"无法获取视频时长：{e}")

    def trim_video(file_path, head_duration, tail_duration, output_folder):
        """
        使用 ffmpeg 裁剪视频，去除片头和片尾。
        """
        try:
            # 获取视频总时长
            total_duration = get_video_duration(file_path)

            # 计算裁剪后的时长
            start_time = head_duration if head_duration else 0
            end_time = total_duration - tail_duration if tail_duration else total_duration
            duration = end_time - start_time

            if duration <= 0:
                return False, "裁剪后的时长小于等于 0，无法处理"

            # 构造输出文件路径
            trimmed_folder = os.path.join(output_folder, "trimmed_videos")
            os.makedirs(trimmed_folder, exist_ok=True)  # 创建新文件夹（如果不存在）

            file_name = os.path.basename(file_path)  # 保持文件名一致
            output_path = os.path.join(trimmed_folder, file_name)

            # 使用 ffmpeg 裁剪视频
            cmd_trim = [
                FFMPEG_PATH, "-i", file_path, "-ss", str(start_time), "-t", str(duration),
                "-c", "copy", output_path
            ]
            subprocess.run(cmd_trim, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return True, output_path
        except subprocess.CalledProcessError as e:
            return False, f"ffmpeg 错误：{e.stderr.decode('utf-8')}"
        except Exception as e:
            return False, str(e)

    def execute_trim():
        """
        执行去片头片尾操作。
        """
        folder = default_folder_var.get()
        if not os.path.exists(folder):
            show_toast(root, "路径无效，请检查输入")
            return

        try:
            head_duration = float(head_duration_var.get().strip()) if head_duration_var.get().strip() else None
            tail_duration = float(tail_duration_var.get().strip()) if tail_duration_var.get().strip() else None
        except ValueError:
            show_toast(root, "请输入有效的片头和片尾时长（秒）")
            return

        if head_duration is None and tail_duration is None:
            show_toast(root, "请输入片头或片尾时长")
            return

        # 清空旧内容
        result_inner.config(state="normal")
        result_inner.delete("1.0", tk.END)
        result_inner.config(state="disabled")

        files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)) and f.lower().endswith(('.mp4', '.mkv', '.avi'))]
        if not files:
            append_to_result("✅ 文件夹中没有视频文件。", "green")
            return

        # 更新进度条总步数
        progress_bar.total_steps = len(files)
        progress_bar.reset()

        success_count = 0
        failed_count = 0

        for idx, file in enumerate(files, start=1):
            file_path = os.path.join(folder, file)
            success, result = trim_video(file_path, head_duration, tail_duration, folder)
            if success:
                success_count += 1
                append_to_result(f"成功裁剪：{file} → {result}", "green")
            else:
                failed_count += 1
                append_to_result(f"裁剪失败：{file}，错误：{result}", "red")

            # 更新进度条
            progress_bar.update()

        append_to_result(f"\n裁剪完成：成功 {success_count} 个，失败 {failed_count} 个", "blue")
        show_toast(root, f"裁剪完成：成功 {success_count} 个，失败 {failed_count} 个")

    # 操作按钮区域
    button_frame = ttk.Frame(parent)
    button_frame.pack(pady=10)
    ttk.Button(button_frame, text="执行", command=execute_trim).pack(side=tk.LEFT, padx=10)
