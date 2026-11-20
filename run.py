# -*- coding: utf-8 -*-
"""
Win10 启动入口
用法：python run.py
可选：python run.py --skip-check   （跳过设备连接预检，仅调试时用）
"""
import os
import runpy
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
sys.path.insert(0, BASE_DIR)


class Tee:
    """同时输出到控制台和日志文件。"""
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for s in self.streams:
            try:
                s.write(data)
            except Exception:
                pass

    def flush(self):
        for s in self.streams:
            try:
                s.flush()
            except Exception:
                pass


def preflight():
    """启动前检查依赖和设备连接，避免跑到一半才报错。"""
    print("=" * 60)
    print("汽水音乐自动化脚本 Win10 版 —— 启动预检")
    print("=" * 60)

    # 1. Python 依赖
    required = [
        ("cv2", "opencv-python"),
        ("numpy", "numpy"),
        ("PIL", "pillow"),
        ("rapidocr", "rapidocr"),
        ("onnxruntime", "onnxruntime"),
    ]
    missing = []
    for module_name, pip_name in required:
        try:
            __import__(module_name)
        except ImportError:
            missing.append(pip_name)
    if missing:
        print("[预检失败] 缺少依赖: " + ", ".join(missing))
        print("           请先双击运行 install.bat，或执行: pip install -r requirements.txt")
        return False
    print("[OK] Python 依赖齐全")

    # 2. 后端环境
    from config import SCREEN_BACKEND, ADB_PATH, ADB_DEVICE
    if SCREEN_BACKEND == "adb":
        from win_platform.adb_utils import find_adb, check_connection
        adb = find_adb(ADB_PATH)
        print("[信息] 使用 ADB 后端，adb 路径: %s" % adb)
        ok, msg = check_connection(adb, ADB_DEVICE)
        if not ok:
            print("[预检失败] " + msg)
            print("           若模拟器尚未启动，请先打开模拟器后重试。")
            return False
        print("[OK] " + msg)
    elif SCREEN_BACKEND == "desktop":
        try:
            import pyautogui  # noqa: F401
            print("[OK] 桌面后端 pyautogui 可用")
        except ImportError:
            print("[预检失败] 桌面后端需要 pyautogui: pip install pyautogui")
            return False
    else:
        print("[预检失败] config.py 里 SCREEN_BACKEND 只能是 'adb' 或 'desktop'")
        return False

    print("[预检通过] 开始运行脚本...\n")
    return True


def main():
    log_path = os.path.join(BASE_DIR, "run.log")
    try:
        log_file = open(log_path, "a", encoding="utf-8")
        sys.stdout = Tee(sys.__stdout__, log_file)
        sys.stderr = Tee(sys.__stderr__, log_file)
    except Exception:
        log_file = None

    try:
        skip = "--skip-check" in sys.argv
        if not skip and not preflight():
            return 1

        # 载入原业务脚本（run_name 非 __main__，不会自动执行 main）
        module = runpy.run_path(
            os.path.join(BASE_DIR, "__init__.py"),
            run_name="qishui_core",
        )
        module["main"]()
        return 0
    except KeyboardInterrupt:
        print("\n[退出] 用户按 Ctrl+C 中断")
        return 130
    finally:
        if log_file is not None:
            try:
                log_file.close()
            except Exception:
                pass


if __name__ == "__main__":
    sys.exit(main())
