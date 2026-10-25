"""Behavioral checks: mutations named in test names must break these tests."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

try:
    from studio.operations import Engine, GitHub, OperationError, validate_config
except ImportError:
    Engine = None


def operation(identifier="description", kind="repo_metadata", target="hrniux/demo", desired=None, **extra):
    return {"id": identifier, "kind": kind, "target": target,
            "desired": {"description": "New description"} if desired is None else desired, **extra}


def configuration(*ops):
    return {"schemaVersion": 1, "owner": "hrniux", "operations": list(ops),
            "public_star_allowlist": [f"public/repo{i}" for i in range(20)]}


class PublicGitHub:
    """External boundary fake; engine owns validation, comparison and disk writes."""
    def __init__(self):
        self.login = "hrniux"
        self.writes = []
        self.values = {"description": "Old description", "homepage": None, "private": False,
                       "topics": [], "bio": "old", "full_name": "hrniux/demo"}
        self.error = None
        self.mismatch = False

    def api(self, endpoint, method="GET", payload=None):
        if endpoint == "user" and method == "GET":
            return {"login": self.login, "bio": self.values["bio"]}
        if method in ("PATCH", "PUT", "POST"):
            self.writes.append((endpoint, method, copy.deepcopy(payload)))
            if self.error:
                raise OperationError(self.error, "remote denied")
            if not self.mismatch:
                self.values.update(payload or {})
            return {}
        if endpoint.endswith("/topics"):
            return {"names": self.values.get("names", [])}
        return copy.deepcopy(self.values)


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(Engine, "operations engine has not been implemented")
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.state = Path(self.tmp.name) / "nested/state.json"
        self.gh = PublicGitHub()

    def engine(self, config=None):
        return Engine(config or configuration(operation()), self.state, self.gh)

    def test_plan_and_status_are_offline_and_do_not_create_state(self):
        self.gh.error = 403
        engine = self.engine()
        self.assertEqual(engine.plan()[0]["status"], "pending")
        self.assertEqual(engine.status()[0]["status"], "pending")
        self.assertEqual(self.gh.writes, [])
        self.assertFalse(self.state.exists())
        # The actual command must remain offline even when gh is unavailable.
        config_path = Path(self.tmp.name) / "operations.json"
        config_path.write_text(json.dumps(configuration(operation())))
        result = subprocess.run([sys.executable, "scripts/studio.py", "plan", "--json",
                                 "--config", str(config_path), "--state", str(self.state)],
                                capture_output=True, text=True, env={**os.environ, "PATH": ""}, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)[0]["status"], "pending")
        self.assertFalse(self.state.exists())

    def test_wrong_account_blocks_all_mutations(self):
        self.gh.login = "someone-else"
        with self.assertRaises(OperationError):
            self.engine().apply()
        self.assertEqual(self.gh.writes, [])

    def test_forbidden_persists_and_retries_only_when_explicit(self):
        self.gh.error = 403
        self.assertEqual(self.engine().apply()[0]["status"], "blocked")
        self.assertEqual(json.loads(self.state.read_text())["operations"]["description"]["status"], "blocked")
        self.gh.error = None
        self.engine().apply()
        self.assertEqual(len(self.gh.writes), 1)
        self.assertEqual(self.engine().apply(retry_blocked=True)[0]["status"], "applied")
        self.assertEqual(self.gh.values["description"], "New description")

    def test_applied_skips_but_changed_payload_executes_again(self):
        self.engine().apply()
        self.engine().apply()
        self.assertEqual(len(self.gh.writes), 1)
        config = configuration(operation(desired={"description": "Changed"}))
        self.assertEqual(self.engine(config).status()[0]["status"], "pending")
        self.engine(config).apply()
        self.assertEqual(self.gh.values["description"], "Changed")
        self.assertEqual(len(self.gh.writes), 2)

    def test_readback_mismatch_never_claims_applied(self):
        self.gh.mismatch = True
        result = self.engine().apply()
        self.assertEqual(result[0]["status"], "failed")
        self.assertEqual(self.gh.values["description"], "Old description")

    def test_rejects_unsafe_schema_targets_and_bounds_before_writes(self):
        bad = [operation(kind="shell"), operation(kind=[]), operation(target="other/demo"),
               operation(desired={"description": "ok", "command": "touch /tmp/unsafe"}),
               operation(kind="repo_topics", desired={"topics": ["Upper"]}),
               operation(kind="repo_topics", desired={"topics": ["x"] * 21}),
               operation(kind="user_profile", target="hrniux", desired={"bio": "x" * 161}),
               operation(kind="star", target="unknown/repo", desired={"starred": True}),
               operation(kind="create_repository", target="hrniux/other", desired={"private": False}),
               operation(kind="create_repository", target="hrniux/github-studio", desired={"private": True})]
        for op in bad:
            with self.subTest(op=op), self.assertRaises(ValueError):
                self.engine(configuration(op))
        for ops in [(operation(), operation()), (operation(depends_on=["missing"]),),
                    (operation("a", depends_on=["b"]), operation("b", depends_on=["a"]))]:
            with self.subTest(ops=ops), self.assertRaises(ValueError):
                self.engine(configuration(*ops))
        self.assertEqual(self.gh.writes, [])

    def test_manual_and_failed_dependencies_do_not_prevent_independent_work(self):
        config = configuration(operation("pin", "manual_pin", desired={}),
                               operation("dependent", depends_on=["pin"]),
                               operation("independent"))
        rows = {row["id"]: row for row in self.engine(config).apply()}
        self.assertEqual(rows["pin"]["status"], "manual")
        self.assertEqual(rows["dependent"]["status"], "pending")
        self.assertEqual(rows["independent"]["status"], "applied")
        self.assertEqual(len(self.gh.writes), 1)
        self.assertEqual(list(self.state.parent.glob("*.tmp")), [])

    def test_private_repository_is_rejected_without_leaking_remote_data(self):
        self.gh.values.update(private=True, full_name="private/secret")
        result = self.engine().apply()
        self.assertEqual(result[0]["status"], "failed")
        self.assertEqual(self.gh.writes, [])
        self.assertNotIn("secret", json.dumps(result))

    def test_topics_profile_and_star_use_verified_public_endpoints(self):
        config = configuration(operation("topics", "repo_topics", desired={"topics": ["java", "spring-boot"]}),
                               operation("bio", "user_profile", "hrniux", {"bio": "Builder"}),
                               operation("star", "star", "public/repo0", {"starred": True}))
        rows = self.engine(config).apply()
        self.assertEqual([r["status"] for r in rows], ["applied"] * 3)
        self.assertEqual(self.gh.values["names"], ["java", "spring-boot"])
        self.assertEqual(self.gh.values["bio"], "Builder")
        self.assertIn(("user/starred/public/repo0", "PUT", None), self.gh.writes)

    def test_timeout_is_bounded_and_runner_uses_stdin_and_fixed_host(self):
        seen = []
        def runner(args, **kwargs):
            seen.append((args, kwargs))
            raise subprocess.TimeoutExpired(args, kwargs["timeout"])
        client = GitHub(timeout=0.05, runner=runner)
        with self.assertRaises(OperationError):
            client.api("user", "PATCH", {"bio": "x; $(echo token)"})
        args, kwargs = seen[0]
        self.assertIn("--hostname", args)
        self.assertEqual(args[args.index("--hostname") + 1], "github.com")
        self.assertNotIn("x; $(echo token)", args)
        self.assertEqual(json.loads(kwargs["input"]), {"bio": "x; $(echo token)"})
        self.assertLessEqual(kwargs["timeout"], 30)
        self.assertNotIn("shell", kwargs)

    def test_http_errors_and_failed_independent_operations_are_sanitized(self):
        for code in (401, 403, 500):
            with self.subTest(code=code):
                def runner(args, **kwargs):
                    return subprocess.CompletedProcess(args, 1, "", f"secret token (HTTP {code})")
                with self.assertRaises(OperationError) as caught:
                    GitHub(runner=runner).api("user")
                self.assertEqual(caught.exception.code, code)
                self.assertNotIn("secret", str(caught.exception))
        original_api = self.gh.api
        def selective_failure(endpoint, method="GET", payload=None):
            if endpoint == "repos/hrniux/broken" and method == "PATCH":
                raise OperationError(500, "request_failed")
            return original_api(endpoint, method, payload)
        self.gh.api = selective_failure
        config = configuration(operation("broken", target="hrniux/broken"),
                               operation("dependent", depends_on=["broken"]), operation("independent"))
        self.assertEqual([r["status"] for r in self.engine(config).apply()], ["failed", "pending", "applied"])

    def test_create_public_repository_readback_and_atomic_state_on_failure(self):
        self.gh.values.update(full_name="hrniux/github-studio")
        config = configuration(operation("create", "create_repository", "hrniux/github-studio", {"private": False}))
        self.assertEqual(self.engine(config).apply()[0]["status"], "applied")
        self.assertEqual(self.gh.writes, [])
        self.state.unlink()
        original_api = self.gh.api
        missing = [True]
        def create_when_absent(endpoint, method="GET", payload=None):
            if endpoint == "repos/hrniux/github-studio" and missing[0]:
                missing[0] = False
                raise OperationError(404, "request_failed")
            return original_api(endpoint, method, payload)
        self.gh.api = create_when_absent
        self.assertEqual(self.engine(config).apply()[0]["status"], "applied")
        self.assertEqual(self.gh.writes, [("user/repos", "POST", {"name": "github-studio", "private": False})])
        self.state.write_text("not JSON")
        with self.assertRaises(ValueError):
            self.engine(config).apply()
        self.assertEqual(self.state.read_text(), "not JSON")


if __name__ == "__main__":
    unittest.main()
