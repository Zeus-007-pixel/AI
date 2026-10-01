import numpy as np

h = np.arange(0, 30001, 10000)
rho = 1.225 * np.exp(-h / 8500)

table = np.column_stack([h, rho])            # glue two columns side by side
np.savetxt("rho_table.csv", table, delimiter=",", header="h_m,rho", comments="")

data = np.loadtxt("rho_table.csv", delimiter=",", skiprows=1)
print(data)
print(data[:, 1])                            # the density column
