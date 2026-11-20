# -*- coding: utf-8 -*-
"""
Windows 平台适配层
==================
对外提供与原 ascript.ios.* 完全一致的接口，业务脚本 __init__.py 只需换一行导入即可运行。

  原 iOS                          →  Win10 版
  ------------------------------------------------------------------
  ascript.ios.action              →  win_platform.action
  ascript.ios.system.R            →  win_platform.R
  ascript.ios.system.app_start    →  win_platform.app_start
  ascript.ios.system.screen_size  →  win_platform.screen_size
  ascript.ios.system.notify       →  win_platform.notify
  ascript.ios.screen.Ocr          →  win_platform.Ocr      (RapidOCR)
  ascript.ios.screen.FindImages   →  win_platform.FindImages(OpenCV)
  ascript.ios.node.Selector       →  win_platform.Selector (降级为 None)
"""
from .action import action
from .system import R, app_start, screen_size, notify
from .ocr import Ocr
from .image import FindImages
from .node import Selector

__all__ = [
    "action", "R", "app_start", "screen_size", "notify",
    "Ocr", "FindImages", "Selector",
]
