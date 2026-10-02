"""Merges the rudder and elevons onto the OFM waverider STL (lengths in mm)."""
from hgv_geometry import RUDDER, SEED_WEIGHTS, waverider_geometry

# ==========================================
# MAIN EXECUTION PIPELINE
# ==========================================

# 1. FILE PATHS (Edit these for your setup)
WAVERIDER_INPUT_PATH = r"C:\Users\Rizwan computers\OneDrive\Desktop\Final Year Project\Claude\src\hgv\geometry\waverider_mm.stl"
MERGED_OUTPUT_PATH = r"C:\Users\Rizwan computers\OneDrive\Desktop\Final Year Project\Claude\src\hgv\geometry\waverider_with_deflected_fins.stl"

# The waverider is built with Y up. CATIA's standard views treat Z as up, so
# rotate the export to Z-up for screenshots. Set False to keep the Y-up frame.
EXPORT_Z_UP = True

# Also write the body (with fixed fin roots) and the moving control surfaces as
# two separate STLs, so they can be given different colours in CATIA.
EXPORT_PRESENTATION_PARTS = True

# Rebuild the waverider mesh with clean, evenly shaped triangles. The original
# mesh's sliver triangles show up in CATIA as dark streaks along the edges.
REMESH_BODY = True

# 2. DEFLECTION VARIABLES (degrees; the OpenMDAO component sets these per iteration)
# Elevons: positive = trailing edge up. Rudder: positive = trailing edge toward -Z.
elevon_1_deflection = 5.0   # Left Elevon angle (degrees)
elevon_2_deflection = -5.0  # Right Elevon angle (degrees)
rudder_deflection = 12.0    # Top Vertical Rudder angle (degrees)

# 3. FIN PLANFORMS (mm, degrees)
# The rudder sits on the flat upper surface with its trailing edge at the base.
# The elevon root leading edge sits on the wing leading edge and its trailing
# edge runs along the base line, so it reads as a cranked extension of the wing.
# The fixed root runs out to the wing tip, and the all-moving panel sits fully
# outboard of the tip so it can deflect freely. The span follows from the
# chords and sweep (lower sweep -> longer span).
FIN_SETTINGS = dict(
    weights=SEED_WEIGHTS,           # CST airfoil weights (NACA 0006 approximation)
    rudder=RUDDER,                  # root_chord=800, tip_chord=400, span=500, sweep_le=45
    rudder_fixed_fraction=0.15,
    elevon_root_chord=1000.0,
    elevon_tip_chord=300.0,
    elevon_sweep_le=50.0,
    root_overlap=20.0,              # mm each fin root is pushed into the body
)

geometry = waverider_geometry(WAVERIDER_INPUT_PATH, remesh=REMESH_BODY, **FIN_SETTINGS)
print(f"Elevon: root at z={geometry.elevon_root_z:.0f}, span {geometry.elevon['span']:.0f}, "
      f"moving panel {geometry.elevon_exposed_span:.0f} beyond the wing tip")

# 4. CHECK, UNION AND EXPORT FOR CATIA V5
merged_waverider = geometry.export(MERGED_OUTPUT_PATH, elevon_1_deflection, elevon_2_deflection,
                                   rudder_deflection, z_up=EXPORT_Z_UP,
                                   presentation_parts=EXPORT_PRESENTATION_PARTS)
