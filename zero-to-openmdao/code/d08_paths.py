import openmdao.api as om


class Paraboloid(om.ExplicitComponent):
    def setup(self):
        self.add_input('x', val=0.0)
        self.add_input('y', val=0.0)
        self.add_output('f', val=0.0)
        self.declare_partials('*', '*', method='cs')

    def compute(self, inputs, outputs):
        outputs['f'] = (inputs['x'] - 3.0)**2 + inputs['x'] * inputs['y'] + (inputs['y'] + 4.0)**2 - 3.0


p = om.Problem()
p.model.add_subsystem('parab', Paraboloid())     # no promotes this time
p.setup()

p.set_val('parab.x', 3.0)                        # full "path" names
p.set_val('parab.y', -4.0)
p.run_model()
print(p.get_val('parab.f'))
