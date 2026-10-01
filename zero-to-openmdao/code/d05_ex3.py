class MiniComponent:
    def __init__(self):
        self.inputs = {}
        self.outputs = {}
        self.setup()

    def add_input(self, name, val=0.0):
        self.inputs[name] = val

    def add_output(self, name, val=0.0):
        self.outputs[name] = val

    def setup(self):
        pass

    def compute(self, inputs, outputs):
        pass

    def run(self):
        self.compute(self.inputs, self.outputs)


class Lift(MiniComponent):
    def setup(self):
        self.add_input("q", val=1000.0)
        self.add_input("S", val=10.0)
        self.add_input("CL", val=0.5)
        self.add_output("L")

    def compute(self, inputs, outputs):
        outputs["L"] = inputs["q"] * inputs["S"] * inputs["CL"]


lift = Lift()
lift.run()
print(lift.outputs["L"])
lift.inputs["CL"] = 0.8
lift.run()
print(lift.outputs["L"])
