from model.Canvas import Canvas
from Coord2PixelConverter import Coord2PixelConverter
from model.Pixel import Pixel
from Singleton import Singleton
from Logger import Logger as log

import serial
import time
import platform

class ESP_Controller(Singleton):

    MSG_SENDING_DELAY = 0.0025  # seconds
    last_sending = time.time()
    print_updated_pixels_every = 5
    last_update = 0
    updated_pixel_counter = 0

    @classmethod
    def init(cls):
        # self.connectionial init
        if platform.system() == "Darwin":
            log.info("Serial in Mac usage")
            cls.connection = serial.Serial('/dev/cu.usbserial-0001', 460800)
        else:
            cls.connection = serial.Serial('/dev/ttyUSB0', 460800)
        log.info("Serial connection established, waiting for setup")
        time.sleep(0.5)

    def loop(self):
        self._get_serial_messages()
        update_pixels = Canvas().get_pixels_with_update_pending()
        if len(update_pixels) > 0 and time.time() - self.last_sending >= self.MSG_SENDING_DELAY:
            self._set_pixel(update_pixels[0])  # only set one pixel
            self.updated_pixel_counter += 1
            self.last_sending = time.time()
        if time.time() - self.last_update >= self.print_updated_pixels_every:
            log.info(f"Updated {self.updated_pixel_counter} pixels in {self.print_updated_pixels_every} seconds")
            self.updated_pixel_counter = 0
            self.last_update = time.time()

    def _set_pixel(self, pixel:Pixel):
        index = Coord2PixelConverter().convert_xy2strip_index(pixel.x, pixel.y)
        self._send_set_pixel(index, pixel.target_color[0], pixel.target_color[1], pixel.target_color[2])
        pixel.updated()

    def _send_set_pixel(self, pixel_index, r, g, b):
        # time.sleep(self.MSG_SENDING_DELAY)
        command = f"{int(pixel_index)},{r},{g},{b}\\n"
        self.connection.write(command.encode("utf-8"))
        log.debug(f"Sent serial: '{command.strip()}'")

    def _get_serial_messages(self):
        # Check if there is any data available to read
        while self.connection.in_waiting > 0:
            # Read the available data and print it
            data = self.connection.readline().decode('utf-8').strip()
            log.debug(f"Serial received: {data}")

    def empty_update_chain(self):
        log.info("Emptying update chain ...")
        while len(Canvas().get_pixels_with_update_pending()) > 0:
            self.loop()
        log.info("Update chain empty!")

    def close(self):
        self.connection.close()
        log.info("Closed serial connection")
