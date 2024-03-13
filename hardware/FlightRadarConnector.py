import logging
from datetime import datetime, timedelta
import requests, json
import asyncio
import aiohttp

from Singleton import Singleton
from Coord2PixelConverter import Coord2PixelConverter as coords
from model.Plane import Plane
from Logger import Logger as log

class FlightRadarConnector(Singleton):
    delete_after_sec = 60
    exclude_aircraft_types = ["GLID"]
    retry_after_connection_lost_sec = 10

    @classmethod
    def init(cls):
        cls.planes: list[Plane] = []

    def get_bounds_str(self):
        x_min, y_min, x_max, y_max = coords().get_bounds()
        return f"{y_max},{y_min},{x_min},{x_max}"

    async def start_streaming(self):
        # start the asyncronous stream
        await self._read_sse_stream("http://localhost:3000/api/sse")
        log.info("Started flights SSE stream")

    async def _parse_planes(self, json_data):
        for data in json_data:
            found_match = False
            for plane in self.planes:
                if plane.update_if_match(data):
                    found_match = True
                    break
            if not found_match:
                new = Plane(data)
                if new.x > -1 and new.aircraft_type not in self.exclude_aircraft_types:
                    log.info(f"Added new Plane: {new}")
                    self.planes.append(new)
        # delete planes that are not on the canvas anymore or havent been updated
        for plane in self.planes:
            if plane.x == -1 or plane.y == -1:
                log.warning(f"Removing out of bounds {plane}")
                self.planes.remove(plane)
                continue
            if (datetime.now() - plane.last_update).total_seconds() > self.delete_after_sec:
                log.warning(f"Removing timeout {plane}")
                self.planes.remove(plane)

    def get_planes(self):
        return self.planes

    async def _read_sse_stream(self, url):
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        async for line in response.content:
                            if line:
                                data = line.decode('utf-8')
                                if data.startswith('data:'):
                                    json_data = json.loads(data.replace('data: ', ''))
                                    await self._parse_planes(json_data)
                break  # Exit the loop if connection is successful
            except aiohttp.client_exceptions.ClientConnectorError:
                log.error(f"Connection failed, retrying in {self.retry_after_connection_lost_sec} seconds...")
                await asyncio.sleep(self.retry_after_connection_lost_sec)

