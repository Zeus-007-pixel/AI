import math


def density(h):
    """Return air density in kg/m^3 at altitude h in metres."""
    rho = 1.225 * math.exp(-h / 8500.0)
    return rho


print(density(0))
print(density(30000))

rho_cruise = density(10000)       # store the answer in a variable
print(f"{rho_cruise:.3f}")
