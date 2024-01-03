import math

from Logger import Logger as log
from Singleton import Singleton
from model.Canvas import Canvas


class Coord2PixelConverter(Singleton):
    x_min = 6.45  #6.63  # long
    x_max = 11.18 #11.63  # long
    y_min = 51.1 #51.05  # lat
    y_max = 55.05  #55.2  # lat

    _strip_order = [0, 2, 1, 3, 4, 6, 5, 7, 8, 10, 9]
    _strip_rotations = [1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0]
    _pixels_per_row = 512
    _amount_pixels = 5632

    canvas_width = Canvas().get_width()
    canvas_height = Canvas().get_height()

    def convert_latlong2xy(self, lat, long, flip=True) -> tuple[int, int]:
        # convert
        y_result = round(((lat - self.y_min) * Canvas().get_height()) / (self.y_max - self.y_min))
        x_result = round(((long - self.x_min) * Canvas().get_width()) / (self.x_max - self.x_min))
        y_result = Canvas().get_height() - y_result
        # check out of bounds
        if 0 > x_result or x_result >= Canvas().get_width() or 0 > y_result or y_result >= Canvas().get_height():
            log.debug(f"Converted xy value out of bounds: ({x_result},{y_result})")
            return -1, -1
        else:
            if flip:
                return Canvas().get_width() - x_result, Canvas().get_height() - y_result
            else:
                return x_result, y_result

    def test_lat_long(self, lat, long) -> bool:
        if self.y_min <= lat <= self.y_max and self.x_min <= long <= self.x_max:
            return True
        return False

    def convert_heading2xy_vector(self, heading) -> tuple[int, int]:
        if heading < 0 or heading > 360: raise ValueError(f"Heading {heading} is not between 0 and 360 degrees")
        conversion_dict = {
            22.5: (0,-1), 67.5: (1,-1), 112.5: (1,0),
            157.5: (1,1), 202.5: (0,1), 247.5: (-1,1),
            292.5: (-1,0), 337.5: (-1,-1), 361: (0,-1)
        }
        for threshold, result in conversion_dict.items():
            if heading < threshold: return result

    def convert_xy2strip_index(self, x, y) -> int:
        zig_zag = x % 2
        strip_no = int(y / 8)
        # compensate order of strips
        corrected_strip_no = self._strip_order[strip_no]
        # compensate rotation of the strips
        if self._strip_rotations[strip_no] == 1:
            # forward
            first_pixel_of_row = corrected_strip_no * 512
            index = int(first_pixel_of_row + (y % 8 if not zig_zag else (7 - y % 8)) + x * 8)
        else:
            # backward
            first_pixel_of_row = (corrected_strip_no + 1) * 512 - 1
            index = int(first_pixel_of_row - ((7 - y % 8) if not zig_zag else y % 8) - x * 8)

        #log.debug(f"Converted x={x} y={y} to index {index}")
        if index > self._amount_pixels:
            raise IndexError(f"Pixelindex {index} is out of bounds on strip")
        return index
