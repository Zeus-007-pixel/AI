import numpy as np
import openmdao.api as om


class DynamicPressure(om.ExplicitComponent):
    def initialize(self):
        self.options.declare('num_nodes', types=int, default=1)

    def setup(self):
        nn = self.options['num_nodes']
        self.add_input('rho', val=np.ones(nn), units='kg/m**3')
        self.add_input('v', val=np.ones(nn), units='m/s')
        self.add_output('q', val=np.zeros(nn), units='Pa')

        ar = np.arange(nn)                  # [0, 1, 2, ..., nn-1]
        self.declare_partials('q', 'rho', rows=ar, cols=ar)
        self.declare_partials('q', 'v', rows=ar, cols=ar)

    def compute(self, inputs, outputs):
        outputs['q'] = 0.5 * inputs['rho'] * inputs['v']**2

    def compute_partials(self, inputs, partials):
        partials['q', 'rho'] = 0.5 * inputs['v']**2
        partials['q', 'v'] = inputs['rho'] * inputs['v']


nn = 5
p = om.Problem()
p.model.add_subsystem('dynp', DynamicPressure(num_nodes=nn), promotes=['*'])
p.setup(force_alloc_complex=True)

p.set_val('rho', np.array([1.225, 0.6803, 0.3777, 0.1165, 0.0359]))
p.set_val('v', np.array([100.0, 200.0, 400.0, 800.0, 1600.0]))
p.run_model()
print(p.get_val('q'))

p.check_partials(method='cs', compact_print=True, show_only_incorrect=True)
print('Derivative check finished. Any wrong derivatives are listed above.')
