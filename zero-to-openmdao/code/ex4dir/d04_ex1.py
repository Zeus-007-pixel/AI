import atmos

for h in range(0, 20001, 5000):
    print(f"{h:6d} m   a = {atmos.speed_of_sound(h):.1f} m/s")
