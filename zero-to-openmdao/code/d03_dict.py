vehicle = {
    "name": "Glider-1",
    "mass": 500.0,       # kg
    "S": 10.0,           # wing area, m^2
    "CD0": 0.02,         # zero-lift drag coefficient
}

print(vehicle["mass"])           # look up a value by its key
vehicle["k"] = 0.1               # add a new key/value pair
vehicle["mass"] = 520.0          # change an existing value
print(vehicle)
print("S" in vehicle)            # is this key in the dictionary?

for key, value in vehicle.items():
    print(key, "=", value)
