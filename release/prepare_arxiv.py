#!/usr/bin/env python3
"""Package an already compiled flat manuscript; no scientific computation."""

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import tarfile


FILES = ["main.tex", "main.bbl", "references.bib", "sn-jnl.cls",
         "sn-mathphys-ay.bst"] + [f"Fig{i}.pdf" for i in range(1, 8)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("release/arxiv"))
    args = parser.parse_args()
    payload = {name: (args.source_dir / name).read_bytes() for name in FILES}
    tex = payload["main.tex"].decode("utf-8")
    if re.search(r"DraftPlaceholder|Author TBD|Affiliation TBD|Author to supply", tex):
        raise ValueError("Fill manuscript metadata and declarations before packaging")
    if re.search(r"^\s*\\(?:input|include)\s*\{", tex, re.M):
        raise ValueError("Expected one flat manuscript, with no source includes")
    figures = re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", tex)
    if sorted(figures) != [f"Fig{i}.pdf" for i in range(1, 8)]:
        raise ValueError("Expected exactly seven flat PDF figure references")
    if len(re.findall(rb"^\\bibitem\b", payload["main.bbl"], re.M)) != 14:
        raise ValueError("Expected the complete fourteen-entry compiled bibliography")
    source = args.output_dir / "source"
    source.mkdir(parents=True, exist_ok=True)
    unexpected = {p.name for p in source.iterdir()} - set(FILES)
    if unexpected:
        raise ValueError("Unexpected files in source export: " + ", ".join(sorted(unexpected)))
    for name, data in payload.items():
        (source / name).write_bytes(data)
    archive = args.output_dir / "arxiv-source.tar.gz"
    with archive.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.USTAR_FORMAT) as tar:
                for name in sorted(payload):
                    entry = tarfile.TarInfo(name)
                    entry.size = len(payload[name])
                    entry.mode = 0o644
                    entry.mtime = entry.uid = entry.gid = 0
                    entry.uname = entry.gname = ""
                    tar.addfile(entry, io.BytesIO(payload[name]))
    manifest = {
        "status": "ready-for-arxiv-service-preview",
        "processor": "pdflatex",
        "files": {name: {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
                  for name, data in sorted(payload.items())},
        "archive": {"file": archive.name, "bytes": archive.stat().st_size,
                    "sha256": hashlib.sha256(archive.read_bytes()).hexdigest()},
        "excluded": ["build PDFs", "logs", "auxiliary state", "machine paths", "editor files"],
        "third_party": ["sn-jnl.cls", "sn-mathphys-ay.bst"],
        "note": "Upstream template notices are preserved. This package does not approve submission."
    }
    (args.output_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"files": len(payload), "archive_sha256": manifest["archive"]["sha256"]}))


if __name__ == "__main__":
    main()
