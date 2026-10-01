import openmdao.api as om
from flight_components import FlightCondition

p = om.Problem()
model = p.model
model.add_subsystem('flight', FlightCondition(), promotes=['*'])

bal = om.BalanceComp()
bal.add_balance('alpha', units='rad', val=0.05, lhs_name='L', rhs_name='W', eq_units='N')
model.add_subsystem('trim', bal, promotes=['*'])

model.nonlinear_solver = om.NewtonSolver(solve_subsystems=True, maxiter=20, iprint=0)
model.linear_solver = om.DirectSolver()

p.setup()
p.set_val('h', 0.0)
p.set_val('W', 4905.0)

for v in [40.0, 50.0, 80.0, 120.0]:
    p.set_val('v', v)
    p.run_model()
    print(f"v = {v:5.1f} m/s -> trim alpha = {p.get_val('alpha', units='deg')[0]:6.3f} deg")
