import random
import time
import cv2
import numpy as np
import torch
from ultralytics.utils.plotting import colors

from Handler.CrossroadHandler import ImageHandler, DefaultArea

class Mask:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

mask = Mask(x=581, y=451, width=694, height=264)

area = DefaultArea(coordinates=[
                    [
                        581,
                        519
                    ],
                    [
                        672,
                        451
                    ],
                    [
                        1275,
                        631
                    ],
                    [
                        1275,
                        715
                    ],
                    [
                        1145,
                        714
                    ],
                    [
                        1084,
                        697
                    ],
                    [
                        867,
                        630
                    ],
                    [
                        720,
                        574
                    ]], mask=mask, traffic_light="traffic_light")

video_stream_url = 'https://s2.moidom.citylink.pro/s/private/lwxE1RVRZhSGeVmYHHMkZA/1780866000/0000091167.m3u8'

width = 1200
height = 700


def load_model():
    model = torch.hub.load(
        'ultralytics/yolov5',
        'yolov5l',
        force_reload=True,  # принудительная перезагрузка
        trust_repo=True,  # доверие репозиторию
        verbose=False  # уменьшение вывода
    )
    return model


def plot_one_box(x, im, color=None, label=None, line_thickness=None):
    tl = line_thickness or round(0.002 * (im.shape[0] + im.shape[1]) / 2) + 1
    color = color or [random.randint(0, 255) for _ in range(3)]
    c1, c2 = (int(x[0]), int(x[1])), (int(x[2]), int(x[3]))
    cv2.rectangle(im, c1, c2, color, thickness=tl)
    if label:
        tf = max(tl - 1, 1)  # font thickness
        t_size = cv2.getTextSize(label, 0, fontScale=tl / 3, thickness=tf)[0]
        c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
        cv2.rectangle(im, c1, c2, color, -1)  # filled
        cv2.putText(im, label, (c1[0], c1[1] - 2), 0, tl / 3, [225, 255, 255], thickness=tf, lineType=cv2.LINE_AA)


def capture_stream(model, frame_skip=10):
    cap = cv2.VideoCapture(video_stream_url)

    if cap.isOpened() is False:
        print("Ошибка при открытии видеопотока или файла")

    frame_number = 0

    while cap.isOpened():
        ret, frame = cap.read()
        frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
        if ret is True:
            if frame_number % frame_skip == 0:
                frame = ImageHandler().get_processed_array(frame=frame, area=area)
                process_frame(model, frame)

            frame_number += 1

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            break

    cap.release()


def process_frame(model, frame):
    results = model(frame)

    desired_classes = ['car', 'truck', 'bus']
    confidence_threshold = 0.45

    total_count = 0
    for *box, conf, cls in results.xyxy[0]:
        if results.names[int(cls)] in desired_classes and conf > confidence_threshold:
            total_count += 1
            label = f"{results.names[int(cls)]} {conf:.2f}"
            plot_one_box(box, frame, label=label, color=colors(int(cls)), line_thickness=1)

    resized_frame = cv2.resize(frame, (width, height))

    cv2.putText(resized_frame, f"Total count: {total_count}", (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow('Destination', resized_frame)


if __name__ == "__main__":
    model = load_model()
    process_frame.prev_time = time.time()
    cv2.namedWindow("Destination", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Destination", width, height)
    cv2.setWindowProperty("Destination", cv2.WND_PROP_TOPMOST, 1)
    capture_stream(model)
    cv2.destroyAllWindows()
