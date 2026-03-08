import random
import json
from datetime import datetime, timedelta

TYPES = ["stray", "traffic accident", "abuse", "other"]
CITIES = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]
STREETS = ["Main Street", "Broadway", "Park Avenue", "Central Park", "5th Avenue", "Madison Avenue"]
SPECIES = ["dog", "cat", "bird", "rabbit", "squirrel", "parrot", "puppy", "kitten"]

entries = []

for i in range(1, 1001):
    entry = {
        "id": i,
        "type": random.choice(TYPES),
        "species": random.choice(SPECIES),
        "amount_of_animals": random.randint(1, 5),
        "description": f"Random description {i}",
        "urgency": random.choice([True, False]),
        "location.x": round(random.uniform(10.0, 11.0), 3),
        "location.y": round(random.uniform(20.0, 21.5), 3),
        "city": random.choice(CITIES),
        "street": random.choice(STREETS),
        "number": random.randint(1, 500),
        "zip_code": f"{random.randint(10000, 10005)}",
        "additional_info": f"Additional info {i}",
        "timestamp": (datetime(2023, 10, 10) + timedelta(minutes=i)).isoformat() + "Z",
        "contact_info": {
            "name": f"Person {i}",
            "phone": f"+1-555-{random.randint(1000,9999)}"
        }
    }
    entries.append(entry)

with open("random_entries.txt", "w") as f:
    for entry in entries:
        f.write(json.dumps(entry) + "\n")
