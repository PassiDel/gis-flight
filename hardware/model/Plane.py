from datetime import datetime

from Coord2PixelConverter import Coord2PixelConverter
from model.Canvas import Canvas
from model.CanvasObject import CanvasObject
from Logger import Logger as log


class Plane(CanvasObject):
    idle_color = (100, 100, 100)
    idle_altitude = 200
    max_buffer_length = 20

    tail_thresholds_and_dimm = {
        50: 0.6,
        300: 0.5,
        320: 0.45,
        340: 0.4,
        360: 0.35,
        370: 0.3,
        380: 0.25,
        390: 0.2,
        400: 0.15,
        425: 0.1,
        450: 0.05
    }

    def __init__(self, json_data:dict, last_positions=None):
        """

        :param json_data: example {'altitude': 2850, 'latitude': 52.328, 'longitude': 10.86, 'speed': 164, 'id': '34510073'}
        :param last_positions:
        """
        super().__init__(json_data["latitude"], json_data["longitude"])
        self.altitude = json_data["altitude"]
        self.speed = json_data["speed"]
        self.id = json_data["id"]
        self.last_positions = last_positions if last_positions is not None else []
        self.last_update = datetime.now()
        self.x, self.y = Coord2PixelConverter().convert_latlong2xy(self.center_lat, self.center_long)
        self.aircraft_type = "NA" #"GLID" if json_data["isGlider"] else "NA"

    def __str__(self):
        return f"Plane {self.id} type={self.aircraft_type} pos=({self.x},{self.y}) alt={self.altitude} speed={self.speed}"

    def print(self):
        log.debug(f"printing {self}")
        if self.x >= 0:
            if self.altitude < self.idle_altitude:
                Canvas().set_pixel(self.x, self.y, self.idle_color)
            else:
                self.color = self.altitude_to_red_green_spectrum()
                log.debug(f"Plane color set to {self.color}")
                Canvas().set_pixel(self.x, self.y, self.color)
                for i, data in enumerate(self.tail_thresholds_and_dimm.items()):
                    if self.speed > data[0] and len(self.last_positions) > i:
                        Canvas().set_pixel(self.last_positions[i][0], self.last_positions[i][1], self.color, dim_scale=data[1])
                        # Canvas().set_pixel(self.x - (i + 1) * self.heading_x, self.y - (i + 1) * self.heading_y, dim_tuple)

    def update_if_match(self, json_data) -> bool:
        if self.id != json_data["id"]: return False
        last_position = (self.x, self.y)
        self.__init__(json_data, self.last_positions)
        current_position = (self.x, self.y)
        self.last_update = datetime.now()
        if current_position != last_position and last_position not in self.last_positions:
            self.last_positions.insert(0, last_position)
            if len(self.last_positions) > self.max_buffer_length:
                self.last_positions = self.last_positions[:self.max_buffer_length]
            log.debug(f"{self.id}: Added old position {last_position}. Backlog={len(self.last_positions)}")
        return True

    def altitude_to_red_green_spectrum(self):
        min_val = self.idle_altitude
        mid_val = 30000
        max_val = 40000

        if self.altitude < mid_val:  # Red to Blue transition
            # Map v from [min_val, max_val] to [0, 1]
            x = (self.altitude - min_val) / (mid_val - min_val)
            R = int(255 * (1 - x))
            G = 0
            B = int(255 * x)
        else:  # Blue to Green transition
            x = (self.altitude - mid_val) / (max_val - mid_val)
            R = 0
            G = int(255 * x)
            B = int(255 * (1 - x))

        return R, G, B
