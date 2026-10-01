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

for h in [0.0, 5000.0, 10000.0]:
    p.set_val('h', h)
    p.set_val('v', 100.0)
    p.set_val('alpha', 2.0, units='deg')
    p.run_driver()
    print(f"h = {h/1000:4.1f} km: slowest speed {p.get_val('v')[0]:.2f} m/s")
