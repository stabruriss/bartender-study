import copy
from contextlib import redirect_stdout
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch

import handoff
from bartender_sim.__main__ import run_study, source_fingerprint
from bartender_sim.plan import cells, load_config, parameters_digest


class HandoffTests(unittest.TestCase):
    def test_pending_approval_stops_before_output_is_created(self):
        with patch.dict(os.environ, {"PYTHONHASHSEED": "0"}), self.assertRaises(ValueError):
            handoff.preflight("unit-control-never-run")
        self.assertFalse(Path("outputs/unit-control-never-run").exists())

    def test_reproducibility_hash_covers_full_results_and_case_membership(self):
        a = handoff.determinism_record("m1")
        b = handoff.determinism_record("m4")
        # Both execute locally here; this is a helper control, not a cross-machine claim.
        for record in (a, b):
            record["environment"]["python_hash_seed"] = "0"
        self.assertEqual(handoff.compare(a, b)["records_compared"], 18)
        b["payload"]["records"][0]["result_sha256"] = "0" * 64
        b["payload_sha256"] = handoff.digest(b["payload"])
        with self.assertRaises(ValueError):
            handoff.compare(a, b)
        b = copy.deepcopy(a)
        b["payload"]["records"].pop()
        b["payload_sha256"] = handoff.digest(b["payload"])
        with self.assertRaises(ValueError):
            handoff.compare(a, b)

    def test_output_verification_rejects_missing_and_changed_raw_records(self):
        config = load_config(Path("configs/study-draft.json"))
        config.update(title="TEST ONLY: handoff zero-edit fixture", seeds=list(range(30)))
        config["common"].update(n=1, rate=0, horizon=1, tau=1)
        config["suites"] = [{"name": "zero_edit_control", "axes": {"policy": ["clean_first"]}}]
        config["approval"] = {"status": "approved", "approved_by": "test fixture",
                              "approved_at": "test only", "parameters_sha256": parameters_digest(config)}
        with tempfile.TemporaryDirectory() as temporary, redirect_stdout(io.StringIO()):
            root = Path(temporary)
            config_path, output = root / "config.json", root / "fixture"
            config_path.write_text(json.dumps(config))
            source = {**source_fingerprint(handoff.ROOT), "git_dirty": False}
            with patch("bartender_sim.__main__.source_fingerprint", return_value=source):
                self.assertEqual(run_study(config, cells(config), output), 0)
            approval = {"status": "approved", "approved_by": "test fixture", "approved_at": "test only",
                        "run_id": "fixture", "parameters_sha256": parameters_digest(config),
                        "protocol_sha256": handoff.protocol_hash()}
            handoff.write(output / "RUN_APPROVAL.json", approval)
            handoff.write(output / "execution.json", {
                "status": "complete", "exit_code": 0, "protocol_sha256": handoff.protocol_hash(),
                "approval_sha256": handoff.file_hash(output / "RUN_APPROVAL.json"), "wall_seconds": 0,
                "started_at": "2000-01-01T00:00:00+00:00", "finished_at": "2000-01-01T00:00:00+00:00",
                "environment": {"python": "3.12.4", "implementation": "CPython", "python_hash_seed": "0"}})
            with patch.object(handoff, "CONFIG", config_path):
                self.assertEqual(handoff.verify_output(output)["status"], "pass")
                raw_path = next((output / "runs").iterdir())
                original = raw_path.read_bytes()
                raw = json.loads(gzip.decompress(original))
                raw["scenario"]["tau"] = 99
                raw_path.write_bytes(gzip.compress(json.dumps(raw).encode()))
                self.assertEqual(handoff.verify_output(output)["status"], "hold")
                raw_path.write_bytes(original)
                lines = (output / "summaries.jsonl").read_text().splitlines()
                (output / "summaries.jsonl").write_text("\n".join(lines[:-1]) + "\n")
                self.assertEqual(handoff.verify_output(output)["status"], "hold")

    def test_archive_parts_reassemble_and_contain_no_local_owner_metadata(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "fixture"
            output.mkdir()
            payload = bytes(range(256)) * 12
            (output / "data.bin").write_bytes(payload)
            inventory = handoff.archive(output, root / "parts", part_bytes=1024)
            combined = b"".join(Path(p["path"]).read_bytes() for p in inventory["parts"])
            self.assertEqual(hashlib.sha256(combined).hexdigest(), inventory["archive_sha256"])
            self.assertTrue(all(p["bytes"] <= 1024 for p in inventory["parts"]))
            with tarfile.open(fileobj=io.BytesIO(combined)) as packed:
                member = packed.getmember("fixture/data.bin")
                self.assertEqual((member.uid, member.gid, member.uname, member.gname, member.mtime),
                                 (0, 0, "", "", 0))
                self.assertEqual(packed.extractfile(member).read(), payload)


if __name__ == "__main__":
    unittest.main()
