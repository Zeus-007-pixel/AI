import openmdao.api as om


class Paraboloid(om.ExplicitComponent):
    def setup(self):
        self.add_input('x', val=0.0)
        self.add_input('y', val=0.0)
        self.add_output('f', val=0.0)
        # declare_partials line deliberately missing!

    def compute(self, inputs, outputs):
        x = inputs['x']
        y = inputs['y']
        outputs['f'] = (x - 3.0)**2 + x * y + (y + 4.0)**2 - 3.0


p = om.Problem()
p.model.add_subsystem('parab', Paraboloid(), promotes=['*'])
p.model.add_subsystem('con', om.ExecComp('c = x + y'), promotes=['*'])
p.model.set_input_defaults('x', 3.0)
p.model.set_input_defaults('y', -4.0)
p.driver = om.ScipyOptimizeDriver(optimizer='SLSQP', tol=1e-9)
p.model.add_design_var('x', lower=-50.0, upper=50.0)
p.model.add_design_var('y', lower=-50.0, upper=50.0)
p.model.add_objective('f')
p.model.add_constraint('c', lower=0.0)
p.setup()
result = p.run_driver()
print('Success:', result.success)
print('x =', p.get_val('x'), 'y =', p.get_val('y'), 'f =', p.get_val('f'))
