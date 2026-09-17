#!/usr/bin/env python3
"""Position published conflict rates under an independence mapping.

The output is an effective per-cross-unit collision probability, not the
simulation's p and not an empirical calibration. It does not read simulation
outputs, run a model, or fill missing workload summaries with guessed values.
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
    fields = ['source','metric','conflict_rate','numerator','denominator','unit','m1','m2','p_eff','status']
    out = []
    for r in rows:
        m1 = float(r['m1']) if r['m1'] else None
        m2 = float(r['m2']) if r['m2'] else None
        p = invert(float(r['conflict_rate']), m1, m2) if m1 and m2 else None
        out.append({**{k:r.get(k,'') for k in fields[:8]}, 'p_eff': '' if p is None else f'{p:.12g}', 'status': 'scenario inputs not supplied; see range-positioning.csv' if p is None else 'computed'})
    with open(args.output, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n'); w.writeheader(); w.writerows(out)

if __name__ == '__main__':
    main()
