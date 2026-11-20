# -*- coding: utf-8 -*-
"""ADB 可执行文件查找与命令拼装。"""
import os
import shutil

# 常见模拟器 / SDK 的 adb.exe 位置（只查固定路径，不递归全盘）
_COMMON_ADB_PATHS = [
    os.path.join(os.environ.get("LOCALAPPDATA", ""), "Android", "Sdk", "platform-tools", "adb.exe"),
    os.path.join(os.environ.get("ProgramFiles", ""), "Android", "android-sdk", "platform-tools", "adb.exe"),
    r"C:\Android\platform-tools\adb.exe",
    r"D:\Android\platform-tools\adb.exe",
    r"C:\adb\adb.exe",
    r"D:\adb\adb.exe",
    # 雷电模拟器
    r"C:\leidian\LDPlayer9\adb.exe",
    r"D:\leidian\LDPlayer9\adb.exe",
    r"C:\Program Files\ldplayer9box\adb.exe",
    # 夜神模拟器
    r"C:\Program Files\Nox\bin\adb.exe",
    r"D:\Nox\bin\adb.exe",
    # MuMu 模拟器
    r"C:\Program Files\Netease\MuMu\shell\adb.exe",
    r"D:\Program Files\Netease\MuMu\shell\adb.exe",
    # 蓝叠模拟器
    r"C:\Program Files\BlueStacks_nxt\adb.exe",
]


def find_adb(configured_path=""):
    """按 配置路径 → PATH 环境变量 → 常见安装目录 的顺序找 adb.exe。找不到返回 'adb'。"""
    if configured_path and os.path.isfile(configured_path):
        return configured_path
    found = shutil.which("adb")
    if found:
        return found
    for path in _COMMON_ADB_PATHS:
        if path and os.path.isfile(path):
            return path
    return "adb"


def adb_cmd(adb_path, device=""):
    """拼出 adb 基础命令，例：['D:\\adb\\adb.exe', '-s', 'emulator-5554']"""
    cmd = [adb_path]
    if device:
        cmd += ["-s", device]
    return cmd


def check_connection(adb_path, device=""):
    """返回 (是否连通, 说明文字)"""
    import subprocess
    try:
        r = subprocess.run(
            adb_cmd(adb_path, device) + ["devices"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True, timeout=10,
        )
        lines = [ln.strip() for ln in r.stdout.splitlines() if ln.strip()]
        devices = [ln for ln in lines if "\tdevice" in ln]
        if devices:
            return True, "已连接: " + ", ".join(d.split("\t")[0] for d in devices)
        return False, "未检测到已授权设备。请先启动模拟器/开启手机 USB 调试，并执行 adb devices 确认。"
    except FileNotFoundError:
        return False, "找不到 adb.exe。请在 config.py 里填写 ADB_PATH，或把 adb.exe 加入 PATH。"
    except Exception as e:
        return False, "ADB 连接检查失败: %s" % e
