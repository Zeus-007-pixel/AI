import openmdao.api as om
import matplotlib.pyplot as plt


class Paraboloid(om.ExplicitComponent):
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
p.driver = om.ScipyOptimizeDriver(optimizer='SLSQP', tol=1e-9)
p.model.add_design_var('x', lower=-50.0, upper=50.0)
p.model.add_design_var('y', lower=-50.0, upper=50.0)
p.model.add_objective('f')

p.driver.add_recorder(om.SqliteRecorder('cases.sql'))   # save every iteration

p.setup()
p.set_val('x', 30.0)
p.set_val('y', 30.0)
p.run_driver()

reader = om.CaseReader(p.get_outputs_dir() / 'cases.sql')
cases = reader.get_cases('driver')

f_history = []
for case in cases:
    f_history.append(case.get_val('f')[0])

print(f"{len(cases)} iterations recorded")
print(f"first f = {f_history[0]:.2f}, last f = {f_history[-1]:.4f}")

plt.plot(f_history, marker='o')
plt.xlabel('Iteration')
plt.ylabel('Objective f')
plt.title('Optimizer progress')
plt.grid(True)
plt.savefig('history.png', dpi=150)
plt.show()
