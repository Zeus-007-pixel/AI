import openmdao.api as om


class DynamicPressure(om.ExplicitComponent):
    def setup(self):
        self.add_input('rho', val=1.225, units='kg/m**3')
        self.add_input('v', val=100.0, units='m/s')
        self.add_output('q', val=0.0, units='Pa')
        self.declare_partials('q', 'rho')       # no method: we will supply the formula
        self.declare_partials('q', 'v')

    def compute(self, inputs, outputs):
        outputs['q'] = 0.5 * inputs['rho'] * inputs['v']**2

    def compute_partials(self, inputs, partials):
        rho = inputs['rho']
        v = inputs['v']
        partials['q', 'rho'] = 0.5 * v**2        # dq/drho
        partials['q', 'v'] = rho * v             # dq/dv


p = om.Problem()
p.model.add_subsystem('dynp', DynamicPressure(), promotes=['*'])
p.setup(force_alloc_complex=True)
p.set_val('rho', 0.0184)
p.set_val('v', 2000.0)
p.run_model()

p.check_partials(method='cs', compact_print=True, show_only_incorrect=True)
print('Derivative check finished. Any wrong derivatives are listed above.')
