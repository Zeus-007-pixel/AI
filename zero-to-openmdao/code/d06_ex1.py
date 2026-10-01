import numpy as np

h = np.arange(0, 100001, 1000)          # 0 to 100 km in 1 km steps
rho = 1.225 * np.exp(-h / 8500)

thin = rho < 1e-3                        # True where the air is very thin
first = np.argmax(thin)                  # index of the first True
print(f"Density drops below 0.001 kg/m^3 at {h[first] / 1000:.0f} km")
print(f"{np.sum(thin)} of the {h.size} altitudes are that thin")
