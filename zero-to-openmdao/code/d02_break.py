import math

for h_km in range(0, 101, 5):
    rho = 1.225 * math.exp(-h_km * 1000 / 8500)
    if rho < 0.01:
        print(f"Density first drops below 0.01 kg/m^3 at {h_km} km")
        break                    # leave the loop immediately
