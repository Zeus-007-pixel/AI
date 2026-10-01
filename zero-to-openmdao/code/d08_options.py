import openmdao.api as om


class Lift(om.ExplicitComponent):
    def initialize(self):
        self.options.declare('S', default=10.0, desc='reference area in m**2')

    def setup(self):
        self.add_input('q', val=1000.0, units='Pa')
        self.add_input('CL', val=0.5)
        self.add_output('L', val=0.0, units='N')
        self.declare_partials('*', '*', method='cs')

    def compute(self, inputs, outputs):
        S = self.options['S']
        outputs['L'] = inputs['q'] * S * inputs['CL']


p = om.Problem()
p.model.add_subsystem('big_wing', Lift(S=20.0))       # set the option here
p.model.add_subsystem('small_wing', Lift())           # uses the default, 10.0
p.setup()
p.run_model()

print(p.get_val('big_wing.L'))
print(p.get_val('small_wing.L'))
p.model.list_outputs()
