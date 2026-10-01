def dynamic_pressure(rho, v):
    """Return dynamic pressure q = 0.5 * rho * v^2 in pascals."""
    return 0.5 * rho * v**2


def lift(q, S, CL=0.5):
    """Return lift force in newtons. CL is 0.5 unless you say otherwise."""
    return q * S * CL


q = dynamic_pressure(0.4135, 250.0)
print(q)
print(lift(q, 10.0))               # uses the default CL = 0.5
print(lift(q, 10.0, 0.8))          # CL given by position
print(lift(q, S=10.0, CL=0.8))     # CL given by name (keyword)
print(lift(CL=0.8, S=10.0, q=q))   # with names, the order doesn't matter
