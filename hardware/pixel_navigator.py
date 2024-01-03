import time

from ESP_Controller import ESP_Controller
from model.Canvas import Canvas
from Singleton import Singleton
from Logger import Logger as log


class Pixel_Navigator(Singleton):

    x, y = 0, 0
    cur_color = (50,50,50)
    saved_color = (0,50,0)
    saved_coords = []

    @classmethod
    def init(cls):
        cls.esp_controller = ESP_Controller()
        cls.canvas = Canvas()
        log.info("Controller init")

    def run(self):
        while True:
            try:
                self.update()
                self.esp_controller.empty_update_chain() # wait until everything is updated
                self.get_input()
            except KeyboardInterrupt:
                log.info("Keyboard interrupt, deleting screen ...")
                Canvas().reset_all_pixels()
                self.esp_controller.empty_update_chain()
                self.esp_controller.close()

    def get_input(self):
        command = input("Enter movement command (w,a,s,d or press Enter to display coordinates): ")

        if command == '':
            self.saved_coords.append((self.x, self.y))
            log.info(f"Saved coordinates: ({self.x}, {self.y})")

        for char in command:
            if char.lower() == 'w':
                self.y += 1
            elif char.lower() == 'a':
                self.x += 1
            elif char.lower() == 's':
                self.y -= 1
            elif char.lower() == 'd':
                self.x -= 1
        log.info(f"current coords: ({self.x}, {self.y})")

    def update(self):
        Canvas().set_all_pixels((10,10,10))
        Canvas().set_pixel(self.x, self.y, self.cur_color)
        for x,y in self.saved_coords:
            Canvas().set_pixel(x, y, self.saved_color)


if __name__ == '__main__':
    controller = Pixel_Navigator()
    controller.run()
