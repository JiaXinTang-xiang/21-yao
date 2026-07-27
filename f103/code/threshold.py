import time
from machine import TOUCH
from media.display import *

NUMMAX = 4
WIDTH = 640
HEIGHT = 480

# 每个参数的标签
PARAM_NAMES = [
    "红L_min", "红L_max", "红A_min", "红A_max", "红B_min", "红B_max",
    "黄L_min", "黄L_max", "黄A_min", "黄A_max", "黄B_min", "黄B_max",
    "最小面积", "最大面积", "最小宽度", "最小高度", "最大宽度", "最大高度",
]

# 调节框位置，2列×3行放在屏幕中下方
SITE = [
    (50, 180, 250, 50),   # 0:  红L_min
    (340, 180, 250, 50),  # 1:  红L_max
    (50, 240, 250, 50),   # 2:  红A_min
    (340, 240, 250, 50),  # 3:  红A_max
    (50, 300, 250, 50),   # 4:  红B_min
    (340, 300, 250, 50),  # 5:  红B_max
    (50, 180, 250, 50),   # 6:  黄L_min
    (340, 180, 250, 50),  # 7:  黄L_max
    (50, 240, 250, 50),   # 8:  黄A_min
    (340, 240, 250, 50),  # 9:  黄A_max
    (50, 300, 250, 50),   # 10: 黄B_min
    (340, 300, 250, 50),  # 11: 黄B_max
    (50, 180, 250, 50),   # 12: 最小面积
    (340, 180, 250, 50),  # 13: 最大面积
    (50, 240, 250, 50),   # 14: 最小宽度
    (340, 240, 250, 50),  # 15: 最小高度
    (50, 300, 250, 50),   # 16: 最大宽度
    (340, 300, 250, 50),  # 17: 最大高度
]


