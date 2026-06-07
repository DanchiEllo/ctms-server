import cv2
import torch
from PIL import Image, ImageDraw
import numpy as np


class ImageHandler:
    def __init__(self, ):
        self.image = None
        self.coordinates = None
        self.x = None
        self.y = None
        self.width = None
        self.height = None

    def get_processed_array(self, frame, area):
        self.image = Image.fromarray(frame)
        self.coordinates = area.coordinates
        self.x = area.mask.x
        self.y = area.mask.y
        self.width = area.mask.width
        self.height = area.mask.height

        mask = Image.new('L', self.image.size, 0)
        draw = ImageDraw.Draw(mask)

        coordinates = [(x[0], x[1]) for x in self.coordinates]
        draw.polygon(coordinates, fill=255)

        result = Image.new('RGB', self.image.size)
        draw = ImageDraw.Draw(result)
        draw.rectangle([(0, 0), self.image.size], fill="black")
        result.paste(self.image, mask=mask)

        x = self.x
        y = self.y
        width = self.width
        height = self.height
        cropped_result = result.crop((x, y, x + width, y + height))

        return np.array(cropped_result)


class TrafficLight:
    def __init__(self, uri):
        self.uri = uri

    def send_green_signal(self, seconds):
        #connect to uri and send green signal
        pass

    def send_red_signal(self, seconds):
        #connect to uri and send red signal
        pass

    def switch_to_standart_signal_mode(self):
        pass


class DefaultArea:
    def __init__(self, coordinates, mask, traffic_light):
        self.coordinates = coordinates
        self.mask = mask
        self.traffic_light = traffic_light


class ModifiedArea(DefaultArea):
    def __init__(self, coordinates, mask, traffic_light):
        super().__init__(coordinates, mask, traffic_light)
        self.tuple_count_vehicles = [0, 0]
        self.move_time = 0
        self.average_time_handler = AverageTimeHandler()

    def add_count_vehicles(self, count_vehicles):
        self.tuple_count_vehicles[0] = self.tuple_count_vehicles[1]
        self.tuple_count_vehicles[1] = count_vehicles

    def set_move_time(self):
        self.move_time = self.average_time_handler.calculate_average_time(tuple_count_vehicles=self.tuple_count_vehicles,
                                                                     move_time=self.move_time)


class Camera:
    def __init__(self, uri, areas):
        self.uri = uri
        self.areas = areas

    def get_frame(self):
        cap = cv2.VideoCapture(self.uri)
        if cap.isOpened() is False:
            return None
        else:
            frame = cap.read()[1]
            return frame


class Model:
    def __init__(self):
        self.model = torch.hub.load('ultralytics/yolov5', 'yolov5l')

    def get_count_vehicles(self, frame):
        results = self.model(frame)

        # Классы, которые мы хотим распознавать
        desired_classes = ['car', 'truck', 'bus']
        confidence_threshold = 0.45

        total_count = 0
        for *box, conf, cls in results.xyxy[0]:  # для каждого объекта в изображении
            # Если текущий объект принадлежит к желаемым классам и уверенность выше порога:
            if results.names[int(cls)] in desired_classes and conf > confidence_threshold:
                total_count += 1  # Увеличиваем счетчик

        # Выводим общее количество в консоль
        print(f"Total count: {total_count}")
        return total_count


class AverageTimeHandler:
    def __init__(self):
        self.MAX_SECONDS = 9
        self.MIN_SECONDS = 2

    def calculate_average_time(self, tuple_count_vehicles, move_time):
        difference = tuple_count_vehicles[1] - tuple_count_vehicles[0]
        if difference >= 0:
            if int(move_time + 2) > self.MAX_SECONDS:
                return self.MAX_SECONDS
            else:
                return move_time + 2
        else:
            if int(move_time - 2) < self.MIN_SECONDS:
                return self.MIN_SECONDS
            else:
                return move_time - 2


class CrossroadHandler:
    def __init__(self, crossroad):
        self.crossroad = crossroad
        self.cameras = [Camera(uri=camera.uri, areas=camera.areas) for camera in crossroad.cameras]
        self.traffic_lights = [TrafficLight(uri=traffic_light.uri) for traffic_light in crossroad.traffic_lights]
        self.image_handler = ImageHandler()
        self.move_time = self.crossroad.move_time
        #self.move_time = 2.75
        self.model = Model()
        self.send_all_traffic_lights_red_signal()
        if self.move_time is None:
            for camera in self.cameras:
                areas = []
                for area in camera.areas:
                    areas.append(ModifiedArea(coordinates=area.coordinates, mask=area.mask,
                                              traffic_light=TrafficLight(area.traffic_light.uri)))
                camera.areas = areas
        else:
            for camera in self.cameras:
                areas = []
                for area in camera.areas:
                    areas.append(DefaultArea(coordinates=area.coordinates, mask=area.mask,
                                             traffic_light=TrafficLight(uri=area.traffic_light.uri)))
                camera.areas = areas

        self.calculate()

        pass

    def calculate(self):
        while True:
            for camera in self.cameras:
                for area in camera.areas:
                    count = self.model.get_count_vehicles(self.image_handler.get_processed_array(camera.get_frame(),
                                                                                                 area))
                    if self.move_time is None:
                        area.add_count_vehicles(count)
                        area.set_move_time()
                        time = int(area.move_time * count)
                        area.traffic_light.send_green_signal(seconds=time)
                        print(time)
                    else:
                        time = int(self.move_time * count)
                        area.traffic_light.send_green_signal(seconds=time)
                        print(time)

    def send_all_traffic_lights_red_signal(self):
        for traffic_light in self.traffic_lights:
            traffic_light.send_red_signal(seconds=20)
