import openmdao.api as om


class Weight(om.ExplicitComponent):
    def initialize(self):
        self.options.declare('g', default=9.81, desc='gravity in m/s**2')

    def setup(self):
        self.add_input('m', val=1.0, units='kg')
        self.add_output('W', val=0.0, units='N')
        self.declare_partials('*', '*', method='cs')

    def compute(self, inputs, outputs):
        outputs['W'] = inputs['m'] * self.options['g']


p = om.Problem()
p.model.add_subsystem('earth', Weight())
p.model.add_subsystem('moon', Weight(g=1.62))
p.setup()
p.set_val('earth.m', 1000.0)
p.set_val('moon.m', 1000.0)
p.run_model()
print(p.get_val('earth.W'), p.get_val('moon.W'))
print(p.get_val('earth.W', units='kN'))
