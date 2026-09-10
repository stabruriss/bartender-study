"""Illustrate synchronization and repair delay along a central shared branch."""

from math import atan2, degrees

from matplotlib.patches import Circle

from figure_style import GRAY, INK, arrow, box, canvas, export, text


STEM = "fig2_delay_context"


def labeled_arrow(ax, start, end, label, dashed=False, offset=0.055, size=8.3):
    arrow(ax, start, end, dashed=dashed)
    angle = degrees(atan2(end[1] - start[1], end[0] - start[0]))
    if angle < -90:
        angle += 180
    if angle > 90:
        angle -= 180
    text(ax, (start[0] + end[0]) / 2, (start[1] + end[1]) / 2 + offset,
         label, size=size, ha="center", rotation=angle,
         rotation_mode="anchor",
         bbox={"facecolor": "white", "edgecolor": "none", "pad": 1.3},
         zorder=5)


def landed(ax, x, y):
    ax.add_patch(Circle((x, y), 0.036, facecolor=INK, edgecolor="white",
                        linewidth=0.55, zorder=4))


def conflict(ax, x, y):
    ax.plot([x - 0.045, x + 0.045], [y - 0.045, y + 0.045],
            color=INK, linewidth=1.4, zorder=4)
    ax.plot([x - 0.045, x + 0.045], [y + 0.045, y - 0.045],
            color=INK, linewidth=1.4, zorder=4)


def frame(ax, x, top, title):
    """Agent A and Agent B flank Main; all three lines run downward in time."""
    left, main, right = x + 0.50, x + 1.75, x + 3.00
    text(ax, x, top + 0.59, title, size=10.7, weight="bold")
    for cx, label in [(left, "Agent A"), (right, "Agent B")]:
        box(ax, cx - 0.44, top + 0.07, 0.88, 0.29)
        text(ax, cx, top + 0.215, label, size=9.1, weight="bold", ha="center")
        ax.plot([cx, cx], [top + 0.07, top - 1.89], color="#b7b7b7",
                linewidth=0.7, linestyle=(0, (2, 2)), zorder=0.8)
    text(ax, main, top + 0.215, "Main", size=9.5, weight="bold", ha="center")
    ax.plot([main, main], [top + 0.04, top - 1.87],
            color=INK, linewidth=1.55, zorder=2)
    arrow(ax, (main, top - 1.84), (main, top - 1.96))
    return left, main, right


def accumulated_context(ax, main, top, first, last):
    """Hatching is a qualitative context annotation, not a duration scale."""
    box(ax, main - 0.10, top + last, 0.20, first - last,
        fill="#ededed", hatch="///", edge="#9c9c9c", linewidth=0.55, zorder=0.5)


