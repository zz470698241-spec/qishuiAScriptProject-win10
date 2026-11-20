# -*- coding: utf-8 -*-
"""
OCR 文字识别 —— 对齐原 ascript.ios.screen.Ocr 接口。
Win10 版底层用 RapidOCR（PaddleOCR 模型的 ONNX 轻量版），纯 CPU 可跑，无需 paddlepaddle。

对外接口（业务脚本已用到的）：
  Ocr.set_engine(name)
  Ocr.paddleocr(rect=[x1,y1,x2,y2], pattern=r"跳过") -> [dict, ...]
  Ocr.find(keyword, rect=None, mode=None) -> dict | None

返回 dict 字段：text, confidence, x, y, center_x, center_y, left, top, right, bottom
坐标一律为【全屏绝对坐标】，与原 iOS 接口行为一致。
"""
import re

from config import OCR_MIN_CONFIDENCE
from .screen import screen_capture


class _Ocr:
    def __init__(self):
        self._engine = None
        self.engine_name = "rapidocr"

    def _get_engine(self):
        if self._engine is None:
            # 新版包名是 rapidocr（3.x，支持 Python 3.13）；老版本是 rapidocr_onnxruntime
            # 两个都兼容，谁装了用谁
            try:
                from rapidocr import RapidOCR
            except ImportError:
                try:
                    from rapidocr_onnxruntime import RapidOCR
                except ImportError:
                    raise RuntimeError(
                        "缺少 OCR 依赖。请执行：pip install rapidocr onnxruntime"
                    )
            self._engine = RapidOCR()
        return self._engine

    def set_engine(self, name="rapidocr"):
        """原脚本会调用 Ocr.set_engine('vision')。Win10 版只有一套引擎，记录名字即可。"""
        self.engine_name = name or "rapidocr"
        if self.engine_name not in ("rapidocr", "vision", "paddle", "mlkit"):
            self.engine_name = "rapidocr"
        self._get_engine()  # 提前加载模型，避免第一轮识别时卡顿
        print("[OCR] 引擎就绪: RapidOCR (原脚本请求: %s)" % self.engine_name)

    # ---------- 内部：识别 + 坐标换算 ----------
    def _recognize(self, rect=None):
        img = screen_capture.capture()
        if img is None:
            return []
        h, w = img.shape[:2]
        ox = oy = 0
        if rect:
            x1, y1, x2, y2 = [int(v) for v in rect]
            x1 = max(0, min(x1, w - 1))
            y1 = max(0, min(y1, h - 1))
            x2 = max(x1 + 1, min(x2, w))
            y2 = max(y1 + 1, min(y2, h))
            crop = img[y1:y2, x1:x2]
            ox, oy = x1, y1
        else:
            crop = img

        try:
            out = self._get_engine()(crop)
        except Exception as e:
            print("[OCR] 识别异常: %s" % e)
            return []

        # 新版 rapidocr(3.x) 返回 RapidOCROutput 对象：.txts / .boxes / .scores
        # 旧版 rapidocr_onnxruntime 返回 ([[box, text, score], ...], elapse)
        txts = boxes = scores = None
        if out is not None and hasattr(out, "txts") and hasattr(out, "boxes"):
            txts, boxes, scores = out.txts, out.boxes, out.scores
        elif isinstance(out, (tuple, list)) and len(out) > 0:
            result = out[0]
            if result:
                try:
                    txts = [e[1] for e in result]
                    boxes = [e[0] for e in result]
                    scores = [e[2] for e in result]
                except Exception:
                    txts = boxes = scores = None
        if not txts:
            return []

        items = []
        for text, box, score in zip(txts, boxes, scores):
            try:
                conf = float(score)
            except (TypeError, ValueError):
                continue
            if conf < OCR_MIN_CONFIDENCE:
                continue
            try:
                xs = [float(p[0]) for p in box]
                ys = [float(p[1]) for p in box]
            except Exception:
                continue
            left, top = min(xs) + ox, min(ys) + oy
            right, bottom = max(xs) + ox, max(ys) + oy
            items.append({
                "text": str(text),
                "confidence": conf,
                "left": left, "top": top, "right": right, "bottom": bottom,
                "x": left, "y": top,
                "center_x": (left + right) / 2.0,
                "center_y": (top + bottom) / 2.0,
            })
        return items

    # ---------- 对外接口 ----------
    def paddleocr(self, rect=None, pattern=None, **kwargs):
        """在指定区域识别，按正则 pattern 过滤，返回命中列表（全屏坐标）。"""
        items = self._recognize(rect)
        if pattern:
            try:
                items = [it for it in items if re.search(pattern, it["text"])]
            except re.error as e:
                print("[OCR] 正则无效 %r: %s" % (pattern, e))
                return []
        return items

    def find(self, keyword, rect=None, mode=None, **kwargs):
        """在指定区域找包含 keyword 的文字，返回第一个命中 dict 或 None。"""
        items = self._recognize(rect)
        for it in items:
            if keyword in it["text"]:
                return it
        return None


Ocr = _Ocr()
