class MiniComponent:
    """A tiny imitation of OpenMDAO's ExplicitComponent."""

    def __init__(self):
        self.inputs = {}
        self.outputs = {}
        self.setup()                    # the framework calls YOUR setup

    def add_input(self, name, val=0.0):
        self.inputs[name] = val

    def add_output(self, name, val=0.0):
        self.outputs[name] = val

    def setup(self):
        pass                            # empty: subclasses fill this in

    def compute(self, inputs, outputs):
        pass                            # empty: subclasses fill this in

    def run(self):
        self.compute(self.inputs, self.outputs)   # the framework calls YOUR compute


class DynamicPressure(MiniComponent):
    def setup(self):
        self.add_input("rho", val=1.225)
        self.add_input("v", val=100.0)
        self.add_output("q")

    def compute(self, inputs, outputs):
        outputs["q"] = 0.5 * inputs["rho"] * inputs["v"] ** 2


comp = DynamicPressure()        # __init__ runs, and it calls setup()
comp.inputs["v"] = 2000.0
comp.inputs["rho"] = 0.0184
comp.run()                      # run() calls compute()
print(comp.outputs)
