# features/download711url.py
# -*- coding: utf-8 -*-

"""
下载 711 URL 功能模块
====================

提供两部分：
1. fetch_711pan_download_info  ——  调用 711pan 接口，拿到直链 / verify / message
2. build_download711url_panel ——  Tkinter 面板，供主界面调用

依赖：
    pip install requests
    ui.components.create_result_area
    ui.components.show_toast
"""

from __future__ import annotations

import sys
import os
import time
import requests
import tkinter as tk
from tkinter import ttk
from typing import Dict, Optional, Any
import threading  # 导入线程模块
from datetime import datetime, timedelta

# 项目内组件
from ui.components import create_result_area, show_toast   # noqa: E402
from config.settings import DEFAULT_REQUEST_INTERVAL  # 导入登录信息
from ui.progress_bar import ProgressBar  # 导入进度条组件
from models.manhuaconfig import get_config_value  # 导入查询 manhuaconfig 表的方法
from models.manhuaconfig import get_token_with_updatetime, update_token  # 导入查询和更新 token 的方法


# ----------------------------------------------------------------------
# 业务：调用 711pan 接口
# ----------------------------------------------------------------------
def fetch_711pan_download_info(
    file_id: int,
    token: str,
    index: int = 4,
    *,
    timeout: int = 10,
    proxies: Optional[Dict[str, str]] = None,
    extra_headers: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    获取 711pan 文件直链、verify 字段以及接口返回 message。

    返回：
        {
            "message": "...",
            "download_url": "https://prod-data02...filename=xxx",
            "verify": "1745xxxx-xxxxx"
        }
    """
    url = f"https://api.711pan.cloud/WSApi/common/downloadLink/{file_id}/{index}"
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Authorization": f"Bearer {token}",
        "Origin": "https://www.711pan.cloud",
        "Referer": "https://www.711pan.cloud/",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
        ),
        "Content-Length": "0",
    }
    if extra_headers:
        headers.update(extra_headers)

    resp = requests.post(url, headers=headers, timeout=timeout, proxies=proxies)
    resp.raise_for_status()

    payload = resp.json()
    result_block = payload.get("result", {})
    return {
        "message": payload.get("message"),
        "download_url": result_block.get("result"),
    }

def login_711pan(
    email: str,
    password: str,
    cf_token: str = "",
    *,
    timeout: int = 10,
    proxies: Optional[Dict[str, str]] = None,
    extra_headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    登录 711pan，获取 accessToken。
    """
    url = "https://api.711pan.cloud/WSApi/auth/login"
    payload = {
        "email": email,
        "pwd": password,
        "cfToken": cf_token,
    }

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://www.711pan.cloud",
        "Referer": "https://www.711pan.cloud/",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
        ),
    }
    if extra_headers:
        headers.update(extra_headers)

    resp = requests.post(
        url,
        json=payload,
        headers=headers,
        timeout=timeout,
        proxies=proxies,
    )
    resp.raise_for_status()

    data = resp.json()
    token = (
        data.get("result", {})
            .get("authentication", {})
            .get("accessToken")
    )
    if not token:
        raise ValueError("接口响应中未找到 accessToken")

    return {
        "message": data.get("message"),
        "accessToken": token,
        "memberInfo": data.get("result", {}).get("memberInfo"),
    }


