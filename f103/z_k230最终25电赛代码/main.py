import time, os, sys
import math
from media.sensor import *
from media.display import *
from media.media import *
from libs.YbProtocol import YbProtocol
from ybUtils.YbUart import YbUart
from ybUtils.YbKey import YbKey
from machine import FPIOA, Pin
from machine import TOUCH  # 添加触摸屏支持

from code.threshold import Threshold

key = YbKey()
uart = YbUart(baudrate=115200)

# 设置摄像头参数
WIDTH = 560    # 原始图像宽度
HEIGHT = 360   # 原始图像高度

# 初始化窗口参数
WINDOW_WIDTH = 560   # 窗口宽度（需 ≤ WIDTH=560）
WINDOW_HEIGHT = 280  # 窗口高度（需 ≤ HEIGHT=360）

# 计算窗口初始位置（居中）
WINDOW_X = (WIDTH - 480) // 2    # 水平居中：40
WINDOW_Y = (HEIGHT - 280) // 2   # 垂直居中：40

# 初始化二值化阈值
binary_threshold = [14, 70]

# 初始化面积阈值
area_min_threshold = 250000
area_max_threshold = 900000

def init_sensor():
    """初始化摄像头"""
    sensor = Sensor(width=WIDTH, height=HEIGHT)
    sensor.reset()
    time.sleep_ms(100)
    sensor.set_framesize(width=WIDTH, height=HEIGHT)
    sensor.set_pixformat(Sensor.RGB565)
    return sensor

def init_qita():
    fpioa = FPIOA()
    fpioa.set_function(9, fpioa.UART1_TXD, ie=0, oe=1)
    fpioa.set_function(10, fpioa.UART1_RXD, ie=1, oe=0)

    # 初始化触摸屏
    tp = TOUCH(0)
    return tp

def init_display():
    """初始化显示"""
    Display.init(Display.ST7701, width=640, height=480, to_ide=True)
    MediaManager.init()

