mach = 6.2

if mach < 0.8:
    regime = "subsonic"
elif mach < 1.2:
    regime = "transonic"
elif mach < 5:
    regime = "supersonic"
else:
    regime = "hypersonic"

print(f"Mach {mach} is {regime}")
