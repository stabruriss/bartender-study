"""Serialization and retained-output regression controls; no study seeds."""

from collections import Counter
from contextlib import redirect_stdout
import copy
import csv
import io
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import handoff
from bartender_sim.__main__ import run_study, source_fingerprint
from bartender_sim.plan import cells, load_config, parameters_digest
from bartender_sim.report import summarize, write_csv


class OrderingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temporary.name)
        cls.config = load_config(handoff.CONFIG)
        cls.config.update(title="TEST ONLY: serialization control", seeds=list(range(800001, 800031)))
        cls.config["common"].update(n=1, rate=0, horizon=1, tau=1)
        cls.config["suites"] = [{"name": "serialization_control",
                                 "axes": {"tau": [1, 2], "policy": ["clean_first", "in_place"]}}]
        cls.config["approval"] = {"status": "approved", "approved_by": "test fixture",
                                   "approved_at": "test only",
                                   "parameters_sha256": parameters_digest(cls.config)}
        cls.config_path = cls.root / "config.json"
        cls.config_path.write_text(json.dumps(cls.config))
        original = cls.root / "original"
        source = {**source_fingerprint(handoff.ROOT), "git_dirty": False}
        with patch("bartender_sim.__main__.source_fingerprint", return_value=source), redirect_stdout(io.StringIO()):
            assert run_study(cls.config, cells(cls.config), original) == 0
        approval = {"status": "approved", "approved_by": "test fixture", "approved_at": "test only",
                    "run_id": "fixture", "parameters_sha256": parameters_digest(cls.config),
                    "protocol_sha256": handoff.protocol_hash()}
        handoff.write(original / "RUN_APPROVAL.json", approval)
        handoff.write(original / "execution.json", {
            "status": "complete", "exit_code": 0, "protocol_sha256": handoff.protocol_hash(),
            "approval_sha256": handoff.file_hash(original / "RUN_APPROVAL.json"), "wall_seconds": 0,
            "started_at": "2000-01-01T00:00:00+00:00", "finished_at": "2000-01-01T00:00:00+00:00",
            "environment": {"python": "3.12.4", "implementation": "CPython", "python_hash_seed": "0"}})

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def setUp(self):
        self.case = tempfile.TemporaryDirectory(dir=self.root)
        self.output = Path(self.case.name) / "fixture"
        shutil.copytree(self.root / "original", self.output)
        self.config_patch = patch.object(handoff, "CONFIG", self.config_path)
        self.config_patch.start()

    def tearDown(self):
        self.config_patch.stop()
        self.case.cleanup()

    def test_serialization_changes_order_but_not_verified_content(self):
        saved = handoff.read(self.output / "cells.json")
        regenerated = cells(handoff.read(self.output / "config.json"))
        self.assertNotEqual(saved, regenerated)
        self.assertEqual(Counter(handoff.canonical(c) for c in saved),
                         Counter(handoff.canonical(c) for c in regenerated))
        records = [json.loads(line) for line in (self.output / "summaries.jsonl").read_text().splitlines()]
        _, contrasts = summarize(records)
        rebuilt = Path(self.case.name) / "rebuilt.csv"
        write_csv(rebuilt, contrasts)
        self.assertNotEqual(rebuilt.read_bytes(), (self.output / "paired-differences.csv").read_bytes())
        self.assertEqual(handoff.verify_output(self.output)["status"], "pass")

    def test_csv_row_reordering_is_accepted_without_rewriting_original(self):
        path = self.output / "paired-differences.csv"
        with path.open(newline="") as stream:
            rows = list(csv.reader(stream))
        with path.open("w", newline="") as stream:
            csv.writer(stream).writerows([rows[0], *reversed(rows[1:])])
        before = path.read_bytes()
        self.assertEqual(handoff.verify_output(self.output)["status"], "pass")
        self.assertEqual(path.read_bytes(), before)

    def test_missing_duplicate_and_changed_grid_entries_remain_hold(self):
        path = self.output / "cells.json"
        original = handoff.read(path)
        changed = copy.deepcopy(original)
        changed[0]["scenario"]["tau"] = 99
        for bad in [original[:-1], original + [original[0]], changed]:
            with self.subTest(grid=bad):
                path.write_text(json.dumps(bad))
                self.assertIn("saved grid or parameter digest mismatch",
                              handoff.verify_output(self.output)["issues"])

    def test_missing_duplicate_and_changed_csv_values_remain_hold(self):
        path = self.output / "paired-differences.csv"
        with path.open(newline="") as stream:
            original = list(csv.reader(stream))
        changed = copy.deepcopy(original)
        changed[1][original[0].index("mean")] = "999"
        for bad in [original[:-1], original + [original[1]], changed]:
            with self.subTest(rows=bad[:2]):
                with path.open("w", newline="") as stream:
                    csv.writer(stream).writerows(bad)
                self.assertIn("paired-differences.csv does not match the per-seed records",
                              handoff.verify_output(self.output)["issues"])

    def test_old_execution_protocol_is_not_implicitly_accepted(self):
        path = self.output / "execution.json"
        receipt = handoff.read(path)
        receipt["protocol_sha256"] = "0" * 64
        path.write_text(json.dumps(receipt))
        self.assertIn("execution receipt or protocol approval mismatch",
                      handoff.verify_output(self.output)["issues"])


