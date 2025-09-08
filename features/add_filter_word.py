import tkinter as tk
from tkinter import ttk
from ui.components import show_toast
from config.settings import DEFAULT_FOLDER
import pymysql

def build_add_filter_word_panel(parent, root):
    ttk.Label(parent, text="🚫 添加屏蔽词", font=("Microsoft YaHei UI", 14, "bold")).pack(anchor=tk.W, pady=(0, 20))

    # 屏蔽词输入框
    word_frame = ttk.Frame(parent)
    word_frame.pack(fill=tk.X, pady=6)
    ttk.Label(word_frame, text="屏蔽词：", width=12).pack(side=tk.LEFT)
    word_var = tk.StringVar()
    ttk.Entry(word_frame, textvariable=word_var, width=70).pack(side=tk.LEFT, padx=5)

    # 类型下拉框（显示中文）
    type_frame = ttk.Frame(parent)
    type_frame.pack(fill=tk.X, pady=6)
    ttk.Label(type_frame, text="类型：", width=12, font=("Microsoft YaHei UI", 12)).pack(side=tk.LEFT)
    type_var = tk.StringVar()
    type_map = {
        "违规文件名称关键词": "4",
        "违规文件夹名称关键词": "5",
        "违规文件后缀关键词": "6"
    }
    type_combo = ttk.Combobox(type_frame, textvariable=type_var, width=22, state="readonly", font=("Microsoft YaHei UI", 13))
    type_combo['values'] = list(type_map.keys())
    type_combo.current(0)
    type_combo.pack(side=tk.LEFT, padx=5)
    type_combo.configure(background="#fff", foreground="#000")

    def insert_word():
        word = word_var.get().strip()
        type_ch = type_var.get()
        ktype = type_map.get(type_ch, "")
        if not word:
            show_toast(root, "请输入屏蔽词")
            return
        try:
            conn = pymysql.connect(host="192.168.3.110", user="root", password="root", database="manhua", charset="utf8")
            with conn.cursor() as cursor:
                sql = "INSERT INTO manhuaconfig(kname, kvalue, ktype, ktypech) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, ("711过滤文件屏蔽词", word, ktype, type_ch))
                conn.commit()
            conn.close()
            show_toast(root, f"添加成功：{word} [{type_ch}]")
            word_var.set("")
        except Exception as e:
            show_toast(root, f"添加失败：{e}")

    button_frame = ttk.Frame(parent)
    button_frame.pack(pady=10)
    ttk.Button(button_frame, text="添加屏蔽词", command=insert_word).pack(side=tk.LEFT, padx=10)
