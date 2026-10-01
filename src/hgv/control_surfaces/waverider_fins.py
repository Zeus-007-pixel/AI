import os
import numpy as np
import trimesh
from scipy.special import comb


def cst_airfoil(weights, num_points=100):
    """Generates unit-chord symmetric airfoil coordinates (points clustered at the LE)."""
    x = 1 - np.cos(np.linspace(0, np.pi / 2, num_points))
    x[-1] = 1.0
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

    # The planform is linear in span; extra stations only keep the side-wall
    # triangles well shaped so CATIA shades them cleanly.
    breaks = [z_start, 0.0, z_end] if z_start < 0.0 < z_end else [z_start, z_end]
    station_spacing = 0.05 * root_chord
    stations = [breaks[0]]
    for a, b in zip(breaks[:-1], breaks[1:]):
        n_seg = max(1, int(np.ceil((b - a) / station_spacing)))
        stations.extend(np.linspace(a, b, n_seg + 1)[1:])

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


def _grid_faces(rows, cols, offset):
    """Two triangles per cell of a rows x cols vertex grid stored row-major."""
    i, j = np.meshgrid(np.arange(rows - 1), np.arange(cols - 1), indexing='ij')
    a = (offset + i * cols + j).ravel()
    b, c, d = a + cols, a + cols + 1, a + 1
    return np.concatenate([np.column_stack([a, b, c]), np.column_stack([a, c, d])])


def remesh_waverider(body, n_x=200, n_span=121, n_base=24):
    """
    Rebuilds the waverider as a clean structured mesh of well-shaped triangles.

    The generator's mesh has long sliver fans along the leading edge and at the
    wing tips, which CATIA shades as dark streaks. The new mesh samples the same
    surfaces: the flat upper surface (max Y), the lower surface (ray-cast onto
    the original mesh), and the flat base (max X). Assumes the body is
    symmetric about z=0 and its lower surface is single-valued in Y.
    """
    x_base, y_top, z_tip = body.bounds[1]

    # Leading edge = outline of the flat upper surface, minus the base line
    top = body.submesh([np.where(body.face_normals[:, 1] > 0.999)[0]], append=True)
    edges, counts = np.unique(top.edges_sorted, axis=0, return_counts=True)
    outline = top.vertices[np.unique(edges[counts == 1])]
    le = outline[(outline[:, 0] < x_base - 1e-6) & (outline[:, 2] >= 0)]
    le = np.vstack([le[np.argsort(le[:, 0])], [x_base, y_top, z_tip]])

    # Stations clustered toward the nose, spanwise fractions -1..1
    s = np.linspace(0, 1, n_x)
    x = x_base * (0.5 * s + 0.5 * (1 - np.cos(0.5 * np.pi * s)))
    x[-1] = x_base
    v = np.linspace(-1, 1, n_span)
    X = np.repeat(x[:, None], n_span, axis=1)
    Z = np.interp(x, le[:, 0], le[:, 2])[:, None] * v[None, :]

    # Lower surface: first hit of a ray fired upward from below the body
    probe_x = np.minimum(X, x_base - 0.05).ravel()
    origins = np.column_stack([probe_x, np.full(X.size, body.bounds[0][1] - 10.0), Z.ravel()])
    directions = np.tile([0.0, 1.0, 0.0], (X.size, 1))
    hits, ray_idx, _ = body.ray.intersects_location(origins, directions, multiple_hits=False)
    Y = np.full(X.size, y_top)
    Y[ray_idx] = hits[:, 1]
    Y = Y.reshape(X.shape)
    Y[0, :] = Y[:, 0] = Y[:, -1] = y_top      # nose and leading edges close the shell

    top_v = np.stack([X, np.full_like(X, y_top), Z], axis=-1)
    bot_v = np.stack([X, Y, Z], axis=-1)
    w = np.linspace(0, 1, n_base)[:, None]
    base_v = np.stack([np.full((n_base, n_span), x_base),
                       y_top + w * (Y[-1] - y_top), np.repeat(Z[-1:], n_base, axis=0)], axis=-1)
    base_v[0], base_v[-1] = top_v[-1], bot_v[-1]

    patches, offset = [], 0
    for grid, outward in ((top_v, [0, 1, 0]), (bot_v, [0, -1, 0]), (base_v, [1, 0, 0])):
        rows, cols = grid.shape[:2]
        faces = _grid_faces(rows, cols, offset)
        patch = trimesh.Trimesh(np.vstack([top_v.reshape(-1, 3), bot_v.reshape(-1, 3), base_v.reshape(-1, 3)]),
                                faces, process=False)
        if (patch.face_normals * patch.area_faces[:, None]).sum(0) @ outward < 0:
            faces = faces[:, ::-1]
        patches.append(faces)
        offset += rows * cols

    mesh = trimesh.Trimesh(
        np.vstack([top_v.reshape(-1, 3), bot_v.reshape(-1, 3), base_v.reshape(-1, 3)]),
        np.vstack(patches))
    mesh.update_faces(mesh.nondegenerate_faces())
    mesh.remove_unreferenced_vertices()
    return mesh


