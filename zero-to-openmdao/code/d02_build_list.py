import math

densities = []                     # start with an empty list

for h_km in range(0, 50, 10):      # 0, 10, 20, 30, 40
    rho = 1.225 * math.exp(-h_km * 1000 / 8500)
    densities.append(rho)          # add this result to the list

print(densities)
print(len(densities))
