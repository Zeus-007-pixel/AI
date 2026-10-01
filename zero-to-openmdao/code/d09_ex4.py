import openmdao.api as om
from flight_components import Atmosphere, DynamicPressure, Aero

p = om.Problem()
model = p.model
model.add_subsystem('atmos', Atmosphere())
model.add_subsystem('dynp', DynamicPressure())
model.add_subsystem('aero', Aero(S=10.0))
model.connect('atmos.rho', 'dynp.rho')
model.connect('dynp.q', 'aero.q')
p.setup()

p.set_val('atmos.h', 5000.0)
p.set_val('dynp.v', 100.0)
p.set_val('aero.alpha', 3.0, units='deg')
p.run_model()
print(f"L = {p.get_val('aero.L')[0]:.1f} N, D = {p.get_val('aero.D')[0]:.1f} N")
