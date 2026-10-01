import numpy as np

a = np.array([1.0, 2.0, 3.0])        # from a list
print(a)
print(np.zeros(4))                   # four zeros
print(np.ones(3))                    # three ones
print(np.arange(0, 10, 2))           # start, stop (not included), step
print(np.linspace(0, 1, 5))          # start, stop (included), how many
print(a.shape, a.size, a.dtype)
