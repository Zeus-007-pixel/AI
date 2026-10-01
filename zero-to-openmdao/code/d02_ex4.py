import math

g = 9.81
k = 0.001                        # drag constant, 1/m
v0 = 100.0
angle = math.radians(45)

x = 0.0
y = 0.0
vx = v0 * math.cos(angle)
vy = v0 * math.sin(angle)
dt = 0.001

while y >= 0:
    speed = math.sqrt(vx**2 + vy**2)
    ax = -k * speed * vx             # drag slows the horizontal motion
    ay = -g - k * speed * vy         # gravity plus drag in the vertical
    x = x + vx * dt
    y = y + vy * dt
    vx = vx + ax * dt
    vy = vy + ay * dt

print(f"Range with drag: {x:.1f} m")
