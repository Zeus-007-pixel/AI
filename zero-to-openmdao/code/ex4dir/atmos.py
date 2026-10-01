"""atmos.py - simple atmosphere functions (with speed of sound added)."""
import math

RHO0 = 1.225        # sea-level density, kg/m^3
H_SCALE = 8500.0    # scale height, m


def density(h):
    """Air density in kg/m^3 at altitude h in metres."""
    if h < 0:
        raise ValueError(f"Altitude must not be negative, got {h}")
    return RHO0 * math.exp(-h / H_SCALE)


def temperature(h):
    """Temperature in K at altitude h in metres (troposphere + flat stratosphere)."""
    if h < 11000:
        return 288.15 - 0.0065 * h
    return 216.65


def speed_of_sound(h):
    """Speed of sound in m/s at altitude h in metres."""
    return math.sqrt(1.4 * 287.0 * temperature(h))
