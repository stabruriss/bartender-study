"""Maintainer analysis of accepted aggregate CSVs, with approved grid metadata.

No model imports, raw outputs, per-seed summaries, or simulation calls. See
README.md for estimands, display slices, and limits on the F3 comparison.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import platform
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import FuncFormatter, PercentFormatter
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "deliverables/study-01"
INPUT_HASHES = {
    "summary.csv": "5209b6b2f833ff958bc9320af9d577cef3453eb94ff185822028da80be7e5505",
    "paired-differences.csv": "e703f0a7cacdbf4b7f38a82fbb83ed6fd9dd96096495be52ec6208b842327056",
    "cells.json": "086034341ac0f852c2a6fcb69ec68e2113652b7c74c62a48ad7ff7f71f98ef48",
}
POLICIES = {"clean_first": "Bartender", "in_place": "In-place repair", "kick_back": "Kick-back"}
COLORS = ["#151515", "#575757", "#8a8a8a"]
MARKERS = ["o", "s", "^"]
STYLES = ["-", "-.", ":"]
F1_METRICS = [("author_repair_starts", "Repair starts"),
              ("observed_repair_effort", "Observed repair effort")]
F2_METRICS = [("overlap_pairs_per_time", "Overlap pairs / time"),
              ("first_failures_per_time", "First conflicts / time"),
              ("mean_first_failure_overlap_lines", "Overlap lines at first conflict")]
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9, "axes.titlesize": 10,
    "axes.labelsize": 9, "xtick.labelsize": 8, "ytick.labelsize": 8,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.unicode_minus": False, "pdf.fonttype": 42, "svg.fonttype": "none",
    "svg.hashsalt": "bartender-study-01-analysis-v1", "savefig.facecolor": "white",
})


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(name):
    with (SOURCE / name).open(newline="") as handle:
        return list(csv.DictReader(handle))


def number(value):
    return float(value) if value != "" else float("nan")


def write_csv(path, rows):
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


class Data:
    def __init__(self):
        for name, expected in INPUT_HASHES.items():
            if digest(SOURCE / name) != expected:
                raise ValueError("Accepted input bytes changed: " + name)
        self.grid = json.loads((SOURCE / "cells.json").read_text())
        self.cells = {c["cell_id"]: c for c in self.grid}
        self.rows, self.paired = read_csv("summary.csv"), read_csv("paired-differences.csv")
        self.index = {(r["cell_id"], r["metric"]): r for r in self.rows}
        self.pair_index = {(r["clean_first_cell"], r["metric"]): r for r in self.paired}
        if len(self.cells) != 990 or len(self.rows) != 34650 or len(self.paired) != 11010:
            raise ValueError("Incomplete accepted aggregate delivery")
        if len(self.index) != len(self.rows) or len(self.pair_index) != len(self.paired):
            raise ValueError("Duplicate aggregate keys")
        if {r["cell_id"] for r in self.rows} != set(self.cells):
            raise ValueError("Aggregate cells do not match metadata")
        for row in self.rows:
            if row["suite"] != self.cells[row["cell_id"]]["suite"] or int(row["runs_seen"]) != 30 or int(row["runs_failed"]) != 0:
                raise ValueError("Unexpected suite or completed-seed count")
            n = int(row["n"])
            if not 0 <= n <= 30 or (n == 0) != (row["mean"] == ""):
                raise ValueError("Inconsistent missing-value record")
        for row in self.paired:
            a, b = self.cells[row["clean_first_cell"]], self.cells[row["in_place_cell"]]
            if a["suite"] != b["suite"] or a["scenario"]["policy"] != "clean_first" or b["scenario"]["policy"] != "in_place":
                raise ValueError("Paired contrast identifiers disagree")
            if {k: v for k, v in a["scenario"].items() if k != "policy"} != {k: v for k, v in b["scenario"].items() if k != "policy"}:
                raise ValueError("Paired contrast joins different conditions")

    def select(self, suite, **conditions):
        return [c for c in self.grid if c["suite"] == suite
                and all(c["scenario"][k] == v for k, v in conditions.items())]

    def row(self, cell, metric):
        return self.index[cell["cell_id"], metric]

    def mean(self, cell, metric):
        return number(self.row(cell, metric)["mean"])

    def pooled_dispatches(self, cell):
        numerator = self.row(cell, "dispatches")
        denominator = self.row(cell, "conflict_cohort_n")
        if numerator["n"] != "30" or denominator["n"] != "30":
            raise ValueError("Pooled ratio requires all seed counts in both aggregates")
        return number(numerator["mean"]) / number(denominator["mean"]) if number(denominator["mean"]) else float("nan")


def coords(cell):
    s = cell["scenario"]
    return {"case": cell["case"], "policy": s["policy"], "agents": s["n"],
            "dependency_probability": s["dependency"], "avoidance_probability": s["avoidance"],
            "edit_length_lines": s["length"], "nominal_overlap_probability": cell["p_nominal"],
            "nominal_mu": cell["mu_nominal"], "sync_interval": s["tau"],
            "post_dispatch_wait": s["delta"], "wait_in_characteristic_units": cell["delta_multiple"],
            "observation_horizon": s["horizon"], "baseline_read_time": s["refresh_at"],
            "repair_clock": s["repair_clock"], "base_repair_time": s["repair_time"],
            "edits_per_agent_time": s["rate"], "files": s["files"], "lines_per_file": s["lines"]}


def style(ax):
    ax.grid(axis="y", linewidth=.5, color=".89", zorder=0)
    ax.tick_params(length=3)


def curve(data, ax, cells, metric, x, color, marker, linestyle, label=None):
    values = [data.row(c, metric) for c in cells]
    mean = np.array([number(v["mean"]) for v in values])
    low = np.array([number(v["ci95_low"]) for v in values])
    high = np.array([number(v["ci95_high"]) for v in values])
    ax.fill_between(x, low, high, color=color, alpha=.09, linewidth=0)
    ax.errorbar(x, mean, yerr=[mean-low, high-mean], color=color, marker=marker,
                linestyle=linestyle, markersize=3.7, linewidth=1.15,
                elinewidth=.65, capsize=1.7, label=label)


def save(fig, output, stem, title):
    fig.canvas.draw()
    for ext in ["pdf", "svg"]:
        metadata = {"Title": title, "Creator": "Matplotlib"}
        metadata.update({"CreationDate": None, "ModDate": None} if ext == "pdf" else {"Date": None})
        fig.savefig(output / f"{stem}.{ext}", metadata=metadata)
    plt.close(fig)


def f1(data, avoidance=0., tau=1.):
    slices = [(2, 0.), (4, 0.), (8, 0.), (4, .1), (4, .3)]
    fig, axes = plt.subplots(2, 5, figsize=(11.6, 5.5))
    for col, (agents, dependency) in enumerate(slices):
        for policy, color, marker, ls in [("clean_first", COLORS[0], "o", "-"), ("in_place", COLORS[1], "s", "--")]:
            cells = sorted(data.select("sync_interval", n=agents, dependency=dependency,
                                      avoidance=avoidance, tau=tau, policy=policy), key=lambda c: c["p_nominal"])
            assert len(cells) == 3
            x = [c["p_nominal"] for c in cells]
            for row, (metric, label) in enumerate(F1_METRICS):
                ax = axes[row, col]
                curve(data, ax, cells, metric, x, color, marker, ls, POLICIES[policy])
                ax.set_xscale("log")
                ax.set_xticks(x, [f"{v:.3g}" for v in x])
                style(ax)
                if col == 0:
                    ax.set_ylabel(label)
                if row == 1:
                    ax.set_xlabel("Overlap probability p")
            axes[0, col].set_title(f"{agents} agents\nDependency {dependency:g}")
    fig.suptitle(f"F1  Repair count and work across overlap probabilities\nAvoidance {avoidance:g}; sync interval {tau:g}; observation window 256", fontsize=12, y=.98)
    fig.legend(*axes[0, 0].get_legend_handles_labels(), loc="upper center", bbox_to_anchor=(.5, .88), ncol=2, frameon=False)
    fig.text(.5, .025, "Means and 95% normal intervals across 30 seeds. Vertical scales vary by slice; effort includes observed partial repairs.", ha="center", fontsize=8)
    fig.subplots_adjust(left=.075, right=.97, top=.77, bottom=.13, hspace=.25, wspace=.42)
    return fig


def f2(data, agents=4, dependency=0., policy="clean_first"):
    fig, axes = plt.subplots(3, 3, figsize=(9.8, 8.2), sharex=True)
    handles = []
    for col, length in enumerate([4, 16, 64]):
        for index, avoidance in enumerate([0., .5, .9]):
            cells = sorted(data.select("sync_interval", n=agents, dependency=dependency, policy=policy,
                                      length=length, avoidance=avoidance), key=lambda c: c["scenario"]["tau"])
            assert len(cells) == 7
            x = [c["scenario"]["tau"] for c in cells]
            for row, (metric, label) in enumerate(F2_METRICS):
                ax = axes[row, col]
                curve(data, ax, cells, metric, x, COLORS[index], MARKERS[index], STYLES[index], f"Avoidance {avoidance:g}")
                style(ax)
                ax.set_xscale("log", base=2)
                ax.set_xticks(x, [f"{v:g}".removeprefix("0") if v < 1 else f"{v:g}" for v in x])
                if col == 0:
                    ax.set_ylabel(label)
                if row == 2:
                    ax.set_xlabel("Sync interval τ (model time)")
            if avoidance == 0 and dependency == 0:
                sample = cells[0]
                prediction = [math.comb(agents, 2) * sample["p_nominal"] * sample["scenario"]["rate"] ** 2 * t for t in x]
                axes[0, col].plot(x, prediction, "--", color="black", linewidth=1.2, label="First-order model")
        axes[0, col].set_title(f"p = {cells[0]['p_nominal']:.4g}  ({length}-line edits)")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(.5, .895), ncol=4, frameon=False, fontsize=9)
    fig.suptitle(f"F2  Synchronization interval, overlap and first conflicts\n{POLICIES[policy]}; {agents} agents; dependency {dependency:g}", fontsize=12, y=.98)
    note = "Dashed first-order model: C(n,2)pλ²τ, for zero avoidance/dependency; applies only to overlap pairs." if dependency == 0 else "Dependency is nonzero: the independent-edit first-order prediction is not overlaid."
    fig.text(.5, .042, note, ha="center", fontsize=8)
    fig.text(.5, .022, "95% normal intervals across available seeds. Conflict size excludes seeds with no conflict; actual n is in the full table.", ha="center", fontsize=8)
    fig.subplots_adjust(left=.10, right=.98, top=.82, bottom=.105, hspace=.24, wspace=.29)
    return fig


def f3(data, agents=4, dependency=0., avoidance=0., clock="fixed"):
    fig, axes = plt.subplots(3, 3, figsize=(9.8, 8.4), sharex=True)
    fixed = clock == "fixed"
    for col, length in enumerate([4, 16, 64]):
        for index, refresh in enumerate(["dispatch", "start"]):
            cells = sorted(data.select("repair_delay", n=agents, dependency=dependency, avoidance=avoidance,
                                      repair_clock=clock, refresh_at=refresh, length=length), key=lambda c: c["delta_multiple"])
            assert len(cells) == 6
            x = [c["delta_multiple"] for c in cells]
            completed = [data.mean(c, "author_repair_completions") for c in cells]
            failures = [data.mean(c, "failed_repair_completions") for c in cells]
            conflicts = [data.mean(c, "conflict_cohort_n") for c in cells]
            q = [f/r if r else float("nan") for f, r in zip(failures, completed)]
            landed = [(r-f)/n if n else float("nan") for r, f, n in zip(completed, failures, conflicts)] if dependency == 0 else [float("nan")] * len(x)
            repairs = [r/n if n else float("nan") for r, n in zip(completed, conflicts)]
            label = "Read at dispatch" if refresh == "dispatch" else "Re-read at repair start"
            for row, values in enumerate([q, landed, repairs]):
                axes[row, col].plot(x, values, color=COLORS[index], marker=MARKERS[index],
                                    markersize=4, linewidth=1.2, linestyle="-", label=label)
            if fixed and dependency == 0:
                mu, repair = cells[0]["mu_nominal"], cells[0]["scenario"]["repair_time"]
                fine = np.linspace(0, 4, 201)
                prediction = [-math.expm1(-((t if refresh == "dispatch" else 0) + mu*repair)) for t in fine]
                axes[0, col].plot(fine, prediction, "--", color=COLORS[index], linewidth=1.1,
                                  label="First-order (" + ("dispatch" if refresh == "dispatch" else "start") + ")")
        axes[0, col].set_title(f"p = {cells[0]['p_nominal']:.4g}  ({length}-line edits)")
        for row in range(3):
            ax = axes[row, col]
            ax.axvline(1, color=".78", linewidth=.7, linestyle=":", zorder=0)
            ax.set_xlim(-.1, 4.1)
            ax.set_xticks([0, .5, 1, 2, 4], ["0", ".5", "1", "2", "4"])
            ax.set_xticks([.25], minor=True)
            style(ax)
            if row < 2:
                ax.set_ylim(-.04, 1.04)
                ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
        axes[2, col].set_xlabel("Wait δ (multiples of 1/μ)")
        if dependency != 0:
            axes[1, col].text(.5, .5, "Initial-cohort landings\nnot identifiable with dependency\nfrom these aggregate inputs", transform=axes[1, col].transAxes,
                              ha="center", va="center", fontsize=8)
    axes[0, 0].set_ylabel("Failure fraction among\ncompleted repair attempts")
    axes[1, 0].set_ylabel("Initial conflicts landed\nby window end (pooled)")
    axes[2, 0].set_ylabel("Completed repairs / initial conflict\n(censored at window end)")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(.5, .895), ncol=4, frameon=False, fontsize=8)
    fig.suptitle(f"F3  Completed-attempt failures and finite-window outcomes\n{agents} agents; dependency {dependency:g}; avoidance {avoidance:g}; {clock} repair clock", fontsize=12, y=.98)
    if fixed and dependency == 0:
        note = "First-order q = 1 − exp(−μE): dispatch uses E = δ + R; re-reading uses E = R = 0.25. At δ = 0 both use E = R."
    else:
        note = "No nominal q is drawn: dependency failures or unobserved context-dependent repair times prevent that comparison."
    fig.text(.5, .055, note, ha="center", fontsize=8)
    fig.text(.5, .034, "All ratios pool 30 seeds. Aggregate inputs do not identify ratio intervals. Completed attempts are selected by the queue and cutoff.", ha="center", fontsize=8)
    fig.text(.5, .013, "μ is nominal; the vertical line marks waiting time 1/μ. Windows are fixed per p; no uncensored mean or dispatch distribution is inferred.", ha="center", fontsize=8)
    fig.subplots_adjust(left=.10, right=.98, top=.81, bottom=.12, hspace=.18, wspace=.27)
    return fig


def interval(row):
    if row["mean"] == "":
        return "NA (n=0)"
    return f"{float(row['mean']):.2f} [{float(row['ci95_low']):.2f}, {float(row['ci95_high']):.2f}]"


def tables(data, output):
    write_csv(output / "all-cell-results.csv", [{**r, **coords(data.cells[r["cell_id"]])} for r in data.rows])
    write_csv(output / "all-paired-results.csv", [{**r, **coords(data.cells[r["clean_first_cell"]])} for r in data.paired])
    derived = []
    for c in data.select("repair_delay"):
        a, b = data.row(c, "dispatches"), data.row(c, "conflict_cohort_n")
        derived.append({"cell_id": c["cell_id"], **coords(c), "pooled_dispatches_per_initial_conflict": data.pooled_dispatches(c),
                        **{"dispatches_" + k: a[k] for k in ["n", "mean", "ci95_low", "ci95_high"]},
                        **{"initial_conflicts_" + k: b[k] for k in ["n", "mean", "ci95_low", "ci95_high"]},
                        "ratio_ci95_low": "", "ratio_ci95_high": "", "ratio_interval_status": "not_identifiable_from_aggregate_inputs"})
    write_csv(output / "dispatch-ratios.csv", derived)
    rows, display = [], []
    for agents, dependency in [(2, 0.), (4, 0.), (8, 0.), (4, .1), (4, .3)]:
        for c in sorted(data.select("sync_interval", n=agents, dependency=dependency, avoidance=0., tau=1., policy="clean_first"), key=lambda c: c["p_nominal"]):
            paired = data.pair_index[c["cell_id"], "author_repair_starts"]
            other = data.cells[paired["in_place_cell"]]
            metrics = [data.row(c, "author_repair_starts"), data.row(other, "author_repair_starts"),
                       data.row(c, "observed_repair_effort"), data.row(other, "observed_repair_effort"), paired]
            rows.append({"agents": agents, "dependency": dependency, "p": c["p_nominal"],
                         **{label: interval(row) for label, row in zip(["bartender_repairs", "in_place_repairs", "bartender_effort", "in_place_effort", "paired_repair_difference"], metrics)}})
            display.append([f"{agents} / {dependency:g}", f"{c['p_nominal']:.4g}"] + [interval(r) for r in metrics])
    write_csv(output / "table1-reference.csv", rows)
    fig, ax = plt.subplots(figsize=(13.5, 5.5)); ax.axis("off")
    table = ax.table(cellText=display, colLabels=["Agents /\ndependency", "p", "Bartender\nrepair starts", "In-place\nrepair starts", "Bartender\neffort", "In-place\neffort", "Paired repair difference\nBartender − in-place"],
                     loc="center", cellLoc="center", colWidths=[.075, .065, .16, .16, .17, .19, .18])
    table.auto_set_font_size(False); table.set_fontsize(8); table.scale(1, 1.45)
    for (row, col), cell in table.get_celld().items():
        cell.set_linewidth(.25); cell.set_edgecolor(".75")
        if row == 0:
            cell.set_facecolor(".91"); cell.set_text_props(weight="bold"); cell.set_height(.09)
        elif ((row-1)//3) % 2:
            cell.set_facecolor(".97")
    fig.suptitle("Table 1  Reference slice: mean [95% normal interval], 30 seeds\nSync interval 1; avoidance 0; observation window 256", fontsize=12, y=.97)
    fig.text(.5, .025, "All 990 cells and all 35 metrics are retained in all-cell-results.csv; exact paired intervals are in all-paired-results.csv. No multiple-comparison correction.", ha="center", fontsize=8)
    fig.subplots_adjust(left=.025, right=.975, bottom=.10, top=.84)
    save(fig, output, "table1_reference", "Reference policy comparisons with across-seed intervals")


def numeric_summary(data, output):
    pvalues = sorted({c["p_nominal"] for c in data.grid})
    reference = sorted(data.select("sync_interval", n=4, dependency=0., avoidance=0., tau=1., policy="clean_first"), key=lambda c: c["p_nominal"])
    repair_b, repair_i, effort_b, effort_i = [], [], [], []
    for c in reference:
        paired = data.pair_index[c["cell_id"], "author_repair_starts"]
        other = data.cells[paired["in_place_cell"]]
        repair_b.append(data.mean(c, "author_repair_starts")); repair_i.append(data.mean(other, "author_repair_starts"))
        effort_b.append(data.mean(c, "observed_repair_effort")); effort_i.append(data.mean(other, "observed_repair_effort"))
    all_pairs = [r for r in data.paired if r["metric"] == "author_repair_starts"]
    signs = {"lower": sum(float(r["mean"]) < 0 for r in all_pairs), "equal": sum(float(r["mean"]) == 0 for r in all_pairs), "higher": sum(float(r["mean"]) > 0 for r in all_pairs)}
    fmt = lambda values, places=2: ", ".join(f"{v:.{places}f}" for v in values)
    c2 = sorted(data.select("sync_interval", n=4, dependency=0., avoidance=0., policy="clean_first", length=64), key=lambda c: c["scenario"]["tau"])
    observed, predicted = [data.mean(c, "overlap_pairs_per_time") for c in c2], [6*c["p_nominal"]*c["scenario"]["tau"] for c in c2]
    f3 = {}
    for refresh in ["dispatch", "start"]:
        end = sorted([c for c in data.select("repair_delay", n=4, dependency=0., avoidance=0., repair_clock="fixed", refresh_at=refresh) if c["delta_multiple"] == 4], key=lambda c: c["p_nominal"])
        f3[refresh] = {"pooled_dispatches": [data.pooled_dispatches(c) for c in end],
                       "completed_failure_fraction": [data.mean(c, "failed_repair_completions") / data.mean(c, "author_repair_completions") for c in end],
                       "pooled_landed_fraction": [(data.mean(c, "author_repair_completions") - data.mean(c, "failed_repair_completions")) / data.mean(c, "conflict_cohort_n") for c in end],
                       "completed_repairs_per_initial_conflict": [data.mean(c, "author_repair_completions") / data.mean(c, "conflict_cohort_n") for c in end],
                       "window_fraction": [data.mean(c, "unresolved_over_threshold_fraction") for c in end],
                       "prediction": [math.exp((c["delta_multiple"] if refresh == "dispatch" else 0) + c["mu_nominal"]*c["scenario"]["repair_time"]) for c in end]}
    result = {"reference_p": pvalues, "f1_repairs_bartender": repair_b, "f1_repairs_in_place": repair_i,
              "f1_effort_bartender": effort_b, "f1_effort_in_place": effort_i, "f1_all_paired_cells_signs": signs,
              "f2_largest_overlap_observed_endpoints": [observed[0], observed[-1]], "f2_first_order_endpoints": [predicted[0], predicted[-1]],
              "f3_largest_wait": f3, "aggregate_rows_n_below_30": sum(int(r["n"]) < 30 for r in data.rows),
              "aggregate_rows_n_zero": sum(int(r["n"]) == 0 for r in data.rows)}
    (output / "numeric-summary.json").write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    f2_first = [data.mean(c, "first_failures_per_time") for c in [c2[0], c2[-1]]]
    f2_size = [data.mean(c, "mean_first_failure_overlap_lines") for c in [c2[0], c2[-1]]]
    avoidance_rates = [data.mean(data.select("sync_interval", n=4, dependency=0., avoidance=a, policy="clean_first", length=64, tau=32.)[0], "overlap_pairs_per_time") for a in [0., .5, .9]]
    text = f"""# Numerical summary — study-01, descriptive draft

