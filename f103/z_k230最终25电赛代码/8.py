import time, os, sys
from media.sensor import *
from media.display import *
from media.media import *
import image
from machine import TOUCH
from ybUtils.YbRGB import YbRGB

# 常量定义
NUMMAX = 4
WIDTH = 560
HEIGHT = 360

# 调整颜色框位置
SITE = [
    (0, 0, 0, 0),
    (150, 180, 80, 60),    # 位置1（灰度阈值下限）
    (330, 180, 80, 60),    # 位置2（灰度阈值上限）
    (0, 0, 0, 0),         # 移除位置3
    (0, 0, 0, 0),         # 移除位置4
    (0, 0, 0, 0),         # 移除位置5
    (0, 0, 0, 0),         # 移除位置6
    (150, 180, 80, 60),   # 位置7（窗口宽度）
    (330, 180, 80, 60),   # 位置8（窗口高度）
    (150, 250, 80, 60),   # 位置9（最小面积）
    (330, 250, 80, 60)    # 位置10（最大面积）
]

class Threshold :
    def __init__(self):
        # 初始化所有需要的参数（灰度阈值2个，窗口大小2个，面积阈值2个）
        try:
            with open('/sdcard/code/threshold.txt', 'r') as f:
                data = [int(x) for x in f.read().split(',')]
                # 确保有足够的元素
                self.threshold = [
                    data[0] if len(data) > 0 else 12,   # 灰度阈值下限
                    data[1] if len(data) > 1 else 66,   # 灰度阈值上限
                    0, 0, 0, 0,                         # 占位
                    data[6] if len(data) > 6 else 560,  # 窗口宽度
                    data[7] if len(data) > 7 else 280,  # 窗口高度
                    data[8] if len(data) > 8 else 194960,  # 最小面积
                    data[9] if len(data) > 9 else 900000   # 最大面积
                ]
        except:
            # 默认值
            self.threshold = [
                12, 66,             # 灰度阈值下限/上限
                0, 0, 0, 0,         # 占位
                560, 280,           # 窗口宽度/高度
                194960, 900000      # 最小面积/最大面积
            ]

        self.tp = TOUCH(0)
        self.sensor_flag = 1  # 1: 灰度阈值模式, 2: 窗口大小模式, 3: 面积阈值模式
        self.color_flag = 1   # 当前调节的参数索引（1-2为灰度，7-8为窗口，9-10为面积）

    def Draw_menu(self, img):
        # 使用绿色字体
        text_color = (0, 255, 0)

        # 顶部按钮 - 三个大按钮
        button_width, button_height = 150, 60
        spacing = (560 - 3 * button_width) // 4

        # 顶部按钮
        top_y = 20

        # 返回按钮
        x1 = spacing
        img.draw_rectangle(x1, top_y, button_width, button_height, color=(0, 100, 200))
        img.draw_string_advanced(x1 + 45, top_y + 15, 35, "返回", color=text_color)

        # 功能按钮（模式切换）
        x2 = x1 + button_width + spacing
        img.draw_rectangle(x2, top_y, button_width, button_height, color=(0, 100, 200))
        mode_text = ""
        if self.sensor_flag == 1:
            mode_text = "灰度"
        elif self.sensor_flag == 2:
            mode_text = "窗口"
        elif self.sensor_flag == 3:
            mode_text = "面积"
        img.draw_string_advanced(x2 + 45, top_y + 15, 35, mode_text, color=text_color)

        # 保存按钮
        x3 = x2 + button_width + spacing
        img.draw_rectangle(x3, top_y, button_width, button_height, color=(0, 100, 200))
        img.draw_string_advanced(x3 + 45, top_y + 15, 35, "保存", color=text_color)

        # 底部按钮 - 三个大按钮
        bottom_y = 280
        button_width = 150
        spacing = (560 - 3 * button_width) // 4

        # 减号按钮
        img.draw_rectangle(spacing, bottom_y, button_width, button_height, color=(0, 100, 200))
        img.draw_string_advanced(spacing + 65, bottom_y + 15, 40, "-", color=text_color)

        # 切换按钮
        img.draw_rectangle(spacing * 2 + button_width, bottom_y, button_width, button_height, color=(0, 100, 200))
        img.draw_string_advanced(spacing * 2 + button_width + 45, bottom_y + 15, 35, "切换", color=text_color)

        # 加号按钮
        img.draw_rectangle(spacing * 3 + button_width * 2, bottom_y, button_width, button_height, color=(0, 100, 200))
        img.draw_string_advanced(spacing * 3 + button_width * 2 + 65, bottom_y + 15, 40, "+", color=text_color)

        # 显示当前调节的参数名称
        current_param = ""
        if self.sensor_flag == 1:
            current_param = "灰度下限" if self.color_flag == 1 else "灰度上限"
        elif self.sensor_flag == 2:
            current_param = "窗口宽度" if self.color_flag == 7 else "窗口高度"
        elif self.sensor_flag == 3:
            current_param = "最小面积" if self.color_flag == 9 else "最大面积"

        # 显示参数值
        if self.sensor_flag == 1:
            img.draw_string_advanced(120, 200, 30, f"({self.threshold[0]:03d} , {self.threshold[1]:03d})", color=text_color)
        elif self.sensor_flag == 2:
            img.draw_string_advanced(120, 200, 30, f"{self.threshold[6]}x{self.threshold[7]}", color=text_color)
        elif self.sensor_flag == 3:
            # 确保索引9和10存在
            min_area = self.threshold[8] if len(self.threshold) > 8 else 194960
            max_area = self.threshold[9] if len(self.threshold) > 9 else 900000
            img.draw_string_advanced(120, 200, 30, f"({min_area:,} - {max_area:,})", color=text_color)

        return img

    def witch_key(self, x, y):
        # 顶部按钮尺寸和位置
        top_button_width, top_button_height = 150, 60
        top_spacing = (560 - 3 * top_button_width) // 4
        top_y = 20

        # 底部按钮尺寸和位置
        bottom_button_width, bottom_button_height = 150, 60
        bottom_spacing = (560 - 3 * bottom_button_width) // 4
        bottom_y = 280

        # 顶部按钮区域检测
        x1 = top_spacing
        x2 = x1 + top_button_width + top_spacing
        x3 = x2 + top_button_width + top_spacing

        if x1 <= x <= x1 + top_button_width and top_y <= y <= top_y + top_button_height:
            return "返回"
        elif x2 <= x <= x2 + top_button_width and top_y <= y <= top_y + top_button_height:
            return "模式"
        elif x3 <= x <= x3 + top_button_width and top_y <= y <= top_y + top_button_height:
            return "保存"

        # 底部按钮区域检测
        x1_bottom = bottom_spacing
        x2_bottom = bottom_spacing * 2 + bottom_button_width
        x3_bottom = bottom_spacing * 3 + bottom_button_width * 2

        if x1_bottom <= x <= x1_bottom + bottom_button_width and bottom_y <= y <= bottom_y + bottom_button_height:
            return "-"
        elif x2_bottom <= x <= x2_bottom + bottom_button_width and bottom_y <= y <= bottom_y + bottom_button_height:
            return "切换"
        elif x3_bottom <= x <= x3_bottom + bottom_button_width and bottom_y <= y <= bottom_y + bottom_button_height:
            return "+"

        return 0

    def read_touch(self):
        points = self.tp.read()
        if points:
            pt = points[0]
            _button = self.witch_key(pt.x, pt.y)
            if _button == "返回":
                return 1
            elif _button == "模式":
                return 2
            elif _button == "保存":
                return 4
            elif _button == "-":
                return 5
            elif _button == "切换":
                return 3
            elif _button == "+":
                return 6
        return 0

    def Draw_rectangle(self, img):
        # 只绘制当前模式下有效的调节框
        if (self.sensor_flag == 1 and 1 <= self.color_flag <= 2) or \
           (self.sensor_flag == 2 and 7 <= self.color_flag <= 8) or \
           (self.sensor_flag == 3 and 9 <= self.color_flag <= 10):
            # 确保索引存在
            if self.color_flag < len(SITE):
                img.draw_rectangle(SITE[self.color_flag], color=(255, 0, 0), fill=True)
        return img

    def change_threshold(self, sensor, clock):
        num = 0
        key_last = 0
        key_now = 0
        while True:
            clock.tick()
            img = sensor.snapshot()

            # 根据当前模式处理图像
            if self.sensor_flag == 1:
                # 灰度阈值模式
                img = img.binary([[self.threshold[0], self.threshold[1]]])
                img = img.to_rgb565()
            elif self.sensor_flag == 2:
                # 窗口大小模式
                img = img.to_grayscale()
                img = img.to_rgb565()
            elif self.sensor_flag == 3:
                # 面积阈值模式 - 正常显示原图像
                img = img.to_rgb565()

            # 触摸处理
            key_last = key_now
            key_now = self.read_touch()

            if key_now == key_last and key_now != 0:
                num += 1
            else:
                num = 0

            # 处理返回按钮
            if key_now == 1 and num > NUMMAX:
                # 返回当前调节的参数
                if self.sensor_flag == 1:
                    return [self.threshold[0], self.threshold[1]]
                elif self.sensor_flag == 2:
                    return [self.threshold[6], self.threshold[7]]
                elif self.sensor_flag == 3:
                    # 确保索引存在
                    min_area = self.threshold[8] if len(self.threshold) > 8 else 194960
                    max_area = self.threshold[9] if len(self.threshold) > 9 else 900000
                    return [min_area, max_area]
                time.sleep_ms(300)

            # 处理模式切换
            elif key_now == 2 and num > NUMMAX:
                num = 0
                # 在3种模式之间循环
                self.sensor_flag = self.sensor_flag % 3 + 1
                # 切换模式后重置当前调节项
                if self.sensor_flag == 1:
                    self.color_flag = 1
                elif self.sensor_flag == 2:
                    self.color_flag = 7
                elif self.sensor_flag == 3:
                    self.color_flag = 9
                time.sleep_ms(300)

            # 处理参数切换
            elif key_now == 3 and num > NUMMAX:
                num = 0
                if self.sensor_flag == 1:
                    # 灰度模式下在1和2之间切换
                    self.color_flag = 2 if self.color_flag == 1 else 1
                elif self.sensor_flag == 2:
                    # 窗口模式下在7和8之间切换
                    self.color_flag = 8 if self.color_flag == 7 else 7
                elif self.sensor_flag == 3:
                    # 面积模式下在9和10之间切换
                    self.color_flag = 10 if self.color_flag == 9 else 9
                time.sleep_ms(300)

            # 处理保存
            elif key_now == 4 and num > NUMMAX:
                num = 0
                with open('/sdcard/code/threshold.txt', 'w') as f:
                    f.write(','.join(map(str, self.threshold)))
                # 显示保存成功提示
                img.draw_string_advanced(180, 120, 35, "保存成功", color=(0,255,0))
                Display.show_image(img)
                time.sleep_ms(1000)

            # 处理减号
            elif key_now == 5 and num > NUMMAX:
                num = 0
                if self.sensor_flag == 1:
                    # 灰度阈值调节
                    self.threshold[self.color_flag-1] = max(0, self.threshold[self.color_flag-1] - 1)
                elif self.sensor_flag == 2:
                    # 窗口大小调节
                    if self.color_flag == 7:  # 宽度
                        self.threshold[6] = max(200, self.threshold[6] - 10)
                    else:  # 高度
                        self.threshold[7] = max(150, self.threshold[7] - 10)
                elif self.sensor_flag == 3:
                    # 面积阈值调节
                    if self.color_flag == 9:  # 最小面积
                        # 确保索引存在
                        if len(self.threshold) > 8:
                            self.threshold[8] = max(100, self.threshold[8] - 1000)
                    else:  # 最大面积
                        if len(self.threshold) > 9:
                            self.threshold[9] = max(50000, self.threshold[9] - 1000)
                time.sleep_ms(100)

            # 处理加号
            elif key_now == 6 and num > NUMMAX:
                num = 0
                if self.sensor_flag == 1:
                    # 灰度阈值调节
                    self.threshold[self.color_flag-1] = min(255, self.threshold[self.color_flag-1] + 1)
                elif self.sensor_flag == 2:
                    # 窗口大小调节
                    if self.color_flag == 7:  # 宽度
                        self.threshold[6] = min(WIDTH, self.threshold[6] + 10)
                    else:  # 高度
                        self.threshold[7] = min(HEIGHT, self.threshold[7] + 10)
                elif self.sensor_flag == 3:
                    # 面积阈值调节
                    if self.color_flag == 9:  # 最小面积
                        # 确保索引存在
                        if len(self.threshold) > 8:
                            self.threshold[8] = min(999999, self.threshold[8] + 1000)
                    else:  # 最大面积
                        if len(self.threshold) > 9:
                            self.threshold[9] = min(999999, self.threshold[9] + 1000)
                time.sleep_ms(100)

            # 绘制当前调节框和菜单
            img = self.Draw_rectangle(img)
            img = self.Draw_menu(img)
            Display.show_image(img)
            time.sleep_ms(10)
