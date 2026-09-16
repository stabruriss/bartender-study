#!/usr/bin/env python3
"""Invert published pair-conflict rates into independent overlap p.

This is a transparent arithmetic check. It does not read simulation outputs,
run a model, or fill missing workload summaries with guessed values.
"""
import argparse, csv, math

def invert(q, m1, m2):
    if not (0 < q < 1 and m1 > 0 and m2 > 0):
        return None
    return 1 - (1 - q) ** (1 / (m1 * m2))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    ap.add_argument('--output', required=True)
    args = ap.parse_args()
    with open(args.input, newline='') as f:
        rows = list(csv.DictReader(f))
    fields = ['source','metric','conflict_rate','numerator','denominator','unit','m1','m2','p','status']
    out = []
    for r in rows:
        m1 = float(r['m1']) if r['m1'] else None
        m2 = float(r['m2']) if r['m2'] else None
        p = invert(float(r['conflict_rate']), m1, m2) if m1 and m2 else None
        out.append({**{k:r.get(k,'') for k in fields[:7]}, 'p': '' if p is None else f'{p:.12g}', 'status': 'pending workload summary' if p is None else 'computed'})
    with open(args.output, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(out)

if __name__ == '__main__':
    main()
