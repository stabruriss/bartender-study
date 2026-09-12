"""Publication displays from the accepted aggregates; never executes the model.

The earlier generator and its full-scan outputs remain unchanged. Coordinates
come from cells.json; all observed numbers come from the two accepted CSVs.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import platform

from make_figures import (
    Data, ROOT, SOURCE, INPUT_HASHES, coords, curve, digest, number, save,
    style, write_csv, matplotlib, plt, np,
)
from matplotlib.ticker import PercentFormatter, FuncFormatter, NullLocator

SLICES = [(2, 0.), (4, 0.), (8, 0.), (4, .1), (4, .3)]
METRICS = [("author_repair_starts", "Repair starts"),
           ("observed_repair_effort", "Observed repair work")]
POLICIES = [("clean_first", "Bartender", "#111111", "o", "-"),
            ("in_place", "In-place repair", "#777777", "s", "--")]
READS = [("dispatch", "Read at dispatch", "#111111", "o", "-"),
         ("start", "Re-read at repair start", "#777777", "s", "-.")]
plt.rcParams.update({"font.size": 10, "axes.labelsize": 10,
                     "axes.titlesize": 10, "xtick.labelsize": 9,
                     "ytick.labelsize": 9,
                     "svg.hashsalt": "bartender-study-01-manuscript-v1"})


def reference_cells(data, n, dependency, policy):
    cells = sorted(data.select("sync_interval", n=n, dependency=dependency,
                               avoidance=0., tau=1., policy=policy),
                   key=lambda c: c["p_nominal"])
    if len(cells) != 3:
        raise ValueError("Incomplete repair reference slice")
    return cells


def repair_figure(data):
    fig, axes = plt.subplots(5, 2, figsize=(7.2, 8.8))
    for row, (agents, dependency) in enumerate(SLICES):
        for policy, label, color, marker, line in POLICIES:
            cells = reference_cells(data, agents, dependency, policy)
            x = [c["p_nominal"] for c in cells]
            for col, (metric, title) in enumerate(METRICS):
                ax = axes[row, col]
                if any(number(data.row(c, metric)["ci95_low"]) <= 0 for c in cells):
                    raise ValueError("Log axis would omit a nonpositive interval bound")
                curve(data, ax, cells, metric, x, color, marker, line, label)
                ax.set_xscale("log")
                ax.set_yscale("log")
                ax.set_xlim(x[0] / 1.25, x[-1] * 3.5)
                ax.set_xticks(x, [f"{p:.4f}" for p in x])
                ax.xaxis.set_minor_locator(NullLocator())
                ax.yaxis.set_major_formatter(FuncFormatter(lambda v, pos: f"{v:g}"))
                style(ax)
                ax.set_title(f"{agents} agents, dependency {dependency:g}", loc="left", fontsize=9, pad=5)
                if row == 4:
                    ax.set_xlabel("Overlap probability p (log scale)")
        b = reference_cells(data, agents, dependency, "clean_first")[-1]
        i = reference_cells(data, agents, dependency, "in_place")[-1]
        for col, (metric, _) in enumerate(METRICS):
            ax = axes[row, col]
            vb, vi = data.mean(b, metric), data.mean(i, metric)
            ratio = vi / vb
            xb = b["p_nominal"] * 1.22
            ax.plot([xb, xb], [vb, vi], color=".2", linewidth=.8)
            for yy in [vb, vi]:
                ax.plot([xb / 1.04, xb * 1.04], [yy, yy], color=".2", linewidth=.8)
            ax.text(xb * 1.12, math.sqrt(vb * vi), f"{ratio:.1f}×",
                    va="center", fontsize=10, fontweight="bold")
            lo, hi = ax.get_ylim()
            ax.set_ylim(lo / 1.08, hi * 1.45)
    fig.suptitle("Bartender reduces repair work as overlap grows", fontsize=13, y=.995)
    fig.legend(*axes[0, 0].get_legend_handles_labels(), loc="upper center",
               bbox_to_anchor=(.5, .967), ncol=2, frameon=False)
    fig.text(.29, .903, "Repair starts", ha="center", fontweight="bold")
    fig.text(.78, .903, "Observed repair work", ha="center", fontweight="bold")
    fig.text(.5, .049, "High-p labels: in-place mean / Bartender mean. Both axes logarithmic; panel scales differ.",
             ha="center", fontsize=8)
    fig.text(.5, .030, "Means and 95% normal intervals over 30 seeds; sync interval 1; window 256; relocation 0.",
             ha="center", fontsize=8)
    fig.text(.5, .012, "Work is abstract model effort, including observed partial repairs; it is not elapsed time.",
             ha="center", fontsize=8)
    fig.subplots_adjust(left=.10, right=.985, top=.862, bottom=.11, hspace=.62, wspace=.30)
    return fig


def sync_figure(data):
    metrics = [("overlap_pairs_per_time", "Overlap pairs / time"),
               ("first_failures_per_time", "First conflicts / time"),
               ("mean_first_failure_overlap_lines", "Overlap lines\nat first conflict")]
    fig, axes = plt.subplots(3, 3, figsize=(8.4, 7.0), sharex=True)
    for col, length in enumerate([4, 16, 64]):
        cells = sorted(data.select("sync_interval", n=4, dependency=0.,
                                  avoidance=0., policy="clean_first", length=length),
                       key=lambda c: c["scenario"]["tau"])
        if len(cells) != 7:
            raise ValueError("Incomplete synchronization slice")
        x = [c["scenario"]["tau"] for c in cells]
        for row, (metric, label) in enumerate(metrics):
            ax = axes[row, col]
            curve(data, ax, cells, metric, x, "#111111", "o", "-", "Simulation")
            style(ax)
            ax.set_xscale("log", base=2)
            ax.set_xticks(x, [f"{t:g}".removeprefix("0") if t < 1 else f"{t:g}" for t in x])
            ax.tick_params(axis="x", labelsize=8)
            if col == 0:
                ax.set_ylabel(label)
            if row == 2:
                ax.set_xlabel("Sync interval τ (model time)", fontsize=9)
        p = cells[0]["p_nominal"]
        axes[0, col].plot(x, [math.comb(4, 2) * p * t for t in x],
                          "--", color=".5", linewidth=1.2, label="First-order model (theory)")
        axes[0, col].set_title(f"{length}-line edits\np = {p:.4f}")
    fig.suptitle("Longer sync intervals raise conflict rates\nand can enlarge overlaps", fontsize=13, y=.99)
    fig.legend(*axes[0, 0].get_legend_handles_labels(), loc="upper center",
               bbox_to_anchor=(.5, .91), ncol=2, frameon=False)
    fig.text(.5, .054, "Four agents; no dependency; relocation 0. Dashed model C(n,2)pλ²τ applies only to overlap pairs.", ha="center", fontsize=8)
    fig.text(.5, .031, "95% normal intervals across available seeds; conflict size excludes seeds with no conflict.", ha="center", fontsize=8)
    fig.text(.5, .010, "Short-edit conflict sizes remain nearly flat; vertical scales differ between columns.", ha="center", fontsize=8)
    fig.subplots_adjust(left=.095, right=.985, top=.80, bottom=.13, wspace=.31, hspace=.28)
    return fig


def component_fields(data, cell, metric, prefix):
    row = data.row(cell, metric)
    if row["n"] != "30":
        raise ValueError("Pooled count requires the same 30 seeds")
    return {f"{prefix}_{k}": row[k] for k in ["n", "mean", "ci95_low", "ci95_high"]}


def wait_rows(data):
    rows = []
    for length in [4, 16, 64]:
        for refresh, _, _, _, _ in READS:
            cells = sorted(data.select("repair_delay", n=4, dependency=0., avoidance=0.,
                                      repair_clock="fixed", refresh_at=refresh, length=length),
                           key=lambda c: c["delta_multiple"])
            if [c["delta_multiple"] for c in cells] != [0., .25, .5, 1., 2., 4.]:
                raise ValueError("Unexpected wait grid")
            for c in cells:
                r = data.mean(c, "author_repair_completions")
                f = data.mean(c, "failed_repair_completions")
                n = data.mean(c, "conflict_cohort_n")
                if not 0 <= f <= r or not 0 <= r-f <= n or min(r, n) <= 0:
                    raise ValueError("Invalid zero-dependency cohort accounting")
                s = c["scenario"]
                exposure = (s["delta"] if refresh == "dispatch" else 0.) + s["repair_time"]
                rows.append({"cell_id": c["cell_id"], **coords(c),
                             **component_fields(data, c, "conflict_cohort_n", "initial_conflicts"),
                             **component_fields(data, c, "author_repair_completions", "completed_attempts"),
                             **component_fields(data, c, "failed_repair_completions", "failed_attempts"),
                             "initial_conflicts_landed_mean": r-f,
                             "initial_conflicts_landed_fraction": (r-f)/n,
                             "completed_attempt_failure_fraction": f/r,
                             "nominal_exposure": exposure,
                             "nominal_failure_probability": -math.expm1(-c["mu_nominal"] * exposure),
                             "ratio_ci95_low": "", "ratio_ci95_high": "",
                             "ratio_interval_status": "not identified from marginal aggregates"})
    return rows


def wait_figure(rows, failures=False):
    fig, axes = plt.subplots(1, 3, figsize=(8.4, 3.9), sharey=True)
    for col, length in enumerate([4, 16, 64]):
        ax = axes[col]
        for refresh, label, color, marker, line in READS:
            selected = [r for r in rows if r["edit_length_lines"] == length and r["baseline_read_time"] == refresh]
            x = [r["wait_in_characteristic_units"] for r in selected]
            key = "completed_attempt_failure_fraction" if failures else "initial_conflicts_landed_fraction"
            y = [r[key] for r in selected]
            ax.plot(x, y, color=color, marker=marker, linestyle=line,
                    markersize=4, linewidth=1.35, label=label)
            if failures:
                fine = np.linspace(0, 4, 201)
                mu_r = selected[0]["nominal_mu"] * selected[0]["base_repair_time"]
                q = -np.expm1(-((fine if refresh == "dispatch" else np.zeros_like(fine)) + mu_r))
                ax.plot(fine, q, color=color, linestyle="--" if refresh == "dispatch" else ":",
                        linewidth=1.0, label="First-order model (" + ("dispatch" if refresh == "dispatch" else "start") + ")")
            else:
                ax.annotate(f"{y[-1]:.1%}", (x[-1], y[-1]), xytext=(-4, -14 if refresh == "dispatch" else 9),
                            textcoords="offset points", ha="right", fontsize=10, fontweight="bold", color=color)
        p = selected[0]["nominal_overlap_probability"]
        ax.set_title(f"{length}-line edits\np = {p:.4f}")
        ax.axvline(1, color=".8", linestyle=":", linewidth=.8, zorder=0)
        ax.set_xlim(-.14, 4.18)
        ax.set_ylim(-.045, 1.10 if not failures else 1.045)
        ax.set_xticks([0, .5, 1, 2, 4], ["0", ".5", "1", "2", "4"])
        ax.set_xticks([.25], minor=True)
        ax.set_xlabel("Wait δ (multiples of 1/μ)", fontsize=9)
        ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
        style(ax)
        if not failures:
            zero = [r for r in rows if r["edit_length_lines"] == length and r["baseline_read_time"] == "dispatch"][0]
            ax.annotate("Bartender\n(immediate dispatch)", (0, zero["initial_conflicts_landed_fraction"]),
                        xytext=(.31, .24), textcoords="axes fraction", ha="center", fontsize=8,
                        arrowprops={"arrowstyle": "-", "color": ".4", "linewidth": .7})
    axes[0].set_ylabel("Completed attempts that fail" if failures else "Initial conflicts resolved\nwithin the window")
    title = "Waiting increases re-collision with a dispatch-time baseline" if failures else "Waiting leaves more initial conflicts unresolved"
    fig.suptitle(title, fontsize=13, y=.99)
    fig.legend(*axes[0].get_legend_handles_labels(), loc="upper center", bbox_to_anchor=(.5, .91),
               ncol=2, frameon=False, fontsize=8 if failures else 9)
    if failures:
        notes = ["First-order q = 1 − exp(−μE): E = δ + R at dispatch; E ≈ R when re-reading. Fixed R = 0.25.",
                 "Completed attempts are selected by the serial queue and cutoff; these curves do not establish an independent-attempt law."]
    else:
        notes = ["Four agents; no dependency; relocation 0; fixed repair clock. At zero wait: 100%, 100%, 99.8% across the panels.",
                 "Pooled finite-window ratios over 30 seeds, not completion-time statistics. Windows are fixed within each p slice."]
    fig.text(.5, .074, notes[0], ha="center", fontsize=7.5)
    fig.text(.5, .041, notes[1], ha="center", fontsize=7.3)
    fig.text(.5, .010, "Ratio intervals are not identified by the aggregate inputs. The dotted vertical line marks 1/μ, not a threshold.", ha="center", fontsize=7.5)
    fig.subplots_adjust(left=.12, right=.985, top=.685 if failures else .72, bottom=.23, wspace=.16)
    return fig


def repair_rows(data):
    rows = []
    for n, d in SLICES:
        for b, i in zip(reference_cells(data, n, d, "clean_first"), reference_cells(data, n, d, "in_place")):
            row = {"bartender_cell_id": b["cell_id"], "in_place_cell_id": i["cell_id"], **coords(b)}
            for metric, _ in METRICS:
                for c, prefix in [(b, "bartender"), (i, "in_place")]:
                    row.update(component_fields(data, c, metric, f"{prefix}_{metric}"))
                pair = data.pair_index[b["cell_id"], metric]
                row.update({f"paired_{metric}_{k}": pair[k] for k in ["n", "mean", "ci95_low", "ci95_high"]})
                row[f"in_place_over_bartender_{metric}"] = data.mean(i, metric) / data.mean(b, metric)
            rows.append(row)
    return rows


def export_tables(repairs, waits, out):
    paper = [r for r in repairs if (r["agents"] in [4, 8] and r["dependency_probability"] == 0)
             or (r["agents"] == 4 and r["dependency_probability"] == .3 and r["edit_length_lines"] == 64)]
    reference = [r for r in repairs if r["agents"] == 4 and r["dependency_probability"] == 0]
    assert len(repairs) == 15 and len(paper) == 7 and len(reference) == 3 and len(waits) == 36
    for name, rows in [("repair-all-five-slices.csv", repairs), ("repair-reference.csv", reference),
                       ("repair-paper-table.csv", paper), ("wait-reference.csv", waits)]:
        write_csv(out / name, rows)
    repair_tex = []
    for r in paper:
        repair_tex.append(f"{r['agents']}, {r['dependency_probability']:g} & {r['nominal_overlap_probability']:.4f} & " +
                          " & ".join(f"{float(r[p+'_'+m+'_mean']):,.{1 if m == 'author_repair_starts' or float(r[p+'_'+m+'_mean']) < 10 else 0}f}"
                                     for m, _ in METRICS for p in ["bartender", "in_place"]) + r" \\")
    (out / "table4-repair-rows.tex").write_text("% Generated from accepted aggregate means.\n" + "\n".join(repair_tex) + "\n")
    wait_tex = []
    for t in [0., .25, .5, 1., 2., 4.]:
        values = []
        for refresh in ["dispatch", "start"]:
            r = next(r for r in waits if r["edit_length_lines"] == 16 and r["baseline_read_time"] == refresh and r["wait_in_characteristic_units"] == t)
            values.extend(f"{100*r[k]:.0f}\\%" for k in ["initial_conflicts_landed_fraction", "completed_attempt_failure_fraction"])
        wait_tex.append(f"{t:g} & " + " & ".join(values) + r" \\")
    (out / "table5-wait-rows.tex").write_text("% Generated from pooled counts for 16-line edits.\n" + "\n".join(wait_tex) + "\n")
    text = ["# Numerical display summary", "", "All observations come from accepted study-01 aggregates. No simulations were run.", "",
            "## Repair comparison", "", "Reference: four agents, no dependency or relocation, synchronization interval 1. Means over 30 seeds.", "",
            "| Edit lines | Nominal overlap | Repair starts: Bartender / in-place | Repair work: Bartender / in-place |", "|---:|---:|---:|---:|"]
    for r in reference:
        vals = [f"{float(r[p+'_'+m+'_mean']):.2f}" for m, _ in METRICS for p in ["bartender", "in_place"]]
        text.append(f"| {r['edit_length_lines']} | {r['nominal_overlap_probability']:.7f} | {vals[0]} / {vals[1]} | {vals[2]} / {vals[3]} |")
    text += ["", "At high overlap, the in-place/Bartender work ratio is 12.1 for four agents and 28.8 for eight agents, both without dependency. All five slices, including their small reversals and supplied intervals, remain in Figure 4. Ratios divide means; no ratio interval or significance claim is inferred.", "",
             "## Waiting: all three overlaps", "", "Four agents, no dependency or relocation, fixed repair time 0.25. Values pool the 30 seeds. Each row reports the share of initial conflicts resolved by the cutoff and the failure share among completed repair attempts, in percent."]
    for length in [4, 16, 64]:
        text += ["", f"### {length}-line edits", "", "| Wait, in 1/μ | Dispatch: resolved % | Dispatch: failed % | Re-read: resolved % | Re-read: failed % |", "|---:|---:|---:|---:|---:|"]
        for t in [0., .25, .5, 1., 2., 4.]:
            values = []
            for refresh in ["dispatch", "start"]:
                r = next(r for r in waits if r["edit_length_lines"] == length and r["baseline_read_time"] == refresh and r["wait_in_characteristic_units"] == t)
                values.extend(f"{100*r[k]:.2f}" for k in ["initial_conflicts_landed_fraction", "completed_attempt_failure_fraction"])
            text.append(f"| {t:g} | " + " | ".join(values) + " |")
    text += ["", "At zero wait the resolved fractions are 100%, 100%, and 99.7622% for 4-, 16-, and 64-line edits respectively, for both read timings. At the longest wait, dispatch-time reading resolves 27.4–51.6%; re-reading resolves 69.6–79.1%. Completed-attempt failure fractions are 72.9–83.7% and 0.5–1.7%, respectively.", "",
             "The window is max(256, 32/μ), held fixed across waiting values within each overlap slice. The queue and cutoff select which attempts complete. These are finite-window proportions, not mean completion times or an uncensored geometric mean. Nominal q is an unfitted comparison, not a verified independent-attempt probability.", "",
             "`wait-reference.csv` retains all three component means, seed counts, and supplied 95% intervals. The resolved numerator is completed minus failed attempts; its interval and ratio intervals cannot be recovered without covariance. `repair-paper-table.csv` contains all seven repair rows used in the paper, with exact means, supplied intervals, and paired differences.", "",
             "## Synchronization interval", "", "Figure 5 shows only relocation 0. The overlap-pair rate and first-conflict rate rise over the seven synchronization intervals. First-conflict overlap grows for the longer edits; the short-edit series remains nearly flat. The first-order line is drawn only for overlap pairs. The full three-setting relocation scan remains in `../results/`, together with every original aggregate and paired result.", ""]
    (out / "NUMBERS.md").write_text("\n".join(text))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "analysis/manuscript")
    out = parser.parse_args().output_dir
    out.mkdir(parents=True, exist_ok=True)
    data = Data()
    waits, repairs = wait_rows(data), repair_rows(data)
    for stem, fig, title in [
        ("fig4_repairs_overlap", repair_figure(data), "Repair starts and work against overlap probability"),
        ("fig5_sync_interval", sync_figure(data), "Synchronization interval and conflicts"),
        ("fig6_wait_resolved", wait_figure(waits), "Initial conflicts resolved within the observation window"),
        ("fig7_wait_failures", wait_figure(waits, failures=True), "Completed repair attempts that collide again"),
    ]:
        save(fig, out, stem, title)
    export_tables(repairs, waits, out)
    if {name: digest(SOURCE / name) for name in INPUT_HASHES} != INPUT_HASHES:
        raise ValueError("Accepted input bytes changed during analysis")
    artifacts = [p for p in sorted(out.iterdir()) if p.suffix in [".csv", ".tex", ".svg", ".pdf", ".md"]]
    manifest = {"study": "study-01", "scope": "Four manuscript displays; accepted aggregate inputs only",
                "inputs": INPUT_HASHES, "input_hashes_unchanged": True,
                "scripts": {p.name: digest(p) for p in [Path(__file__), Path(__file__).with_name("make_figures.py")]},
                "python": platform.python_version(), "matplotlib": matplotlib.__version__, "numpy": np.__version__,
                "repair_rows": 15, "paper_repair_rows": 7, "reference_repair_rows": 3, "wait_rows": 36,
                "ratio_intervals": "not identifiable; source component intervals retained",
                "outputs": {p.name: {"sha256": digest(p), "bytes": p.stat().st_size} for p in artifacts}}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"status": "PASS", "figures": 4, "repair_rows": 15, "wait_rows": 36,
                      "accepted_inputs_unchanged": True}))


if __name__ == "__main__":
    main()
