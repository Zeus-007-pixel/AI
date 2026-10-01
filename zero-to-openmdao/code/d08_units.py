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

p.set_val('rho', 0.0184)                 # no units given: uses kg/m**3
p.set_val('v', 7200.0, units='km/h')     # OpenMDAO converts km/h to m/s for you
p.run_model()

print(p.get_val('v'))                    # stored in the component's own units
print(p.get_val('q'))                    # in Pa
print(p.get_val('q', units='kPa'))       # converted on the way out
