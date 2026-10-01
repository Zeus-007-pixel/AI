import numpy as np
import openmdao.api as om


class Atmosphere(om.ExplicitComponent):
    def initialize(self):
        self.options.declare('num_nodes', types=int, default=1)

    def setup(self):
        nn = self.options['num_nodes']
        self.add_input('h', val=np.zeros(nn), units='m')
        self.add_output('rho', val=np.ones(nn), units='kg/m**3')
        ar = np.arange(nn)
        self.declare_partials('rho', 'h', rows=ar, cols=ar)

    def compute(self, inputs, outputs):
        outputs['rho'] = 1.225 * np.exp(-inputs['h'] / 8500.0)

    def compute_partials(self, inputs, partials):
        partials['rho', 'h'] = -1.225 / 8500.0 * np.exp(-inputs['h'] / 8500.0)


nn = 4
p = om.Problem()
p.model.add_subsystem('atmos', Atmosphere(num_nodes=nn), promotes=['*'])
p.setup(force_alloc_complex=True)
p.set_val('h', np.linspace(0, 30000, nn))
p.run_model()
print(p.get_val('rho'))
p.check_partials(method='cs', compact_print=True, show_only_incorrect=True)
print('Derivative check finished. Any wrong derivatives are listed above.')
