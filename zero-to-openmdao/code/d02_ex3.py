import math

g = 9.81
v0 = 100.0                       # launch speed, m/s
angle = math.radians(45)         # convert degrees to radians

x = 0.0
y = 0.0
vx = v0 * math.cos(angle)
vy = v0 * math.sin(angle)
dt = 0.001
max_height = 0.0

while y >= 0:
    x = x + vx * dt
    y = y + vy * dt
    vy = vy - g * dt
    if y > max_height:
        max_height = y

print(f"Range: {x:.1f} m (formula says {v0**2 / g:.1f} m)")
print(f"Max height: {max_height:.1f} m (formula says {v0**2 / (4 * g):.1f} m)")
