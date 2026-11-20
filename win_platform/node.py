# -*- coding: utf-8 -*-
"""控件树查询兜底 —— 对齐原 ascript.ios.node.Selector 接口。

iOS 有 WDA 控件树，Win10 通过截图/OCR 控制时没有等价的 App 控件树。
原脚本只在直播间关闭按钮的最后一层兜底用到它，前面已有「模板匹配 + OCR」两层，
所以这里做优雅降级：返回 None，让脚本继续走后续逻辑，不中断运行。
"""


class _Node:
    """占位节点对象，保证 if node: 判断可用。"""
    def __init__(self, label=""):
        self.label_name = label

    def click(self):
        return False


class Selector:
    def __init__(self):
        self._label = None

    def label(self, text):
        self._label = text
        return self

    def find(self):
        print("[控件查询] Win10 版无 App 控件树，已跳过（前面已尝试模板匹配/OCR 关闭按钮）")
        return None
