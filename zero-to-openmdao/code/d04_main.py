import atmos                      # load our own file atmos.py
from atmos import temperature     # or pull one name straight in

print(atmos.density(10000))
print(temperature(10000))
print(atmos.RHO0)
