from contextlib import redirect_stdout, redirect_stderr
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest

from bartender_sim.__main__ import main, run_study
from bartender_sim.plan import cells, load_config, parameters_digest, require_approval


CONFIG = Path(__file__).resolve().parents[1] / "configs" / "study-draft.json"


class PlanTests(unittest.TestCase):
    def test_proposed_config_validates_but_cannot_run(self):
        config = load_config(CONFIG)
        # This control must still work after the actual study is approved.
        config["approval"] = {"status": "proposed"}
        cells(config)
        with tempfile.TemporaryDirectory() as folder:
            proposed = Path(folder) / "proposed.json"
            proposed.write_text(json.dumps(config))
            output = Path(folder) / "must-not-exist"
            with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as exit:
                main(["run", "--config", str(proposed), "--output", str(output)])
            self.assertEqual(exit.exception.code, 2)
            self.assertFalse(output.exists())

    def test_parameter_change_invalidates_approval(self):
        config = load_config(CONFIG)
        config["approval"] = {"status": "approved", "approved_by": "test fixture",
                              "approved_at": "test only", "parameters_sha256": parameters_digest(config)}
        require_approval(config)
        config["common"]["tau"] *= 2
        with self.assertRaises(ValueError):
            require_approval(config)

    def test_zero_edit_pipeline_control_preserves_every_seed(self):
        # I/O control only: no random edits or study parameter scan is run.
        config = copy.deepcopy(load_config(CONFIG))
        config["title"] = "TEST ONLY: zero-edit output pipeline"
        config["seeds"] = list(range(30))
        config["common"].update(n=1, rate=0, horizon=1, tau=1)
        config["suites"] = [{"name": "zero_edit_control", "axes": {"policy": ["clean_first"]}}]
        config["approval"] = {"status": "approved", "approved_by": "test fixture",
                              "approved_at": "test only", "parameters_sha256": parameters_digest(config)}
        with tempfile.TemporaryDirectory() as folder, redirect_stdout(io.StringIO()):
            output = Path(folder) / "control"
            self.assertEqual(run_study(config, cells(config), output), 0)
            manifest = json.loads((output / "manifest.json").read_text())
            self.assertEqual(manifest["status"], "complete")
            self.assertEqual(manifest["completed_runs"], 30)
            self.assertEqual(len(list((output / "runs").iterdir())), 30)
            records = [json.loads(line) for line in (output / "summaries.jsonl").read_text().splitlines()]
            self.assertTrue(all(r["metrics"]["generated_edits"] == 0 for r in records))
            with self.assertRaises(FileExistsError):
                run_study(config, cells(config), output)


if __name__ == "__main__":
    unittest.main()
