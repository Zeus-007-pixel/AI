import numpy as np

h_km = np.arange(0, 81, 10)
rho = 1.225 * np.exp(-h_km * 1000 / 8500)
print(rho)
