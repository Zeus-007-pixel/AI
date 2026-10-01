import numpy as np


def f(x):
    return np.sin(x)


x = 1.0
exact = np.cos(x)            # we know the true slope of sin is cos

for h in [1e-1, 1e-4, 1e-8, 1e-12]:
    fd = (f(x + h) - f(x)) / h                  # finite difference
    cs = np.imag(f(x + 1j * h)) / h             # complex step (1j is the imaginary unit)
    print(f"h = {h:.0e}   FD error = {abs(fd - exact):.1e}   CS error = {abs(cs - exact):.1e}")
