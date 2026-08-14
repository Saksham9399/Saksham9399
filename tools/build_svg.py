"""Regenerate light_mode.svg and dark_mode.svg from a single row spec.

Every row of the right-hand column is padded to WIDTH monospace cells, using the
same dot-run formula as justify_format() in today.py, so the first workflow run
reproduces the committed layout instead of shifting it.

    .venv/bin/python tools/build_svg.py
"""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

ART_X = 15
WIDTH = 60
TEXT_X = 420        # clears the 40-cell art column: 15 + 40 * 9.6px = 399
FIRST_Y, STEP = 30, 20
CARD_W, CARD_H = 1015, 630

THEMES = {
    'light_mode.svg': {
        'bg': '#f6f8fa', 'fg': '#24292f', 'key': '#953800',
        'value': '#0a3069', 'cc': '#c2cfde', 'add': '#1a7f37', 'del': '#cf222e',
    },
    'dark_mode.svg': {
        'bg': '#161b22', 'fg': '#c9d1d9', 'key': '#ffa657',
        'value': '#a5d6ff', 'cc': '#616e7f', 'add': '#3fb950', 'del': '#f85149',
    },
}


def esc(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def rule(label):
    return f'{label} -' + '—' * (WIDTH - len(label) - 5) + '-—-'


def dots(count):
    return ' ' + '.' * (count - 2) + ' '


def kv(key, value):
    """A static `. Key.Sub: ..... value` row padded to WIDTH cells."""
    parts = key.split('.')  # each segment is styled, the separators are not
    key_len = sum(len(p) for p in parts) + len(parts) - 1
    run = WIDTH - 2 - key_len - 1 - len(value)
    keyed = '.'.join(f'<tspan class="key">{esc(p)}</tspan>' for p in parts)
    return (f'<tspan class="cc">. </tspan>{keyed}:'
            f'<tspan class="cc">{dots(run)}</tspan>'
            f'<tspan class="value">{esc(value)}</tspan>')


def field(element_id, value, length, cls='value'):
    """A `<dots><value>` pair today.py rewrites. Occupies length + 2 cells."""
    return (f'<tspan class="cc" id="{element_id}_dots">{dots(length - len(value) + 2)}</tspan>'
            f'<tspan class="{cls}" id="{element_id}">{esc(value)}</tspan>')


# Rewritten fields with no dot leader, so their row breathes as the number grows.
# Maps id -> the digit count its row is laid out for.
NOMINAL = {'contrib_data': 2, 'loc_add': 7}


def bare(element_id, value, cls='value'):
    return f'<tspan class="{cls}" id="{element_id}">{esc(value)}</tspan>'


# Stat values here are placeholders; the workflow overwrites them on first run.
ROWS = [
    rule('saksham@agarwal'),
    kv('OS', 'macOS, Ubuntu Linux'),
    ('<tspan class="cc">. </tspan><tspan class="key">Uptime</tspan>:'
     + field('age_data', '27 years, 5 months, 5 days', 49)),
    kv('Host', 'Danalto (IoT Asset Tracking)'),
    kv('Kernel', 'Software Engineer, Full Stack (Python)'),
    kv('Shell', 'Dublin, Ireland'),
    kv('IDE', 'VS Code, PyCharm, Claude Code'),
    '<tspan class="cc">. </tspan>',
    kv('Languages.Programming', 'Python, TypeScript, Go, SQL, C++'),
    kv('Stack.Backend', 'Django, DRF, FastAPI, Flask'),
    kv('Stack.Frontend', 'React, TypeScript, Redux, HTML5'),
    kv('Stack.Data', 'PostgreSQL, Redis, Kafka, Flink'),
    kv('Stack.Cloud', 'AWS (ECS, Lambda, S3), Docker, Terraform'),
    kv('Stack.Quality', 'TDD, pytest, Jest, GitHub Actions'),
    kv('Stack.GenAI', 'Claude Code, Copilot, MCP, OpenAI'),
    '<tspan class="cc">. </tspan>',
    rule('- Education'),
    kv('M.A.I.', 'Computer Engineering, Trinity College, 2022'),
    kv('B.A.I.', 'Computer Engineering, Trinity College, 2021'),
    '<tspan class="cc">. </tspan>',
    rule('- Contact'),
    kv('Email.Personal', 'asaksham75@gmail.com'),
    kv('Email.Academic', 'saagarwa@tcd.ie'),
    kv('LinkedIn', 'sakshamagarwal93'),
    kv('GitHub', 'Saksham9399'),
    '<tspan class="cc">. </tspan>',
    rule('- GitHub Stats'),
    ('<tspan class="cc">. </tspan><tspan class="key">Repos</tspan>:'
     + field('repo_data', '22', 7)
     + ' {<tspan class="key">Contributed</tspan>: ' + bare('contrib_data', '24')
     + '} | <tspan class="key">Stars</tspan>:' + field('star_data', '0', 14)),
    ('<tspan class="cc">. </tspan><tspan class="key">Commits</tspan>:'
     + field('commit_data', '0', 23)
     + ' | <tspan class="key">Followers</tspan>:' + field('follower_data', '9', 10)),
    ('<tspan class="cc">. </tspan><tspan class="key">Lines of Code</tspan>:'
     + field('loc_data', '0', 12)
     + ' ( ' + bare('loc_add', '0', 'addColor') + '<tspan class="addColor">++</tspan>, '
     + field('loc_del', '0', 10, 'delColor') + '<tspan class="delColor">--</tspan> )'),
]


def ascii_rows():
    out = subprocess.run(
        [sys.executable, str(ROOT / 'tools' / 'ascii_portrait.py'), '--tspans'],
        capture_output=True, text=True, check=True)
    return out.stdout.rstrip('\n').split('\n')


def build(filename, theme):
    art = '\n'.join(ascii_rows())
    body = '\n'.join(
        f'<tspan x="{TEXT_X}" y="{FIRST_Y + i * STEP}">{row}</tspan>'
        for i, row in enumerate(ROWS))
    svg = f'''<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,monospace" width="{CARD_W}px" height="{CARD_H}px" font-size="16px">
<style>
@font-face {{
src: local('Consolas'), local('Consolas Bold');
font-family: 'ConsolasFallback';
font-display: swap;
-webkit-size-adjust: 109%;
size-adjust: 109%;
}}
.key {{fill: {theme['key']};}}
.value {{fill: {theme['value']};}}
.addColor {{fill: {theme['add']};}}
.delColor {{fill: {theme['del']};}}
.cc {{fill: {theme['cc']};}}
text, tspan {{white-space: pre;}}
</style>
<rect width="{CARD_W}px" height="{CARD_H}px" fill="{theme['bg']}" rx="15"/>
<text x="{ART_X}" y="90" fill="{theme['fg']}" class="ascii">
{art}
</text>
<text x="{TEXT_X}" y="{FIRST_Y}" fill="{theme['fg']}">
{body}
</text>
</svg>
'''
    (ROOT / filename).write_text(svg, encoding='utf-8')
    print(f'wrote {filename}')


def check_widths():
    import html
    import re
    for i, row in enumerate(ROWS):
        plain = html.unescape(re.sub(r'<[^>]+>', '', row))
        width = len(plain)
        for element_id, nominal in NOMINAL.items():
            seeded = re.search(rf'id="{element_id}">([^<]*)<', row)
            if seeded:
                width += nominal - len(seeded.group(1))
        if plain != '. ' and width != WIDTH:
            raise SystemExit(f'row {i} (y={FIRST_Y + i * STEP}) is {width} cells, '
                             f'expected {WIDTH}: {plain!r}')


if __name__ == '__main__':
    check_widths()
    for name, theme in THEMES.items():
        build(name, theme)
