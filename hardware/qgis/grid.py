from qgis.core import QgsProject, QgsRectangle, QgsVectorLayer, QgsFeature, QgsGeometry
from qgis.PyQt.QtCore import QVariant
import itertools
from pyproj import Transformer
import statistics
from math import sin, cos, atan2, radians, degrees

# Define grid dimensions (columns x rows)
grid_dimensions = (64, 88)  # Adjusted to 0-indexed (63,87) as the maximum
wgs84_epsg = "EPSG:4326"
map_epsg = "EPSG:25832"  # LCC:"EPSG:5243"

# Define cities with x, y (grid coordinates) and longitude, latitude
# long, lat from https://www.findlatitudeandlongitude.com/find-latitude-and-longitude-from-address/
cities = {
    "Dingelstädt": {"x": 53, "y": 5, "lat": 51.31556, "long": 10.31944},
    "Holzheim": {"x": 2, "y": 1, "lat": 51.161296, "long": 6.668334},
    "Neede": {"x": 2, "y": 23, "lat": 52.135029, "long": 6.611339},
    "Juist": {"x": 8, "y": 57, "lat": 53.678448, "long": 6.995608},
    "List": {"x": 27, "y": 87, "lat": 55.01774, "long": 8.435997},
    "Puttgarden": {"x": 63, "y": 76, "lat": 54.496498, "long": 11.212112},
    "Wittenburg": {"x": 62, "y": 54, "lat": 53.5, "long": 11.067},
    "Grasleben": {"x": 62, "y": 27, "lat": 52.307238, "long": 11.015511},
    "Petershagen": {"x": 34, "y": 28, "lat": 52.383, "long": 8.967},
    "Hochdonn": {"x": 38, "y": 65, "lat": 54.023203, "long": 9.287125},
}

# Transformer for coordinate conversion
# EPSG:5243 is given in Easting, Northing which corresponds to x and y coordinate
transformer = Transformer.from_crs(wgs84_epsg, map_epsg, always_xy=True)

# Convert geographic coordinates to LCC
for city, data in cities.items():
    data['utm_x'], data['utm_y'] = transformer.transform(data['long'], data['lat'])

# Function to calculate the distance and angle between two points in both systems
def calculate_distance_and_angle(city1, city2):
    # Projected coordinate system differences
    utm_x_distance = abs(city1['utm_x'] - city2['utm_x'])
    utm_y_distance = abs(city1['utm_y'] - city2['utm_y'])
    # Grid coordinate system differences
    grid_x_distance = abs(city1['x'] - city2['x'])
    grid_y_distance = abs(city1['y'] - city2['y'])
    
    # Calculate distances
    proj_distance = (utm_x_distance**2 + utm_y_distance**2)**0.5
    grid_distance = (grid_x_distance**2 + grid_y_distance**2)**0.5
    
    # Calculate angles in radians and convert to degrees
    proj_angle = degrees(atan2(utm_y_distance, utm_x_distance))
    grid_angle = degrees(atan2(grid_y_distance, grid_x_distance))
    
    # Calculate rotation angle
    rotation_angle = proj_angle - grid_angle
    
    return proj_distance, grid_distance, rotation_angle

# Function to calculate mean spacing and mean rotation angle
def calculate_mean_spacing_and_rotation(cities):
    cosines = []
    sines = []
    spacings = []
    total_pairs = 0
    
    for (name1, city1), (name2, city2) in itertools.combinations(cities.items(), 2):
        proj_distance, grid_distance, rotation_angle = calculate_distance_and_angle(city1, city2)
        if grid_distance != 0:
            spacing = proj_distance / grid_distance
            spacings.append(spacing)
            # Convert angle to radians for trigonometric functions
            angle_rad = radians(rotation_angle)
            cosines.append(cos(angle_rad))
            sines.append(sin(angle_rad))
            total_pairs += 1
            print(f"{name1}-{name2} spacing:{spacing} sin={sin(angle_rad)} cos={cos(angle_rad)}")
    
    mean_spacing = statistics.mean(spacings)
    # Calculate mean angle from vectors
    mean_cosine = statistics.mean(cosines)
    mean_sine = statistics.mean(sines)
    mean_rotation_angle = degrees(atan2(mean_sine, mean_cosine))

    print(f"Mean: spacing={mean_spacing} angle={mean_rotation_angle} pairs={total_pairs}")
    print(f"Spacing: min={min(spacings)} max={max(spacings)} st_dev={statistics.stdev(spacings)}")
    
    return mean_spacing, mean_rotation_angle

# Function to check if a grid cell corresponds to a city
def is_calibration_cell(x, y, cities):
    for city in cities.values():
        if city['x'] == x and city['y'] == y:
            return True
    return False

# Function to rotate a point around another point by a given angle
def rotate_point(origin, point, angle):
    angle_rad = radians(angle)
    ox, oy = origin
    px, py = point

    qx = ox + cos(angle_rad) * (px - ox) - sin(angle_rad) * (py - oy)
    qy = oy + sin(angle_rad) * (px - ox) + cos(angle_rad) * (py - oy)
    return qx, qy

# calculate mean spacing from all the cities
mean_spacing, mean_rotation_angle = calculate_mean_spacing_and_rotation(cities)

# Create a memory layer to store the grid
grid_layer = QgsVectorLayer(f"Polygon?crs={map_epsg}", "GridLayer", "memory")
provider = grid_layer.dataProvider()
provider.addAttributes([QgsField("id", QVariant.Int), QgsField("x", QVariant.Int), QgsField("y", QVariant.Int), QgsField("calibration", QVariant.Bool)])
grid_layer.updateFields()

# pick the most middle city to make calculations from, so errors are highest on the edges
origin_city = cities["Petershagen"]
# Use the origin city's UTM coordinates as the rotation origin
origin_x, origin_y = origin_city['utm_x'], origin_city['utm_y']

# Calculate the lower left corner of the grid based on the origin city
min_utm_x = origin_city['utm_x'] - origin_city['x'] * mean_spacing
min_utm_y = origin_city['utm_y'] - origin_city['y'] * mean_spacing
print(f"minimum UTM: x={min_utm_x} y={min_utm_y}")

# Create grid cells and add to the layer
id = 0
for x in range(grid_dimensions[0]):
    for y in range(grid_dimensions[1]):
        # Calculate the center of the rectangle without rotation
        center_x = min_utm_x + x * mean_spacing
        center_y = min_utm_y + y * mean_spacing

        # Rotate the center point around the origin city
        rotated_center_x, rotated_center_y = rotate_point((origin_x, origin_y), (center_x, center_y), mean_rotation_angle)
        # print(f"rotated {center_x},{center_y} to {rotated_center_x},{rotated_center_y}")
        
        # Offset the corners from the rotated center to create the rectangle
        rect = QgsRectangle(
            rotated_center_x - mean_spacing / 2,
            rotated_center_y - mean_spacing / 2,
            rotated_center_x + mean_spacing / 2,
            rotated_center_y + mean_spacing / 2
        )

        # Create and add the feature as before
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromRect(rect))
        calibration_flag = is_calibration_cell(x, y, cities)
        feature.setAttributes([id, x, y, calibration_flag])
        provider.addFeature(feature)
        id += 1

grid_layer.updateExtents()
QgsProject.instance().addMapLayer(grid_layer)