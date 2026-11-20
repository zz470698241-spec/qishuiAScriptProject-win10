# -*- coding: utf-8 -*-
"""
屏幕截图模块 —— 统一返回 OpenCV 的 BGR 图像 (numpy ndarray)。
  - adb 后端    : 截安卓设备 / 模拟器屏幕（设备落盘 + pull，稳定不受 Windows CRLF 干扰）
  - desktop 后端: 用 pyautogui 截 Win10 桌面
"""
import os
import subprocess
import tempfile

import cv2
import numpy as np
from PIL import Image

from config import SCREEN_BACKEND, ADB_PATH, ADB_DEVICE
from .adb_utils import find_adb, adb_cmd


class ScreenCapture:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ScreenCapture, cls).__new__(cls)
            cls._instance._ready = False
        return cls._instance

    def _init(self):
        if self._ready:
            return
        self._adb = find_adb(ADB_PATH)
        self._pyautogui = None
        self._cached_size = None
        self._remote_shot = "/sdcard/.qishui_win_screen.png"
        self._local_shot = os.path.join(tempfile.gettempdir(), "qishui_win_screen.png")
        self._ready = True

    # ---------- 对外接口 ----------
    def capture(self):
        """返回 BGR ndarray；失败返回 None。"""
        self._init()
        if SCREEN_BACKEND == "adb":
            return self._capture_adb()
        return self._capture_desktop()

    def size(self):
        """返回 (宽, 高)；缓存首次结果，避免每次都截图。"""
        self._init()
        if self._cached_size is None:
            img = self.capture()
            if img is not None:
                h, w = img.shape[:2]
                self._cached_size = (int(w), int(h))
        return self._cached_size

    # ---------- 后端实现 ----------
    def _capture_adb(self):
        base = adb_cmd(self._adb, ADB_DEVICE)
        try:
            # 先删旧缓存，避免截图失败时误读到上一轮的陈旧画面
            if os.path.isfile(self._local_shot):
                try:
                    os.remove(self._local_shot)
                except Exception:
                    pass
            subprocess.run(
                base + ["shell", "screencap", "-p", self._remote_shot],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10,
            )
            subprocess.run(
                base + ["pull", self._remote_shot, self._local_shot],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15,
            )
            if not os.path.isfile(self._local_shot):
                return None
            img = Image.open(self._local_shot).convert("RGB")
            return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        except Exception as e:
            print("[截图失败] ADB 截图异常: %s" % e)
            return None

    def _capture_desktop(self):
        try:
            if self._pyautogui is None:
                import pyautogui
                self._pyautogui = pyautogui
            img = self._pyautogui.screenshot()
            return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        except Exception as e:
            print("[截图失败] pyautogui 截图异常: %s" % e)
            return None


# 模块级单例，其他模块直接 import 使用
screen_capture = ScreenCapture()
