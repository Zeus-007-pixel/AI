from scipy.optimize import minimize_scalar


def negative_LD(CL):
    CD = 0.02 + 0.1 * CL**2
    return -CL / CD


result = minimize_scalar(negative_LD, bounds=(0.01, 1.5), method="bounded")
print(f"Best CL = {result.x:.4f}, L/D = {-result.fun:.3f}")
