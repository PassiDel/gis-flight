from model.Pixel import Pixel
from Singleton import Singleton
from Logger import Logger as log


class Canvas(Singleton):
    _width = 64
    _height = 88
    _y_start_of_double_layered_zone = 42
    _height_of_double_layered_zone = 4
    _dim_scale_double_layered_zone = 1.8
    _dim_factor_double_layered_zone_additive = 1.8
    pixels = None

    @classmethod
    def init(cls):
        cls.pixels = [[Pixel(x, y) for y in range(cls._height)] for x in range(cls._width)]

    def get_pixel(self, x, y):
        return self.pixels[x][y]

    def set_pixel(self, x:int, y:int, color: tuple[int, int, int], dim_scale=None, additive=False):
        # make double layered zone a bit brighter
        if y in range(self._y_start_of_double_layered_zone,
                      self._y_start_of_double_layered_zone + self._height_of_double_layered_zone):
            dim_scale = dim_scale * self._dim_factor_double_layered_zone_additive if dim_scale is not None \
                else self._dim_scale_double_layered_zone
        try:
            # update pixel
            self.get_pixel(x,y).set_color(color, additive=additive, dim=dim_scale)
        except IndexError as e:
            log.debug(f"Cannot set Pixel ({x},{y}): out of range of Canvas!")

    def get_pixels_with_update_pending(self) -> list:
        out = []
        for x in range(self._width):
            for y in range(self._height):
                p:Pixel = self.get_pixel(x,y)
                if p.is_update_pending():
                    out.append(p)
        return out

    def get_width(self) -> int:
        return self._width

    def get_height(self) -> int:
        return self._height

    def reset_all_pixels(self):
        for x in range(self._width):
            for y in range(self._height):
                self.get_pixel(x, y).reset()

    def set_all_pixels(self, color:tuple):
        start_double_zone = 42
        for x in range(self._width):
            for y in range(self._height):
                self.set_pixel(x, y, color)

