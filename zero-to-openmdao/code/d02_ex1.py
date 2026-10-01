mach_numbers = [0.5, 0.95, 2.0, 7.5]

for mach in mach_numbers:
    if mach < 0.8:
        regime = "subsonic"
    elif mach < 1.2:
        regime = "transonic"
    elif mach < 5:
        regime = "supersonic"
    else:
        regime = "hypersonic"
    print(f"Mach {mach}: {regime}")
