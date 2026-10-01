import numpy as np
import openmdao.api as om


class Atmosphere(om.ExplicitComponent):
    def setup(self):
        self.add_input('h', val=0.0, units='m')
        self.add_output('rho', val=1.225, units='kg/m**3')
        self.declare_partials('*', '*', method='cs')

    def compute(self, inputs, outputs):
        outputs['rho'] = 1.225 * np.exp(-inputs['h'] / 8500.0)


p = om.Problem()
p.model.add_subsystem('atmos', Atmosphere(), promotes=['*'])
p.setup()

p.set_val('h', 8500.0)
p.run_model()
print(p.get_val('rho'))

p.set_val('h', 30.0, units='km')
p.run_model()
print(p.get_val('rho'))
