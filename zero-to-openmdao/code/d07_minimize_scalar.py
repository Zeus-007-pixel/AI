import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import minimize_scalar

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


def flight_range(angle_deg):
    """Simulate one shot and return the range in metres."""
    a = np.radians(angle_deg)
    start = [0.0, 0.0, 100 * np.cos(a), 100 * np.sin(a)]
    sol = solve_ivp(rates, (0, 100), start, events=hit_ground, rtol=1e-8, atol=1e-8)
    return sol.y[0, -1]


def objective(angle_deg):
    return -flight_range(angle_deg)      # minimise MINUS range = maximise range


result = minimize_scalar(objective, bounds=(1, 89), method="bounded")
print(result.success)
print(f"Best angle: {result.x:.2f} deg")
print(f"Best range: {-result.fun:.1f} m")
