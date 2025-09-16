# import json

# with open("data/vehicles.json", "r") as f:
#     old_data = json.load(f)

# new_data = {}

# for vehicle in old_data:
#     owner = vehicle.get("owner", "unknown")
#     vid = str(vehicle.get("id"))

#     vehicle_copy = {k: v for k, v in vehicle.items() if k not in ["owner", "id"]}
#     new_data[owner][vid] = vehicle_copy

# with open("data/vehicles_converted.json", "w") as f:
#     json.dump(new_data, f, indent=4)

