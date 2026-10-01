import numpy as np
import trimesh
from scipy.special import comb


def cst_airfoil(weights, num_points=100):
    """Generates unit-chord symmetric airfoil coordinates."""
    x = np.linspace(0, 1, num_points)
    C = (x ** 0.5) * ((1 - x) ** 1.0)
    N_order = len(weights) - 1
    S = np.zeros_like(x)
    for i in range(N_order + 1):
        S += weights[i] * comb(N_order, i) * (x ** i) * ((1 - x) ** (N_order - i))
    return x, C * S, -C * S


def generate_fin_mesh(weights, root_chord, tip_chord, span, sweep_le,
                      z_start=0.0, z_end=None, num_points=100):
    """
    Builds a watertight fin solid between span stations z_start and z_end.

    Local frame: chord along +X (root leading edge at x=0), thickness along Y,
    span along +Z (root at z=0, tip at z=span). A negative z_start extends the
    root section straight down so the root can be buried inside the body.
    """
    if z_end is None:
        z_end = span
    x_unit, y_upper, _ = cst_airfoil(weights, num_points)
    tip_offset = span * np.tan(np.radians(sweep_le))

    # Closed section ring: upper surface LE -> TE, then lower surface TE -> LE.
    # The LE and TE points are shared by both surfaces, so they appear once.
    ring_x = np.concatenate([x_unit, x_unit[-2:0:-1]])
    ring_y = np.concatenate([y_upper, -y_upper[-2:0:-1]])
    n_ring = len(ring_x)

    # The planform is linear in span, so the end stations (plus z=0 when the
    # root is extended) describe the fin exactly.
    stations = [z_start, z_end]
    if z_start < 0.0 < z_end:
        stations = [z_start, 0.0, z_end]

    vertices = []
    for z in stations:
        fraction = np.clip(z / span, 0.0, 1.0)
        local_chord = root_chord + fraction * (tip_chord - root_chord)
        local_le_x = fraction * tip_offset
        vertices.append(np.column_stack([local_le_x + ring_x * local_chord,
                                         ring_y * local_chord,
                                         np.full(n_ring, z)]))
    vertices = np.vstack(vertices)

    faces = []
    # Side walls joining consecutive stations
    for s in range(len(stations) - 1):
        a, b = s * n_ring, (s + 1) * n_ring
        for j in range(n_ring):
            k = (j + 1) % n_ring
            faces.append([a + j, a + k, b + k])
            faces.append([a + j, b + k, b + j])

    # End caps, triangulated as strips between matching upper/lower points.
    # Works for any section whose upper surface lies above the lower one.
    upper = np.arange(num_points)
    lower = np.concatenate([[0], n_ring - np.arange(1, num_points - 1), [num_points - 1]])
    cap = []
    for i in range(num_points - 1):
        for tri in ([upper[i + 1], upper[i], lower[i]],
                    [upper[i + 1], lower[i], lower[i + 1]]):
            if len(set(tri)) == 3:
                cap.append(tri)
    cap = np.array(cap)
    faces.extend(cap)                                            # root cap
    faces.extend(cap[:, ::-1] + (len(stations) - 1) * n_ring)    # tip cap

    mesh = trimesh.Trimesh(vertices=vertices, faces=np.array(faces))
    if mesh.volume < 0:
        mesh.invert()
    return mesh


def split_and_deflect_fin(weights, root_chord, tip_chord, span, sweep_le,
                          fixed_span_fraction, deflection_deg, root_overlap=0.0):
    """
    Builds a fin as a fixed root stub plus an all-moving outer panel, both as
    closed solids in the local fin frame (chord +X, thickness Y, span +Z).

    The moving panel is rotated about the spanwise axis through the
    quarter-chord of its mean aerodynamic chord. Positive deflection moves
    the trailing edge toward +Y (local).
    """
    split_z = span * fixed_span_fraction
    planform = (weights, root_chord, tip_chord, span, sweep_le)

    # Generating each piece directly (instead of slicing one mesh) gives
    # closed end caps, so both pieces are valid volumes for the boolean.
    fixed_part = generate_fin_mesh(*planform, z_start=-root_overlap, z_end=split_z)
    moving_part = generate_fin_mesh(*planform, z_start=split_z, z_end=span)

    if deflection_deg != 0:
        # Quarter-chord of the moving panel's mean aerodynamic chord
        panel_root = root_chord + fixed_span_fraction * (tip_chord - root_chord)
        taper = tip_chord / panel_root
        panel_span = span - split_z
        mac = (2.0 / 3.0) * panel_root * (1 + taper + taper ** 2) / (1 + taper)
        z_mac = split_z + (panel_span / 3.0) * (1 + 2 * taper) / (1 + taper)
        pivot_x = z_mac * np.tan(np.radians(sweep_le)) + 0.25 * mac

        rot_mat = trimesh.transformations.rotation_matrix(
            np.radians(deflection_deg), [0, 0, 1], [pivot_x, 0.0, split_z])
        moving_part.apply_transform(rot_mat)

    return fixed_part, moving_part


def load_body(path):
    """Loads the waverider STL and applies basic repairs so it is a closed volume."""
    mesh = trimesh.load(path, force='mesh')
    if not mesh.is_volume:
        mesh.merge_vertices()
        mesh.update_faces(mesh.nondegenerate_faces())
        mesh.fill_holes()
        mesh.fix_normals()
    return mesh


