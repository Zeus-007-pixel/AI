import math


class Vehicle:
    def __init__(self, name, mass, S):
        self.name = name
        self.mass = mass
        self.S = S

    def weight(self, g=9.81):
        return self.mass * g

    def describe(self):
        return f"{self.name}: {self.mass} kg"


class Glider(Vehicle):                       # a Glider IS A Vehicle, plus more
    def __init__(self, name, mass, S, CD0, k):
        super().__init__(name, mass, S)      # let Vehicle store name, mass, S
        self.CD0 = CD0                       # then store the extra data
        self.k = k

    def max_LD(self):
        """Best lift-to-drag ratio for the polar CD = CD0 + k*CL^2."""
        return 1.0 / (2.0 * math.sqrt(self.CD0 * self.k))

    def describe(self):                      # replace ("override") the parent's version
        return f"{self.name}: {self.mass} kg glider, best L/D {self.max_LD():.1f}"


g1 = Glider("Glider-1", 500.0, 10.0, 0.02, 0.1)
print(g1.weight())          # inherited from Vehicle
print(g1.max_LD())          # defined in Glider
print(g1.describe())        # Glider's own version wins
