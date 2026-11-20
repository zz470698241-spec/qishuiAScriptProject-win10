# -*- coding: utf-8 -*-
"""
汽水音乐自动化脚本 —— Win10 版全局配置
================================================
只需要改这个文件，不用动业务逻辑代码（__init__.py）。
"""

# ========== 控制后端（选一个）==========
# "adb"     : 通过 ADB 控制安卓手机 / 安卓模拟器（推荐）
#             坐标体系与原 iOS 脚本一致（竖屏手机），原脚本所有百分比区域可直接复用。
# "desktop" : 通过 pyautogui 控制 Win10 桌面窗口
#             需要先把汽水音乐窗口全屏/竖屏显示，否则识别区域会错位。
SCREEN_BACKEND = "adb"

# ========== ADB 配置（SCREEN_BACKEND = "adb" 时生效）==========
# adb.exe 完整路径。留空 = 自动在 PATH 和常见模拟器目录里找。
# 例：ADB_PATH = r"D:\adb\platform-tools\adb.exe"
ADB_PATH = ""

# 多台设备同时连接时填设备序列号（用 adb devices 查看）；单设备留空即可。
ADB_DEVICE = ""

# 汽水音乐【安卓版】包名。注意 iOS 原脚本用的是 com.soda.music，安卓包名不同。
# 不确定时执行：adb shell pm list packages | grep -i soda
APP_PACKAGE = "com.soda.music.android"

# ========== 桌面后端配置（SCREEN_BACKEND = "desktop" 时生效）==========
# 汽水音乐 PC 客户端 exe 路径；留空 = 脚本只提示手动打开窗口。
DESKTOP_EXE_PATH = ""

# ========== OCR 配置 ==========
# Win10 版统一使用 RapidOCR（比 PaddleOCR 轻，不需要 paddlepaddle 框架，纯 CPU 可跑）
OCR_ENGINE = "rapidocr"
# 识别置信度门槛（0~1），低于此值的结果直接丢弃
OCR_MIN_CONFIDENCE = 0.5

# ========== 图像模板匹配 ==========
# FindImages 模板匹配阈值，越高越严格（0~1）
TEMPLATE_CONFIDENCE = 0.8

# ========== 其他 ==========
# 启动 App 后是否顺便打印 ADB 连接信息
VERBOSE_ADB_INFO = False
