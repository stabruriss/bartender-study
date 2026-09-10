"""Draw the four-worktree example in Section 5.2; no simulation is run."""

from figure_style import GRAY, LIGHT, arrow, box, canvas, export, text


STEM = "fig1_repair_timelines"


def repair(ax, x, y, worktree, landed, poisoned=False):
    """A repair block records identities present when that repair starts."""
    width, height = 1.18, 0.72
    box(ax, x, y, width, height)
    box(ax, x, y, 0.12, height, fill=LIGHT,
        hatch="xxx" if poisoned else "////", linewidth=0.6)
    text(ax, x + 0.65, y + 0.50, f"Repair {worktree}",
         size=10.2, weight="bold", ha="center")
    text(ax, x + 0.65, y + 0.29, "Already landed", size=8.1, ha="center")
    text(ax, x + 0.65, y + 0.105, landed, size=9.3, ha="center")


def draw():
    fig, ax = canvas(3.75)
    text(ax, 0.26, 3.47, "Clean work first changes the repair ledger",
         size=13.1, weight="bold")
    text(ax, 0.26, 3.17,
         "Scan order: A → B → C → D. Initially, A and C are clean; B and D conflict with the base.",
         size=9.0)

    xs = [1.73, 3.13, 4.53, 5.93]
    upper, lower = 2.05, 0.99
    text(ax, 0.26, upper + 0.46, "In-place repair", size=10.5, weight="bold")
    text(ax, 0.26, upper + 0.17, "3 repairs", size=12.2, weight="bold")
    text(ax, 0.26, lower + 0.46, "Bartender", size=10.5, weight="bold")
    text(ax, 0.26, lower + 0.17, "2 repairs", size=12.2, weight="bold")

    for start, end in zip(xs, xs[1:]):
        arrow(ax, (start + 1.18, upper + 0.36), (end - 0.035, upper + 0.36))
    box(ax, xs[0], upper, 1.18, 0.72, fill="#f4f4f4")
    text(ax, xs[0] + 0.59, upper + 0.44, "A lands",
         size=10.2, weight="bold", ha="center")
    text(ax, xs[0] + 0.59, upper + 0.19, "No repair", size=8.8, ha="center")
    repair(ax, xs[1], upper, "B", "{A}")
    repair(ax, xs[2], upper, "C", "{A, B}", poisoned=True)
    repair(ax, xs[3], upper, "D", "{A, B, C}")
    text(ax, xs[2] + 0.59, upper - 0.17, "B's repair makes C conflict",
         size=8.2, ha="center", color=GRAY)

    # The automatic pass retains the original A, B, C, D scan order.
    box(ax, xs[0], lower, 2.58, 0.72, edge=GRAY, zorder=0.5)
    text(ax, xs[0] + 1.29, lower + 0.54, "Automatic pass",
         size=9.2, weight="bold", ha="center")
    for index, (name, state) in enumerate(
        [("A", "lands"), ("B", "held"), ("C", "lands"), ("D", "held")]
    ):
        x = xs[0] + 0.10 + index * 0.62
        box(ax, x, lower + 0.08, 0.51, 0.32,
            fill="#f4f4f4" if state == "lands" else "white",
            linestyle="-" if state == "lands" else (0, (2, 1)),
            edge=GRAY, linewidth=0.65)
        text(ax, x + 0.255, lower + 0.24, f"{name} {state}",
             size=8.0, ha="center")
        if index < 3:
            arrow(ax, (x + 0.515, lower + 0.24), (x + 0.60, lower + 0.24))
    arrow(ax, (xs[0] + 2.58, lower + 0.36), (xs[2] - 0.035, lower + 0.36))
    arrow(ax, (xs[2] + 1.18, lower + 0.36), (xs[3] - 0.035, lower + 0.36))
    repair(ax, xs[2], lower, "B", "{A, C}")
    repair(ax, xs[3], lower, "D", "{A, C, B}")

    # A paper legend uses patterns, outlines, and text rather than color.
    legend_y = 0.62
    box(ax, 0.26, legend_y - 0.07, 0.19, 0.14, fill="#f4f4f4", edge=GRAY)
    text(ax, 0.53, legend_y, "Land without repair", size=8.4)
    box(ax, 2.20, legend_y - 0.07, 0.19, 0.14, fill=LIGHT, hatch="////")
    text(ax, 2.47, legend_y, "Repair", size=8.4)
    box(ax, 3.34, legend_y - 0.07, 0.19, 0.14, fill=LIGHT, hatch="xxx")
    text(ax, 3.61, legend_y, "Repair caused by an earlier repair", size=8.4)
    text(ax, 0.26, 0.34,
         "Already landed: original worktree identities at repair start; every repaired item then lands.",
         size=8.2, color=GRAY)
    text(ax, 0.26, 0.13,
         "Event order only. Spacing does not encode elapsed time or repair effort.",
         size=8.2, color=GRAY)
    return fig


if __name__ == "__main__":
    export(draw(), STEM, "Clean work first changes the repair ledger",
           "Schematic of the four-worktree fixed-batch example. "
           "Three author repairs under in-place repair and two under Bartender. "
           "Block spacing is not a time or effort scale.")
