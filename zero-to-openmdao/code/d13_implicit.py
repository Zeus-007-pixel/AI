import numpy as np
import openmdao.api as om
from flight_components import FlightCondition


class LiftEqualsWeight(om.ImplicitComponent):
    """Finds the angle of attack 'alpha' that makes lift equal weight."""

    def setup(self):
        self.add_input('L', val=0.0, units='N')
        self.add_input('W', val=0.0, units='N')
        self.add_output('alpha', val=0.05, units='rad')
        self.declare_partials('alpha', ['L', 'W'], method='cs')

    def apply_nonlinear(self, inputs, outputs, residuals):
        # the residual must become ZERO when the answer is right
        residuals['alpha'] = inputs['L'] - inputs['W']


p = om.Problem()
model = p.model
model.add_subsystem('flight', FlightCondition(), promotes=['*'])
model.add_subsystem('trim', LiftEqualsWeight(), promotes=['*'])

model.nonlinear_solver = om.NewtonSolver(solve_subsystems=True, maxiter=20, iprint=2)
model.linear_solver = om.DirectSolver()

p.setup()
p.set_val('h', 0.0)
p.set_val('v', 50.0)
p.set_val('W', 4905.0)
p.run_model()

print(f"Trim angle of attack: {p.get_val('alpha', units='deg')[0]:.3f} deg")
print(f"Lift: {p.get_val('L')[0]:.3f} N")
