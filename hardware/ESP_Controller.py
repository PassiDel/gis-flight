from model.Canvas import Canvas
from Coord2PixelConverter import Coord2PixelConverter
from model.Pixel import Pixel
from Singleton import Singleton
from Logger import Logger as log

import serial
import time
import platform


class ESP_Controller(Singleton):
    # SETTINGS
    MSG_SENDING_DELAY = 0.006 # seconds
    print_updated_pixels_every = 5
    wait_for_ESP_response = 2  # seconds
    check_pixels_to_be_updated_every = 1 # seconds
    # SETTINGS END
    last_sending = time.time()
    last_update = 0
    last_pixel_update = 0
    updated_pixel_counter = 0
    last_ESP_response = time.time()
    pixels_to_be_updated = []

    @classmethod
    def init(cls):
        # init serial connection based on system (mac or raspberry)
        if platform.system() == "Darwin":
            log.info("Serial in Mac usage")
            cls.connection = serial.Serial('/dev/cu.usbserial-0001', 460800)
        else:
            cls.connection = serial.Serial('/dev/serial0', 460800)  # hardware serial via GPIO 14 and 15
        log.info("Serial connection established, waiting for setup")
        time.sleep(0.5)

    def loop(self):
        self._get_serial_messages()
        if time.time() - self.last_pixel_update >= self.check_pixels_to_be_updated_every or len(self.pixels_to_be_updated) == 0:
            self.pixels_to_be_updated = Canvas().get_pixels_with_update_pending()
            self.last_pixel_update = time.time()
        # check if pixels need to be updated and wait time is
        if len(self.pixels_to_be_updated) > 0 and time.time() - self.last_sending >= self.MSG_SENDING_DELAY:
            self._set_pixel(self.pixels_to_be_updated[0])  # only set one pixel
            self.pixels_to_be_updated.pop(0)  # remove from the queue
            self.updated_pixel_counter += 1
            self.last_sending = time.time()
        # print the amount of updated pixels
        if time.time() - self.last_update >= self.print_updated_pixels_every:
            log.info(f"Updated {self.updated_pixel_counter} pixels in {self.print_updated_pixels_every} seconds. Still in queue: {len(self.pixels_to_be_updated)}")
            self.updated_pixel_counter = 0
            self.last_update = time.time()

    def _set_pixel(self, pixel:Pixel):
        index = Coord2PixelConverter().convert_xy2strip_index(pixel.x, pixel.y)
        self._send_set_pixel(index, pixel.target_color[0], pixel.target_color[1], pixel.target_color[2])
        pixel.updated()

    def _send_serial(self, command):
        self.connection.write(command.encode("utf-8"))
        log.debug(f"Sent serial: '{command.strip()}'")

    def _send_set_pixel(self, pixel_index, r, g, b):
        command = f"{int(pixel_index)},{r},{g},{b}\\n"
        self._send_serial(command)

    def set_wait_time(self, wait_time_ms):
        command = f"W {int(wait_time_ms)}\\n"
        time.sleep(self.MSG_SENDING_DELAY)
        self._send_serial(command)

    def clear_canvas(self):
        self._send_serial(f"C\\n")

    def _get_serial_messages(self):
        # Check if there is any data available to read
        while self.connection.in_waiting > 0:
            # Read the available data and print it
            data = self.connection.readline().decode('utf-8').strip()
            log.debug(f"Serial received: {data}")
            self.last_ESP_response = time.time()

    def esp_busy(self) -> bool:
        # is determined based on the last message from the ESP
        busy = (time.time() - self.last_ESP_response) <= self.wait_for_ESP_response
        #log.info(f"busy {busy}")
        return busy

    def empty_update_chain(self):
        log.info("Clearing canvas ...")
        time.sleep(self.MSG_SENDING_DELAY)
        self.clear_canvas()
        Canvas().reset_all_pixels()
        pixels_to_be_updated = Canvas().get_pixels_with_update_pending()
        while len(self.pixels_to_be_updated) > 0:
            self._set_pixel(pixels_to_be_updated[0])  # only set one pixel
            pixels_to_be_updated.pop(0)
            time.sleep(self.MSG_SENDING_DELAY)
        log.info("Clearing done!")

    def close(self):
        self.connection.close()
        log.info("Closed serial connection")
