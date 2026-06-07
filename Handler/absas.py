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

class Area:
    def __init__(self):
        self.tuple_count_vehicles = [0, 0]
        self.move_time = 0

    def add_count_vehicles(self, count_vehicles):
        self.tuple_count_vehicles[0] = self.tuple_count_vehicles[1]
        self.tuple_count_vehicles[1] = count_vehicles

    def set_move_time(self):
        self.move_time = AverageTimeHandler().calculate_average_time(tuple_count_vehicles=self.tuple_count_vehicles,
                                                                     move_time=self.move_time)

if __name__ == "__main__":
    area = Area()
    area.set_move_time()
    area.add_count_vehicles(6)
    area.set_move_time()
    area.add_count_vehicles(7)
    area.set_move_time()
    area.add_count_vehicles(4)
    area.set_move_time()
