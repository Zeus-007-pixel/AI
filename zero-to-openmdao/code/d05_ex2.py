import math


class Vehicle:
    def __init__(self, name, mass, S):
        self.name = name
        self.mass = mass
        self.S = S

    def weight(self, g=9.81):
        return self.mass * g


class HGV(Vehicle):
    def __init__(self, name, mass, S, nose_radius):
        super().__init__(name, mass, S)
        self.nose_radius = nose_radius          # m

    def heat_rate(self, rho, v):
        """Stagnation-point heat rate in W/m^2 (Sutton-Graves)."""
        return 1.7415e-4 * math.sqrt(rho / self.nose_radius) * v**3


vehicle = HGV("HGV-1", 1000.0, 2.0, 0.1)
q_dot = vehicle.heat_rate(0.0184, 2000.0)
print(f"Heat rate: {q_dot / 1e6:.2f} MW/m^2")
print(f"Weight: {vehicle.weight():.0f} N")
