import numpy as np
import openmdao.api as om
from scipy.integrate import solve_ivp


def glider_rates(t, state, alpha, m, S):
    """Flat-Earth glider equations of motion. state = [x, h, v, gamma]."""
    x, h, v, gamma = state
    g = 9.81
    rho = 1.225 * np.exp(-h / 8500.0)
    q = 0.5 * rho * v**2
    CL = 4.0 * alpha
    CD = 0.02 + 0.1 * CL**2
    L = q * S * CL
    D = q * S * CD
    return [v * np.cos(gamma),
            v * np.sin(gamma),
            -D / m - g * np.sin(gamma),
            (L / m - g * np.cos(gamma)) / v]


def reach_ground(t, state, alpha, m, S):
    return state[1]                       # height


reach_ground.terminal = True
reach_ground.direction = -1


class GlideSimulation(om.ExplicitComponent):
    """Flies the glider at a constant angle of attack until it lands."""

    def initialize(self):
        self.options.declare('m', default=500.0, desc='mass, kg')
        self.options.declare('S', default=10.0, desc='wing area, m**2')

    def setup(self):
        self.add_input('alpha', val=0.05, units='rad')
        self.add_input('h0', val=5000.0, units='m')
        self.add_input('v0', val=100.0, units='m/s')
        self.add_output('range', val=0.0, units='m')
        self.add_output('flight_time', val=0.0, units='s')
        self.declare_partials('*', '*', method='fd', step=1e-6, step_calc='rel')

    def compute(self, inputs, outputs):
        alpha = inputs['alpha'][0]
        start = [0.0, inputs['h0'][0], inputs['v0'][0], 0.0]
        sol = solve_ivp(glider_rates, (0.0, 1e5), start,
                        args=(alpha, self.options['m'], self.options['S']),
                        events=reach_ground, rtol=1e-10, atol=1e-8)
        outputs['range'] = sol.y[0, -1]
        outputs['flight_time'] = sol.t[-1]


p = om.Problem()
p.model.add_subsystem('sim', GlideSimulation(m=1000.0), promotes=['*'])

p.driver = om.ScipyOptimizeDriver(optimizer='SLSQP', tol=1e-8)
p.model.add_design_var('alpha', lower=1.0, upper=15.0, units='deg')
p.model.add_objective('range', ref=-1e4)        # negative ref = maximise

p.setup()
p.set_val('alpha', 3.0, units='deg')
p.run_driver()

print(f"Best constant alpha: {p.get_val('alpha', units='deg')[0]:.2f} deg")
print(f"Range: {p.get_val('range', units='km')[0]:.2f} km")
print(f"Flight time: {p.get_val('flight_time')[0]:.0f} s")
