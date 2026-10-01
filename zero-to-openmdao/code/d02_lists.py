altitudes_km = [0, 10, 20, 30, 40]

print(altitudes_km)
print(altitudes_km[0])      # first item (counting starts at 0!)
print(altitudes_km[2])      # third item
print(altitudes_km[-1])     # last item
print(altitudes_km[1:3])    # a "slice": items 1 and 2 (stops BEFORE 3)
print(len(altitudes_km))    # how many items

altitudes_km.append(50)     # add an item to the end
print(altitudes_km)

altitudes_km[0] = 5         # replace the first item
print(altitudes_km)
print(sum(altitudes_km), min(altitudes_km), max(altitudes_km))
