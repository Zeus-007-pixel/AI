import openmdao.api as om


class Paraboloid(om.ExplicitComponent):
    """f(x, y) = (x - 3)^2 + x*y + (y + 4)^2 - 3"""

    def setup(self):
        self.add_input('x', val=0.0)
        self.add_input('y', val=0.0)
        self.add_output('f', val=0.0)
        self.declare_partials('*', '*', method='cs')

    def compute(self, inputs, outputs):
        x = inputs['x']
        y = inputs['y']
        outputs['f'] = (x - 3.0)**2 + x * y + (y + 4.0)**2 - 3.0


p = om.Problem()
p.model.add_subsystem('parab', Paraboloid(), promotes=['*'])
p.setup()

p.set_val('x', 3.0)
p.set_val('y', -4.0)
p.run_model()
print(p.get_val('f'))

p.set_val('x', 5.0)
p.set_val('y', -2.0)
p.run_model()
print(p.get_val('f'))
print(p.get_val('f')[0])
