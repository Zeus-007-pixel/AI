import atmos

altitudes = [1000, -50, 12000, -3000, 25000]
skipped = 0

for h in altitudes:
    try:
        print(f"{h} m: {atmos.density(h):.4f} kg/m^3")
    except ValueError:
        skipped = skipped + 1

print(f"Skipped {skipped} bad altitudes")
