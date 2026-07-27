from maix import app, camera, display, image, nn, uart
import os

# MaixCam2 UART4: A21 is TX and A22 is RX.
# Connect A21 to the STM32 USART2 RX (PA3), A22 to USART2 TX (PA2), and join GND.
VISION_UART_DEVICE = "/dev/ttyS4"
VISION_BAUDRATE = 115200

# Maix -> STM32: 12 | count | digit_1 | digit_2 | digit_3 | digit_4 | xor | 5B
# Every frame is fixed at 8 bytes. Unused digit positions are zero-filled.
# count 0 means no valid group; count 1 through 4 means that many left-to-right digits.
RESULT_HEAD = 0x12
RESULT_TAIL = 0x5B
VALID_COUNTS = (1, 2, 3, 4)

CONF_TH = 0.50
STABLE_CONF_TH = 0.65
def find_model():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    except Exception:
        base_dir = "."

    candidates = [
        os.path.join(base_dir, "best.mud"),
        "best.mud",
        "/root/best.mud",
        "/root/models/best/best.mud",
        "/root/models/maixhub/best/best.mud",
    ]

    for path in candidates:
        if os.path.exists(path):
            return path
    raise RuntimeError("best.mud not found. Put all model files beside main.py.")


def xor_checksum(values):
    checksum = 0
    for value in values:
        checksum ^= value
    return checksum


def send_digit_group(serial, digits):
    """Send a fixed-length frame with digits ordered from left to right."""
    count = len(digits)
    payload = [count] + list(digits) + [0] * (4 - count)
    frame = bytes([RESULT_HEAD] + payload + [xor_checksum(payload), RESULT_TAIL])
    serial.write(frame)
    return frame


def recognized_digits(objs):
    """Return a valid left-to-right digit group, or an empty group on failure."""
    digits = []
    for obj in objs:
        if obj.class_id < 0 or obj.class_id > 7 or obj.score < STABLE_CONF_TH:
            continue
        digits.append((obj.x + obj.w // 2, obj.class_id + 1))

    if len(digits) not in VALID_COUNTS:
        return ()

    digits.sort(key=lambda item: item[0])
    return tuple(item[1] for item in digits)


def draw_detections(img, detector, objs):
    for obj in objs:
        img.draw_rect(obj.x, obj.y, obj.w, obj.h, color=image.COLOR_RED)
        if obj.class_id < len(detector.labels):
            label = detector.labels[obj.class_id]
        else:
            label = str(obj.class_id + 1)
        y = obj.y if obj.y > 12 else 12
        img.draw_string(obj.x, y - 12, "%s: %.2f" % (label, obj.score), color=image.COLOR_RED)


model_path = find_model()
detector = nn.YOLO11(model=model_path, dual_buff=True)
cam = camera.Camera(640, 480, detector.input_format())
dis = display.Display(640, 480)
serial = uart.UART(VISION_UART_DEVICE, VISION_BAUDRATE)

print("vision continuously sending, uart:", VISION_UART_DEVICE, VISION_BAUDRATE)
last_sent_frame = None

while not app.need_exit():
    try:
        img = cam.read()
        if img is None:
            continue

        objs = detector.detect(img, conf_th=CONF_TH, iou_th=0.45)
        draw_detections(img, detector, objs)

        digits = recognized_digits(objs)
        # Send every processed frame. An empty group produces 12 00 00 00 00 00 00 5B.
        frame = send_digit_group(serial, digits)
        if frame != last_sent_frame:
            print("send:", list(frame))
            last_sent_frame = frame
        img.draw_string(4, 4, "SEND %d" % len(digits), color=image.COLOR_GREEN)

        dis.show(img)
    except Exception as err:
        print("loop error:", err)
