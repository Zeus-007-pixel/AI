def lift_drag(vehicle, rho, v, CL):
    """Return (lift, drag) in newtons for a vehicle dictionary."""
    q = 0.5 * rho * v**2
    CD = vehicle["CD0"] + vehicle["k"] * CL**2
    L = q * vehicle["S"] * CL
    D = q * vehicle["S"] * CD
    return L, D


glider = {"name": "Glider-1", "mass": 500.0, "S": 10.0, "CD0": 0.02, "k": 0.1}
L, D = lift_drag(glider, 1.225, 40.0, 0.5)
print(f"L = {L:.0f} N, D = {D:.0f} N, L/D = {L / D:.2f}")
