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


for v0 in [50.0, 100.0, 200.0]:
    best_angle = 0
    best_range = 0.0
    for angle in range(1, 90):
        r = projectile_range(angle, v0=v0, k=0.001)
        if r > best_range:
            best_range = r
            best_angle = angle
    print(f"v0 = {v0:5.1f} m/s: best angle {best_angle} deg, range {best_range:.1f} m")
