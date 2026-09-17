#!/usr/bin/env python3

import importlib.util
import math
from pathlib import Path
import subprocess
import tempfile
import unittest


HERE = Path(__file__).resolve().parent


def load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


extract = load("extract_pr_diff_counts", "extract_pr_diff_counts.py")
summarize = load("summarize_range_positioning", "summarize_range_positioning.py")
calibration = load("calibration", "calibration.py")


class ExtractionTests(unittest.TestCase):
    def test_output_omits_source_paths_and_agent_labels(self):
        row = {
            "stratum": "same",
            "repo": "owner/repo",
            "prA": "1",
            "prB": "2",
            "agentA": "one",
            "agentB": "two",
            "label": "CONFLICT",
            "n_files": "2",
            "files": "private-looking/path|another/path",
            "types": "content|modify/delete",
        }
        output = extract.blank_output(row, "git version test")
        self.assertTrue(output["conflict_has_content"] == "true")
        self.assertTrue(output["conflict_is_content_only"] == "false")
        for omitted in ("agentA", "agentB", "n_files", "files", "types"):
            self.assertNotIn(omitted, output)

    def test_binary_safe_diff_counting(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
            subprocess.run(
                ["git", "config", "user.email", "test@example.invalid"],
                cwd=repo,
                check=True,
            )
            tracked = repo / "invalid-utf8.txt"
            tracked.write_bytes(b"line one\n\x85old\n")
            subprocess.run(["git", "add", "."], cwd=repo, check=True)
            subprocess.run(["git", "commit", "-qm", "base"], cwd=repo, check=True)
            base = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
            tracked.write_bytes(b"line one\n\x85new\n")
            subprocess.run(["git", "add", "."], cwd=repo, check=True)
            subprocess.run(["git", "commit", "-qm", "head"], cwd=repo, check=True)
            head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
            self.assertEqual(extract.git_diff_counts(repo, base, head), (1, 1))


class PositioningTests(unittest.TestCase):
    def test_inversion_round_trip(self):
        q = 0.198
        n = 16
        p_eff = summarize.invert(q, n)
        self.assertAlmostEqual(1 - (1 - p_eff) ** n, q)
        self.assertAlmostEqual(calibration.invert(q, 4, 4), p_eff)

    def test_dimensionless_intensity_round_trip(self):
        q = 119 / 601
        theta = summarize.overlap_intensity(q)
        self.assertAlmostEqual(1 - math.exp(-theta), q)
        self.assertEqual(summarize.point_position(theta, theta - 0.01, theta + 0.01), "inside interval")
        expected = summarize.bernoulli_expected_overlaps(q, 102)
        self.assertAlmostEqual(expected, 102 * summarize.invert(q, 102))
        self.assertLess(abs(expected - theta), 0.001)

    def test_wilson_and_type7_quantiles(self):
        low, high = summarize.wilson(119, 601)
        self.assertTrue(0.168 < low < 0.169)
        self.assertTrue(0.231 < high < 0.232)
        self.assertEqual(summarize.percentile([1, 2, 3, 4], 0.25), 1.75)
        self.assertEqual(summarize.percentile([1, 2, 3, 4], 0.50), 2.5)
        self.assertEqual(summarize.percentile([1, 2, 3, 4], 0.75), 3.25)

    def test_scan_interval_labels(self):
        self.assertEqual(
            summarize.interval_position(0.004, 0.02, 0.003, 0.07),
            "inside scan",
        )
        self.assertEqual(
            summarize.interval_position(0.001, 0.01, 0.003, 0.07),
            "partly overlaps scan",
        )

    def test_source_rate_is_not_changed_by_current_retrieval_failure(self):
        rows = [
            {
                "stratum": "same",
                "label": "CONFLICT",
                "conflict_has_content": "true",
                "conflict_is_content_only": "true",
                "status": "API_NOT_FOUND_A",
            },
            {
                "stratum": "same",
                "label": "CLEAN",
                "conflict_has_content": "false",
                "conflict_is_content_only": "false",
                "status": "OK",
            },
            {
                "stratum": "same",
                "label": "UNAVAIL_fetch",
                "conflict_has_content": "false",
                "conflict_is_content_only": "false",
                "status": "UNAVAIL_fetch",
            },
        ]
        rates = summarize.rate_definitions(rows, "same")
        self.assertEqual(rates[0], ("structural-inclusive textual conflict", 1, 2))
        self.assertEqual(rates[1], ("conflict with any content component", 1, 2))
        self.assertEqual(rates[2], ("content-only conflict", 1, 2))

    def test_mapping_checks_labels_and_derived_content_flags(self):
        source = [
            {
                "stratum": "same",
                "repo": "owner/repo",
                "prA": "1",
                "prB": "2",
                "label": "CONFLICT",
                "types": "content|modify/delete",
            }
        ]
        counts = [
            {
                "stratum": "same",
                "repo": "owner/repo",
                "prA": "1",
                "prB": "2",
                "label": "CONFLICT",
                "conflict_has_content": "true",
                "conflict_is_content_only": "false",
            }
        ]
        self.assertTrue(summarize.validate_mapping(source, counts)["fields_match"])
        counts[0]["conflict_is_content_only"] = "true"
        result = summarize.validate_mapping(source, counts)
        self.assertFalse(result["fields_match"])
        self.assertEqual(result["field_mismatches"][0]["field"], "conflict_is_content_only")


if __name__ == "__main__":
    unittest.main()
