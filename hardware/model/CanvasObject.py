from Coord2PixelConverter import Coord2PixelConverter
from model.Canvas import Canvas


class CanvasObject:
    color = (255, 255, 255)

    def __init__(self, center_lat, center_long):
        self.center_lat = center_lat
        self.center_long = center_long

    def print_in_color(self, color:tuple[int,int,int]):
        self.color = color
        self.print()

    def print(self):
        x, y = Coord2PixelConverter().convert_latlong2xy(self.center_lat, self.center_long)
        if x >= 0: Canvas().set_pixel(x, y, self.color)
