"""Check that coordinate/source/coverage/style corruption is rejected.

Only temporary copies are changed. The declared plot-data checksum is updated
in each copy, so this tests more than detection of an outdated file hash.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
import tempfile

from verify_plot_data import ROOT, sha, verify


def main():
    source = ROOT / "analysis/manuscript"
    with (source / "plot-data.csv").open(newline="") as handle:
        original = list(csv.DictReader(handle))
    results = []
    with tempfile.TemporaryDirectory(prefix="plot-verifier-") as temporary:
        for case in ["alter_y", "wrong_cell", "missing_point", "duplicate_point", "wrong_baseline_style"]:
            directory = Path(temporary) / case
            directory.mkdir()
            for path in source.iterdir():
                if path.is_file() and path.name not in ["plot-data.csv", "manifest.json"]:
                    (directory / path.name).symlink_to(path)
            rows = [dict(r) for r in original]
            i = next(i for i, r in enumerate(rows) if r["figure"] == "fig6_wait_resolved"
                     and r["formula"] == "completed_minus_failed_over_initial")
            if case == "alter_y":
                rows[i]["y"] = str(float(rows[i]["y"]) + .02)
            elif case == "wrong_cell":
                rows[i]["cell_id"] = rows[0]["cell_id"]
            elif case == "missing_point":
                rows.pop(i)
            elif case == "duplicate_point":
                rows.append(dict(rows[i]))
            else:
                i = next(i for i, r in enumerate(rows) if r["formula"].startswith("zero_wait_reference:"))
                rows[i]["line_style"] = "--"
            path = directory / "plot-data.csv"
            with path.open("w", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(original[0]), lineterminator="\n")
                writer.writeheader()
                writer.writerows(rows)
            manifest = json.loads((source / "manifest.json").read_text())
            manifest["outputs"]["plot-data.csv"] = {"sha256": sha(path), "bytes": path.stat().st_size}
            manifest["plot_coordinate_rows"] = len(rows)
            (directory / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
            try:
                verify(directory)
            except ValueError as exc:
                results.append({"case": case, "status": "correctly_rejected", "reason": str(exc)})
            else:
                raise RuntimeError("Verifier accepted corrupted data: " + case)
    result = {"status": "pass", "cases": results, "verifier_sha256": sha(ROOT / "analysis/verify_plot_data.py"),
              "check_script_sha256": sha(Path(__file__)), "original_plot_data_sha256": sha(source / "plot-data.csv"),
              "note": "Temporary copies only; declared plot-data hashes updated before checking coordinate/source/coverage/style failures."}
    (source / "plot-verifier-negative-checks.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": "pass", "corruptions_rejected": len(results)}))


if __name__ == "__main__":
    main()