# ==========================================
# MAIN EXECUTION PIPELINE
# ==========================================

# 1. FILE PATHS (Edit these for your setup)
WAVERIDER_INPUT_PATH = r"C:\Users\Rizwan computers\OneDrive\Desktop\Final Year Project\Claude\src\hgv\geometry\waverider_mm.stl"
MERGED_OUTPUT_PATH = r"C:\Users\Rizwan computers\OneDrive\Desktop\Final Year Project\Claude\src\hgv\geometry\waverider_with_deflected_fins.stl"

# Set to False to merge the fins onto the real waverider STL
USE_DUMMY_BODY = True

# Fin sizes and positions below are in metres. If the waverider STL is in
# millimetres, set this to 1000.0 so the fins are scaled to match.
UNIT_SCALE = 1.0

# How far (m) each fin root is pushed into the body so the union welds them
# together. Increase it if a fin root does not reach the body surface.
ROOT_OVERLAP = 0.02

# 2. DEFLECTION VARIABLES (Modify these values at each optimization loop step)
# Elevons: positive = trailing edge up (+Y). Rudder: positive = trailing edge toward -Z.
elevon_1_deflection = 5.0   # Left Elevon angle (degrees)
elevon_2_deflection = -5.0  # Right Elevon angle (degrees)
rudder_deflection = 12.0    # Top Vertical Rudder angle (degrees)

# Vehicle frame: X aft, Y up, Z spanwise
if USE_DUMMY_BODY:
    # Stand-in body: 4.0 long (x = 0..4), 0.64 tall (y = +/-0.32), 2.86 wide (z = +/-1.43)
    wr_mesh = trimesh.creation.box(extents=[4.0, 0.64, 2.86])
    wr_mesh.apply_translation([2.0, 0.0, 0.0])
else:
    wr_mesh = load_body(WAVERIDER_INPUT_PATH)
    print(f"Waverider bounds:\n{wr_mesh.bounds}")
    if wr_mesh.extents.max() > 100 and UNIT_SCALE == 1.0:
        print("WARNING: waverider looks like it is in mm; set UNIT_SCALE = 1000.0")

# Seed weights (NACA 0006 approximation)
seed_weights = np.array([0.0848, 0.0804, 0.0729, 0.0800, 0.0594, 0.0867])

RUDDER = dict(root_chord=0.80, tip_chord=0.40, span=0.50, sweep_le=45)
ELEVON = dict(root_chord=1.00, tip_chord=0.30, span=0.35, sweep_le=74)

# --- TOP RUDDER ---
r_fixed, r_moving = split_and_deflect_fin(
    seed_weights, **RUDDER, fixed_span_fraction=0.15,
    deflection_deg=rudder_deflection, root_overlap=ROOT_OVERLAP)
# Stand the rudder up (local span +Z -> +Y) and move it to the rear top centreline
stand_up = trimesh.transformations.rotation_matrix(np.radians(-90), [1, 0, 0])
for part in (r_fixed, r_moving):
    part.apply_transform(stand_up)
    part.apply_translation([3.20, 0.32, 0.0])

# --- LEFT ELEVON (z = -1.43, extends outboard toward -Z) ---
el_fixed, el_moving = split_and_deflect_fin(
    seed_weights, **ELEVON, fixed_span_fraction=0.20,
    deflection_deg=elevon_1_deflection, root_overlap=ROOT_OVERLAP)
mirror_z = trimesh.transformations.reflection_matrix([0, 0, 0], [0, 0, 1])
for part in (el_fixed, el_moving):
    part.apply_transform(mirror_z)
    part.apply_translation([3.00, 0.0, -1.43])

# --- RIGHT ELEVON (z = +1.43, extends outboard toward +Z) ---
er_fixed, er_moving = split_and_deflect_fin(
    seed_weights, **ELEVON, fixed_span_fraction=0.20,
    deflection_deg=elevon_2_deflection, root_overlap=ROOT_OVERLAP)
for part in (er_fixed, er_moving):
    part.apply_translation([3.00, 0.0, 1.43])

fin_parts = {
    'rudder fixed': r_fixed, 'rudder moving': r_moving,
    'left elevon fixed': el_fixed, 'left elevon moving': el_moving,
    'right elevon fixed': er_fixed, 'right elevon moving': er_moving,
}
for part in fin_parts.values():
    part.apply_scale(UNIT_SCALE)

# 3. CHECK EVERY PART IS A CLOSED VOLUME BEFORE THE BOOLEAN
all_parts = {'waverider': wr_mesh, **fin_parts}
for name, part in all_parts.items():
    if not part.is_volume:
        raise ValueError(
            f"'{name}' is not a closed volume (watertight={part.is_watertight}, "
            f"winding consistent={part.is_winding_consistent}). "
            "Repair the STL (e.g. in MeshLab) before merging.")

# 4. BOOLEAN UNION FOR SEAMLESS GEOMETRY
merged_waverider = trimesh.boolean.union(list(all_parts.values()))

if merged_waverider.body_count > 1:
    print(f"WARNING: result has {merged_waverider.body_count} separate bodies; "
          "a fin is not touching the waverider. Check positions, UNIT_SCALE and ROOT_OVERLAP.")

# 5. EXPORT FOR CATIA V5
merged_waverider.export(MERGED_OUTPUT_PATH)
print(f"Successfully compiled geometry! File saved to: {MERGED_OUTPUT_PATH}")
