import openmdao.api as om


class DynamicPressure(om.ExplicitComponent):
    def setup(self):
        self.add_input('rho', val=1.225, units='kg/m**3')
        self.add_input('v', val=100.0, units='m/s')
        self.add_output('q', val=0.0, units='Pa')
        self.declare_partials('*', '*', method='cs')

    def compute(self, inputs, outputs):
        outputs['q'] = 0.5 * inputs['rho'] * inputs['v']**2


p = om.Problem()
p.model.add_subsystem('dynp', DynamicPressure(), promotes=['*'])
p.setup()
p.set_val('rho', 0.0184)
p.set_val('v', 2000.0)
p.run_model()

print(p.get_val('q', units='Pa'))
print(p.get_val('q', units='kPa'))
print(p.get_val('q', units='psi'))
print(p.get_val('q', units='atm'))
