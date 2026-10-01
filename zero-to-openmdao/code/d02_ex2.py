import math

rho0 = 1.225
densities = []

for h_km in range(0, 81, 10):
    rho = rho0 * math.exp(-h_km * 1000 / 8500)
    densities.append(rho)
    print(f"{h_km:2d} km: {rho:.6f} kg/m^3")

for h_km in range(0, 81, 1):
    rho = rho0 * math.exp(-h_km * 1000 / 8500)
    if rho < 0.01 * rho0:
        print(f"Below 1% of sea-level density from {h_km} km")
        break
