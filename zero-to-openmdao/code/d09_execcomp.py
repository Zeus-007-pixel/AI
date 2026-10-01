import openmdao.api as om

p = om.Problem()
p.model.add_subsystem('ratio', om.ExecComp('LD = L / D'), promotes=['*'])
p.model.add_subsystem('excess',
                      om.ExecComp('dL = L - m * g',
                                  dL={'units': 'N'},
                                  L={'units': 'N'},
                                  m={'units': 'kg'},
                                  g={'units': 'm/s**2', 'val': 9.81}),
                      promotes=['*'])
p.model.set_input_defaults('L', 5000.0, units='N')
p.setup()

p.set_val('D', 450.0)
p.set_val('m', 500.0)
p.run_model()
print(p.get_val('LD'), p.get_val('dL'))
