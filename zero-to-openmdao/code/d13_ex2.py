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
p.set_val('W', 4905.0)
p.set_val('v', 50.0)

for h in [0.0, 5000.0, 10000.0]:
    p.set_val('h', h)
    p.run_model()
    print(f"h = {h/1000:4.1f} km -> trim alpha = {p.get_val('alpha', units='deg')[0]:6.3f} deg")
