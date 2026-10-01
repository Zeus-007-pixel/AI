# Should print the total distance of three flight legs
legs_km = [120.5, 98.0, 143.2]
total = 0

for leg in legs_km:
    total = total + leg
    print("leg:", leg, "running total:", total)     # debugging print

print(f"Total distance: {total:.1f} km")
