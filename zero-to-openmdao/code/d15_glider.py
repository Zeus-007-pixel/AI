import numpy as np
import matplotlib.pyplot as plt
import openmdao.api as om
import dymos as dm


# ---------------------------------------------------------------- 1. THE ODE
class GliderODE(om.ExplicitComponent):
    """2D glider over a flat Earth. Given states + controls, return state rates."""

    def initialize(self):
        self.options.declare('num_nodes', types=int)

    def setup(self):
        nn = self.options['num_nodes']
        # states
        self.add_input('h', val=np.ones(nn), units='m')
        self.add_input('v', val=np.ones(nn), units='m/s')
        self.add_input('gamma', val=np.zeros(nn), units='rad')
        # control
        self.add_input('alpha', val=np.zeros(nn), units='rad')
        # parameters (fixed design values)
        self.add_input('m', val=np.ones(nn), units='kg')
        self.add_input('S', val=np.ones(nn), units='m**2')

        # state rates
        self.add_output('x_dot', val=np.zeros(nn), units='m/s')
        self.add_output('h_dot', val=np.zeros(nn), units='m/s')
        self.add_output('v_dot', val=np.zeros(nn), units='m/s**2')
        self.add_output('gamma_dot', val=np.zeros(nn), units='rad/s')
        # extra output we want to constrain/plot
        self.add_output('q', val=np.zeros(nn), units='Pa')

        self.declare_coloring(wrt='*', method='cs')

    def compute(self, inputs, outputs):
        h, v, gamma = inputs['h'], inputs['v'], inputs['gamma']
        alpha, m, S = inputs['alpha'], inputs['m'], inputs['S']
        g = 9.81

        rho = 1.225 * np.exp(-h / 8500.0)        # simple exponential atmosphere
        q = 0.5 * rho * v**2                     # dynamic pressure
        CL = 4.0 * alpha                         # lift curve slope (per rad)
        CD = 0.02 + 0.1 * CL**2                  # drag polar
        L = q * S * CL
        D = q * S * CD

        outputs['x_dot'] = v * np.cos(gamma)
        outputs['h_dot'] = v * np.sin(gamma)
        outputs['v_dot'] = -D / m - g * np.sin(gamma)
        outputs['gamma_dot'] = (L / m - g * np.cos(gamma)) / v
        outputs['q'] = q


# ---------------------------------------------------------------- 2. PROBLEM + OPTIMIZER
p = om.Problem()
p.driver = om.ScipyOptimizeDriver(optimizer='SLSQP', maxiter=300)
p.driver.declare_coloring()

# ---------------------------------------------------------------- 3. TRAJECTORY + PHASE
traj = p.model.add_subsystem('traj', dm.Trajectory())
phase = traj.add_phase('glide', dm.Phase(ode_class=GliderODE,
                                         transcription=dm.Radau(num_segments=15, order=3)))

# time
phase.set_time_options(fix_initial=True, duration_bounds=(10, 5000), duration_ref=100, units='s')

# states
phase.add_state('x', rate_source='x_dot', units='m', fix_initial=True, ref=1e4)
phase.add_state('h', rate_source='h_dot', units='m', fix_initial=True, lower=0, ref=1e3)
phase.add_state('v', rate_source='v_dot', units='m/s', fix_initial=True, lower=10, ref=100)
phase.add_state('gamma', rate_source='gamma_dot', units='rad', fix_initial=True,
                lower=-np.pi / 2, upper=np.pi / 2)

# control
phase.add_control('alpha', units='deg', lower=-5, upper=15, rate_continuity=True)

# parameters
phase.add_parameter('m', units='kg', val=500.0, opt=False)
phase.add_parameter('S', units='m**2', val=10.0, opt=False)

# constraints
phase.add_boundary_constraint('h', loc='final', equals=0.0, units='m')
phase.add_path_constraint('q', upper=20000.0, units='Pa', ref=1e4)
phase.add_path_constraint('alpha', upper=15.0, units='deg')   # enforce the limit everywhere

# objective: maximize final x  (minimize -x)
phase.add_objective('x', loc='final', ref=-1e4)

# extra things to record
phase.add_timeseries_output('q')

p.setup()

# ---------------------------------------------------------------- 4. INITIAL GUESS
phase.set_time_val(initial=0.0, duration=600.0)
phase.set_state_val('x', [0.0, 50000.0])
phase.set_state_val('h', [5000.0, 0.0])
phase.set_state_val('v', [100.0, 60.0])
phase.set_state_val('gamma', [0.0, -0.1])
phase.set_control_val('alpha', [3.0, 3.0], units='deg')

# ---------------------------------------------------------------- 5. RUN
dm.run_problem(p, simulate=True, make_plots=True)

# ---------------------------------------------------------------- 6. RESULTS
t = p.get_val('traj.glide.timeseries.time')
x = p.get_val('traj.glide.timeseries.x', units='km')
h = p.get_val('traj.glide.timeseries.h', units='km')
a = p.get_val('traj.glide.timeseries.alpha', units='deg')
print(f'flight time {t[-1, 0]:.1f} s, range {x[-1, 0]:.2f} km, final h {h[-1, 0]:.4f} km')
print(f'alpha between {a.min():.2f} and {a.max():.2f} deg')

# ---------------------------------------------------------------- 7. PLOTS
plt.figure()
plt.plot(x, h)
plt.xlabel('Downrange (km)')
plt.ylabel('Altitude (km)')
plt.title('Optimal glide path')
plt.grid(True)
plt.savefig('glide_path.png', dpi=150)

plt.figure()
plt.plot(t, a)
plt.xlabel('Time (s)')
plt.ylabel('Angle of attack (deg)')
plt.title('Optimal angle of attack')
plt.grid(True)
plt.savefig('glide_alpha.png', dpi=150)
plt.show()
