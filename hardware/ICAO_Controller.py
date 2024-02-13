import time

from ESP_Controller import ESP_Controller
from FlightRadarConnector import FlightRadarConnector
from model.Canvas import Canvas
# from ESP_Simulator import ESP_Simulator
from Singleton import Singleton
from Logger import Logger as log


class ICAO_Controller(Singleton):
    first_interval = 20
    update_interval = 5
    last_update = 0
    show_cities = True
    show_planes = True

    @classmethod
    def init(cls):
        cls.esp_controller = ESP_Controller()
        cls.canvas = Canvas()
        log.info("Controller init")

    def run(self):
        counter = 0
        while True:
            try:
                interval = self.first_interval if counter < 2 else self.update_interval
                if time.time() - self.last_update >= interval:
                    log.info(f"Starting data retrieval n°{counter+1}")
                    self.update()
                    self.last_update = time.time()
                    counter += 1
                self.esp_controller.loop()
                # time.sleep(0.5)
            except KeyboardInterrupt:
                Canvas().reset_all_pixels()
                self.esp_controller.empty_update_chain()
                self.esp_controller.close()

    def update(self):
        Canvas().reset_all_pixels()

        # Canvas().set_all_pixels((30,30,30))

        if self.show_planes:
            planes = FlightRadarConnector().get_planes()
            log.info(f"Planes found: {len(planes)}")
            for plane in planes:
                plane.print()


if __name__ == '__main__':
    controller = ICAO_Controller()
    controller.run()
