def kinetic_energy(m, v):
    energy = 0.5 * m * v**2       # 'energy' only exists inside this function
    return energy


E = kinetic_energy(1000.0, 2000.0)
print(E)
print(energy)                     # error: 'energy' does not exist out here
