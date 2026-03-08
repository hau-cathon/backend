from geopy.distance import geodesic

def calculate_distance(loc1, loc2):
    # First location
    cords_x1 = float(loc1['x'])
    cords_y1 = float(loc1['y'])
    coords_1 = (cords_x1, cords_y1)

    # Second location
    cords_x2 = float(loc2['x'])
    cords_y2 = float(loc2['y'])
    coords_2 = (cords_x2, cords_y2)

    # Calculate distance between two points
    distance = geodesic(coords_1, coords_2).km

    return distance