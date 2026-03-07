# test.py
from distanceCalculator import calculate_distance

limit = 0.1 # in km 

entry1 = {
    "location.x": "52.2296756",
    "location.y": "21.0122345"
}
entry2 = {
    "location.x": "52.2300000",
    "location.y": "21.0130000"
}

result = calculate_distance(entry1, entry2)

# print(result)
# result : 0.06354998962889624km
if result < limit:
    print("The two locations are within the limit and are considered the same.")