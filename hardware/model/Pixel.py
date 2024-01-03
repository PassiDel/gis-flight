import random
import time

from Logger import Logger as log

# Gamma correction
gamma = 1.5
gamma_table = [int((i / 255.0) ** gamma * 255.0) for i in range(256)]
scaling = (1.0, 1.0, 1.0)
update_range = (120,180)  #sec

class Pixel:
    def __init__(self, x: int, y: int):
        self.x: int = x
        self.y: int = y
        self.current_color: tuple[int, int, int] = (999, 999, 999) # set cur color to something not reachable, so the pixels are updated at least once
        self.target_color: tuple[int, int, int] = (0, 0, 0)
        self.last_update = time.time()

    def set_color(self, color: tuple[int, int, int], dim=None, additive=False):
        color = (
                gamma_table[round(scaling[0] * color[0])],
                gamma_table[round(scaling[1] * color[1])],
                gamma_table[round(scaling[2] * color[2])]
                )
        if dim is not None:
            color = _dim_color(color, scale=dim)
        if additive:
            tmp_color = [0,0,0]
            for i in range(0,3):
                tmp_color[i] = round(self.target_color[i] + color[i])
                if tmp_color[i] > 255: tmp_color[i] = 255
            color = tuple(tmp_color)
        if color != self.target_color:
            self.target_color = color
            log.debug(f"updated target color for {self} -> {color}")

    def __str__(self):
        return f"Pixel({self.x}|{self.y})"

    def reset(self):
        self.target_color = (0, 0, 0)

    def is_update_pending(self) -> bool:
        if self.current_color != self.target_color: return True
        #if time.time() > self.last_update + random.randint(update_range[0], update_range[1]):
        #    log.info(f"Triggered Update for {self} by time")
        #    return True
        return False

    def updated(self):
        log.debug(f"Updated {self} from {self.current_color} to {self.target_color}")
        self.current_color = self.target_color
        self.last_update = time.time()


def _dim_color(color: tuple[int, int, int], to=None, scale=None):
    c = color
    if to is not None:
        c = (to if c[0] > to else c[0], to if c[1] > to else c[1], to if c[2] > to else c[2])
    if scale is not None:
        c = tuple(int(val * scale) for val in c)
    #log.debug(f"Dimmed color {color} to {c}")
    return c