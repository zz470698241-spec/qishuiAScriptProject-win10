# -*- coding: utf-8 -*-
"""图像模板匹配 —— 对齐原 ascript.ios.screen.FindImages.find 接口。"""
import cv2

from config import TEMPLATE_CONFIDENCE
from .screen import screen_capture


class _FindImages:
    def find(self, template_path, confidence=None, rect=None, **kwargs):
        """
        在截图里找模板图。
        返回 {center_x, center_y, confidence, x, y, width, height} 或 None。
        坐标一律为全屏绝对坐标。
        """
        img = screen_capture.capture()
        if img is None:
            return None
        template = cv2.imread(template_path, cv2.IMREAD_COLOR)
        if template is None:
            print("[找图] 模板图读取失败: %s" % template_path)
            return None

        tpl_h, tpl_w = template.shape[:2]
        ox = oy = 0
        search = img
        if rect:
            h, w = img.shape[:2]
            x1, y1, x2, y2 = [int(v) for v in rect]
            x1 = max(0, min(x1, w - 1))
            y1 = max(0, min(y1, h - 1))
            x2 = max(x1 + 1, min(x2, w))
            y2 = max(y1 + 1, min(y2, h))
            search = img[y1:y2, x1:x2]
            ox, oy = x1, y1

        sh, sw = search.shape[:2]
        if tpl_h > sh or tpl_w > sw:
            print("[找图] 模板(%dx%d) 大于搜索区(%dx%d)，跳过" % (tpl_w, tpl_h, sw, sh))
            return None

        try:
            res = cv2.matchTemplate(search, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)
        except Exception as e:
            print("[找图] 匹配异常: %s" % e)
            return None

        threshold = TEMPLATE_CONFIDENCE if confidence is None else float(confidence)
        if max_val < threshold:
            return None

        left = max_loc[0] + ox
        top = max_loc[1] + oy
        return {
            "center_x": left + tpl_w / 2.0,
            "center_y": top + tpl_h / 2.0,
            "confidence": float(max_val),
            "x": left, "y": top,
            "width": tpl_w, "height": tpl_h,
        }


FindImages = _FindImages()
