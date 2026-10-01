import math

mu = 3.986e14          # Earth's gravitational parameter, m^3/s^2
R_earth = 6.371e6      # Earth's radius, m
h = 100e3              # altitude, m (100 km)

r = R_earth + h                  # distance from Earth's centre
v_orbit = math.sqrt(mu / r)      # circular orbit speed

print(math.pi)
print(v_orbit)
