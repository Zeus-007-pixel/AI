import numpy as np

# rows = Mach numbers, columns = angles of attack
CL_table = np.array([
    [0.10, 0.20, 0.30],     # Mach 2
    [0.08, 0.17, 0.26],     # Mach 4
    [0.07, 0.15, 0.23],     # Mach 6
])

print(CL_table.shape)       # (rows, columns)
print(CL_table[1, 2])       # row 1, column 2
print(CL_table[0, :])       # all of row 0
print(CL_table[:, 1])       # all of column 1