# ----------------------------------------------------------------------
# GUI：功能面板
# ----------------------------------------------------------------------
def build_download711url_panel(parent: tk.Widget, root: tk.Tk) -> None:
    """
    在给定 parent Frame 中构建“下载 711 URL”面板。
    """
    ttk.Label(
        parent,
        text="📥 下载 711 URL 工具",
        font=("Microsoft YaHei UI", 14, "bold"),
    ).pack(anchor=tk.W, pady=(0, 20))

    # ===== 表单行 =====
    form = ttk.Frame(parent)
    form.pack(fill=tk.X, pady=10)

    # file_id 输入框
    ttk.Label(form, text="file_id 列表：").grid(row=0, column=0, sticky="w")
    file_id_entry = tk.Text(form, height=5, width=60, wrap="word")
    file_id_entry.grid(row=0, column=1, columnspan=3, padx=5, sticky="we")

    # token 输入框
    ttk.Label(form, text="token：").grid(row=1, column=0, sticky="w")
    token_var = tk.StringVar()
    token_entry = ttk.Entry(form, textvariable=token_var, width=48)
    token_entry.grid(row=1, column=1, columnspan=3, padx=5, sticky="we")

    # 请求间隔输入框
    ttk.Label(form, text="请求间隔（秒）：").grid(row=2, column=0, sticky="w")
    interval_var = tk.StringVar(value=str(DEFAULT_REQUEST_INTERVAL))
    ttk.Entry(form, textvariable=interval_var, width=10).grid(row=2, column=1, padx=5, sticky="w")

    # ===== 进度条 =====
    progress_bar = ProgressBar(parent, total_steps=1)  # 初始化进度条，稍后更新总步数

    # 成功结果框
    ttk.Label(parent, text="成功结果：", font=("Microsoft YaHei UI", 12)).pack(anchor=tk.W, pady=(10, 5))
    success_text = tk.Text(parent, wrap="word", height=10, bg="#2e2e2e", fg="#00ff88", font=("Microsoft YaHei UI", 10))
    success_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    success_text.config(state="disabled")

    # 失败结果框
    ttk.Label(parent, text="失败结果：", font=("Microsoft YaHei UI", 12)).pack(anchor=tk.W, pady=(10, 5))
    failed_text = tk.Text(parent, wrap="word", height=5, bg="#2e2e2e", fg="#ff5555", font=("Microsoft YaHei UI", 10))
    failed_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    failed_text.config(state="disabled")

    def parse_url_thread():
        """
        在新线程中执行解析任务。
        """
        file_ids_text = file_id_entry.get("1.0", tk.END).strip()
        token = token_var.get().strip()
        interval = interval_var.get().strip()

        if not file_ids_text:
            show_toast(root, "请输入 file_id 列表")
            return

        try:
            interval = float(interval)
        except ValueError:
            show_toast(root, "请求间隔必须是数字")
            return

        # 查询数据库中的 token
        token_data = get_token_with_updatetime("token")
        if token_data:
            db_token = token_data["kvalue"]
            db_updatetime = token_data["updatetime"]

            # 检查 token 是否在 3 天内有效
            if db_updatetime and (datetime.now() - db_updatetime) < timedelta(days=3):
                token = db_token
                show_toast(root, "使用数据库中的 token")
            else:
                token = None  # 需要重新登录获取 token

        # 如果未输入 token 或数据库中的 token 无效，则进行登录
        if not token:
            try:
                email = get_config_value("id")  # 从 manhuaconfig 表获取邮箱
                password = get_config_value("passwd")  # 从 manhuaconfig 表获取密码
                login_result = login_711pan(email=email, password=password)
                token = login_result["accessToken"]
                token_var.set(token)  # 更新 token 输入框
                update_token("token", token)  # 更新数据库中的 token 和更新时间
                show_toast(root, "登录成功，已更新 token")
            except Exception as e:
                show_toast(root, f"登录失败：{e}")
                return

        # 如果使用数据库中的 token 登录失败，则重新登录
        try:
            # 测试 token 是否有效
            fetch_711pan_download_info(file_id=1, token=token)
        except Exception:
            try:
                email = get_config_value("id")
                password = get_config_value("passwd")
                login_result = login_711pan(email=email, password=password)
                token = login_result["accessToken"]
                token_var.set(token)
                update_token("token", token)  # 更新数据库中的 token 和更新时间
                show_toast(root, "重新登录成功，已更新 token")
            except Exception as e:
                show_toast(root, f"重新登录失败：{e}")
                return

        file_ids = []
        for line in file_ids_text.splitlines():
            if "fileId=" in line:
                file_id = line.split("fileId=")[-1].strip()
                file_ids.append(file_id)

        success_results = []
        failed_ids = []

        # 更新进度条总步数
        progress_bar.total_steps = len(file_ids)
        progress_bar.reset()

        for idx, file_id in enumerate(file_ids, start=1):
            try:
                result = fetch_711pan_download_info(file_id=int(file_id), token=token)
                success_results.append(result["download_url"])  # 仅显示 URL
            except Exception:
                failed_ids.append(file_id)
            progress_bar.update()  # 更新进度条
            time.sleep(interval)

        # 显示成功结果
        success_text.config(state="normal")
        success_text.delete("1.0", tk.END)
        success_text.insert(tk.END, "\n".join(success_results))  # 仅显示 URL 列表
        success_text.config(state="disabled")

        # 显示失败结果
        failed_text.config(state="normal")
        failed_text.delete("1.0", tk.END)
        failed_text.insert(tk.END, f"失败总数: {len(failed_ids)}\n失败的 file_id: {', '.join(failed_ids)}")
        failed_text.config(state="disabled")

    def parse_url():
        """
        启动新线程执行解析任务。
        """
        threading.Thread(target=parse_url_thread, daemon=True).start()

    # 解析按钮
    ttk.Button(form, text="解析", command=parse_url).grid(
        row=2, column=2, columnspan=2, padx=5, sticky="e"
    )

    # token 输入列自动伸缩
    form.columnconfigure(1, weight=1)

from . import register_feature

def _init_feature(parent, root):
    build_download711url_panel(parent, root)

register_feature("下载 711 URL")(_init_feature)

