rho = 0.0184       # air density at about 30 km, kg/m^3
v = 2000.0         # speed, m/s

q = 0.5 * rho * v**2

print(f"Dynamic pressure: {q:.0f} Pa")
print(f"Dynamic pressure: {q / 1000:.1f} kPa")
