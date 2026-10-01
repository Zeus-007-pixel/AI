"""Assemble the course page from HTML fragments, tested code files and their real outputs."""
import base64
import html
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
CODE = os.path.join(ROOT, 'code')
OUT = os.path.join(ROOT, 'outputs')
SRC = os.path.join(ROOT, 'src')

PARTS = ['head.html', 'intro.html'] + [f'day{n:02d}.html' for n in range(1, 16)] + ['end.html']


def find_code(name):
    for folder in (CODE, os.path.join(CODE, 'ex4dir')):
        path = os.path.join(folder, name)
        if os.path.exists(path):
            return path
    raise FileNotFoundError(name)


def code_block(text, label, lang='python'):
    return (f'<figure class="code"><figcaption><span class="fname">{html.escape(label)}</span>'
            f'<button class="copy" type="button">Copy</button></figcaption>'
            f'<pre><code class="language-{lang}">{html.escape(text.rstrip())}</code></pre></figure>')


def out_block(text, label='Output'):
    return (f'<figure class="out"><figcaption>{html.escape(label)}</figcaption>'
            f'<pre><code class="nohighlight">{html.escape(text.rstrip())}</code></pre></figure>')


def sub_code(m):
    parts = m.group(1).split('|')
    name = parts[0].strip()
    label = parts[1].strip() if len(parts) > 1 else name
    with open(find_code(name)) as f:
        return code_block(f.read(), label)


def sub_out(m):
    parts = m.group(1).split('|')
    name = parts[0].strip()
    with open(os.path.join(OUT, name + '.txt')) as f:
        text = f.read()
    lines = text.rstrip('\n').split('\n')
    label = 'Output'
    for opt in parts[1:]:
        key, _, val = opt.strip().partition('=')
        if key == 'tail':
            lines = lines[-int(val):]
        elif key == 'head':
            lines = lines[:int(val)]
        elif key == 'grep':
            lines = [l for l in lines if re.search(val, l)]
        elif key == 'label':
            label = val
    return out_block('\n'.join(lines), label)


def sub_img(m):
    parts = m.group(1).split('|')
    name = parts[0].strip()
    alt = parts[1].strip() if len(parts) > 1 else name
    with open(os.path.join(CODE, name), 'rb') as f:
        data = base64.b64encode(f.read()).decode()
    return (f'<figure class="plot"><img src="data:image/png;base64,{data}" alt="{html.escape(alt)}" loading="lazy">'
            f'<figcaption>{html.escape(alt)}</figcaption></figure>')


def sub_inline(tag, lang):
    def fn(m):
        attrs = m.group(1) or ''
        label_m = re.search(r'label="([^"]*)"', attrs)
        text = m.group(2).strip('\n')
        if lang == 'out':
            return out_block(text, label_m.group(1) if label_m else 'Output')
        return code_block(text, label_m.group(1) if label_m else ('Terminal' if lang == 'bash' else 'Python'), lang)
    return fn


def build():
    pieces = []
    for part in PARTS:
        with open(os.path.join(SRC, part)) as f:
            pieces.append(f.read())
    page = '\n'.join(pieces)
    page = re.sub(r'<py( [^>]*)?>(.*?)</py>', sub_inline('py', 'python'), page, flags=re.S)
    page = re.sub(r'<sh( [^>]*)?>(.*?)</sh>', sub_inline('sh', 'bash'), page, flags=re.S)
    page = re.sub(r'<txt( [^>]*)?>(.*?)</txt>', sub_inline('txt', 'out'), page, flags=re.S)
    page = re.sub(r'\{\{code:(.*?)\}\}', sub_code, page)
    page = re.sub(r'\{\{out:(.*?)\}\}', sub_out, page)
    page = re.sub(r'\{\{img:(.*?)\}\}', sub_img, page)
    leftover = re.findall(r'\{\{[^}]*\}\}', page)
    if leftover:
        raise SystemExit(f'Unresolved placeholders: {leftover[:5]}')
    with open(os.path.join(ROOT, 'zero-to-openmdao.html'), 'w') as f:
        f.write(page)
    print(f'Wrote zero-to-openmdao.html ({len(page) / 1024:.0f} KB)')


if __name__ == '__main__':
    build()
