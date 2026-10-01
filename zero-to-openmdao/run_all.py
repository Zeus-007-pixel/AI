import os, re, subprocess, sys, glob, json

root = os.path.dirname(os.path.abspath(__file__))
code = os.path.join(root, 'code')
outdir = os.path.join(root, 'outputs')
os.makedirs(outdir, exist_ok=True)
env = dict(os.environ, MPLBACKEND='Agg', PYTHONUNBUFFERED='1')

files = sorted(glob.glob(os.path.join(code, '*.py')))
# d04_read_file.py reads the CSV that d04_write_file.py creates, so run it last
files.sort(key=lambda f: os.path.basename(f) == 'd04_read_file.py')
jobs = [(f, code) for f in files]
jobs += [(f, os.path.join(code, 'ex4dir')) for f in sorted(glob.glob(os.path.join(code, 'ex4dir', 'd04_*.py')))]
skip = {'flight_components.py', 'atmos_ex1.py'}
for path, cwd in jobs:
    name = os.path.basename(path)
    if name in skip:
        continue
    r = subprocess.run([sys.executable, path], cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=900)
    text = r.stdout
    lines = [l for l in text.splitlines() if 'INF_BOUND' not in l]
    text = '\n'.join(lines)
    text = text.replace(os.path.join(code, 'ex4dir') + os.sep, '').replace(code + os.sep, '')
    text = re.sub(r'/usr/local/lib/python3\.11/dist-packages/', '.../site-packages/', text)
    open(os.path.join(outdir, name + '.txt'), 'w').write(text.rstrip() + '\n')
    print(f'{name}: exit {r.returncode}, {len(lines)} lines')
