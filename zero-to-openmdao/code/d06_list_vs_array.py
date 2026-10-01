import numpy as np

my_list = [1, 2, 3]
my_array = np.array([1, 2, 3])

print(my_list * 2)       # a list is REPEATED
print(my_array * 2)      # an array is MULTIPLIED, element by element
print(my_array + 10)
print(my_array ** 2)
print(my_array * np.array([10, 20, 30]))   # element 1 x element 1, and so on
print(np.sqrt(my_array))
