import math

altitudes_km = [0, 10, 20, 30, 40]

for h_km in altitudes_km:
    h = h_km * 1000                      # convert km to m
    rho = 1.225 * math.exp(-h / 8500)    # air density, kg/m^3
    print(f"{h_km} km -> {rho:.4f} kg/m^3")

print("Done")
