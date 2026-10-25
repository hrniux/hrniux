"""Read-only observations must never rewrite historical checkpoints."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from studio.operations import Engine, OperationError, fingerprint
from tests.test_operations import configuration, operation


class ReadOnlyGitHub:
    def __init__(self):
        self.responses = {"user": {"login": "hrniux", "bio": "Builder"}}
        self.calls = []

    def api(self, endpoint, method="GET", payload=None):
        self.calls.append((endpoint, method, payload))
        if method != "GET":
            raise AssertionError("audit attempted a remote write")
        response = self.responses.get(endpoint, OperationError(None, "request_failed"))
        if isinstance(response, Exception):
            raise response
        return copy.deepcopy(response)


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.state = self.root / "state.json"
        self.gh = ReadOnlyGitHub()

    def engine(self, *ops):
        return Engine(configuration(*ops), self.state, self.gh)

    def test_blocked_matching_remote_preserves_checkpoint_bytes_and_history(self):
        op = operation()
        self.state.write_text(json.dumps({"schemaVersion": 1, "operations": {"description": {
            "fingerprint": fingerprint(op), "status": "blocked", "reason": "permission_denied"}}}))
        before = self.state.read_bytes()
        self.gh.responses["repos/hrniux/demo"] = {"private": False, "full_name": "HRNIUX/DEMO",
                                                        "description": "New description", "homepage": "other"}
        engine = self.engine(op)
        report_path = self.root / "report.json"
        report = engine.audit(report=report_path)
        row = report["operations"][0]
        self.assertEqual((row["local_status"], row["remote_status"]), ("blocked", "matches"))
        self.assertEqual(self.state.read_bytes(), before)
        self.assertEqual(engine.status()[0]["status"], "blocked")
        self.assertEqual(json.loads(report_path.read_text()), report)
        self.assertEqual(report["schemaVersion"], 1)
        self.assertRegex(report["checked_at_utc"], r"^\d{4}-\d{2}-\d{2}T.*Z$")
        self.assertEqual(report["config_fingerprint"], fingerprint(configuration(op)))
        self.assertEqual(report["counts"], {"matches": 1, "differs": 0, "missing": 0, "unavailable": 0, "manual": 0})
        self.assertNotIn("other", json.dumps(report))

    def test_topics_order_profile_create_and_manual_observations_cache_reads(self):
        self.gh.responses.update({"repos/hrniux/demo": {"private": False, "full_name": "hrniux/demo", "description": "old"},
                                  "repos/hrniux/demo/topics": {"names": ["spring", "java"]},
                                  "repos/hrniux/github-studio": OperationError(404, "request_failed")})
        report = self.engine(operation(), operation("topics", "repo_topics", desired={"topics": ["java", "spring"]}),
                             operation("topics2", "repo_topics", desired={"topics": ["java"]}),
                             operation("bio", "user_profile", "hrniux", {"bio": "Builder"}),
                             operation("create", "create_repository", "hrniux/github-studio", {"private": False}),
                             operation("pin", "manual_pin", desired={})).audit()
        self.assertEqual([r["remote_status"] for r in report["operations"]],
                         ["differs", "matches", "differs", "matches", "missing", "manual"])
        self.assertEqual([c[0] for c in self.gh.calls].count("repos/hrniux/demo"), 1)
        self.assertEqual([c[0] for c in self.gh.calls].count("repos/hrniux/demo/topics"), 1)
        self.assertEqual([c[0] for c in self.gh.calls].count("user"), 1)
        self.assertFalse(self.state.exists())
        self.engine(operation()).audit()
        self.assertEqual([c[0] for c in self.gh.calls].count("repos/hrniux/demo"), 2)

    def test_star_204_404_403_and_read_failures_are_classified_without_leaking(self):
        for response, expected in [(None, "matches"), (OperationError(404, "raw secret"), "missing"),
                                   (OperationError(403, "raw secret"), "unavailable"),
                                   (OperationError(None, "raw secret"), "unavailable")]:
            with self.subTest(expected=expected, response=response):
                self.gh.responses.update({"repos/public/repo0": {"private": False, "full_name": "public/repo0"},
                                          "user/starred/public/repo0": response})
                result = self.engine(operation("star", "star", "public/repo0", {"starred": True})).audit()
                self.assertEqual(result["operations"][0]["remote_status"], expected)
                self.assertNotIn("raw secret", json.dumps(result))
        for response, expected in [(OperationError(404, "raw secret"), "missing"),
                                   (OperationError(403, "raw secret"), "unavailable"),
                                   (OperationError(None, "request_timeout"), "unavailable")]:
            with self.subTest(expected=expected):
                self.gh.responses["repos/hrniux/demo"] = response
                self.assertEqual(self.engine(operation()).audit()["operations"][0]["remote_status"], expected)

    def test_private_cross_owner_and_malformed_reads_cannot_match(self):
        for response in ({"private": True, "full_name": "private/secret", "description": "New description"},
                         {"private": False, "full_name": "other/demo", "description": "New description"},
                         {"private": False, "description": "New description"}, [], None):
            with self.subTest(response=response):
                self.gh.responses["repos/hrniux/demo"] = response
                result = self.engine(operation()).audit()
                self.assertEqual(result["operations"][0]["remote_status"], "unavailable")
                self.assertNotIn("secret", json.dumps(result))
                self.assertNotIn("other/demo", json.dumps(result))
        self.gh.responses["repos/hrniux/demo"] = {"private": False, "full_name": "hrniux/demo"}
        for value in ({}, {"names": "java"}, {"names": [[]]}, None):
            self.gh.responses["repos/hrniux/demo/topics"] = value
            self.assertEqual(self.engine(operation("t", "repo_topics", desired={"topics": ["java"]})).audit()
                             ["operations"][0]["remote_status"], "unavailable")

    def test_failed_reads_are_cached_and_account_404_never_proves_missing(self):
        self.gh.responses["repos/hrniux/demo"] = OperationError(403, "raw secret")
        report = self.engine(operation(), operation("second")).audit()
        self.assertEqual([row["remote_status"] for row in report["operations"]], ["unavailable", "unavailable"])
        self.assertEqual([call[0] for call in self.gh.calls].count("repos/hrniux/demo"), 1)
        self.gh.responses["user"] = OperationError(404, "raw secret")
        self.assertEqual(self.engine(operation()).audit()["operations"][0]["remote_status"], "unavailable")

    def test_absent_desired_metadata_fields_and_malformed_profile_cannot_match(self):
        op = operation(desired={"description": ""})
        self.gh.responses["repos/hrniux/demo"] = {"private": False, "full_name": "hrniux/demo"}
        self.assertEqual(self.engine(op).audit()["operations"][0]["remote_status"], "unavailable")
        self.gh.responses["repos/hrniux/demo"]["description"] = []
        self.assertEqual(self.engine(op).audit()["operations"][0]["remote_status"], "unavailable")
        self.gh.responses["repos/hrniux/demo"]["description"] = None
        self.assertEqual(self.engine(op).audit()["operations"][0]["remote_status"], "matches")
        for value in ({"login": "hrniux"}, {"login": "hrniux", "bio": []}):
            self.gh.responses["user"] = value
            self.assertEqual(self.engine(operation("bio", "user_profile", "hrniux", {"bio": ""})).audit()
                             ["operations"][0]["remote_status"], "unavailable")

    def test_wrong_account_and_failed_identity_are_unavailable_without_other_reads(self):
        for value in ({"login": "secret-account"}, None, OperationError(403, "raw secret")):
            self.gh.responses["user"] = value
            self.gh.calls.clear()
            result = self.engine(operation(), operation("pin", "manual_pin", desired={})).audit()
            self.assertEqual([r["remote_status"] for r in result["operations"]], ["unavailable", "manual"])
            self.assertEqual(len(self.gh.calls), 1)
            self.assertFalse(self.state.exists())
            self.assertNotIn("secret", json.dumps(result))

    def test_engine_apply_and_audit_reject_report_aliases_before_api_or_mutation(self):
        self.state.write_text('{"schemaVersion":1,"operations":{}}')
        before = self.state.read_bytes()
        link = self.root / "sym.json"
        link.symlink_to(self.state)
        hard = self.root / "hard.json"
        os.link(self.state, hard)
        for report in (self.state, self.root / "x/../state.json", link, hard):
            for method in ("apply", "audit"):
                with self.subTest(report=report, method=method), self.assertRaises(ValueError):
                    getattr(self.engine(operation()), method)(report=report)
                self.assertEqual(self.state.read_bytes(), before)
                self.assertEqual(self.gh.calls, [])

    def test_cli_rejects_all_config_state_report_aliases_and_preserves_files(self):
        config_path = self.root / "config.json"
        config_path.write_text(json.dumps(configuration(operation())))
        self.state.write_text('{"schemaVersion":1,"operations":{}}')
        config_before, state_before = config_path.read_bytes(), self.state.read_bytes()
        marker = self.root / "api-called"
        executable = self.root / "gh"
        executable.write_text("#!" + sys.executable + "\nfrom pathlib import Path\nimport json\n"
                              + "Path(" + repr(str(marker)) + ").touch()\n"
                              + 'print(json.dumps({"login":"hrniux","private":False,"full_name":"hrniux/demo"}))\n')
        executable.chmod(0o755)
        for original in (config_path, self.state):
            sym = self.root / (original.stem + "-sym.json")
            sym.symlink_to(original)
            hard = self.root / (original.stem + "-hard.json")
            os.link(original, hard)
            for report in (original, sym, hard):
                for command in ("audit", "apply"):
                    result = subprocess.run([sys.executable, "scripts/studio.py", command, "--config", str(config_path),
                                             "--state", str(self.state), "--report", str(report)],
                                            capture_output=True, text=True, env={**os.environ, "PATH": str(self.root)}, timeout=5)
                    self.assertEqual(result.returncode, 2, result.stderr)
                    self.assertFalse(marker.exists(), "alias rejection must precede API calls")
                    self.assertNotIn("Traceback", result.stderr)
                    self.assertEqual(config_path.read_bytes(), config_before)
                    self.assertEqual(self.state.read_bytes(), state_before)
        for command in ("plan", "status", "apply", "audit"):
            result = subprocess.run([sys.executable, "scripts/studio.py", command, "--config", str(config_path),
                                     "--state", str(config_path)], capture_output=True, text=True,
                                    env={**os.environ, "PATH": ""}, timeout=5)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            self.assertEqual(config_path.read_bytes(), config_before)

    def test_malformed_state_records_fail_before_calls_and_cli_has_no_traceback(self):
        valid = {"fingerprint": fingerprint(operation()), "status": "blocked", "reason": "permission_denied"}
        malformed = [[], None, 1, {"schemaVersion": True, "operations": {}}, {"schemaVersion": 1, "operations": []}]
        for key, values in {"status": [[], {}, None, "other"], "reason": [[], {}, None],
                            "fingerprint": [[], {}, None, "bad"]}.items():
            for value in values:
                record = dict(valid, **{key: value})
                malformed.append({"schemaVersion": 1, "operations": {"description": record}})
        malformed.extend({"schemaVersion": 1, "operations": {"description": value}}
                         for value in (None, [], {}, {"status": "pending"}))
        config_path = self.root / "config.json"
        config_path.write_text(json.dumps(configuration(operation())))
        for value in malformed:
            with self.subTest(value=value):
                self.state.write_text(json.dumps(value))
                before = self.state.read_bytes()
                with self.assertRaises(ValueError):
                    self.engine(operation())
                self.assertEqual(self.state.read_bytes(), before)
                self.assertEqual(self.gh.calls, [])
                result = subprocess.run([sys.executable, "scripts/studio.py", "status", "--config", str(config_path),
                                         "--state", str(self.state)], capture_output=True, text=True, timeout=5)
                self.assertEqual(result.returncode, 2)
                self.assertNotIn("Traceback", result.stderr)

    def test_cli_audit_unavailable_exit_one_json_report_and_no_state_creation(self):
        config_path = self.root / "config.json"
        config_path.write_text(json.dumps(configuration(operation())))
        report_path = self.root / "report.json"
        result = subprocess.run([sys.executable, "scripts/studio.py", "audit", "--config", str(config_path),
                                 "--state", str(self.state), "--json", "--report", str(report_path)],
                                capture_output=True, text=True, env={**os.environ, "PATH": ""}, timeout=5)
        self.assertEqual(result.returncode, 1, result.stderr)
        result_json = json.loads(result.stdout)
        self.assertEqual(result_json["counts"]["unavailable"], 1)
        self.assertEqual(json.loads(report_path.read_text()), result_json)
        self.assertFalse(self.state.exists())


if __name__ == "__main__":
    unittest.main()
