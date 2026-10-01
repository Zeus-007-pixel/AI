import atmos

altitudes = [0, 5000, -100, 20000]

for h in altitudes:
    try:
        rho = atmos.density(h)
        print(f"{h} m: {rho:.4f} kg/m^3")
    except ValueError as err:
        print(f"Skipped {h}: {err}")
