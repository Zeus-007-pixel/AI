import numpy as np

rho = 1.225
S = 10.0
CLa = 4.0
W = 4905.0

for v in [40.0, 50.0, 80.0, 120.0]:
    q = 0.5 * rho * v**2
    alpha = W / (q * S * CLa)          # from L = q*S*CLa*alpha = W
    print(f"v = {v:5.1f} m/s -> alpha = {np.degrees(alpha):6.3f} deg (hand calculation)")
