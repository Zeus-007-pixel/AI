"""
OpenMDAO wrapper for the control-surface geometry.

Inputs are the three deflection angles; each evaluation re-assembles the
vehicle, optionally writes it to an STL for the aero/CFD step, and outputs
the vehicle's volume and wetted area. Only the moving surfaces are rebuilt per
evaluation; the body and fixed fin roots are built once in HGVGeometry.
"""
import openmdao.api as om

from hgv_geometry import HGVGeometry, lifting_body_geometry, waverider_geometry


class ControlSurfaceGeometry(om.ExplicitComponent):
    """Deflections (deg) in -> merged vehicle STL + volume and wetted area out."""

    def initialize(self):
        self.options.declare('geometry', types=HGVGeometry, recordable=False,
                             desc='Body + fin layout, e.g. from lifting_body_geometry()')
        self.options.declare('stl_path', default=None, types=str, allow_none=True,
                             desc='Write the merged vehicle here on every evaluation')
        self.options.declare('z_up', default=False, types=bool,
                             desc='Write the STL Z-up (CATIA) instead of the Y-up vehicle frame')

    def setup(self):
        self.add_input('elevon_left_deflection', val=0.0, units='deg',
                       desc='Left (-Z) elevon, +ve = trailing edge up')
        self.add_input('elevon_right_deflection', val=0.0, units='deg',
                       desc='Right (+Z) elevon, +ve = trailing edge up')
        self.add_input('rudder_deflection', val=0.0, units='deg',
                       desc='Rudder, +ve = trailing edge toward -Z')
        self.add_output('volume', val=0.0, units='mm**3')
        self.add_output('wetted_area', val=0.0, units='mm**2')
        self.add_discrete_output('stl_file', val='', desc='Path of the STL written this evaluation')
        # The mesh has no analytic derivatives, so use finite differences
        self.declare_partials(['volume', 'wetted_area'], '*', method='fd',
                              step=0.25, step_calc='abs')

    def compute(self, inputs, outputs, discrete_inputs, discrete_outputs):
        geometry = self.options['geometry']
        angles = (inputs['elevon_left_deflection'].item(),
                  inputs['elevon_right_deflection'].item(),
                  inputs['rudder_deflection'].item())
        stl_path = self.options['stl_path']
        if stl_path:
            merged = geometry.export(stl_path, *angles, z_up=self.options['z_up'],
                                     presentation_parts=False, verbose=False)
        else:
            merged = geometry.assemble(*angles)
        outputs['volume'] = merged.volume
        outputs['wetted_area'] = merged.area
        discrete_outputs['stl_file'] = stl_path or ''


if __name__ == '__main__':
    # Example: one evaluation of the geometry inside an OpenMDAO problem.
    # In your optimisation, connect your aero/CFD component to 'stl_file' (or
    # read the STL it names), add your objective and constraints, and set a driver.
    import sys
    vehicle = sys.argv[1] if len(sys.argv) > 1 else 'lifting_body'
    if vehicle == 'waverider':
        geometry = waverider_geometry(r"C:\Users\Rizwan computers\OneDrive\Desktop\Final Year Project\Claude\src\hgv\geometry\waverider_mm.stl")
    else:
        geometry = lifting_body_geometry()

    prob = om.Problem()
    prob.model.add_subsystem('geometry', ControlSurfaceGeometry(geometry=geometry,
                                                                stl_path=f'{vehicle}_current.stl'),
                             promotes=['*'])
    prob.model.add_design_var('elevon_left_deflection', lower=-20.0, upper=20.0)
    prob.model.add_design_var('elevon_right_deflection', lower=-20.0, upper=20.0)
    prob.model.add_design_var('rudder_deflection', lower=-20.0, upper=20.0)
    prob.setup()

    prob.set_val('elevon_left_deflection', 5.0, units='deg')
    prob.set_val('elevon_right_deflection', -5.0, units='deg')
    prob.set_val('rudder_deflection', 12.0, units='deg')
    prob.run_model()
    print('STL:', prob.get_val('stl_file'))
    print('volume [m^3]:', prob.get_val('volume', units='m**3').item())
    print('wetted area [m^2]:', prob.get_val('wetted_area', units='m**2').item())
