with open("atmosphere.csv", "r") as f:
    lines = f.readlines()

print(lines[0])            # the header
for line in lines[1:]:     # skip the header
    parts = line.strip().split(",")
    h = float(parts[0])
    rho = float(parts[1])
    print(f"h = {h:7.0f} m   rho = {rho}")
