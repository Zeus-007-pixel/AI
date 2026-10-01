import atmos

with open("atmosphere_full.csv", "w") as f:
    f.write("altitude_m,density_kg_m3,temperature_K,speed_of_sound_m_s\n")
    for h in range(0, 30001, 1000):
        f.write(f"{h},{atmos.density(h):.6f},{atmos.temperature(h):.2f},{atmos.speed_of_sound(h):.2f}\n")

print("Wrote atmosphere_full.csv")
