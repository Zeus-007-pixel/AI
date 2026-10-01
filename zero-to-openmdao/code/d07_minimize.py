from scipy.optimize import minimize


def f(xy):
    x, y = xy                      # xy holds two numbers; unpack them
    return (x - 3.0)**2 + x * y + (y + 4.0)**2 - 3.0


result = minimize(f, x0=[3.0, -4.0], method="SLSQP")
print(result.x, result.fun)


def x_plus_y(xy):
    return xy[0] + xy[1]           # SciPy keeps this >= 0


con = {"type": "ineq", "fun": x_plus_y}
result = minimize(f, x0=[3.0, -4.0], method="SLSQP", constraints=[con])
print(result.x, result.fun)
