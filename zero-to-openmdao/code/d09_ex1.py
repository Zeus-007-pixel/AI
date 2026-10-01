import openmdao.api as om


class Weight(om.ExplicitComponent):
    def initialize(self):
        self.options.declare('g', default=9.81)

    def setup(self):
        self.add_input('m', val=1.0, units='kg')
        self.add_output('W', val=0.0, units='N')
        self.declare_partials('*', '*', method='cs')

    def compute(self, inputs, outputs):
        outputs['W'] = inputs['m'] * self.options['g']


class Lift(om.ExplicitComponent):
    def initialize(self):
        self.options.declare('S', default=10.0)

    def setup(self):
        self.add_input('q', val=1000.0, units='Pa')
        self.add_input('CL', val=0.5)
        self.add_output('L', val=0.0, units='N')
        self.declare_partials('*', '*', method='cs')

    def compute(self, inputs, outputs):
        outputs['L'] = inputs['q'] * self.options['S'] * inputs['CL']


class LiftCheck(om.Group):
    def setup(self):
        self.add_subsystem('weight', Weight(), promotes=['*'])
        self.add_subsystem('lift', Lift(S=10.0), promotes=['*'])
        self.add_subsystem('excess',
                           om.ExecComp('dL = L - W', dL={'units': 'N'},
                                       L={'units': 'N'}, W={'units': 'N'}),
                           promotes=['*'])


p = om.Problem()
p.model.add_subsystem('check', LiftCheck(), promotes=['*'])
p.setup()
p.set_val('m', 500.0)
p.set_val('q', 1531.25)
p.set_val('CL', 0.32)
p.run_model()
print(f"W = {p.get_val('W')[0]:.1f} N, L = {p.get_val('L')[0]:.1f} N, L - W = {p.get_val('dL')[0]:.1f} N")