class RecollectionTests(unittest.TestCase):
    def test_approval_inventory_and_append_only_record_gates(self):
        config = load_config(handoff.CONFIG)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            output, original = root / "outputs/control", root / "deliverables/control"
            output.mkdir(parents=True)
            original.mkdir(parents=True)
            handoff.write(root / "config.json", config)
            handoff.write(output / "execution.json", {"protocol_sha256": "1" * 64})
            handoff.write(output / "RUN_APPROVAL.json", {"fixture": "test only"})
            (output / "payload.txt").write_text("retained diagnostic bytes\n")
            handoff.write(original / "verification.json", {"status": "hold", "issues": ["old comparator"]})
            (original / "RUN_REPORT.md").write_text("Original HOLD report\n")
            inventory = {"archive_sha256": "2" * 64,
                         "files": [{"path": f"control/{p.name}", "bytes": p.stat().st_size,
                                    "sha256": handoff.file_hash(p)} for p in output.iterdir()]}
            handoff.write(original / "artifact-index.json", inventory)
            controls = {"status": "pass", "tests_run": 1, "failure_ids": [], "error_ids": [], "skipped_ids": [],
                        "protocol_sha256": "3" * 64,
                        "environment": {"python": "3.12.4", "python_hash_seed": "0"}}
            handoff.write(root / "validation/controls-recheck.json", controls)
            approval = {"status": "pending", "scope": "collect-only", "approved_by": "test fixture",
                        "approved_at": "test only", "run_id": "control", "verification_id": "check-01",
                        "parameters_sha256": parameters_digest(config), "protocol_sha256": "3" * 64,
                        "execution_protocol_sha256": "1" * 64,
                        "execution_receipt_sha256": handoff.file_hash(output / "execution.json"),
                        "execution_approval_sha256": handoff.file_hash(output / "RUN_APPROVAL.json"),
                        "artifact_index_sha256": handoff.file_hash(original / "artifact-index.json"),
                        "original_verification_sha256": handoff.file_hash(original / "verification.json"),
                        "controls_record": "validation/controls-recheck.json"}
            handoff.write(root / "REVALIDATION_APPROVAL.json", approval)
            preserved = {str(p): p.read_bytes() for p in original.iterdir()}
            previous_cwd = Path.cwd()
            try:
                os.chdir(root)
                with patch.object(handoff, "ROOT", root), patch.object(handoff, "CONFIG", Path("config.json")), \
                        patch.object(handoff, "require_environment"), \
                        patch.object(handoff, "protocol_hash", return_value="3" * 64), \
                        patch.object(handoff, "verify_output", return_value={"status": "pass", "issues": []}) as verify:
                    with self.assertRaisesRegex(ValueError, "collect-only approval"):
                        handoff.collect("control", "check-01")
                    verify.assert_not_called()
                    self.assertFalse((original / "rechecks").exists())
                    approval["status"] = "approved"
                    handoff.write(Path("REVALIDATION_APPROVAL.json"), approval, mode="w")
                    self.assertEqual(handoff.collect("control", "check-01"), 0)
                    verify.assert_called_once_with(Path("outputs/control"), execution_protocol_sha256="1" * 64)
                    result = handoff.read(original / "rechecks/check-01/verification.json")
                    self.assertTrue(result["raw_files_match_original_inventory"])
                    with self.assertRaisesRegex(ValueError, "already exists"):
                        handoff.collect("control", "check-01")
                    approval["verification_id"] = "check-02"
                    handoff.write(Path("REVALIDATION_APPROVAL.json"), approval, mode="w")
                    (output / "payload.txt").write_text("changed diagnostic bytes\n")
                    verify.return_value = {"status": "pass", "issues": []}
                    self.assertEqual(handoff.collect("control", "check-02"), 1)
                    result = handoff.read(original / "rechecks/check-02/verification.json")
                    self.assertIn("raw files differ from the original archive inventory", result["issues"])
                    for name, contents in preserved.items():
                        self.assertEqual(Path(name).read_bytes(), contents)
            finally:
                os.chdir(previous_cwd)


if __name__ == "__main__":
    unittest.main()
