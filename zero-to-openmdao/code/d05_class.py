class Vehicle:
    """A flying vehicle described by its mass and reference area."""

    def __init__(self, name, mass, S):
        self.name = name        # store the inputs on the object
        self.mass = mass        # kg
        self.S = S              # reference area, m^2

    def weight(self, g=9.81):
        """Weight in newtons."""
        return self.mass * g

    def wing_loading(self):
        """Mass per unit area, kg/m^2."""
        return self.mass / self.S


glider = Vehicle("Glider-1", 500.0, 10.0)    # make one object
hgv = Vehicle("HGV-1", 1000.0, 2.0)          # make another object

print(glider.name, glider.mass)
print(glider.weight())
print(hgv.wing_loading())

hgv.mass = 1100.0                  # change one object's data
print(hgv.wing_loading())
print(glider.wing_loading())       # the other object is unaffected
