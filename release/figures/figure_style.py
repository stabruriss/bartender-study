"""Shared drawing and vector export helpers for the Section 5 schematics."""

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle


INK = "#202020"
GRAY = "#626262"
LIGHT = "#e5e5e5"
WIDTH = 7.6

matplotlib.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9.5,
    "text.color": INK,
    "axes.unicode_minus": False,
    "hatch.linewidth": 0.55,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "svg.fonttype": "none",
    "svg.hashsalt": "bartender-section-five-schematics",
    "savefig.facecolor": "white",
})


def canvas(height):
    fig = plt.figure(figsize=(WIDTH, height), facecolor="white")
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set(xlim=(0, WIDTH), ylim=(0, height))
    ax.axis("off")
    return fig, ax


def text(ax, x, y, value, size=9.5, weight="normal", color=INK, **kwargs):
    return ax.text(x, y, value, fontsize=size, fontweight=weight, color=color,
                   va="center", linespacing=1.35, **kwargs)


def box(ax, x, y, width, height, fill="white", hatch=None,
        edge=INK, linewidth=0.8, linestyle="-", zorder=2):
    patch = Rectangle((x, y), width, height, facecolor=fill, edgecolor=edge,
                      linewidth=linewidth, hatch=hatch, linestyle=linestyle,
                      zorder=zorder)
    ax.add_patch(patch)
    return patch


def arrow(ax, start, end, dashed=False, curve=0, zorder=1):
    patch = FancyArrowPatch(
        start, end, arrowstyle="-|>", mutation_scale=8,
        linewidth=0.85, color=GRAY,
        linestyle=(0, (3, 2)) if dashed else "-",
        connectionstyle=f"arc3,rad={curve}", shrinkA=0, shrinkB=0,
        zorder=zorder,
    )
    ax.add_patch(patch)
    return patch


def export(fig, stem, title, description):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).parent)
    parser.add_argument("--preview-dir", type=Path,
                        help="Optional directory for a PNG preview.")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    fig.canvas.draw()
    fig.savefig(args.output_dir / f"{stem}.pdf", metadata={
        "Title": title, "Subject": description, "Creator": "Matplotlib",
        "CreationDate": None, "ModDate": None,
    })
    fig.savefig(args.output_dir / f"{stem}.svg", metadata={
        "Title": title, "Description": description,
        "Creator": "Matplotlib", "Date": None,
    })
    if args.preview_dir is not None:
        args.preview_dir.mkdir(parents=True, exist_ok=True)
        fig.savefig(args.preview_dir / f"{stem}.png", dpi=200)
    plt.close(fig)

