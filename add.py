#!/usr/bin/env python3
"""Log a solved problem, scaffold its file, refresh the stats card, optionally push.

  python add.py hdlbits "Vector reversal" --cat Vectors     # scaffold + log
  (paste your solution into the file it prints)
  python add.py --push                                      # commit + push
"""
import argparse, csv, os, re, subprocess, datetime as dt
import stats

TEMPLATE = '''// Platform : {plat}
// Problem  : {name}
// Category : {cat}
// Solved   : {date}
// Approach :

// Rename the module/ports to match the problem statement.
module top_module (
    // TODO: ports
);

    // TODO: logic

endmodule
'''


def slug(s):
    return re.sub(r'[^a-z0-9]+', '_', s.lower()).strip('_')


def git(*args):
    return subprocess.run(['git', *args], cwd=stats.ROOT, check=False)


def main():
    ap = argparse.ArgumentParser(description='Log a solved RTL problem.')
    ap.add_argument('platform', nargs='?', choices=list(stats.GOALS))
    ap.add_argument('problem', nargs='?')
    ap.add_argument('--cat', default='', help='category, e.g. FSM, Vectors, Counters')
    ap.add_argument('--ext', default='v', choices=['v', 'sv'])
    ap.add_argument('--date', default=None, help='YYYY-MM-DD, to backfill an older solve')
    ap.add_argument('--push', action='store_true', help='pull, commit and push everything')
    a = ap.parse_args()

    msg = None
    if a.platform and a.problem:
        date = dt.date.fromisoformat(a.date).isoformat() if a.date else dt.datetime.now(stats.TZ).date().isoformat()
        rel = f'{a.platform}/{slug(a.problem)}.{a.ext}'
        path = os.path.join(stats.ROOT, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if os.path.exists(path):
            print(f'kept existing file: {rel}')
        else:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(TEMPLATE.format(plat=stats.NAMES[a.platform], name=a.problem, cat=a.cat or '-', date=date))
            print(f'created: {rel}  <- paste your solution here')
        dup = any(r['platform'] == a.platform and r['problem'].strip().lower() == a.problem.strip().lower() for r in stats.load())
        if dup:
            print('already in log.csv, not logging it twice')
        else:
            new = not os.path.exists(stats.LOG) or os.path.getsize(stats.LOG) == 0
            with open(stats.LOG, 'a', newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                if new:
                    w.writerow(['date', 'platform', 'problem', 'category', 'path'])
                w.writerow([date, a.platform, a.problem, a.cat, rel])
            msg = f'solve: {stats.NAMES[a.platform]} - {a.problem}'
        stats.main()
    elif not a.push:
        ap.print_help()
        return

    if a.push:
        if msg is None:
            rows = stats.load()
            last = max(rows, key=lambda r: r['d']) if rows else None
            msg = f'solve: {stats.NAMES.get(last["platform"], last["platform"])} - {last["problem"]}' if last else 'update journal'
        git('pull', '--rebase', '--autostash')
        git('add', '-A')
        git('commit', '-m', msg)
        git('push')


if __name__ == '__main__':
    main()
