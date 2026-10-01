# A ball thrown straight up, simulated in small time steps
g = 9.81       # gravity, m/s^2
h = 0.0        # height, m
v = 30.0       # upward speed, m/s
t = 0.0        # time, s
dt = 0.01      # time step, s

while h >= 0:
    h = h + v * dt      # new height = old height + speed * time step
    v = v - g * dt      # new speed  = old speed  - gravity * time step
    t = t + dt          # move the clock forward

print(f"The ball lands after about {t:.2f} s")
print(f"Exact answer from physics: {2 * 30.0 / g:.2f} s")
