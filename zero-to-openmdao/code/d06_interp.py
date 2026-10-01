import numpy as np

alpha_table = np.array([0.0, 5.0, 10.0, 15.0, 20.0])     # deg
CL_table = np.array([0.00, 0.18, 0.37, 0.52, 0.61])      # lift coefficient

print(np.interp(7.5, alpha_table, CL_table))              # one value

alphas = np.array([2.0, 7.5, 12.0])
print(np.interp(alphas, alpha_table, CL_table))           # many values at once
