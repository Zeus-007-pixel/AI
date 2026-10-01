import atmos

with open("atmosphere.csv", "w") as f:
    f.write("altitude_m,density_kg_m3,temperature_K\n")      # header line
    for h in range(0, 30001, 5000):
        rho = atmos.density(h)
        T = atmos.temperature(h)
        f.write(f"{h},{rho:.5f},{T:.2f}\n")                 # \n = new line

print("Wrote atmosphere.csv")
