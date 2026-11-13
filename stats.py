#!/usr/bin/env python3
"""Reads log.csv and renders stats/progress.svg (animated card) and PROBLEMS.md."""
import csv, os, datetime as dt
from collections import defaultdict
from xml.dom import minidom

try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo('Asia/Kolkata')          # streaks roll over at midnight IST
except Exception:
    TZ = dt.timezone(dt.timedelta(hours=5, minutes=30))

ROOT = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(ROOT, 'log.csv')
GOALS = {'hdlbits': 100, 'logicode': 50}    # edit freely: only drives the progress bars
NAMES = {'hdlbits': 'HDLBits', 'logicode': 'Logicode'}
COLORS = {'hdlbits': '#37e6ff', 'logicode': '#e8a23a'}
WEEKS = 30

F = "'JetBrains Mono','Fira Code',Consolas,'Courier New',monospace"
CY, CU, GR, DIM, TX, BG, PN = '#37e6ff', '#e8a23a', '#5dffa8', '#7d93a8', '#dff6ff', '#050b14', '#0a1626'


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def load():
    rows = []
    if os.path.exists(LOG):
        with open(LOG, newline='', encoding='utf-8') as f:
            for r in csv.DictReader(f):
                try:
                    r['d'] = dt.date.fromisoformat(r['date'].strip())
                except Exception:
                    continue
                r['platform'] = r['platform'].strip().lower()
                rows.append(r)
    return rows


def streaks(days, today):
    run = longest = 0
    prev = None
    for d in sorted(days):
        run = run + 1 if prev and (d - prev).days == 1 else 1
        longest = max(longest, run)
        prev = d
    cur = 0
    d = today if today in days else today - dt.timedelta(days=1)   # streak stays alive until the day ends
    while d in days:
        cur += 1
        d -= dt.timedelta(days=1)
    return cur, longest


