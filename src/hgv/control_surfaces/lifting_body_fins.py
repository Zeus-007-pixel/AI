"""
Flat-bottomed lifting body (HTV-2 / DF-ZF style) with the same rudder and
elevons as the waverider, sized to the waverider's overall dimensions (mm).

Unlike the OFM waverider (flat freestream surface on top, shaped compression
surface underneath, flown near zero angle of attack), this body has a flat
windward bottom and an arched top, and makes lift by flying nose-up.
"""
from hgv_geometry import RUDDER, SEED_WEIGHTS, lifting_body_geometry

# ==========================================
# MAIN EXECUTION PIPELINE
# ==========================================

# 1. FILE PATHS (Edit these for your setup)
MERGED_OUTPUT_PATH = r"C:\Users\Rizwan computers\OneDrive\Desktop\Final Year Project\Claude\src\hgv\geometry\lifting_body_with_deflected_fins.stl"

# The body is built with Y up. CATIA's standard views treat Z as up, so
# rotate the export to Z-up for screenshots. Set False to keep the Y-up frame.
EXPORT_Z_UP = True

# Also write the body (with fixed fin roots) and the moving control surfaces as
# two separate STLs, so they can be given different colours in CATIA.
EXPORT_PRESENTATION_PARTS = True

# 2. BODY SHAPE (matched to waverider_mm.stl: same length, span, height and planform)
# planform edge  z = HALF_SPAN * (x/L)^N_PLANFORM   (0.72 fits the waverider's leading edge)
# ridge height   h = HEIGHT * (x/L)^N_HEIGHT        (1 = straight wedge in side view)
# upper surface  y = h * (1 - (z/z_edge)^2)^N_SECTION (1 = sharp side edges, < 1 = rounder)
BODY_SHAPE = dict(length=3998.9, half_span=1428.3, height=636.4,
                  n_planform=0.72, n_height=1.0, n_section=1.0)

# 3. DEFLECTION VARIABLES (degrees; the OpenMDAO component sets these per iteration)
# Elevons: positive = trailing edge up. Rudder: positive = trailing edge toward -Z.
elevon_1_deflection = 5.0   # Left Elevon angle (degrees)
elevon_2_deflection = -5.0  # Right Elevon angle (degrees)
rudder_deflection = 12.0    # Top Vertical Rudder angle (degrees)

# 4. FIN PLANFORMS (mm, degrees) - same as the waverider
# Rudder on the centreline ridge, trailing edge at the base. Elevon root leading
# edge on the body's side edge, trailing edge along the base line, lower surface
# flush with the flat bottom, all-moving panel fully outboard of the side edge.
FIN_SETTINGS = dict(
    weights=SEED_WEIGHTS,           # CST airfoil weights (NACA 0006 approximation)
    rudder=RUDDER,                  # root_chord=800, tip_chord=400, span=500, sweep_le=45
    rudder_fixed_fraction=0.15,
    elevon_root_chord=1000.0,
    elevon_tip_chord=300.0,
    elevon_sweep_le=50.0,
    root_overlap=20.0,              # mm each fin root is pushed into the body
)

geometry = lifting_body_geometry(**BODY_SHAPE, **FIN_SETTINGS)
body = geometry.body
print(f"Lifting body: length {body.bounds[1][0]:.0f}, span {2 * body.bounds[1][2]:.0f}, "
      f"height {body.extents[1]:.0f}, volume {body.volume / 1e9:.3f} m^3")
print(f"Elevon: root at z={geometry.elevon_root_z:.0f}, span {geometry.elevon['span']:.0f}, "
      f"moving panel {geometry.elevon_exposed_span:.0f} beyond the side edge")

# 5. CHECK, UNION AND EXPORT FOR CATIA V5
merged_lifting_body = geometry.export(MERGED_OUTPUT_PATH, elevon_1_deflection, elevon_2_deflection,
                                      rudder_deflection, z_up=EXPORT_Z_UP,
                                      presentation_parts=EXPORT_PRESENTATION_PARTS)
