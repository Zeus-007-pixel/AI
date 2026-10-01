a = 301.7          # speed of sound at 30 km, m/s
mach = 5

v = mach * a                 # m/s
v_kmh = v * 3.6              # 1 m/s = 3.6 km/h

print(f"Mach {mach} is {v:.0f} m/s, or {v_kmh:.0f} km/h")