def wing_station_for_chord(body, chord, x_base, z_tip):
    """Spanwise station z where the wing's local chord (leading edge to base) equals `chord`."""
    zs = np.linspace(0.3 * z_tip, z_tip - 1.0, 80)
    chords = []
    for z in zs:
        section = body.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
        chords.append(x_base - section.vertices[:, 0].min())
    # Local chord shrinks toward the tip, so reverse for np.interp
    return float(np.interp(chord, chords[::-1], zs[::-1]))


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

# How far (mm) each fin root is pushed into the body so the union welds them
ROOT_OVERLAP = 20.0

# 2. DEFLECTION VARIABLES (Modify these values at each optimization loop step)
# Elevons: positive = trailing edge up. Rudder: positive = trailing edge toward -Z.
elevon_1_deflection = 5.0   # Left Elevon angle (degrees)
elevon_2_deflection = -5.0  # Right Elevon angle (degrees)
rudder_deflection = 12.0    # Top Vertical Rudder angle (degrees)

# 3. FIN PLANFORMS (mm, degrees)
# Seed weights (NACA 0006 approximation)
seed_weights = np.array([0.0848, 0.0804, 0.0729, 0.0800, 0.0594, 0.0867])

RUDDER = dict(root_chord=800.0, tip_chord=400.0, span=500.0, sweep_le=45.0)
RUDDER_FIXED_FRACTION = 0.15

# The elevon root leading edge sits on the wing leading edge and its trailing
# edge runs along the base line, so it reads as a cranked extension of the wing.
# The fixed root runs out to the wing tip, and the all-moving panel sits fully
# outboard of the tip so it can deflect freely. The span follows from the
# chords and sweep (lower sweep -> longer span).
ELEVON_ROOT_CHORD = 1000.0
ELEVON_TIP_CHORD = 300.0
ELEVON_SWEEP_LE = 50.0

# --- LOAD WAVERIDER (vehicle frame: X aft, Y up, Z spanwise) ---
wr_mesh = load_body(WAVERIDER_INPUT_PATH)
if REMESH_BODY:
    remeshed = remesh_waverider(wr_mesh)
    if remeshed.is_volume and abs(remeshed.volume / wr_mesh.volume - 1) < 0.005:
        wr_mesh = remeshed
    else:
        print("WARNING: remeshing did not reproduce the body; using the original mesh.")
x_base = wr_mesh.bounds[1][0]   # base plane
y_top = wr_mesh.bounds[1][1]    # flat upper (freestream) surface
z_tip = wr_mesh.bounds[1][2]    # wing-tip half-span

# --- TOP RUDDER (on the flat upper surface, trailing edge at the base) ---
r_fixed, r_moving = split_and_deflect_fin(
    seed_weights, **RUDDER, fixed_span_fraction=RUDDER_FIXED_FRACTION,
    deflection_deg=rudder_deflection, root_overlap=ROOT_OVERLAP)
# Stand the rudder up (local span +Z -> +Y) and move it to the rear top centreline
stand_up = trimesh.transformations.rotation_matrix(np.radians(-90), [1, 0, 0])
for part in (r_fixed, r_moving):
    part.apply_transform(stand_up)
    part.apply_translation([x_base - RUDDER['root_chord'], y_top, 0.0])

