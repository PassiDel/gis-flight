import logging
from datetime import datetime, timedelta

import FlightRadar24
from FlightRadar24 import FlightRadar24API

from Singleton import Singleton
from Coord2PixelConverter import Coord2PixelConverter as coords
from model.Plane import Plane
from Logger import Logger as log

class FlightRadarConnector(Singleton):
    delete_after_sec = 60
    exclude_aircraft_types = ["GLID"]

    @classmethod
    def init(cls):
        cls.fr_api = FlightRadar24API()
        cls.planes: list[Plane] = []

    def get_bounds_str(self):
        x_min, y_min, x_max, y_max = coords().get_bounds()
        return f"{y_max},{y_min},{x_min},{x_max}"

    def get_planes(self) -> list[Plane]:
        flights = self.fr_api.get_flights(bounds=self.get_bounds_str())
        for flight in flights:
            flight: FlightRadar24.Flight = flight
            found_match = False
            for plane in self.planes:
                if plane.update_if_match(flight):
                    found_match = True
                    break
            if not found_match:
                new = Plane(flight)
                if new.x > -1 and new.aircraft_type not in self.exclude_aircraft_types:
                    log.info(f"Added new Plane: {new}")
                    self.planes.append(new)
        # delete planes that are not on the canvas anymore or havent been updated
        for plane in self.planes:
            if plane.x == -1 or plane.y == -1:
                log.warning(f"Removing out of bounds {plane}")
                self.planes.remove(plane)
                continue
            if (datetime.now() - plane.last_update).total_seconds() > self.delete_after_sec:
                log.warning(f"Removing timeout {plane}")
                self.planes.remove(plane)
        return self.planes