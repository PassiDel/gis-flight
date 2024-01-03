from qgis.core import QgsProject, QgsRectangle, QgsVectorLayer, QgsFeature, QgsGeometry
from qgis.PyQt.QtCore import QVariant
import itertools
from pyproj import Transformer


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
transformer = Transformer.from_crs("EPSG:4326", "EPSG:25832", always_xy=True)

# Convert geographic coordinates to UTM
for city, data in cities.items():
    data['utm_x'], data['utm_y'] = transformer.transform(data['long'], data['lat'])

# Function to calculate the distance between two points in grid space
def calculate_distance(city1, city2):
    utm_x_distance = abs(city1['utm_x'] - city2['utm_x'])
    utm_y_distance = abs(city1['utm_y'] - city2['utm_y'])
    grid_x_distance = abs(city1['x'] - city2['x'])
    grid_y_distance = abs(city1['y'] - city2['y'])
    return utm_x_distance, utm_y_distance, grid_x_distance, grid_y_distance

# Function to calculate mean spacing
def calculate_mean_spacing(cities):
    total_x_spacing, total_y_spacing, total_pairs = 0, 0, 0

    for (name1, city1), (name2, city2) in itertools.combinations(cities.items(), 2):
        x_dist, y_dist, grid_x_dist, grid_y_dist = calculate_distance(city1, city2)
        
        # Avoid division by zero for cities at the same grid position
        if grid_x_dist != 0 and grid_y_dist != 0:
            x_spacing = x_dist / grid_x_dist
            y_spacing = y_dist / grid_y_dist
            print(f"{name1}-{name2} x={x_spacing} y={y_spacing}")
            total_x_spacing += x_spacing
            total_y_spacing += y_spacing
            total_pairs += 1

    mean_x_spacing = total_x_spacing / total_pairs
    mean_y_spacing = total_y_spacing / total_pairs
    print(f"Mean: x={x_spacing} y={y_spacing}")
    
    return mean_x_spacing, mean_y_spacing

# Define grid dimensions (columns x rows)
grid_dimensions = (64, 88)  # Adjusted to 0-indexed (63,87) as the maximum

# calculate mean spacing from all the cities
x_spacing, y_spacing = calculate_mean_spacing(cities)

# Create a memory layer to store the grid
grid_layer = QgsVectorLayer(f"Polygon?crs=EPSG:25832", "GridLayer", "memory")
provider = grid_layer.dataProvider()
provider.addAttributes([QgsField("id", QVariant.Int), QgsField("x", QVariant.Int), QgsField("y", QVariant.Int), QgsField("calibration", QVariant.Bool)])
grid_layer.updateFields()

# pick the most middle city to make calculations from, so errors are highest on the edges
origin_city = cities["Petershagen"]

# Calculate the lower left corner of the grid based on the origin city
min_utm_x = origin_city['utm_x'] - origin_city['x'] * x_spacing
min_utm_y = origin_city['utm_y'] - origin_city['y'] * y_spacing

# Function to check if a grid cell corresponds to a city
def is_calibration_cell(x, y, cities):
    for city in cities.values():
        if city['x'] == x and city['y'] == y:
            return True
    return False

# Create grid cells and add to the layer
id = 0
for x in range(grid_dimensions[0]):
    for y in range(grid_dimensions[1]):
        # Calculate the center of the rectangle
        center_x = min_utm_x + x * x_spacing
        center_y = min_utm_y + y * y_spacing

        # Offset the corners from the center
        rect = QgsRectangle(
            center_x - x_spacing / 2,
            center_y - y_spacing / 2,
            center_x + x_spacing / 2,
            center_y + y_spacing / 2
        )

        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromRect(rect))
        #y_corrected = grid_dimensions[1] - y
        calibration_flag = is_calibration_cell(x, y, cities)
        feature.setAttributes([id, x, y, calibration_flag])
        provider.addFeature(feature)
        id += 1

grid_layer.updateExtents()
QgsProject.instance().addMapLayer(grid_layer)