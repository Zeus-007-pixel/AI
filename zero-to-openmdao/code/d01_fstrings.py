import math

mu = 3.986e14
R_earth = 6.371e6
h = 100e3
v_orbit = math.sqrt(mu / (R_earth + h))

print(f"Orbit speed: {v_orbit} m/s")
print(f"Orbit speed: {v_orbit:.1f} m/s")
print(f"Orbit speed: {v_orbit / 1000:.2f} km/s")
print(f"Altitude {h / 1000:.0f} km gives {v_orbit:.0f} m/s")
