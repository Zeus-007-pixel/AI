import math

mu = 3.986e14
R_earth = 6.371e6
h = 400e3                    # ISS altitude, m

v = math.sqrt(mu / (R_earth + h))
period = 2 * math.pi * (R_earth + h) / v     # time for one orbit, s

print(f"Speed: {v:.0f} m/s")
print(f"One orbit takes {period / 60:.1f} minutes")
