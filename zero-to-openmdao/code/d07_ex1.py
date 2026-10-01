import numpy as np
import matplotlib.pyplot as plt

h = np.linspace(0, 100000, 300)
rho = 1.225 * np.exp(-h / 8500)

plt.plot(rho, h / 1000)
plt.xscale("log")                    # logarithmic x-axis
plt.xlabel("Density (kg/m³, log scale)")
plt.ylabel("Altitude (km)")
plt.title("Exponential atmosphere, 0–100 km")
plt.grid(True)
plt.savefig("density_log.png", dpi=150)
plt.show()
