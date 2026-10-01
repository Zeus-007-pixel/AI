import openmdao.api as om
from flight_components import FlightCondition

p = om.Problem()
p.model.add_subsystem('flight', FlightCondition(), promotes=['*'])
p.model.add_subsystem('ratio',
                      om.ExecComp('LD = L / D', L={'units': 'N'}, D={'units': 'N'}),
                      promotes=['*'])

p.driver = om.ScipyOptimizeDriver(optimizer='SLSQP', tol=1e-9)
p.model.add_design_var('alpha', lower=0.5, upper=20.0, units='deg')
p.model.add_objective('LD', scaler=-1.0)          # scaler=-1 turns "minimise" into "maximise"

p.setup()
p.set_val('h', 0.0)
p.set_val('v', 50.0)
p.set_val('alpha', 2.0, units='deg')
p.run_driver()

print(f"Best alpha: {p.get_val('alpha', units='deg')[0]:.2f} deg")
print(f"Best L/D:   {p.get_val('LD')[0]:.3f}")