class Threshold:
    def __init__(self):
        try:
            with open('/sdcard/code/threshold.txt', 'r') as f:
                data = [int(x) for x in f.read().split(',')]
                self.threshold = [
                    data[0] if len(data) > 0 else 41,
                    data[1] if len(data) > 1 else 69,
                    data[2] if len(data) > 2 else 9,
                    data[3] if len(data) > 3 else 67,
                    data[4] if len(data) > 4 else -16,
                    data[5] if len(data) > 5 else 57,
                    data[6] if len(data) > 6 else 63,
                    data[7] if len(data) > 7 else 96,
                    data[8] if len(data) > 8 else -25,
                    data[9] if len(data) > 9 else 35,
                    data[10] if len(data) > 10 else 22,
                    data[11] if len(data) > 11 else 99,
                    data[12] if len(data) > 12 else 1000,
                    data[13] if len(data) > 13 else 30000,
                    data[14] if len(data) > 14 else 10,
                    data[15] if len(data) > 15 else 10,
                    data[16] if len(data) > 16 else 300,
                    data[17] if len(data) > 17 else 300,
                ]
        except:
            self.threshold = [
                41, 69, 9, 67, -16, 57,
                63, 96, -25, 35, 22, 99,
                1000, 30000, 10, 10, 300, 300,
            ]

        self.tp = TOUCH(0)
        self.sensor_flag = 1   # 1:红, 2:黄, 3:尺寸
        self.color_flag = 0    # 当前参数索引

        self._key_last = 0
        self._num = 0

    # ---------- 按钮坐标 ----------
    def _btn_coords(self):
        bw, bh = 150, 60
        sp = (WIDTH - 3 * bw) // 4
        top_y, bot_y = 20, 400
        x1 = sp
        x2 = sp + bw + sp
        x3 = sp * 2 + bw * 2 + sp * 2
        return {
            "返回": (x1, top_y, x1 + bw, top_y + bh),
            "模式": (x2, top_y, x2 + bw, top_y + bh),
            "保存": (x3, top_y, x3 + bw, top_y + bh),
            "-":   (sp, bot_y, sp + bw, bot_y + bh),
            "切换": (sp * 2 + bw, bot_y, sp * 2 + bw * 2, bot_y + bh),
            "+":   (sp * 3 + bw * 2, bot_y, sp * 3 + bw * 3, bot_y + bh),
        }

    def witch_key(self, x, y):
        for name, (x1, y1, x2, y2) in self._btn_coords().items():
            if x1 <= x <= x2 and y1 <= y <= y2:
                return name
        return None

    def read_touch(self):
        points = self.tp.read()
        if not points:
            return 0
        pt = points[0]
        btn = self.witch_key(pt.x, pt.y)
        mapping = {"返回": 1, "模式": 2, "保存": 4, "-": 5, "切换": 3, "+": 6}
        return mapping.get(btn, 0)

    # ---------- 绘制 ----------
    def _mode_label(self):
        return {1: "红色阈值", 2: "黄色阈值", 3: "尺寸过滤"}[self.sensor_flag]

    def Draw_menu(self, img):
        GREEN = (0, 255, 0)
        bw, bh = 150, 60
        sp = (WIDTH - 3 * bw) // 4
        top_y, bot_y = 20, 400

        # 顶部三个按钮
        for lx, label in [
            (sp, "返回"),
            (sp + bw + sp, self._mode_label()),
            (sp * 2 + bw * 2 + sp * 2, "保存"),
        ]:
            img.draw_rectangle(lx, top_y, bw, bh, color=(0, 100, 200))
            img.draw_string_advanced(lx + 15, top_y + 15, 28, label, color=GREEN)

        # 底部三个按钮
        for lx, label in [
            (sp, "-"),
            (sp * 2 + bw, "切换"),
            (sp * 3 + bw * 2, "+"),
        ]:
            img.draw_rectangle(lx, bot_y, bw, bh, color=(0, 100, 200))
            img.draw_string_advanced(lx + 55, bot_y + 15, 35, label, color=GREEN)

        # 参数信息
        name = PARAM_NAMES[self.color_flag]
        val = self.threshold[self.color_flag]
        img.draw_string_advanced(50, 110, 28, f"调节: {name}", color=(255, 255, 0))
        img.draw_string_advanced(50, 140, 24, f"当前值: {val}", color=(255, 255, 255))

        t = self.threshold
        if self.sensor_flag == 1:
            img.draw_string_advanced(50, 165, 20,
                f"红 L:{t[0]}-{t[1]} A:{t[2]}-{t[3]} B:{t[4]}-{t[5]}", color=(255, 150, 150))
        elif self.sensor_flag == 2:
            img.draw_string_advanced(50, 165, 20,
                f"黄 L:{t[6]}-{t[7]} A:{t[8]}-{t[9]} B:{t[10]}-{t[11]}", color=(255, 255, 150))
        else:
            img.draw_string_advanced(50, 165, 20,
                f"面积 {t[12]}-{t[13]} 宽 {t[14]}-{t[16]} 高 {t[15]}-{t[17]}", color=(150, 255, 150))

        return img

    def Draw_rectangle(self, img):
        if self.color_flag < len(SITE):
            img.draw_rectangle(SITE[self.color_flag], color=(255, 0, 0), thickness=3)
        return img

    # ---------- 步长 / 范围 ----------
    def _get_step(self):
        if self.sensor_flag == 3 and self.color_flag not in (14, 15):
            return 10
        return 1

    def _get_bounds(self):
        idx = self.color_flag
        if self.sensor_flag in (1, 2):
            pos = idx % 6
            if pos in (0, 1):      return 0, 100      # L
            elif pos in (2, 3):    return -128, 127   # A
            else:                  return -128, 127   # B
        else:
            if idx == 12:          return 10, 100000
            elif idx == 13:        return 100, 500000
            elif idx in (14, 15):  return 1, 200
            else:                  return 10, 500

    # ---------- 主调节（每帧调用） ----------
    def change_threshold(self, sensor, clock):
        """每帧调用。返回 None 表示仍在调节；返回 list 表示调节完成"""
        img = sensor.snapshot()

        # 视觉反馈：根据当前模式显示处理后的图像
        if self.sensor_flag == 1:
            # 红色阈值模式：显示二值化图，白=匹配，黑=不匹配
            img = img.binary([tuple(self.threshold[0:6])])
            img = img.to_rgb565()
        elif self.sensor_flag == 2:
            # 黄色阈值模式：显示二值化图
            img = img.binary([tuple(self.threshold[6:12])])
            img = img.to_rgb565()
        else:
            # 尺寸过滤模式：显示两种颜色的 blob 检测结果（带尺寸过滤）
            red_blobs = img.find_blobs(
                [tuple(self.threshold[0:6])], area_threshold=50, pixels_threshold=30, merge=True)
            yellow_blobs = img.find_blobs(
                [tuple(self.threshold[6:12])], area_threshold=50, pixels_threshold=30, merge=True)
            t = self.threshold
            for b in (red_blobs or []):
                w, h, a = b.w(), b.h(), b.area()
                if t[12] <= a <= t[13] and t[14] <= w <= t[16] and t[15] <= h <= t[17]:
                    color = (255, 0, 0)
                else:
                    color = (100, 100, 100)
                img.draw_rectangle(b.x(), b.y(), w, h, color=color, thickness=2)
            for b in (yellow_blobs or []):
                w, h, a = b.w(), b.h(), b.area()
                if t[12] <= a <= t[13] and t[14] <= w <= t[16] and t[15] <= h <= t[17]:
                    color = (255, 255, 0)
                else:
                    color = (100, 100, 100)
                img.draw_rectangle(b.x(), b.y(), w, h, color=color, thickness=2)

        # 触摸处理
        key_now = self.read_touch()

        if key_now == self._key_last and key_now != 0:
            self._num += 1
        else:
            self._num = 0
        self._key_last = key_now

        result = None

        # —— 返回 ——
        if key_now == 1 and self._num > NUMMAX:
            t = self.threshold
            result = [
                t[0], t[1], t[2], t[3], t[4], t[5],
                t[6], t[7], t[8], t[9], t[10], t[11],
                t[12], t[13], t[14], t[15], t[16], t[17],
            ]
            self._num = 0

        # —— 模式切换 ——
        if key_now == 2 and self._num > NUMMAX:
            self.sensor_flag = self.sensor_flag % 3 + 1
            self.color_flag = {1: 0, 2: 6, 3: 12}[self.sensor_flag]
            self._num = 0
            time.sleep_ms(300)

        # —— 参数切换 ——
        if key_now == 3 and self._num > NUMMAX:
            self._num = 0
            ranges = {1: (0, 5), 2: (6, 11), 3: (12, 17)}
            lo, hi = ranges[self.sensor_flag]
            self.color_flag = lo if self.color_flag >= hi else self.color_flag + 1
            time.sleep_ms(300)

        # —— 保存 ——
        if key_now == 4 and self._num > NUMMAX:
            self._num = 0
            try:
                with open('/sdcard/code/threshold.txt', 'w') as f:
                    f.write(','.join(map(str, self.threshold)))
                img.draw_string_advanced(200, 80, 30, "保存成功", color=(0, 255, 0))
            except Exception as e:
                img.draw_string_advanced(200, 80, 30, f"保存失败", color=(255, 0, 0))
            time.sleep_ms(800)

        # —— 减 ——
        if key_now == 5 and self._num > NUMMAX:
            self._num = 0
            step = self._get_step()
            lo, _ = self._get_bounds()
            idx = self.color_flag
            self.threshold[idx] = max(lo, self.threshold[idx] - step)
            time.sleep_ms(80)

        # —— 加 ——
        if key_now == 6 and self._num > NUMMAX:
            self._num = 0
            step = self._get_step()
            _, hi = self._get_bounds()
            idx = self.color_flag
            self.threshold[idx] = min(hi, self.threshold[idx] + step)
            time.sleep_ms(80)

        # 叠加 UI
        img = self.Draw_rectangle(img)
        img = self.Draw_menu(img)

        Display.show_image(img)
        time.sleep_ms(10)
        return result  # None: 继续调节; list: 完成
