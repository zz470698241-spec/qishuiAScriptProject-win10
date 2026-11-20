# -*- coding: utf-8 -*-
"""
端到端自检脚本 —— 用合成屏幕图 + 真实 OCR 驱动核心业务全流程
==============================================================
用途：
  1. 验证代码逻辑完整跑通（不依赖真实手机/模拟器）
  2. 作为部署后的环境自检工具：python selftest.py

原理：
  - 用 PIL 画出模拟的 App 界面（含"跳过广告""免""领取成功""领取奖励""元开通"等文字）
  - monkeypatch screen_capture.capture 让截图返回这些合成画面
  - monkeypatch action.click 记录点击而不真实操作设备
  - monkeypatch time.sleep 加速（测试模式）
  - 依次驱动业务脚本的 5 个阶段函数 + 核心循环，断言返回值符合预期

运行：python selftest.py
"""
import os
import runpy
import sys
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
sys.path.insert(0, BASE_DIR)

from PIL import Image, ImageDraw, ImageFont

FONT_PATH = r"C:\Windows\Fonts\simhei.ttf"
SCREEN_W, SCREEN_H = 1080, 1920

PASS = "[PASS]"
FAIL = "[FAIL]"
_results = []


def check(name, cond, detail=""):
    tag = PASS if cond else FAIL
    _results.append((name, bool(cond)))
    print("  %s %s %s" % (tag, name, ("- " + detail) if detail else ""))
    return cond


def load_font(size):
    if os.path.exists(FONT_PATH):
        return ImageFont.truetype(FONT_PATH, size)
    return ImageFont.load_default()


def make_screen(texts):
    """生成一张模拟竖屏，texts = [(文字, x比例, y比例, 字号), ...]"""
    img = Image.new("RGB", (SCREEN_W, SCREEN_H), "white")
    d = ImageDraw.Draw(img)
    # 画个顶部状态栏底纹，让画面更像真实截图
    d.rectangle([0, 0, SCREEN_W, 120], fill=(235, 235, 235))
    for text, xp, yp, size in texts:
        d.text((int(SCREEN_W * xp), int(SCREEN_H * yp)), text,
               fill="black", font=load_font(size))
    return img


def to_bgr(pil_img):
    import cv2
    import numpy as np
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)


