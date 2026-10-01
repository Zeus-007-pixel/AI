import numpy as np

mach_table = np.array([2.0, 4.0, 6.0, 8.0, 10.0])
CLa_table = np.array([2.5, 2.0, 1.7, 1.6, 1.55])     # per radian

for mach in [5.0, 7.3]:
    CLa = np.interp(mach, mach_table, CLa_table)
    print(f"Mach {mach}: CL_alpha = {CLa:.3f} per rad")