def shibie_rect(img, bin_img, start_time):
    global area_min_threshold, area_max_threshold

    target_found = False
    rects = bin_img.find_rects(roi=(WINDOW_X, WINDOW_Y, WINDOW_WIDTH, WINDOW_HEIGHT), threshold=15000)
    for rect in rects:
        if rect:
            x, y, w, h = rect.rect()
            area = rect.magnitude()
            print(f"Found inner rect, area: {area}")

            # 使用调节后的面积阈值
            if area_min_threshold <= area <= area_max_threshold:
                aspect_ratio = w / h if h != 0 else 0

                if (1 < aspect_ratio < 6):
                    cx = x + w // 2
                    cy = y + h // 2

                    x_coord = (cx - 640 // 2)
                    y_coord = (cy - 480 // 2)

                    message = f"${x_coord},{y_coord},#@"
                    uart.write(message)

                    img.draw_rectangle(rect.rect(), color=(0, 255, 0), thickness=2)
                    img.draw_circle(cx, cy, 5, color=(255, 0, 0), thickness=2)
                    img.draw_string_advanced(x, y-15, 12,
                                            f"Area: {area}, Aspect: {aspect_ratio:.2f}",
                                            color=(255, 255, 0))

                    target_found = True
                    break

    # 显示目标状态
    status = "Target Found" if target_found else "No Target"
    img.draw_string_advanced(40, 250, 20, status, color=(255, 0, 0))

    # 显示帧率
    elapsed = time.ticks_ms() - start_time
    fps = 1000 / elapsed if elapsed > 0 else 0
    img.draw_string_advanced(40, 50, 30, f"fps:{fps:.1f}", color=(255, 0, 0))


    # 显示当前模式和参数
    img.draw_string_advanced(40, 100, 20, f"{binary_threshold[0]},{binary_threshold[1]}", color=(0, 255, 150))
    img.draw_string_advanced(40, 300, 20, f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}", color=(0, 0, 255))
    img.draw_string_advanced(40, 200, 20, f" {area_min_threshold:,}-{area_max_threshold:,}", color=(0, 255, 255))


def main():
    global WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_X, WINDOW_Y, binary_threshold
    global area_min_threshold, area_max_threshold

    try:
        # 初始化触摸屏
        tp = init_qita()
        sensor = init_sensor()
        init_display()
        sensor.run()
        clock = time.clock()

        # 初始化阈值调整实例
        thr = Threshold()

        # 设置阈值初始值
        binary_threshold[0] = thr.threshold[0]
        binary_threshold[1] = thr.threshold[1]
        WINDOW_WIDTH = thr.threshold[6]
        WINDOW_HEIGHT = thr.threshold[7]

        area_min_threshold = thr.threshold[8]
        area_max_threshold = thr.threshold[9]


        # 重新计算窗口位置
        WINDOW_X = (WIDTH - WINDOW_WIDTH) // 2
        WINDOW_Y = (HEIGHT - WINDOW_HEIGHT) // 2

        # 长按检测变量
        touch_counter = 0
        in_threshold_mode = False  # 是否在阈值调整模式中

        while True:
            start_time = time.ticks_ms()
            clock.tick()
            os.exitpoint()

            # 触摸检测 - 长按进入调节模式
            points = tp.read()
            if points and not in_threshold_mode:
                touch_counter += 1
                if touch_counter > 50:
                    in_threshold_mode = True
                    print("长按进入调节模式")
            else:
                touch_counter = max(0, touch_counter - 1)

            # 调节模式处理
            if in_threshold_mode:
                # 调用调节函数，等待返回
                new_params = thr.change_threshold(sensor, clock)
                if new_params is not None:
                    # 根据当前模式更新参数
                    if thr.sensor_flag == 1:
                        # 更新灰度阈值
                        binary_threshold[0] = new_params[0]
                        binary_threshold[1] = new_params[1]

                    elif thr.sensor_flag == 2:
                        # 更新窗口大小
                        WINDOW_WIDTH = max(200, min(WIDTH, new_params[0]))
                        WINDOW_HEIGHT = max(150, min(HEIGHT, new_params[1]))
                        WINDOW_X = (WIDTH - WINDOW_WIDTH) // 2
                        WINDOW_Y = (HEIGHT - WINDOW_HEIGHT) // 2

                        print(f"更新窗口大小: {WINDOW_WIDTH}x{WINDOW_HEIGHT}")
                    elif thr.sensor_flag == 3:
                        # 更新面积阈值
                        area_min_threshold = new_params[0]
                        area_max_threshold = new_params[1]
                        print(f"更新面积阈值: {area_min_threshold:,} - {area_max_threshold:,}")

                    in_threshold_mode = False  # 退出调节模式

            # 正常识别模式
            if not in_threshold_mode:
                img = sensor.snapshot()
                gray_img = img.to_grayscale()
                bin_img = gray_img.binary([(binary_threshold[0], binary_threshold[1])])

                # 绘制识别区域窗口
                img.draw_rectangle(WINDOW_X, WINDOW_Y, WINDOW_WIDTH, WINDOW_HEIGHT,
                                 color=(135, 206, 235))

                # 执行识别
                shibie_rect(img, bin_img, start_time)

                # 显示图像
                Display.show_image(img, x=(640 - WIDTH) // 2, y=(480 - HEIGHT) // 2)

            time.sleep_ms(50)

    except KeyboardInterrupt as e:
        print("用户中断 / User interrupted: ", e)
    except Exception as e:
        print(f"发生错误 / Error occurred: {e}")
        # 打印详细的错误信息
        import sys
        sys.print_exception(e)
    finally:
        try:
            if 'sensor' in locals() and isinstance(sensor, Sensor):
                sensor.stop()
            Display.deinit()
            MediaManager.deinit()
            uart.deinit()
        except:
            pass

if __name__ == "__main__":
    main()
