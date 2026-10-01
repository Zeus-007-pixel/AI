import openmdao.api as om


class Aero(om.ExplicitComponent):
    def initialize(self):
        self.options.declare('S', default=10.0)
        self.options.declare('CLa', default=4.0)
        self.options.declare('CD0', default=0.02)
        self.options.declare('k', default=0.1)

    def setup(self):
        self.add_input('q', val=0.0, units='Pa')
        self.add_input('alpha', val=0.0, units='rad')
        self.add_output('L', val=0.0, units='N')
        self.add_output('D', val=0.0, units='N')
        self.declare_partials(['L', 'D'], ['q', 'alpha'])

    def compute(self, inputs, outputs):
        S, CLa = self.options['S'], self.options['CLa']
        CD0, k = self.options['CD0'], self.options['k']
        q, alpha = inputs['q'], inputs['alpha']
        CL = CLa * alpha
        outputs['L'] = q * S * CL
        outputs['D'] = q * S * (CD0 + k * CL**2)

    def compute_partials(self, inputs, partials):
        S, CLa = self.options['S'], self.options['CLa']
        CD0, k = self.options['CD0'], self.options['k']
        q, alpha = inputs['q'], inputs['alpha']
        CL = CLa * alpha
        partials['L', 'q'] = S * CL
        partials['L', 'alpha'] = q * S * CLa
        partials['D', 'q'] = S * (CD0 + k * CL**2)
        partials['D', 'alpha'] = q * S * 2.0 * k * CL * CLa


p = om.Problem()
p.model.add_subsystem('aero', Aero(), promotes=['*'])
p.setup(force_alloc_complex=True)
p.set_val('q', 3401.25)
p.set_val('alpha', 0.05)
p.run_model()
p.check_partials(method='cs', compact_print=True, show_only_incorrect=True)
print('Derivative check finished. Any wrong derivatives are listed above.')
