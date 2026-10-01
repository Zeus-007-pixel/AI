import math


class Vehicle:
    def __init__(self, name, mass, S):
        self.name = name
        self.mass = mass
        self.S = S

    def weight(self, g=9.81):
        return self.mass * g

    def stall_speed(self, rho, CL_max):
        """Slowest speed (m/s) at which lift can still equal weight."""
        return math.sqrt(2.0 * self.weight() / (rho * self.S * CL_max))


glider = Vehicle("Glider-1", 500.0, 10.0)
print(f"Stall speed at sea level: {glider.stall_speed(1.225, 1.2):.1f} m/s")
print(f"Stall speed at 10 km: {glider.stall_speed(0.3777, 1.2):.1f} m/s")
