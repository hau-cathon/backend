from geopy.distance import geodesic

import json

def calculate_distance(loc1, loc2):
    # First location
    cords_x1 = float(loc1['location.x'])
    cords_y1 = float(loc1['location.y'])
    coords_1 = (cords_x1, cords_y1)

    # Second location
    cords_x2 = float(loc2['location.x'])
    cords_y2 = float(loc2['location.y'])
    coords_2 = (cords_x2, cords_y2)

    # Calculate distance between two points
    distance = geodesic(coords_1, coords_2).km

    return distance