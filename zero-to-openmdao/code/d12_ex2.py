import numpy as np
import openmdao.api as om


class GliderODE(om.ExplicitComponent):
    def initialize(self):
        self.options.declare('num_nodes', types=int)

    def setup(self):
        nn = self.options['num_nodes']
        self.add_input('h', val=np.ones(nn), units='m')
        self.add_input('v', val=np.ones(nn), units='m/s')
        self.add_input('gamma', val=np.zeros(nn), units='rad')
        self.add_input('alpha', val=np.zeros(nn), units='rad')
        self.add_input('m', val=np.ones(nn), units='kg')
        self.add_input('S', val=np.ones(nn), units='m**2')

        self.add_output('x_dot', val=np.zeros(nn), units='m/s')
        self.add_output('h_dot', val=np.zeros(nn), units='m/s')
        self.add_output('v_dot', val=np.zeros(nn), units='m/s**2')
        self.add_output('gamma_dot', val=np.zeros(nn), units='rad/s')
        self.add_output('q', val=np.zeros(nn), units='Pa')
        self.add_output('n', val=np.zeros(nn))            # load factor L/W (no units)

        self.declare_coloring(wrt='*', method='cs')

    def compute(self, inputs, outputs):
        h, v, gamma = inputs['h'], inputs['v'], inputs['gamma']
        alpha, m, S = inputs['alpha'], inputs['m'], inputs['S']
        g = 9.81

        rho = 1.225 * np.exp(-h / 8500.0)
        q = 0.5 * rho * v**2
        CL = 4.0 * alpha
        CD = 0.02 + 0.1 * CL**2
        L = q * S * CL
        D = q * S * CD

        outputs['x_dot'] = v * np.cos(gamma)
        outputs['h_dot'] = v * np.sin(gamma)
        outputs['v_dot'] = -D / m - g * np.sin(gamma)
        outputs['gamma_dot'] = (L / m - g * np.cos(gamma)) / v
        outputs['q'] = q
        outputs['n'] = L / (m * g)


nn = 3
p = om.Problem()
p.model.add_subsystem('ode', GliderODE(num_nodes=nn), promotes=['*'])
p.setup()
p.set_val('h', [5000.0, 3000.0, 1000.0])
p.set_val('v', [100.0, 80.0, 60.0])
p.set_val('gamma', np.radians([0.0, -5.0, -5.0]))
p.set_val('alpha', np.radians([3.0, 6.0, 9.0]))
p.set_val('m', 500.0 * np.ones(nn))
p.set_val('S', 10.0 * np.ones(nn))
p.run_model()
print('load factor n =', p.get_val('n'))
