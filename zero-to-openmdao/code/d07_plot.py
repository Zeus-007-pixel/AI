import numpy as np
import matplotlib.pyplot as plt

h = np.linspace(0, 80000, 200)       # 200 altitudes for a smooth curve
rho = 1.225 * np.exp(-h / 8500)

plt.plot(rho, h / 1000)              # x values first, then y values
plt.xlabel("Density (kg/m³)")
plt.ylabel("Altitude (km)")
plt.title("Exponential atmosphere")
plt.grid(True)
plt.savefig("density.png", dpi=150)  # save a picture file
plt.show()                           # open a window with the plot
