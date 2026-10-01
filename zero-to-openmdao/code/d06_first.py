import numpy as np

h = np.linspace(0, 80000, 9)         # 9 evenly spaced altitudes, 0 to 80 km
rho = 1.225 * np.exp(-h / 8500)      # all 9 densities in ONE line, no loop

print(h)
print(rho)
