import math
import numpy as np

angles = np.array([0.0, 0.5, 1.0])
print(np.sin(angles))      # works on the whole array
print(math.sin(angles))    # math only works on single numbers
