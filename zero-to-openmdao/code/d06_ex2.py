import numpy as np

alpha_deg = np.linspace(0, 20, 201)       # 0, 0.1, 0.2, ... 20 degrees
alpha = np.radians(alpha_deg)
CL = 4.0 * alpha
CD = 0.02 + 0.1 * CL**2
LD = CL / CD

i = np.argmax(LD)
print(f"Best L/D = {LD[i]:.2f} at alpha = {alpha_deg[i]:.1f} deg (CL = {CL[i]:.3f})")
