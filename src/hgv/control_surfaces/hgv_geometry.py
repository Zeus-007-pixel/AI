"""Shared geometry for HGV bodies and all-moving control fins (lengths in mm)."""
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
    planform = (weights, root_chord, tip_chord, span, sweep_le)
    # Generating each piece directly (instead of slicing one mesh) gives
    # closed end caps, so both pieces are valid volumes for the boolean.
    fixed_part = generate_fin_mesh(*planform, z_start=-root_overlap,
                                   z_end=span * fixed_span_fraction)
    moving_part = moving_fin_panel(*planform, fixed_span_fraction, deflection_deg)
    return fixed_part, moving_part


def moving_fin_panel(weights, root_chord, tip_chord, span, sweep_le,
                     fixed_span_fraction, deflection_deg):
    """The all-moving outer panel of split_and_deflect_fin on its own."""
    split_z = span * fixed_span_fraction
    moving_part = generate_fin_mesh(weights, root_chord, tip_chord, span, sweep_le,
                                    z_start=split_z, z_end=span)
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
    return moving_part


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


def closed_body_mesh(X, Z, y_upper, y_lower, n_base=24):
    """
    Closed structured mesh from an upper and a lower surface sampled on the same
    (X, Z) grid. Rows run nose -> base and columns run edge to edge across the
    span. The two surfaces must meet on the first row (nose) and the first and
    last columns (side edges); the last row is closed off by a flat base.
    """
    upper = np.stack([X, y_upper, Z], axis=-1)
    lower = np.stack([X, y_lower, Z], axis=-1)
    w = np.linspace(0, 1, n_base)[:, None, None]
    base = upper[-1][None] + w * (lower[-1] - upper[-1])[None]
    base[0], base[-1] = upper[-1], lower[-1]

    grids = ((upper, [0, 1, 0]), (lower, [0, -1, 0]), (base, [1, 0, 0]))
    vertices = np.vstack([grid.reshape(-1, 3) for grid, _ in grids])
    patches, offset = [], 0
    for grid, outward in grids:
        rows, cols = grid.shape[:2]
        faces = _grid_faces(rows, cols, offset)
        tri = vertices[faces]
        if np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]).sum(0) @ outward < 0:
            faces = faces[:, ::-1]
        patches.append(faces)
        offset += rows * cols

    mesh = trimesh.Trimesh(vertices, np.vstack(patches))
    mesh.update_faces(mesh.nondegenerate_faces())
    mesh.remove_unreferenced_vertices()
    return mesh


def _stations(n_x):
    """Normalised stations 0..1, clustered toward the nose."""
    s = np.linspace(0, 1, n_x)
    psi = 0.5 * s + 0.5 * (1 - np.cos(0.5 * np.pi * s))
    psi[-1] = 1.0
    return psi


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

    x = x_base * _stations(n_x)
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

    return closed_body_mesh(X, Z, np.full_like(X, y_top), Y, n_base)


def cst_lifting_body(length, half_span, height, n_planform=0.72, n_height=1.0,
                     n_section=1.0, n_x=200, n_span=121, n_base=24):
    """
    Flat-bottomed lifting body (HTV-2 / DF-ZF style) built from CST-style
    class functions.

    Frame: X aft (nose at x=0, base at x=length), Y up (flat windward bottom at
    y=0), Z spanwise. With psi = x/length and eta = z/z_edge in [-1, 1]:
        planform half-width   z_edge(psi) = half_span * psi**n_planform
        ridge height          h(psi)      = height * psi**n_height
        upper surface         y(psi, eta) = h(psi) * (1 - eta**2)**n_section
    n_section = 1 gives sharp side edges (chines); values < 1 give fuller,
    rounder shoulders.
    """
    psi = _stations(n_x)
    eta = np.linspace(-1, 1, n_span)
    X = np.repeat(length * psi[:, None], n_span, axis=1)
    Z = (half_span * psi ** n_planform)[:, None] * eta[None, :]
    y_upper = (height * psi ** n_height)[:, None] * ((1 - eta ** 2) ** n_section)[None, :]
    return closed_body_mesh(X, Z, y_upper, np.zeros_like(X), n_base)


def upper_surface_height(body, x, z):
    """Y of the body's upper surface at each (x, z), from rays cast down from above."""
    x, z = np.atleast_1d(x).astype(float), np.atleast_1d(z).astype(float)
    origins = np.column_stack([x, np.full(len(x), body.bounds[1][1] + 10.0), z])
    directions = np.tile([0.0, -1.0, 0.0], (len(x), 1))
    hits, ray_idx, _ = body.ray.intersects_location(origins, directions, multiple_hits=False)
    y = np.full(len(x), np.nan)
    y[ray_idx] = hits[:, 1]
    return y