def draw():
    fig, ax = canvas(8.60)
    text(ax, 0.26, 8.29, "Delay changes what reaches Main before a repair",
         size=12.9, weight="bold")
    text(ax, 0.26, 8.00,
         "Time runs downward. Dots: landed edits. ×: conflict. Events and spacing are schematic.",
         size=8.8, color=GRAY)

    text(ax, 0.26, 7.63, "(a) Synchronization interval, τ", size=11.2, weight="bold")
    text(ax, 0.26, 7.35,
         "auth.rs: A edits lines 10–20 on Monday; B will edit lines 15–25.", size=9.1)
    upper = 6.43
    a, main, b = frame(ax, 0.26, upper, "Daily synchronization")
    labeled_arrow(ax, (a, upper - 0.15), (main, upper - 0.65), "Mon: A lands")
    landed(ax, main, upper - 0.65)
    labeled_arrow(ax, (main, upper - 0.78), (b, upper - 1.01), "Read base")
    text(ax, b, upper - 1.18, "B starts Tuesday", size=8.0, ha="center",
         bbox={"facecolor": "white", "edgecolor": "none", "pad": 1.1})
    labeled_arrow(ax, (b, upper - 1.34), (main, upper - 1.69), "B lands")
    landed(ax, main, upper - 1.69)
    text(ax, main, upper - 2.20, "A is already in B's base;\nat most one local hunk in this example.",
         size=8.8, ha="center")

    a, main, b = frame(ax, 3.96, upper, "Weekly synchronization")
    accumulated_context(ax, main, upper, -0.96, -1.69)
    labeled_arrow(ax, (a, upper - 0.15), (main, upper - 0.95), "Fri: A lands")
    landed(ax, main, upper - 0.95)
    for dy in [-1.14, -1.34, -1.51]:
        landed(ax, main, upper + dy)
    text(ax, main - 0.25, upper - 1.32, "other edits", size=8.0,
         rotation=90, ha="center", color=GRAY)
    labeled_arrow(ax, (b, upper - 0.30), (main, upper - 1.69), "Fri: B submits")
    conflict(ax, main, upper - 1.69)
    text(ax, main, upper - 2.20, "The same overlap on Friday,\nwith a week of surrounding changes.",
         size=8.8, ha="center")

    ax.plot([3.8, 3.8], [4.03, 7.12], color="#d0d0d0", linewidth=0.7)
    ax.plot([0.26, 7.34], [3.91, 3.91], color="#b0b0b0", linewidth=0.8)
    text(ax, 0.26, 3.63, "(b) Waiting after dispatch, δ", size=11.2, weight="bold")
    text(ax, 0.26, 3.35,
         "10:00: detect the conflict and dispatch to A. A repairs from that snapshot.", size=9.1)
    lower = 2.42
    a, main, b = frame(ax, 0.26, lower, "Immediate repair")
    conflict(ax, main, lower - 0.13)
    labeled_arrow(ax, (main, lower - 0.22), (a, lower - 0.50), "Dispatch")
    labeled_arrow(ax, (a, lower - 0.65), (main, lower - 1.04),
                  "Repair + submit", size=8.1)
    landed(ax, main, lower - 1.04)
    labeled_arrow(ax, (b, lower - 0.75), (main, lower - 1.58), "Other edits")
    landed(ax, main, lower - 1.58)
    text(ax, main, lower - 2.19, "A repairs against fresh context;\nits repair lands before B's next edit.",
         size=8.8, ha="center")

    a, main, b = frame(ax, 3.96, lower, "Repair two days later")
    accumulated_context(ax, main, lower, -0.84, -1.61)
    conflict(ax, main, lower - 0.13)
    labeled_arrow(ax, (main, lower - 0.22), (a, lower - 0.50), "Dispatch")
    labeled_arrow(ax, (b, lower - 0.41), (main, lower - 0.85), "Other edits")
    for dy in [-0.85, -1.06, -1.27]:
        landed(ax, main, lower + dy)
    text(ax, a + 0.14, lower - 0.92, "2-day wait", size=8.3,
         rotation=90, ha="center", color=GRAY)
    text(ax, main + 0.24, lower - 1.24, "Main advances", size=8.0,
         rotation=90, ha="center", color=GRAY)
    labeled_arrow(ax, (a, lower - 1.33), (main, lower - 1.60), "Re-submit")
    conflict(ax, main, lower - 1.60)
    labeled_arrow(ax, (main, lower - 1.68), (a, lower - 1.85),
                  "Possible retry", dashed=True, offset=-0.025, size=8.0)
    text(ax, main, lower - 2.19, "Other edits accumulate during the wait;\nre-submission may conflict again.",
         size=8.8, ha="center")
    ax.plot([3.8, 3.8], [0.13, 3.11], color="#d0d0d0", linewidth=0.7)
    return fig


if __name__ == "__main__":
    export(draw(), STEM, "Delay changes what reaches Main before a repair",
           "Schematic timelines with Agent A and Agent B flanking Main. "
           "Daily versus weekly synchronization and immediate versus delayed repair. "
           "Dots and spacing are illustrative, not observations. "
           "The waiting example uses a dispatch-time snapshot; renewed conflict is possible, not guaranteed.")
