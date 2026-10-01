import openmdao.api as om

p = om.Problem()
p.model.add_subsystem('ratio', om.ExecComp('LD = L / D'), promotes=['*'])
p.setup()
om.n2(p, outfile='my_model_n2.html', show_browser=False)   # set show_browser=True to open it
print('N2 diagram written')