# --- ELEVON LAYOUT FROM THE WING GEOMETRY ---
z_root = wing_station_for_chord(wr_mesh, ELEVON_ROOT_CHORD, x_base, z_tip)
# Unswept trailing edge: the leading edge closes the chord difference over the span
elevon_span = (ELEVON_ROOT_CHORD - ELEVON_TIP_CHORD) / np.tan(np.radians(ELEVON_SWEEP_LE))
if z_root + elevon_span <= z_tip:
    raise ValueError("Elevon does not reach past the wing tip; lower ELEVON_SWEEP_LE "
                     "or increase ELEVON_ROOT_CHORD.")
ELEVON = dict(root_chord=ELEVON_ROOT_CHORD, tip_chord=ELEVON_TIP_CHORD,
              span=elevon_span, sweep_le=ELEVON_SWEEP_LE)
elevon_fixed_fraction = (z_tip - z_root) / elevon_span
print(f"Elevon: root at z={z_root:.0f}, span {elevon_span:.0f}, "
      f"moving panel {z_root + elevon_span - z_tip:.0f} beyond the wing tip")
# Drop the fin so its upper surface is flush with the flat top at max thickness
y_elevon = y_top - cst_airfoil(seed_weights)[1].max() * ELEVON_ROOT_CHORD
x_elevon = x_base - ELEVON_ROOT_CHORD

# --- LEFT ELEVON (extends outboard toward -Z) ---
el_fixed, el_moving = split_and_deflect_fin(
    seed_weights, **ELEVON, fixed_span_fraction=elevon_fixed_fraction,
    deflection_deg=elevon_1_deflection, root_overlap=ROOT_OVERLAP)
mirror_z = trimesh.transformations.reflection_matrix([0, 0, 0], [0, 0, 1])
for part in (el_fixed, el_moving):
    part.apply_transform(mirror_z)
    part.apply_translation([x_elevon, y_elevon, -z_root])

# --- RIGHT ELEVON (extends outboard toward +Z) ---
er_fixed, er_moving = split_and_deflect_fin(
    seed_weights, **ELEVON, fixed_span_fraction=elevon_fixed_fraction,
    deflection_deg=elevon_2_deflection, root_overlap=ROOT_OVERLAP)
for part in (er_fixed, er_moving):
    part.apply_translation([x_elevon, y_elevon, z_root])

fixed_parts = {'rudder fixed': r_fixed, 'left elevon fixed': el_fixed,
               'right elevon fixed': er_fixed}
moving_parts = {'rudder moving': r_moving, 'left elevon moving': el_moving,
                'right elevon moving': er_moving}

# 4. CHECK EVERY PART IS A CLOSED VOLUME BEFORE THE BOOLEAN
all_parts = {'waverider': wr_mesh, **fixed_parts, **moving_parts}
for name, part in all_parts.items():
    if not part.is_volume:
        raise ValueError(
            f"'{name}' is not a closed volume (watertight={part.is_watertight}, "
            f"winding consistent={part.is_winding_consistent}). "
            "Repair the STL (e.g. in MeshLab) before merging.")

# 5. BOOLEAN UNION FOR SEAMLESS GEOMETRY
merged_waverider = trimesh.boolean.union(list(all_parts.values()))

if merged_waverider.body_count > 1:
    print(f"WARNING: result has {merged_waverider.body_count} separate bodies; "
          "a fin is not touching the waverider. Check the fin layout and ROOT_OVERLAP.")

# 6. EXPORT FOR CATIA V5
to_z_up = trimesh.transformations.rotation_matrix(np.radians(90), [1, 0, 0])
outputs = {MERGED_OUTPUT_PATH: merged_waverider}
if EXPORT_PRESENTATION_PARTS:
    stem = os.path.splitext(MERGED_OUTPUT_PATH)[0]
    outputs[stem + '_body.stl'] = trimesh.boolean.union([wr_mesh, *fixed_parts.values()])
    outputs[stem + '_controls.stl'] = trimesh.util.concatenate(list(moving_parts.values()))

for path, mesh in outputs.items():
    if EXPORT_Z_UP:
        mesh.apply_transform(to_z_up)
    mesh.export(path)
    print(f"Saved: {path}")
