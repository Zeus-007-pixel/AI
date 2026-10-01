import numpy as np

h = np.linspace(0, 80000, 9)
rho = 1.225 * np.exp(-h / 8500)

print(rho[0])            # first element
print(rho[-1])           # last element
print(rho[2:5])          # elements 2, 3, 4
print(rho[::2])          # every second element

high = h > 40000         # a True/False array, one value per element
print(high)
print(h[high])           # only the altitudes where 'high' is True
print(rho[h > 40000])    # same idea, in one line

print(rho.max(), rho.min(), rho.mean())
print(np.argmax(rho))    # the INDEX of the largest value
