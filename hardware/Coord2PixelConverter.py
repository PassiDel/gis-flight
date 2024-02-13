import json
from pyproj import Transformer

from Logger import Logger as log
from Singleton import Singleton
from model.Canvas import Canvas

GEOJSON_FILE = "../src/grid.geojson"
def get_utm_from_geojson(x, y):
    with open(GEOJSON_FILE, 'r') as file:
        geojson = json.load(file)
        for feature in geojson.get('features', []):
            if feature.get('properties', {}).get('x') == x and feature.get('properties', {}).get('y') == y:
                return feature.get('geometry', {}).get('coordinates')[0]
        return None
def extract_epsg():
    with open(GEOJSON_FILE, 'r') as file:
        geojson = json.load(file)
        crs = geojson.get('crs')
        if crs:
            # Extract the name property within the CRS which contains the EPSG code
            crs_name = crs.get('properties', {}).get('name')
            if crs_name and 'EPSG' in crs_name:
                # Extract the EPSG code from the name
                epsg_code = crs_name.split('::')[-1]
                return epsg_code
        return None


class Coord2PixelConverter(Singleton):
    canvas_width = Canvas().get_width()
    canvas_height = Canvas().get_height()

    # get the corners in UTM from geojson files
    _south_west = get_utm_from_geojson(0,0)[0]  # furthest corner is (min, min) UTM
    _north_east = get_utm_from_geojson(canvas_width-1,canvas_height-1)[2]  # furthest corner is (max, max) UTM
    x_min = _south_west[0] #6.45  # long
    x_max = _north_east[0] #11.18  # long
    y_min = _south_west[1] #51.1  # lat
    y_max = _north_east[1] #55.05  # lat

    # get epsg from geojson
    _epsg = extract_epsg()
    log.info(f"Extracted EPSG zone from geojson: {_epsg}")
    # Create a transformer from WGS84 to the extracted UTM zone
    _transformer = Transformer.from_crs("epsg:4326", f"epsg:{_epsg}", always_xy=True)
    _reverse_transformer = Transformer.from_crs(f"epsg:{_epsg}", "epsg:4326", always_xy=True)

    # attributes of the matrix panel (canvas)
    _strip_order = [0, 2, 1, 3, 4, 6, 5, 7, 8, 10, 9]
    _strip_rotations = [1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0]
    _pixels_per_row = 512
    _amount_pixels = 5632

    def convert_latlong2utm(self, lat, long):
        easting, northing = self._transformer.transform(long, lat)
        return easting, northing

    def convert_utm2latlong(self, easting, northing):
        lat, long = self._reverse_transformer.transform(easting, northing)
        return lat, long

    def convert_latlong2xy(self, lat, long, flip=False) -> tuple[int, int]:
        # convert to utm
        easting, northing = self.convert_latlong2utm(lat, long)
        # get x and y on canvas based on UTM
        y_result = round(((northing - self.y_min) * self.canvas_height) / (self.y_max - self.y_min))
        x_result = round(((easting - self.x_min) * self.canvas_width) / (self.x_max - self.x_min))
        y_result = self.canvas_height - y_result
        # check out of bounds
        if 0 > x_result or x_result >= self.canvas_width or 0 > y_result or y_result >= self.canvas_height:
            log.debug(f"Converted xy value out of bounds: ({x_result},{y_result})")
            return -1, -1
        else:
            if flip:
                return self.canvas_width - x_result, self.canvas_height - y_result
            else:
                return x_result, y_result

    def test_lat_long(self, lat, long) -> bool:
        easting, northing = self.convert_latlong2utm(lat, long)
        if self.y_min <= northing <= self.y_max and self.x_min <= easting <= self.x_max:
            return True
        return False

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


