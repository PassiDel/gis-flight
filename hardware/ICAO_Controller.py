import asyncio
import time
from ESP_Controller import ESP_Controller
from FlightRadarConnector import FlightRadarConnector
from model.Canvas import Canvas
# from ESP_Simulator import ESP_Simulator
from Singleton import Singleton
from Logger import Logger as log


class ICAO_Controller(Singleton):
    #first_interval = 20
    update_interval = 0.5
    show_cities = True
    show_planes = True

    @classmethod
    def init(cls):
        cls.esp_controller = ESP_Controller()
        cls.canvas = Canvas()
        log.info("ICAO Controller init")

    async def run(self):
        await self.esp_controller.init()
        await self.esp_controller.set_wait_time(0)
        asyncio.create_task(FlightRadarConnector().start_streaming())
        await self.esp_controller.start()
        while True:
            try:
                Canvas().reset_all_pixels()

                if self.show_planes:
                    planes = FlightRadarConnector().get_planes()
                    #log.info(f"Planes found: {len(planes)}")
                    for plane in planes:
                        plane.print()

                await asyncio.sleep(self.update_interval)
            except KeyboardInterrupt:
                # blocking functions
                Canvas().reset_all_pixels()
                self.esp_controller.empty_update_chain()
                await self.esp_controller.close()
                break


if __name__ == '__main__':
    controller = ICAO_Controller()
    asyncio.run(controller.run())
