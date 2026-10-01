import openmdao.api as om
from flight_components import FlightCondition

p = om.Problem()
p.model.add_subsystem('flight', FlightCondition(), promotes=['*'])
p.model.add_subsystem('excess',
                      om.ExecComp('dL = L - m * g',
                                  dL={'units': 'N'}, L={'units': 'N'},
                                  m={'units': 'kg', 'val': 500.0},
                                  g={'units': 'm/s**2', 'val': 9.81}),
                      promotes=['*'])

p.driver = om.ScipyOptimizeDriver(optimizer='SLSQP', tol=1e-8)

p.model.add_design_var('v', lower=5.0, upper=300.0, units='m/s')
p.model.add_design_var('alpha', lower=0.0, upper=12.0, units='deg')
p.model.add_objective('v', ref=10.0)
p.model.add_constraint('dL', lower=0.0, ref=1000.0)

p.setup()
p.set_val('h', 0.0)
p.set_val('v', 100.0)
p.set_val('alpha', 2.0, units='deg')

result = p.run_driver()
print('Success:', result.success)
print(f"Slowest speed: {p.get_val('v')[0]:.2f} m/s")
print(f"Angle of attack: {p.get_val('alpha', units='deg')[0]:.2f} deg")
print(f"Lift minus weight: {p.get_val('dL')[0]:.3f} N")
