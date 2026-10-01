import numpy as np
import openmdao.api as om


class Atmosphere(om.ExplicitComponent):
    def setup(self):
        self.add_input('h', val=0.0, units='m')
        self.add_output('rho', val=1.225, units='kg/m**3')
        self.declare_partials('*', '*', method='cs')

    def compute(self, inputs, outputs):
        outputs['rho'] = 1.225 * np.exp(-inputs['h'] / 8500.0)


class DynamicPressure(om.ExplicitComponent):
    def setup(self):
        self.add_input('rho', val=1.225, units='kg/m**3')
        self.add_input('v', val=100.0, units='m/s')
        self.add_output('q', val=0.0, units='Pa')
        self.declare_partials('*', '*', method='cs')

    def compute(self, inputs, outputs):
        outputs['q'] = 0.5 * inputs['rho'] * inputs['v']**2


p = om.Problem()
p.model.add_subsystem('atmos', Atmosphere())
p.model.add_subsystem('dynp', DynamicPressure())
p.model.connect('atmos.rho', 'dynp.rho')        # output -> input, by full path
p.setup()

p.set_val('atmos.h', 5000.0)
p.set_val('dynp.v', 100.0)
p.run_model()
print(p.get_val('dynp.q'))
