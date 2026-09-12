"""Export coordinates from the actual Matplotlib artists before vector saving.

This module loads no input files and computes no scientific estimates. It uses
already loaded source rows for provenance fields. The independent verifier
reconstructs the coordinates from the accepted inputs.
"""
from __future__ import annotations

import math
import json


def tag(line, *, cells, formula, x_definition, panel, source_metrics=(), errors=None, series_label=None):
    line._source_record = {"cells": cells, "formula": formula,
                           "x_definition": x_definition, "panel": panel,
                           "source_metrics": source_metrics, "errors": errors,
                           "series_label": line.get_label() if series_label is None else series_label}
    return line


def tag_errorbar(ax, *, cells, metric, x_definition, panel):
    container = ax.containers[-1]
    return tag(container.lines[0], cells=cells, formula="summary_mean",
               x_definition=x_definition, panel=panel, source_metrics=(metric,),
               errors=container.lines[2][0], series_label=container.get_label())


def coordinates(fig, name, input_hashes, source_index):
    rows = []
    for axes_index, ax in enumerate(fig.axes):
        for line in ax.lines:
            source = getattr(line, "_source_record", None)
            if source is None:
                continue  # Reference ticks, annotation brackets and error caps.
            xs, ys = line.get_xdata(orig=False), line.get_ydata(orig=False)
            cells = source["cells"]
            if len(cells) == 1:
                cells = cells * len(xs)
            if len(cells) != len(xs) or len(xs) != len(ys):
                raise ValueError("Artist/source coordinate count mismatch")
            segments = source["errors"].get_segments() if source["errors"] is not None else None
            if segments is not None and len(segments) != len(xs):
                raise ValueError("Error-bar coordinate count mismatch")
            for index, (x, y, cell) in enumerate(zip(xs, ys, cells)):
                if not math.isfinite(x) or not math.isfinite(y):
                    raise ValueError("Nonfinite displayed coordinate")
                low, high = "", ""
                if segments is not None:
                    segment = segments[index]
                    if len(segment) != 2 or any(abs(v[0]-x) > 1e-12 for v in segment):
                        raise ValueError("Error bar does not match its plotted point")
                    low, high = float(segment[0][1]), float(segment[1][1])
                rows.append({"figure": name, "axes_index": axes_index, "panel": source["panel"],
                             "series": source["series_label"], "point_index": index,
                             "cell_id": cell["cell_id"],
                             "source_metrics": "|".join(source["source_metrics"]),
                             "source_components_json": json.dumps({metric: {
                                 field: source_index[cell["cell_id"], metric][field]
                                 for field in ["n", "mean", "ci95_low", "ci95_high"]}
                                 for metric in source["source_metrics"]}, sort_keys=True, separators=(",", ":")),
                             "observations_sha256": "" if source["formula"].startswith("nominal_") else input_hashes["summary.csv"],
                             "metadata_sha256": input_hashes["cells.json"],
                             "formula": source["formula"], "x_definition": source["x_definition"],
                             "x": float(x), "y": float(y), "ci95_low": low, "ci95_high": high,
                             "line_style": line.get_linestyle(), "marker": line.get_marker(),
                             "x_axis_scale": ax.get_xscale(), "y_axis_scale": ax.get_yscale()})
    return rows
