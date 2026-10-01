import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

g = 9.81       # gravity, m/s^2
k = 0.001      # drag constant, 1/m


def rates(t, state):
    """Return how fast each part of the state changes."""
    x, y, vx, vy = state
    speed = np.sqrt(vx**2 + vy**2)
    return [vx, vy, -k * speed * vx, -g - k * speed * vy]


def hit_ground(t, state):
    return state[1]               # the height; the event fires when it reaches 0


hit_ground.terminal = True        # stop the simulation when the event fires
hit_ground.direction = -1         # only when height is going DOWN through 0

angle = np.radians(45)
start = [0.0, 0.0, 100 * np.cos(angle), 100 * np.sin(angle)]   # x, y, vx, vy

sol = solve_ivp(rates, (0, 100), start, events=hit_ground, max_step=0.05)

x = sol.y[0]          # row 0 of the answer = x at every time
y = sol.y[1]          # row 1 = y at every time
print(f"Flight time: {sol.t[-1]:.2f} s, range: {x[-1]:.1f} m")

plt.plot(x, y)
plt.xlabel("Downrange (m)")
plt.ylabel("Height (m)")
plt.title("Projectile with drag, 45° launch")
plt.axis("equal")
plt.grid(True)
plt.savefig("projectile.png", dpi=150)
plt.show()
