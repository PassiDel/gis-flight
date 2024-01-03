from datetime import datetime

import FlightRadar24

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

    def __init__(self, flight: FlightRadar24.Flight, last_positions=None):
        super().__init__(flight.latitude, flight.longitude)
        self.altitude = int(flight.get_altitude().rstrip(" ft"))
        self.heading = int(flight.get_heading().rstrip("°"))
        self.heading_x, self.heading_y = Coord2PixelConverter().convert_heading2xy_vector(self.heading)
        self.speed = int(flight.get_ground_speed().rstrip(" kts"))
        self.flight: FlightRadar24.Flight = flight
        self.last_positions = last_positions if last_positions is not None else []
        self.last_update = datetime.now()
        self.x, self.y = Coord2PixelConverter().convert_latlong2xy(self.center_lat, self.center_long)
        self.aircraft_type = flight.aircraft_code

    def __str__(self):
        return f"Plane {self.flight.callsign} type={self.aircraft_type} pos=({self.x},{self.y}) alt={self.altitude} speed={self.speed}"

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

    def update_if_match(self, flight: FlightRadar24.Flight) -> bool:
        if self.flight.callsign != flight.callsign: return False
        last_position = (self.x, self.y)
        self.__init__(flight, self.last_positions)
        current_position = (self.x, self.y)
        self.last_update = datetime.now()
        if current_position != last_position and last_position not in self.last_positions:
            self.last_positions.insert(0, last_position)
            if len(self.last_positions) > self.max_buffer_length:
                self.last_positions = self.last_positions[:self.max_buffer_length]
            log.debug(f"{self.flight.callsign}: Added old position {last_position}. Backlog={len(self.last_positions)}")
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
