# -*- coding: utf-8 -*-
"""系统能力：资源路径 R、启动 App app_start、屏幕尺寸 screen_size、通知 notify。

对齐原 ascript.ios.system 的接口，业务脚本无需改动调用方式。
"""
import os
import subprocess
import winsound

from config import SCREEN_BACKEND, ADB_PATH, ADB_DEVICE, APP_PACKAGE, DESKTOP_EXE_PATH, VERBOSE_ADB_INFO
from .adb_utils import find_adb, adb_cmd, check_connection
from .screen import screen_capture

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class _R:
    """资源路径：R.img('xxx.png') -> res/img/xxx.png 的绝对路径。"""
    @staticmethod
    def img(name):
        return os.path.join(PROJECT_ROOT, "res", "img", name)

    @staticmethod
    def path(*parts):
        return os.path.join(PROJECT_ROOT, *parts)


R = _R()


def screen_size():
    """返回 (宽, 高) 或 None，与原接口一致。"""
    return screen_capture.size()


def app_start(bundle_id=None, name=None):
    """启动汽水音乐。ADB 后端用包名启动；桌面后端启动 exe 或提示手动打开。返回 bool。"""
    if SCREEN_BACKEND == "adb":
        adb = find_adb(ADB_PATH)
        if VERBOSE_ADB_INFO:
            ok, msg = check_connection(adb, ADB_DEVICE)
            print("[ADB] " + msg)
        package = APP_PACKAGE or bundle_id or ""
        if not package:
            print("[启动失败] config.py 里 APP_PACKAGE 为空")
            return False
        try:
            # monkey 方式不需要知道具体 Activity 名，最省事
            cmd = adb_cmd(adb, ADB_DEVICE) + [
                "shell", "monkey", "-p", package,
                "-c", "android.intent.category.LAUNCHER", "1",
            ]
            r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               universal_newlines=True, timeout=15)
            if r.returncode == 0 and "Error" not in r.stdout:
                print("[启动] 已发送启动指令: %s" % package)
                return True
            print("[启动失败] %s" % (r.stdout or r.stderr or "未知错误"))
            return False
        except Exception as e:
            print("[启动失败] %s" % e)
            return False

    # desktop 后端
    if DESKTOP_EXE_PATH and os.path.isfile(DESKTOP_EXE_PATH):
        try:
            os.startfile(DESKTOP_EXE_PATH)
            print("[启动] 已启动: %s" % DESKTOP_EXE_PATH)
            return True
        except Exception as e:
            print("[启动失败] %s" % e)
            return False
    print("[启动] 请在 Win10 桌面上手动打开汽水音乐窗口，脚本将据此截图识别。")
    return True


def notify(msg):
    """轻量通知：控制台打印 + 系统提示音（失败静默忽略，不影响主流程）。"""
    print("[通知] %s" % msg)
    try:
        winsound.MessageBeep(winsound.MB_ICONASTERISK)
    except Exception:
        pass
