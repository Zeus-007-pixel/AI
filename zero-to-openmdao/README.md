# Zero to OpenMDAO

A 15-day crash course that takes a complete beginner from a first Python program to
OpenMDAO optimization and a first Dymos trajectory optimization.

- `zero-to-openmdao.html` is the finished course page. Open it in a browser.
- `code/` holds every example and exercise solution from the course, named by day
  (`d01_hello.py`, `d10_slowest.py`, ...). `atmos.py` and `flight_components.py` are
  modules that later days import. The Day 4 exercise files that use the extended
  `atmos.py` are in `code/ex4dir/`.
- `outputs/` holds the real output of each script, which the page shows under the code.
- `src/` holds the page fragments, one per day.

Rebuild the page after editing a fragment or a script:

```
python run_all.py   # run every script and save its output
python build.py     # assemble zero-to-openmdao.html
```

Tested with Python 3.11, NumPy 2.4, SciPy 1.17, Matplotlib 3.11, OpenMDAO 3.45.1, Dymos 1.15.1.
