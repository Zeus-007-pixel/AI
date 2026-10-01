import math


def speed_of_sound(T):
    """Speed of sound in air (m/s) at temperature T (K)."""
    gamma = 1.4
    R = 287.0
    return math.sqrt(gamma * R * T)


def mach_number(v, T):
    """Mach number for speed v (m/s) at temperature T (K)."""
    return v / speed_of_sound(T)


print(f"a at 288.15 K: {speed_of_sound(288.15):.1f} m/s")
print(f"Mach at 2000 m/s and 226.5 K: {mach_number(2000.0, 226.5):.2f}")
