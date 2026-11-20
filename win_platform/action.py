# -*- coding: utf-8 -*-
"""点击动作：对齐原 ascript.ios.action 的 action.click(x, y) 接口。"""
import subprocess

from config import SCREEN_BACKEND, ADB_PATH, ADB_DEVICE
from .adb_utils import find_adb, adb_cmd
from .screen import screen_capture


class _Action:
    def __init__(self):
        self._adb = find_adb(ADB_PATH)
        self._pyautogui = None

    def click(self, x, y):
        """点击屏幕绝对坐标（设备坐标 / 桌面坐标，取决于后端）。"""
        x, y = int(x), int(y)
        if SCREEN_BACKEND == "adb":
            cmd = adb_cmd(self._adb, ADB_DEVICE) + ["shell", "input", "tap", str(x), str(y)]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
        else:
            if self._pyautogui is None:
                import pyautogui
                self._pyautogui = pyautogui
            self._pyautogui.click(x, y)

    # 备用：滑动（原脚本注释里提到右滑关闭弹窗，暂未使用）
    def swipe(self, x1, y1, x2, y2, duration_ms=300):
        if SCREEN_BACKEND == "adb":
            cmd = adb_cmd(self._adb, ADB_DEVICE) + [
                "shell", "input", "swipe",
                str(int(x1)), str(int(y1)), str(int(x2)), str(int(y2)), str(int(duration_ms)),
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
        else:
            if self._pyautogui is None:
                import pyautogui
                self._pyautogui = pyautogui
            self._pyautogui.moveTo(x1, y1)
            self._pyautogui.dragTo(x2, y2, duration=duration_ms / 1000.0)


action = _Action()
