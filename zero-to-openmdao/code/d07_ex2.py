import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

g = 9.81
k = 0.001


def rates(t, state):
    x, y, vx, vy = state
    speed = np.sqrt(vx**2 + vy**2)
    return [vx, vy, -k * speed * vx, -g - k * speed * vy]


def hit_ground(t, state):
    return state[1]


hit_ground.terminal = True
hit_ground.direction = -1

for angle_deg in [20, 30, 45, 60]:
    a = np.radians(angle_deg)
    start = [0.0, 0.0, 100 * np.cos(a), 100 * np.sin(a)]
    sol = solve_ivp(rates, (0, 100), start, events=hit_ground, max_step=0.05)
    plt.plot(sol.y[0], sol.y[1], label=f"{angle_deg}°")
    print(f"{angle_deg} deg: range {sol.y[0, -1]:.1f} m")

plt.xlabel("Downrange (m)")
plt.ylabel("Height (m)")
plt.title("Launch angle comparison (with drag)")
plt.legend()
plt.grid(True)
plt.savefig("angles.png", dpi=150)
plt.show()
