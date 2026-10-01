import math


def density(h_km):
    """Air density in kg/m^3. h_km is altitude in KILOMETRES."""
    return 1.225 * math.exp(-h_km / 8500.0)


print(f"Density at 30 km: {density(30):.4f} kg/m^3")   # should be about 0.0359
