import json
from shapely.geometry import shape, Point
from shapely.ops import nearest_points
import rtree

from Logger import Logger as log
from Singleton import Singleton
from model.Canvas import Canvas

GEOJSON_FILE = "../src/grid.geojson"

class Coord2PixelConverter(Singleton):
    canvas_width = Canvas().get_width()
    canvas_height = Canvas().get_height()

    # initialize the geojson file
    log.info("Parsing geojson file ...")
    with open(GEOJSON_FILE, 'r') as f:
        _geojson = json.load(f)
    # Create spatial index
    _geo_index = rtree.index.Index()
    for idx, feature in enumerate(_geojson['features']):
        geom = shape(feature['geometry'])
        _geo_index.insert(idx, geom.bounds)
    # init the bounds
    x_min, x_max, y_min, y_max = None, None, None, None
    log.info("... geojson parsing done")

    # attributes of the matrix panel (canvas)
    _strip_order = [0, 2, 1, 3, 4, 6, 5, 7, 8, 10, 9]
    _strip_rotations = [1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0]
    _pixels_per_row = 512
    _amount_pixels = 5632

    def get_bounds(self):
        if self.x_min is None:
            north_east = self._get_polygon_points_by_xy(self.canvas_width-1, self.canvas_height-1) # start at 0
            south_west = self._get_polygon_points_by_xy(0,0)
            if north_east is None or south_west is None:
                raise TypeError("Geojson file does not contain polygons that correspond to canvas maxima!")
            self.x_max, self.y_max = north_east[2] # top right corner of polygon
            self.x_min, self.y_min = south_west[0] # bottom left corner of polygon
        return self.x_min, self.y_min, self.x_max, self.y_max

    # Function to find the polygon containing a specific point
    def _find_polygon(self, long, lat):
        point = Point(long, lat)
        for idx in self._geo_index.intersection((long, lat, long, lat)):
            if shape(self._geojson['features'][idx]['geometry']).contains(point):
                return (
                    self._geojson['features'][idx]['properties']['x'],
                    self._geojson['features'][idx]['properties']['y']
                )
        return None

    def _find_closest_polygon(self, long, lat):
        point = Point(long, lat)
        min_distance = None
        closest_polygon = None
        closest_xy = None

        # find the nearest polygon
        for idx in self._geo_index.nearest((long, lat, long, lat), 1):  # Adjust the number of nearest neighbors as needed
            polygon = shape(self._geojson['features'][idx]['geometry'])
            nearest_point = nearest_points(point, polygon)[1]
            distance = point.distance(nearest_point)

            if min_distance is None or distance < min_distance:
                min_distance = distance
                closest_polygon = polygon
                closest_xy = self._geojson['features'][idx]['properties']['x'], self._geojson['features'][idx]['properties']['y']

        log.info(f"Found closest polygon for ({long},{lat}) -> xy:{closest_xy} with distance {min_distance}. {closest_polygon}")
        return closest_xy

    def _get_polygon_points_by_xy(self, x, y):
        for feature in self._geojson['features']:
            if feature['properties'].get('x') == x and feature['properties'].get('y') == y:
                polygon = shape(feature['geometry'])
                # Accessing the exterior coordinates of the polygon
                return list(polygon.exterior.coords)
        return None

    def convert_latlong2xy(self, lat, long) -> tuple[int, int]:
        result = self._find_polygon(long, lat)
        if result is None:
            log.warning(f"Coordinates ({long},{lat}) out of bounds!")
            return -1, -1
            # alternative: get the closest polygon
            # result = self._find_closest_polygon(long, lat)
        x_result, y_result = result
        # flip x sides
        return self.canvas_width-1 - x_result, y_result

    def test_lat_long(self, lat, long) -> bool:
        result = self.convert_latlong2xy(lat, long)
        if result != (-1, -1): return True
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