All values below are generated from the accepted aggregate CSVs; p values are
{fmt(pvalues, 6)} in ascending order. The reference display uses four agents,
zero dependency and zero avoidance unless stated otherwise.

**F1.** At synchronization interval 1, mean repair starts are
{fmt(repair_b)} for Bartender and {fmt(repair_i)} for in-place repair;
mean observed effort is {fmt(effort_b)} and {fmt(effort_i)}, respectively.
Across all 315 paired synchronization cells, Bartender's mean repair count is
lower in {signs['lower']}, equal in {signs['equal']} and higher in {signs['higher']}; these are signs of observed means, not significance decisions.

**F2.** For the largest p and zero avoidance, increasing the synchronization
interval from 0.125 to 32 changes observed overlap pairs per time from
{observed[0]:.4f} to {observed[-1]:.4f}; the corresponding first-order line runs
from {predicted[0]:.4f} to {predicted[-1]:.4f}.
Mean first-conflict rate changes from {f2_first[0]:.4f} to {f2_first[1]:.4f}
per time, and mean overlap size at first conflict from {f2_size[0]:.2f} to {f2_size[1]:.2f} lines.
At interval 32, the overlap-pair rates for avoidance 0, 0.5 and 0.9 are
{fmt(avoidance_rates, 4)} per time, respectively.