def render(rows, today):
    per_day = defaultdict(int)
    for r in rows:
        per_day[r['d']] += 1
    uniq = {(r['platform'], r['problem'].strip().lower()) for r in rows}
    by_plat = defaultdict(int)
    for p, _ in uniq:
        by_plat[p] += 1
    cur, best = streaks(set(per_day), today)
    W, H = 1000, 286
    glow = 'filter="url(#glow)"'
    b = []

    def t(x, y, s, size=12, fill=TX, w='normal', anchor='start', extra=''):
        b.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{w}" fill="{fill}" text-anchor="{anchor}" {extra}>{s}</text>')

    t(36, 44, 'RTL PRACTICE LOG', 20, TX, 'bold', extra=glow)
    t(36, 64, 'HDLBits + Logicode, one problem at a time', 12, DIM)
    t(930, 44, f'last {WEEKS} weeks', 11, DIM, anchor='end')
    for x, val, lab, col in ((36, len(uniq), 'solved', CY), (156, cur, 'day streak', CU), (276, best, 'best streak', GR)):
        t(x, 134, str(val), 44, col, 'bold', extra=glow)
        t(x, 156, lab, 11, DIM)

    for i, p in enumerate(GOALS):
        y = 196 + i * 30
        n = by_plat.get(p, 0)
        w = 220 * min(1, n / GOALS[p])
        t(36, y, NAMES[p], 12, TX)
        b.append(f'<rect x="124" y="{y-9}" width="220" height="9" rx="4.5" fill="#0e2236"/>')
        b.append(f'<rect x="124" y="{y-9}" width="{w:.1f}" height="9" rx="4.5" fill="{COLORS[p]}" {glow}>'
                 f'<animate attributeName="width" from="0" to="{w:.1f}" dur="1.2s" fill="freeze"/></rect>')
        t(400, y, f'{n}/{GOALS[p]}', 11, DIM, anchor='end')

    x0, y0 = 450, 96
    start = today - dt.timedelta(days=today.weekday()) - dt.timedelta(weeks=WEEKS - 1)
    last_month = None
    for col in range(WEEKS):
        mon = start + dt.timedelta(weeks=col)
        if mon.month != last_month:
            t(x0 + col * 16, y0 - 8, mon.strftime('%b'), 9, DIM)
            last_month = mon.month
        for row in range(7):
            d = mon + dt.timedelta(days=row)
            if d > today:
                continue
            n = per_day.get(d, 0)
            fill = '#0e2236' if n == 0 else '#14506b' if n == 1 else '#1b8aa8' if n == 2 else CY
            stroke = f' stroke="{CU}" stroke-width="1.5"' if d == today else ''
            a = (col * 7 + row) * 0.006 / 1.6
            b.append(f'<rect x="{x0+col*16}" y="{y0+row*16}" width="13" height="13" rx="3" fill="{fill}"{stroke}>'
                     f'<animate attributeName="opacity" values="0;0;1;1" keyTimes="0;{a:.3f};{a+0.09:.3f};1" dur="1.6s" fill="freeze"/></rect>')
    for row, lab in ((0, 'Mon'), (2, 'Wed'), (4, 'Fri')):
        t(x0 - 8, y0 + row * 16 + 10, lab, 9, DIM, anchor='end')
    t(770, 234, 'less', 9, DIM)
    for i, c in enumerate(('#0e2236', '#14506b', '#1b8aa8', CY)):
        b.append(f'<rect x="{796+i*16}" y="225" width="11" height="11" rx="2.5" fill="{c}"/>')
    t(866, 234, 'more', 9, DIM)

    b.append(f'<circle cx="40" cy="266" r="3.5" fill="{GR}" {glow}><animate attributeName="opacity" values="1;.2;1" dur="1.4s" repeatCount="indefinite"/></circle>')
    if rows:
        last = max(rows, key=lambda r: r['d'])
        b.append(f'<text x="52" y="270" font-size="11" fill="{DIM}"><tspan fill="{GR}">latest</tspan>  {esc(last["problem"])} '
                 f'({NAMES.get(last["platform"], esc(last["platform"]))}) on {last["d"].isoformat()}</text>')
    else:
        t(52, 270, 'no entries yet: run add.py to log your first problem', 11, DIM)

    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{F}">'
            '<defs><filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.5" result="b"/>'
            '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
            '<pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M20 0H0V20" fill="none" stroke="#0e2236" stroke-width="1"/></pattern></defs>'
            f'<rect width="{W}" height="{H}" rx="14" fill="{BG}"/><rect width="{W}" height="{H}" rx="14" fill="url(#grid)"/>'
            + ''.join(b) +
            f'<rect x=".75" y=".75" width="{W-1.5}" height="{H-1.5}" rx="14" fill="none" stroke="#12324a" stroke-width="1.5"/></svg>')


def problems_md(rows, today):
    uniq = {(r['platform'], r['problem'].strip().lower()) for r in rows}
    cur, best = streaks({r['d'] for r in rows}, today)
    out = ['# Solved problems', '', f'**{len(uniq)}** unique problems | current streak **{cur}** | best streak **{best}**', '']
    for p in GOALS:
        mine = sorted((r for r in rows if r['platform'] == p), key=lambda r: r['d'], reverse=True)
        out += [f'## {NAMES[p]} ({len({r["problem"].strip().lower() for r in mine})})', '']
        if not mine:
            out += ['Nothing logged yet.', '']
            continue
        out += ['| Date | Problem | Category | Solution |', '| :-- | :-- | :-- | :-- |']
        for r in mine:
            link = f'[code]({r["path"]})' if r.get('path') else ''
            out.append(f'| {r["date"]} | {r["problem"]} | {r.get("category", "")} | {link} |')
        out.append('')
    return '\n'.join(out)


def main():
    rows = load()
    today = dt.datetime.now(TZ).date()
    os.makedirs(os.path.join(ROOT, 'stats'), exist_ok=True)
    svg = render(rows, today)
    minidom.parseString(svg)
    with open(os.path.join(ROOT, 'stats', 'progress.svg'), 'w', encoding='utf-8') as f:
        f.write(svg)
    with open(os.path.join(ROOT, 'PROBLEMS.md'), 'w', encoding='utf-8') as f:
        f.write(problems_md(rows, today))
    print(f'stats refreshed: {len({(r["platform"], r["problem"].strip().lower()) for r in rows})} unique problems logged')


if __name__ == '__main__':
    main()