def wing_station_for_chord(body, chord, x_base, z_tip):
    """Spanwise station z where the wing's local chord (leading edge to base) equals `chord`."""
    zs = np.linspace(0.3 * z_tip, z_tip - 1.0, 80)
    chords = []
    for z in zs:
        section = body.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
        chords.append(x_base - section.vertices[:, 0].min())
    # Local chord shrinks toward the tip, so reverse for np.interp
    return float(np.interp(chord, chords[::-1], zs[::-1]))


# Seed weights (NACA 0006 approximation)
SEED_WEIGHTS = np.array([0.0848, 0.0804, 0.0729, 0.0800, 0.0594, 0.0867])
RUDDER = dict(root_chord=800.0, tip_chord=400.0, span=500.0, sweep_le=45.0)
_STAND_UP = trimesh.transformations.rotation_matrix(np.radians(-90), [1, 0, 0])
_MIRROR_Z = trimesh.transformations.reflection_matrix([0, 0, 0], [0, 0, 1])
_TO_Z_UP = trimesh.transformations.rotation_matrix(np.radians(90), [1, 0, 0])


class HGVGeometry:
    """
    A body with a top rudder and two side elevons, re-assembled at any set of
    deflections.

    The fin layout and the body welded to the fixed fin roots are built once;
    assemble() only rebuilds the three moving surfaces, so it is cheap to call
    from an optimizer loop.

    Vehicle frame: X aft, Y up, Z spanwise, body base at max X.
    elevon_flush: 'top' puts the elevons flush with the flat upper surface (OFM
    waverider), 'bottom' flush with the flat lower surface (lifting body).
    Elevon root leading edges sit on the body's side edge and their trailing
    edges run along the base; the moving panels sit fully outboard of the side
    edge. Deflection signs: elevons +ve = trailing edge up, rudder +ve =
    trailing edge toward -Z.
    """

    def __init__(self, body, elevon_flush, weights=SEED_WEIGHTS, rudder=RUDDER,
                 rudder_fixed_fraction=0.15, elevon_root_chord=1000.0,
                 elevon_tip_chord=300.0, elevon_sweep_le=50.0, root_overlap=20.0):
        self.body = body
        self.weights = weights
        x_base, y_top, z_tip = body.bounds[1]
        y_bottom = body.bounds[0][1]
        half_thickness = cst_airfoil(weights)[1].max()

        # Rudder on the centreline at its surface height, averaged along the root;
        # the root extends down far enough to meet the lowest point of the surface.
        self.rudder = dict(rudder, fixed_span_fraction=rudder_fixed_fraction)
        x_rudder = x_base - rudder['root_chord']
        ridge = upper_surface_height(body, np.linspace(x_rudder, x_base - 1.0, 17), np.zeros(17))
        self.rudder_offset = [x_rudder, ridge.mean(), 0.0]
        rudder_overlap = (ridge.mean() - ridge.min()) + root_overlap

        # Elevons: unswept trailing edge, so the leading edge closes the chord
        # difference over the span
        self.elevon_root_z = wing_station_for_chord(body, elevon_root_chord, x_base, z_tip)
        elevon_span = (elevon_root_chord - elevon_tip_chord) / np.tan(np.radians(elevon_sweep_le))
        if self.elevon_root_z + elevon_span <= z_tip:
            raise ValueError("Elevon does not reach past the side edge; lower elevon_sweep_le "
                             "or increase elevon_root_chord.")
        self.elevon = dict(root_chord=elevon_root_chord, tip_chord=elevon_tip_chord,
                           span=elevon_span, sweep_le=elevon_sweep_le,
                           fixed_span_fraction=(z_tip - self.elevon_root_z) / elevon_span)
        self.elevon_exposed_span = self.elevon_root_z + elevon_span - z_tip
        if elevon_flush == 'top':
            y_elevon = y_top - half_thickness * elevon_root_chord
        elif elevon_flush == 'bottom':
            y_elevon = y_bottom + half_thickness * elevon_root_chord
        else:
            raise ValueError("elevon_flush must be 'top' or 'bottom'")
        x_elevon = x_base - elevon_root_chord
        self.left_offset = [x_elevon, y_elevon, -self.elevon_root_z]
        self.right_offset = [x_elevon, y_elevon, self.elevon_root_z]

        r_fixed = generate_fin_mesh(weights, **rudder, z_start=-rudder_overlap,
                                    z_end=rudder['span'] * rudder_fixed_fraction)
        e_planform = {k: v for k, v in self.elevon.items() if k != 'fixed_span_fraction'}
        e_end = elevon_span * self.elevon['fixed_span_fraction']
        self.fixed_parts = {
            'rudder fixed': self._place_rudder(r_fixed),
            'left elevon fixed': self._place_left(
                generate_fin_mesh(weights, **e_planform, z_start=-root_overlap, z_end=e_end)),
            'right elevon fixed': self._place_right(
                generate_fin_mesh(weights, **e_planform, z_start=-root_overlap, z_end=e_end)),
        }
        self._check_volumes({'body': body, **self.fixed_parts})
        self._body_with_roots = None

    def _place_rudder(self, part):
        part.apply_transform(_STAND_UP)       # local span +Z -> +Y
        part.apply_translation(self.rudder_offset)
        return part

    def _place_left(self, part):
        part.apply_transform(_MIRROR_Z)       # extend outboard toward -Z
        part.apply_translation(self.left_offset)
        return part

    def _place_right(self, part):
        part.apply_translation(self.right_offset)
        return part

    @staticmethod
    def _check_volumes(parts):
        for name, part in parts.items():
            if not part.is_volume:
                raise ValueError(
                    f"'{name}' is not a closed volume (watertight={part.is_watertight}, "
                    f"winding consistent={part.is_winding_consistent}). "
                    "Repair the STL (e.g. in MeshLab) before merging.")

    @property
    def body_with_roots(self):
        """Body welded to the fixed fin roots (independent of the deflections)."""
        if self._body_with_roots is None:
            self._body_with_roots = trimesh.boolean.union([self.body, *self.fixed_parts.values()])
        return self._body_with_roots

    def moving_parts(self, elevon_left_deg, elevon_right_deg, rudder_deg):
        """The three all-moving surfaces at the given deflections (degrees)."""
        w = self.weights
        parts = {
            'rudder moving': self._place_rudder(moving_fin_panel(w, **self.rudder, deflection_deg=rudder_deg)),
            'left elevon moving': self._place_left(moving_fin_panel(w, **self.elevon, deflection_deg=elevon_left_deg)),
            'right elevon moving': self._place_right(moving_fin_panel(w, **self.elevon, deflection_deg=elevon_right_deg)),
        }
        self._check_volumes(parts)
        return parts

    def assemble(self, elevon_left_deg, elevon_right_deg, rudder_deg):
        """The whole vehicle as one watertight mesh, in the Y-up vehicle frame."""
        return self._merge(self.moving_parts(elevon_left_deg, elevon_right_deg, rudder_deg))

    def _merge(self, moving):
        merged = trimesh.boolean.union([self.body_with_roots, *moving.values()])
        if merged.body_count > 1:
            print(f"WARNING: result has {merged.body_count} separate bodies; "
                  "a fin is not touching the body. Check the fin layout and root overlap.")
        return merged

    def export(self, output_path, elevon_left_deg, elevon_right_deg, rudder_deg,
               z_up=True, presentation_parts=True, verbose=True):
        """
        Writes the merged vehicle to output_path and returns it (Y-up frame).

        With presentation_parts, also writes <name>_body.stl (body + fixed fin
        roots) and <name>_controls.stl (moving surfaces) so they can be coloured
        separately in CATIA. z_up rotates the written files from the Y-up
        vehicle frame to CATIA's Z-up convention.
        """
        moving = self.moving_parts(elevon_left_deg, elevon_right_deg, rudder_deg)
        merged = self._merge(moving)
        outputs = {output_path: merged}
        if presentation_parts:
            stem = os.path.splitext(output_path)[0]
            outputs[stem + '_body.stl'] = self.body_with_roots
            outputs[stem + '_controls.stl'] = trimesh.util.concatenate(list(moving.values()))
        for path, mesh in outputs.items():
            if z_up:
                mesh = mesh.copy()
                mesh.apply_transform(_TO_Z_UP)
            mesh.export(path)
            if verbose:
                print(f"Saved: {path}")
        return merged


def waverider_geometry(stl_path, remesh=True, **fin_kwargs):
    """HGVGeometry for the OFM waverider STL (elevons flush with its flat top)."""
    body = load_body(stl_path)
    if remesh:
        remeshed = remesh_waverider(body)
        if remeshed.is_volume and abs(remeshed.volume / body.volume - 1) < 0.005:
            body = remeshed
        else:
            print("WARNING: remeshing did not reproduce the body; using the original mesh.")
    return HGVGeometry(body, elevon_flush='top', **fin_kwargs)


def lifting_body_geometry(length=3998.9, half_span=1428.3, height=636.4, n_planform=0.72,
                          n_height=1.0, n_section=1.0, **fin_kwargs):
    """HGVGeometry for the CST lifting body (elevons flush with its flat bottom).
    Defaults match the waverider's length, span, height and planform."""
    body = cst_lifting_body(length, half_span, height, n_planform=n_planform,
                            n_height=n_height, n_section=n_section)
    return HGVGeometry(body, elevon_flush='bottom', **fin_kwargs)
