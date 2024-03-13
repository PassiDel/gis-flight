from model.Canvas import Canvas
from Coord2PixelConverter import Coord2PixelConverter
from model.Pixel import Pixel
from Singleton import Singleton
from Logger import Logger as log

import asyncio
import serial_asyncio
import time
import platform


class ESP_Controller(Singleton):
    # SETTINGS
    MSG_SENDING_DELAY = 0.006 # seconds
    print_updated_pixels_every = 5
    wait_for_ESP_response = 2  # seconds
    check_pixels_to_be_updated_every = 1 # seconds
    # SETTINGS END
    updated_pixel_counter = 0
    last_ESP_response = time.time()
    pixels_to_be_updated = []
    tasks = []

    @classmethod
    async def init(cls):
        # init serial connection based on system (mac or raspberry)
        if platform.system() == "Darwin":
            log.info("Serial in Mac usage")
            cls.reader, cls.writer = await serial_asyncio.open_serial_connection(url='/dev/cu.usbserial-0001', baudrate=460800)
        else:
            cls.reader, cls.writer = await serial_asyncio.open_serial_connection(url='/dev/serial0', baudrate=460800) # hardware serial via GPIO 14 and 15
        log.info("Serial connection established, waiting for setup")
        await asyncio.sleep(0.5)  # Use asyncio.sleep for non-blocking sleep

    async def start(self):
        # Start background tasks
        self.tasks.append(asyncio.create_task(self.get_serial_messages()))
        self.tasks.append(asyncio.create_task(self.get_pixels_to_be_updated()))
        self.tasks.append(asyncio.create_task(self.update_pixels()))
        self.tasks.append(asyncio.create_task(self.print_update_infos()))
        log.info("Started ESP background tasks")

    # # # TASKS # # #

    async def get_serial_messages(self):
        # Check if there is any data available to read
        try:
            while True:
                # Await a newline-terminated line from the serial port
                # Adjust the byte limit as necessary for your application
                line = await self.reader.readline()
                if line:
                    message = line.decode('utf-8').rstrip()  # Decode and strip newline
                    log.debug(f"Serial received: {message}")
                    self.last_ESP_response = time.time()
        except asyncio.CancelledError:
            log.info("Serial read task cancelled")
        except Exception as e:
            log.error(f"Error reading serial messages: {e}")

    async def get_pixels_to_be_updated(self):
        try:
            while True:
                self.pixels_to_be_updated = Canvas().get_pixels_with_update_pending()
                await asyncio.sleep(self.check_pixels_to_be_updated_every)
        except asyncio.CancelledError:
            log.info("Pixels to be updated task cancelled")

    async def update_pixels(self):
        try:
            while True:
                # check if pixels need to be updated
                if len(self.pixels_to_be_updated) > 0:
                    await self._set_pixel(self.pixels_to_be_updated[0])  # only set one pixel
                    self.pixels_to_be_updated.pop(0)  # remove from the queue
                    self.updated_pixel_counter += 1
                await asyncio.sleep(self.MSG_SENDING_DELAY)
        except asyncio.CancelledError:
            log.info("Update Pixels task cancelled")

    async def print_update_infos(self):
        try:
            while True:
                # print the amount of updated pixels
                log.info(f"Updated {self.updated_pixel_counter} pixels in {self.print_updated_pixels_every} seconds. Still in queue: {len(self.pixels_to_be_updated)}")
                self.updated_pixel_counter = 0
                await asyncio.sleep(self.print_updated_pixels_every)
        except asyncio.CancelledError:
            log.info("Update Info task cancelled")
            pass

    # # # HELPER FUNCTIONS # # #

    async def _set_pixel(self, pixel:Pixel):
        index = Coord2PixelConverter().convert_xy2strip_index(pixel.x, pixel.y)
        await self._send_set_pixel(index, pixel.target_color[0], pixel.target_color[1], pixel.target_color[2])
        pixel.updated()

    async def _send_serial(self, command):
        self.writer.write(command.encode("utf-8"))
        await self.writer.drain()
        log.debug(f"Sent serial: '{command.strip()}'")

    async def _send_set_pixel(self, pixel_index, r, g, b):
        command = f"{int(pixel_index)},{r},{g},{b}\\n"
        await self._send_serial(command)

    async def set_wait_time(self, wait_time_ms):
        command = f"W {int(wait_time_ms)}\\n"
        await asyncio.sleep(self.MSG_SENDING_DELAY)
        await self._send_serial(command)

    async def clear_canvas(self):
        await self._send_serial(f"C\\n")

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

    async def close(self):
        for task in self.tasks:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    log.info("Task cancelled.")
        self.writer.close()
        await self.writer.wait_closed()
        log.info("Closed serial connection")
