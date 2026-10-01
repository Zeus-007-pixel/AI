import math


def projectile_range(angle_deg, v0=100.0, k=0.0):
    """Simulate a projectile and return how far it flies, in metres."""
    g = 9.81
    angle = math.radians(angle_deg)
    x, y = 0.0, 0.0
    vx = v0 * math.cos(angle)
    vy = v0 * math.sin(angle)
    dt = 0.001
    while y >= 0:
        speed = math.sqrt(vx**2 + vy**2)
        x = x + vx * dt
        y = y + vy * dt
        vx = vx - k * speed * vx * dt
        vy = vy - (g + k * speed * vy) * dt
    return x


best_angle = 0
best_range = 0.0

for angle in range(1, 90):               # try 1, 2, ..., 89 degrees
    r = projectile_range(angle, k=0.001)
    if r > best_range:                   # better than anything so far?
        best_range = r
        best_angle = angle

print(f"Best angle with drag: {best_angle} deg, range {best_range:.1f} m")
print(f"Without drag, 45 deg gives {projectile_range(45):.1f} m")
