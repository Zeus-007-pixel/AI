import math


def glide_ratio(CL, CD0=0.02, k=0.1):
    """Lift-to-drag ratio for a simple drag polar CD = CD0 + k*CL^2."""
    return CL / (CD0 + k * CL**2)


best_CL = 0.0
best_LD = 0.0
CL = 0.05
while CL <= 1.5:
    LD = glide_ratio(CL)
    if LD > best_LD:
        best_LD = LD
        best_CL = CL
    CL = CL + 0.01

print(f"Best CL by search: {best_CL:.2f}, L/D = {best_LD:.2f}")
print(f"Theory: CL = {math.sqrt(0.02 / 0.1):.3f}, L/D = {1 / (2 * math.sqrt(0.02 * 0.1)):.2f}")
