import math


def atmosphere(h):
    """Return (density in kg/m^3, temperature in K) at altitude h in metres."""
    rho = 1.225 * math.exp(-h / 8500.0)
    if h < 11000:
        T = 288.15 - 0.0065 * h
    else:
        T = 216.65
    return rho, T


rho, T = atmosphere(5000)      # "unpack" the two answers into two names
print(f"rho = {rho:.4f} kg/m^3, T = {T:.2f} K")

result = atmosphere(5000)      # or keep them together as one "tuple"
print(result)
print(result[0], result[1])