**F3.** At post-dispatch waiting time 4/μ with dispatch-time snapshots and a
fixed repair clock, completed-attempt failure fractions are
{fmt(f3['dispatch']['completed_failure_fraction'], 4)}, against nominal q values
{fmt([1-1/v for v in f3['dispatch']['prediction']], 4)}; re-reading at repair
start gives {fmt(f3['start']['completed_failure_fraction'], 4)} against
{fmt([1-1/v for v in f3['start']['prediction']], 4)}.
The pooled initial-conflict landing fractions at the window end are
{fmt([100*v for v in f3['dispatch']['pooled_landed_fraction']], 2)}% for dispatch-time
snapshots and {fmt([100*v for v in f3['start']['pooled_landed_fraction']], 2)}% for
re-reading; completed repairs per initial conflict are
{fmt(f3['dispatch']['completed_repairs_per_initial_conflict'], 3)} and
{fmt(f3['start']['completed_repairs_per_initial_conflict'], 3)}, respectively.

Coverage and statistical note: all 990 cells, 35 metrics and 11,010 paired
rows are retained. Of 34,650 aggregate rows, {result['aggregate_rows_n_below_30']}
have fewer than 30 nonmissing seed observations, including
{result['aggregate_rows_n_zero']} with n=0. Source intervals are mean ±
1.96 × sample SD / √n, pointwise and unadjusted. F3 uses finite-window pooled
totals, not an uncensored expected number of rounds; a ratio interval and a
dispatch-count distribution cannot be recovered from these aggregate inputs.
Both variants use waiting time δ on the horizontal axis; the starting-point
baseline has E=R throughout. Both q curves use nominal μ without fitting.
The initial-conflict landing identity is used only at zero dependency.
"""
    (output / "NUMERIC_SUMMARY.md").write_text(text)
    fig = plt.figure(figsize=(8.27, 11.69))
    plain = text.replace("**", "").split("\n", 1)[1].strip()
    paragraphs = [" ".join(p.split()) for p in plain.split("\n\n")]
    body = "\n\n".join(textwrap.fill(p, width=108) for p in paragraphs)
    fig.text(.07, .95, "Numerical summary — study-01", va="top", fontsize=14, weight="bold")
    fig.text(.07, .905, body, va="top", fontsize=9.5, linespacing=1.5)
    fig.savefig(output / "NUMERIC_SUMMARY.pdf", metadata={"Title": "Descriptive numerical summary", "Creator": "Matplotlib", "CreationDate": None, "ModDate": None})
    plt.close(fig)


def mechanism_check(data, output):
    rows = []
    for c in data.select("repair_delay"):
        s = c["scenario"]
        completed = data.mean(c, "author_repair_completions")
        failed = data.mean(c, "failed_repair_completions")
        conflict = data.mean(c, "conflict_cohort_n")
        exposure = ((s["delta"] if s["refresh_at"] == "dispatch" else 0) + s["repair_time"]) if s["repair_clock"] == "fixed" else None
        # With dependency=0, a fixed-footprint conflict cannot become clean
        # through a mechanical retry; each conflict landing completes a repair.
        unresolved_conflicts = conflict - (completed - failed) if s["dependency"] == 0 else None
        if unresolved_conflicts is not None and (data.mean(c, "dependency_rescues_without_repair") != 0 or unresolved_conflicts < -1e-9):
            raise ValueError("No-rescue conflict-cohort accounting failed")
        duration = s["delta"] + s["repair_time"]
        row = {"cell_id": c["cell_id"], **coords(c),
               "mean_completed_repair_attempts": completed, "mean_failed_completed_repairs": failed,
               "pooled_failure_fraction_completed_repairs": failed/completed if completed else "",
               "fixed_clock_collision_exposure": exposure if exposure is not None else "",
               "first_order_failure_probability": -math.expm1(-c["mu_nominal"]*exposure) if exposure is not None else "",
               "mean_initial_conflicts": conflict, "mean_dispatches": data.mean(c, "dispatches"),
               "pooled_dispatches_per_initial_conflict": data.pooled_dispatches(c),
               "mean_unresolved_initial_conflicts_no_dependency": unresolved_conflicts if unresolved_conflicts is not None else "",
               "pooled_unresolved_initial_conflict_fraction_no_dependency": unresolved_conflicts/conflict if unresolved_conflicts is not None and conflict else "",
               "seed_mean_over_five_unresolved_fraction": data.mean(c, "unresolved_over_threshold_fraction"),
               "window_divided_by_minimum_attempt_slot": s["horizon"]/duration,
               "maximum_completed_attempts_per_window": math.floor(s["horizon"]/duration),
               "maximum_dispatches_per_window_no_dependency": math.floor(s["horizon"]/duration)+1 if s["dependency"] == 0 and s["repair_clock"] == "fixed" else "",
               "unobserved_tail_mean_upper_bound": "not_identifiable_without_future_process_assumptions"}
        rows.append(row)
    write_csv(output / "attempt-failures-and-censoring.csv", rows)
    reference = sorted([r for r in rows if r["agents"] == 4 and r["dependency_probability"] == 0
                        and r["repair_clock"] == "fixed" and r["wait_in_characteristic_units"] == 4],
                       key=lambda r: (r["baseline_read_time"], r["nominal_overlap_probability"]))
    lines = ["# F3 mechanism and observable limits", "", "Static source facts (unchanged study model):",
             "", "1. Every call to `_dispatch` schedules repair start at current time plus δ for kick-back (`bartender_sim/model.py:301–307`). There is no first-dispatch exception. Failed repair completion clears the repair slot and requests another sync (`:393–411`), which dispatches through the same function (`:335–340`).",
             "2. Completed-repair failure fraction below is the pooled sum of failed completions divided by completed repairs. It excludes scheduled mechanical apply failures and uncompleted attempts. With zero dependency, these failures are overlap collisions. It does not establish independence or a stationary probability for all future attempts.",
             "3. No extra drain follows the fixed cutoff (`:429–446`). More than five ejections and still unlanded is a subset of right censoring, not its full extent. In the zero-dependency, fixed-footprint model, a detected conflict cannot disappear before a successful repair: subtracting successful repair completions from the initial-conflict count identifies the unlanded initial cohort. This identity is not applied to dependency cases.", "",
             "Reference: four agents, zero dependency/avoidance, fixed repair time 0.25, post-dispatch wait 4/μ. All observed values are computed from the accepted CSV counts; model probabilities and window budgets use only approved grid metadata.", "",
             "| Baseline read | p | Completed repair failures / completions | Nominal q | Pooled dispatches / initial conflict | Pooled initial conflicts unlanded | Seed-mean >5 ejections, unlanded | H/(δ+R) |",
             "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for r in reference:
        lines.append(f"| {r['baseline_read_time']} | {r['nominal_overlap_probability']:.6f} | {r['pooled_failure_fraction_completed_repairs']:.5f} | {r['first_order_failure_probability']:.5f} | {r['pooled_dispatches_per_initial_conflict']:.3f} | {r['pooled_unresolved_initial_conflict_fraction_no_dependency']:.2%} | {r['seed_mean_over_five_unresolved_fraction']:.2%} | {r['window_divided_by_minimum_attempt_slot']:.3f} |")
    lines += ["", "Each completed attempt occupies δ+R in the fixed-clock single repair slot. Thus H/(δ+R) bounds the total number of completed attempts per seed across all conflicts, not attempts per conflict. For the three reference p values this permits at most 7, 7 and 13 completions, respectively; without dependency rescue there can be at most one additional pending dispatch at cutoff. This is a within-window scheduling bound, not a bound on the missing future tail.",
              "", "**No finite, data-supported upper bound on the uncensored mean correction is identifiable from the aggregate inputs.** The undispatched or repeatedly ejected conflicts can require an unknown number of future attempts; the aggregate files contain neither their individual histories nor their unobserved future. The >5 subgroup's observed contribution cannot be isolated from these CSVs either. A geometric continuation, stationary q, independence, or a guaranteed finite future horizon would be additional assumptions, not measured corrections. Therefore the finite-window ratio is not a direct estimate of the uncensored geometric mean exp(μE); the original exponential-mean overlay was withdrawn for incompatible estimands. Revised F3 compares observed completed-attempt failures with nominal q and shows finite-window landings separately; it is not a fitted survival estimate.",
              "", "No simulation, parameter, approval, original output or first-order formula has been altered or fitted. Full dispatch-count distributions remain a separately scoped analysis decision."]
    (output / "MECHANISM_CHECK.md").write_text("\n".join(lines)+"\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "analysis/results")
    parser.add_argument("--main-only", action="store_true", help="Skip the full-grid supplementary PDF atlases.")
    args = parser.parse_args()
    output = args.output_dir
    output.mkdir(parents=True, exist_ok=True)
    data = Data()
    save(f1(data), output, "f1_repairs_overlap", "F1: repair count and effort across overlap probabilities")
    save(f2(data), output, "f2_sync_interval", "F2: synchronization interval, overlaps and first conflicts")
    save(f3(data), output, "f3_attempts_and_landings", "F3: completed-attempt failures and finite-window landings")
    tables(data, output)
    numeric_summary(data, output)
    mechanism_check(data, output)
    pages = {}
    if not args.main_only:
        metadata = {"Creator": "Matplotlib", "CreationDate": None, "ModDate": None}
        with PdfPages(output / "supplement_f1_all_sync_slices.pdf", metadata=metadata) as pdf:
            for avoidance in [0., .5, .9]:
                for tau in [.125, .25, .5, 1., 2., 8., 32.]:
                    fig = f1(data, avoidance, tau); pdf.savefig(fig); plt.close(fig)
            pages["f1"] = pdf.get_pagecount()
        with PdfPages(output / "supplement_f2_all_agents_dependencies_policies.pdf", metadata=metadata) as pdf:
            for agents, dependency in [(2, 0.), (4, 0.), (8, 0.), (4, .1), (4, .3)]:
                for policy in ["clean_first", "in_place"]:
                    fig = f2(data, agents, dependency, policy); pdf.savefig(fig); plt.close(fig)
            pages["f2"] = pdf.get_pagecount()
        with PdfPages(output / "supplement_f3_all_delay_slices.pdf", metadata=metadata) as pdf:
            for agents, dependency, avoidance in [(2, 0., 0.), (4, 0., 0.), (8, 0., 0.), (4, .1, 0.), (4, .1, .5)]:
                for clock in ["fixed", "context"]:
                    fig = f3(data, agents, dependency, avoidance, clock); pdf.savefig(fig); plt.close(fig)
            pages["f3"] = pdf.get_pagecount()
    if any(digest(SOURCE / name) != expected for name, expected in INPUT_HASHES.items()):
        raise ValueError("Input mutation during analysis")
    manifest = {"analysis_version": 2, "python": platform.python_version(), "matplotlib": matplotlib.__version__,
                "numpy": np.__version__, "script_sha256": digest(Path(__file__)),
                "inputs_sha256": {"deliverables/study-01/" + k: v for k, v in INPUT_HASHES.items()},
                "cells": len(data.cells), "summary_rows": len(data.rows), "paired_rows": len(data.paired),
                "full_grid_supplement_pages": pages, "source_inputs_unchanged": True,
                "files": {p.name: {"bytes": p.stat().st_size, "sha256": digest(p)} for p in sorted(output.iterdir()) if p.is_file() and p.name != "analysis-manifest.json"}}
    (output / "analysis-manifest.json").write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n")
    print(json.dumps({"cells": manifest["cells"], "summary_rows": manifest["summary_rows"], "paired_rows": manifest["paired_rows"], "supplement_pages": pages, "source_inputs_unchanged": True}, indent=2))


if __name__ == "__main__":
    main()
