import math

from Coord2PixelConverter import Coord2PixelConverter
from model.Canvas import Canvas
from model.CanvasObject import CanvasObject
from Logger import Logger as log

class City(CanvasObject):
    color = (1,1,0)
    density_to_start_val = {
        0: 0,
        0.05: 1,
        0.2: 1,
        0.3: 10,
        500: 20,
        1000: 30,
        2000: 50
    }
    DIM_FACTOR = 0.3

    def __init__(self, city_dict: dict):
        coords = city_dict["coords"]
        super().__init__(float(coords["lat"]), float(coords["lon"]))
        self.name = city_dict["name"]
        self.population = int(city_dict["population"])
        self.state = city_dict["state"]
        self.area = float(city_dict["area"]) if "area" in city_dict.keys() else 0.0
        self.radius = math.sqrt(self.area/(2*math.pi))
        #if self.radius > 5: self.radius = 5
        self.density = round(self.population / self.area) if self.area > 0 else 0

    def __str__(self): return f"{self.name} r={round(self.radius)} p={round(self.population/1000)}k d={self.density}"

    def __repr__(self): return self.__str__()

    def print_point(self):
        log.debug(f"Printing City point {self}")
        x, y = Coord2PixelConverter().convert_latlong2xy(self.center_lat, self.center_long)
        Canvas().set_pixel(x, y, (200,200,200), dim_scale=1, additive=True)

    def print(self):
        log.debug(f"Printing City {self}")
        start_color = self.color
        for i, data in enumerate(self.density_to_start_val.items()):
            if self.density > data[0]:
                start_color = tuple(self.color[i]*data[1] for i in range(3))
        if start_color == (0,0,0): return

        pixels = self.get_radius_around()
        log.debug(f"City {self} pixels and dims: {pixels}")
        for pix in pixels:
            if pix[0] >= 0: Canvas().set_pixel(pix[0], pix[1], start_color, dim_scale=pix[2], additive=True)

    def get_radius_around(self, dim_factor=DIM_FACTOR) -> list:
        x_center, y_center = Coord2PixelConverter().convert_latlong2xy(self.center_lat, self.center_long)
        r = round(self.radius)
        out = [(x_center, y_center, 1)]
        for x_i in range(-r, r + 1):
            for y_i in range(-r, r + 1):
                # Check if the point is inside the circle
                if x_i ** 2 + y_i ** 2 <= r ** 2:
                    dim = dim_factor / max(abs(x_i), abs(y_i)) if max(abs(x_i), abs(y_i)) != 0 else 1
                    out.append((x_center + x_i, y_center + y_i, dim))
        return out