def main():
    print("=" * 64)
    print("汽水音乐脚本 Win10 版 —— 端到端自检 (selftest)")
    print("=" * 64)

    # ---------- 0. 依赖检查 ----------
    print("\n[0/6] 依赖检查")
    for mod in ["cv2", "numpy", "PIL", "rapidocr", "onnxruntime"]:
        try:
            __import__(mod)
            check("依赖 " + mod, True)
        except ImportError:
            check("依赖 " + mod, False, "未安装，请运行 install.bat")
    if not all(c for _, c in _results):
        print("\n依赖不全，自检中止。")
        return 1

    # ---------- 载入业务脚本与适配层 ----------
    core = runpy.run_path(os.path.join(BASE_DIR, "__init__.py"), run_name="selftest_core")
    import win_platform.screen as screen_mod
    # 业务脚本 core['action'] 是 win_platform 的 _Action 单例，直接 patch 它即可
    # （不需要单独 import action 模块）

    # ---------- 1. OCR 引擎初始化 ----------
    print("\n[1/6] OCR 引擎初始化（真实加载模型）")
    core["Ocr"].set_engine("paddle")
    check("OCR 引擎就绪", core["Ocr"]._engine is not None)

    # monkeypatch：截图、点击、sleep（仅测试进程内生效）
    state = {"frame": None, "clicks": []}

    def fake_capture():
        return to_bgr(state["frame"]) if state["frame"] is not None else None

    def fake_click(x, y):
        state["clicks"].append((round(float(x), 1), round(float(y), 1)))

    screen_mod.screen_capture.capture = fake_capture
    screen_mod.screen_capture.size = lambda: (SCREEN_W, SCREEN_H)
    core["action"].click = fake_click
    _real_time = time  # 保存真实 time 模块引用（下面会 patch core 的 time）
    core_ns_time = core["time"]

    class _FastTime:
        time = staticmethod(_real_time.time)
        strftime = staticmethod(_real_time.strftime)
        localtime = staticmethod(_real_time.localtime)
        @staticmethod
        def sleep(_s):
            pass  # 测试模式跳过等待

    core["time"] = _FastTime
    # 业务脚本各阶段函数内部还 import 了 screen_size，指向适配层单例，size 已被 patch
    core["init_regions"]()

    # ---------- 2. 阶段一B：跳过开屏广告 ----------
    print("\n[2/6] 阶段一B —— 跳过开屏广告（识别右上角「跳过」）")
    state["clicks"] = []
    state["frame"] = make_screen([("跳过广告", 0.82, 0.075, 40)])
    ok = core["skip_splash_ad"](timeout=3)
    check("识别并点击跳过", ok, "点击点=%s" % state["clicks"])
    check("点击落在右上角区域",
          any(x > SCREEN_W * 0.7 and y < SCREEN_H * 0.2 for x, y in state["clicks"]))

    # ---------- 3. 阶段二：关续费会员弹窗 ----------
    print("\n[3/6] 阶段二 —— 关闭续费会员弹窗（识别底部「元开通」）")
    state["clicks"] = []
    state["frame"] = make_screen([("连续包月12元开通", 0.20, 0.90, 44)])
    ok = core["close_membership_popup"]()
    check("识别并关闭弹窗", ok, "点击点=%s" % state["clicks"])

    # ---------- 4. 阶段三：进广告入口 ----------
    print("\n[4/6] 阶段三 —— 监测进广告入口（「免」字 / 「立即解锁」）")
    state["clicks"] = []
    state["frame"] = make_screen([("免", 0.75, 0.07, 52)])
    ok = core["wait_for_mian_button"](timeout=3, allow_mian=True)
    check("识别并点击「免」字入场", ok, "点击点=%s" % state["clicks"])

    state["clicks"] = []
    state["frame"] = make_screen([("立即解锁", 0.40, 0.60, 52)])
    ok = core["wait_for_mian_button"](timeout=3, allow_mian=False)
    check("识别并点击「立即解锁」入场", ok, "点击点=%s" % state["clicks"])

    # ---------- 5. 阶段四+五：等倒计时 + 领奖两步 ----------
    print("\n[5/6] 阶段四/五 —— 等倒计时 → 点「领取成功」 → 点「领取奖励」")
    # 5a 等广告倒计时：检测右上角"领取成功"
    state["clicks"] = []
    state["frame"] = make_screen([("领取成功", 0.62, 0.06, 42)])
    ok = core["wait_ad_countdown"](timeout=3)
    check("识别广告结束信号「领取成功」", ok)

    # 5b 领奖两步：先"领取成功"，再"领取奖励"（用帧序列模拟点击后的界面变化）
    state["clicks"] = []
    frames = [
        make_screen([("领取成功", 0.62, 0.06, 42)]),   # 第1步目标
        make_screen([("领取奖励", 0.40, 0.45, 50)]),   # 第2步目标
    ]
    seq = {"i": 0}
    def seq_capture():
        f = frames[min(seq["i"], len(frames) - 1)]
        return to_bgr(f)
    screen_mod.screen_capture.capture = seq_capture
    # 让每次点击后自动切到下一帧（模拟界面跳转）
    def advancing_click(x, y):
        state["clicks"].append((round(float(x), 1), round(float(y), 1)))
        seq["i"] += 1
    core["action"].click = advancing_click
    res = core["claim_reward"]()
    check("两步领奖流程返回成功", res == 1, "点击序列=%s" % state["clicks"])
    check("恰好点击 2 次", len(state["clicks"]) == 2)

    # 恢复简单 capture
    screen_mod.screen_capture.capture = fake_capture
    core["action"].click = fake_click

    # ---------- 6. 核心循环控制逻辑 ----------
    print("\n[6/6] 核心循环控制 —— 领奖成功累加 + 连续空跑自动退出")
    # 用受控桩函数替换"等待广告/领奖"，只验证 run_ad_loop 的循环决策逻辑，
    # 避免真实 30s 超时 x10 轮的长等待（UI 识别已在第 2~5 步用真实 OCR 验证过）
    # runpy 返回的 core 是模块字典副本；函数对象真正的全局命名空间在 __globals__
    # patch 函数本身必须改 __globals__ 才生效（截图/点击是单例对象属性，改对象即可）
    fn_globals = core["run_ad_loop"].__globals__
    seq = {"ad": 0, "claim": 0}
    def stub_wait_ad(timeout=30):
        seq["ad"] += 1
        return seq["ad"] <= 2   # 前 2 轮有广告
    def stub_claim():
        seq["claim"] += 1
        return 1                # 有广告的两轮都领奖成功
    fn_globals["wait_ad_countdown"] = stub_wait_ad
    fn_globals["claim_reward"] = stub_claim
    total = core["run_ad_loop"]()
    check("核心循环累加成功次数", total == 2, "返回成功次数=%s (期望2)" % total)
    check("空跑达到上限后自动退出(未死循环)", seq["ad"] == 12,
          "等待广告调用次数=%s (期望12=2成功+10空跑)" % seq["ad"])

    # ---------- 汇总 ----------
    print("\n" + "=" * 64)
    passed = sum(1 for _, c in _results if c)
    total_n = len(_results)
    print("自检结果：%d/%d 项通过" % (passed, total_n))
    if passed == total_n:
        print("结论：核心逻辑全部跑通 ✅（模拟屏幕 + 真实 OCR 验证）")
        print("说明：真机端到端需另外准备 安卓模拟器/手机 + ADB + 汽水音乐App，本机自检不覆盖!")
        return 0
    else:
        print("结论：存在失败项 ❌，请检查上方 [FAIL] 条目")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        import traceback
        print("\n[自检异常] %s" % e)
        traceback.print_exc()
        sys.exit(1)
