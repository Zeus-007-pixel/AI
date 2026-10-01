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


class Aero(om.ExplicitComponent):
    def initialize(self):
        self.options.declare('S', default=10.0, desc='wing area, m**2')
        self.options.declare('CLa', default=4.0, desc='lift slope, per rad')
        self.options.declare('CD0', default=0.02, desc='zero-lift drag coefficient')
        self.options.declare('k', default=0.1, desc='induced drag factor')

    def setup(self):
        self.add_input('q', val=0.0, units='Pa')
        self.add_input('alpha', val=0.0, units='rad')
        self.add_output('L', val=0.0, units='N')
        self.add_output('D', val=0.0, units='N')
        self.declare_partials('*', '*', method='cs')

    def compute(self, inputs, outputs):
        S = self.options['S']
        CL = self.options['CLa'] * inputs['alpha']
        CD = self.options['CD0'] + self.options['k'] * CL**2
        outputs['L'] = inputs['q'] * S * CL
        outputs['D'] = inputs['q'] * S * CD


class FlightCondition(om.Group):
    def setup(self):
        self.add_subsystem('dynp', DynamicPressure(), promotes=['*'])   # WRONG ORDER
        self.add_subsystem('atmos', Atmosphere(), promotes=['*'])
        self.add_subsystem('aero', Aero(S=10.0), promotes=['*'])


p = om.Problem()
p.model.add_subsystem('flight', FlightCondition(), promotes=['*'])
p.setup()

p.set_val('h', 5000.0)
p.set_val('v', 100.0)
p.set_val('alpha', 3.0, units='deg')
p.run_model()

print(f"rho = {p.get_val('rho')[0]:.4f} kg/m^3")
print(f"q   = {p.get_val('q')[0]:.1f} Pa")
print(f"L   = {p.get_val('L')[0]:.1f} N")
print(f"D   = {p.get_val('D')[0]:.1f} N")
