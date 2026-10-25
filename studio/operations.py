"""Explicit public GitHub operations, durable checkpoints, and safe reporting."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile


class OperationError(Exception):
    def __init__(self, code, reason):
        self.code = code
        self.reason = reason
        super().__init__(reason)


def fingerprint(operation):
    return hashlib.sha256(json.dumps(operation, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False).encode()).hexdigest()


def validate_config(config):
    def require(condition):
        if not condition:
            raise ValueError("Invalid operations configuration")

    require(isinstance(config, dict))
    require(set(config) <= {"schemaVersion", "owner", "operations", "public_star_allowlist"})
    require(type(config.get("schemaVersion")) is int and config["schemaVersion"] == 1)
    require(config.get("owner") == "hrniux")
    ops = config.get("operations")
    require(isinstance(ops, list))
    repo_pattern = r"[A-Za-z0-9][A-Za-z0-9_.-]{0,99}/[A-Za-z0-9_.-]{1,100}"
    allowlist = config.get("public_star_allowlist", [])
    require(isinstance(allowlist, list) and len(allowlist) <= 20)
    require(all(isinstance(x, str) and re.fullmatch(repo_pattern, x) for x in allowlist))
    require(len(allowlist) == len(set(allowlist)))
    identifiers = set()
    for op in ops:
        require(isinstance(op, dict))
        require(set(op) <= {"id", "kind", "target", "desired", "depends_on"})
        require({"id", "kind", "target", "desired"} <= set(op))
        identifier, kind, target, desired = (op[k] for k in ("id", "kind", "target", "desired"))
        require(isinstance(identifier, str) and re.fullmatch(r"[A-Za-z0-9_-]{1,100}", identifier))
        require(identifier not in identifiers)
        identifiers.add(identifier)
        require(isinstance(kind, str) and kind in {"repo_metadata", "repo_topics", "user_profile", "star", "create_repository", "manual_pin"})
        require(isinstance(target, str) and isinstance(desired, dict))
        if kind == "user_profile":
            require(target == "hrniux")
        else:
            require(re.fullmatch(repo_pattern, target) and target.split("/")[1] not in {".", ".."})
            require(target.startswith("hrniux/") or kind == "star")
        if kind == "repo_metadata":
            require(bool(desired) and set(desired) <= {"description", "homepage"})
            require(all(isinstance(v, str) for v in desired.values()))
            require(len(desired.get("description", "")) <= 350)
            homepage = desired.get("homepage", "")
            require(len(homepage) <= 2048 and (not homepage or homepage.startswith(("https://", "http://"))))
        elif kind == "repo_topics":
            require(set(desired) == {"topics"} and isinstance(desired["topics"], list))
            topics = desired["topics"]
            require(len(topics) <= 20)
            require(all(isinstance(x, str) and re.fullmatch(r"[a-z0-9-]{1,50}", x) for x in topics))
            require(len(topics) == len(set(topics)))
        elif kind == "user_profile":
            require(set(desired) == {"bio"} and isinstance(desired["bio"], str) and len(desired["bio"]) <= 160)
        elif kind == "star":
            require(len(allowlist) == 20 and target in allowlist)
            require(set(desired) == {"starred"} and desired["starred"] is True)
        elif kind == "create_repository":
            require(target == "hrniux/github-studio" and set(desired) == {"private"} and desired["private"] is False)
        elif kind == "manual_pin":
            require(set(desired) <= {"position"})
            require("position" not in desired or (type(desired["position"]) is int and 1 <= desired["position"] <= 6))
        dependencies = op.get("depends_on", [])
        require(isinstance(dependencies, list) and all(isinstance(x, str) for x in dependencies))
        require(len(dependencies) == len(set(dependencies)))
    by_id = {op["id"]: op for op in ops}
    visited, active = set(), set()

    def visit(identifier):
        require(identifier in by_id and identifier not in active)
        if identifier in visited:
            return
        active.add(identifier)
        for dependency in by_id[identifier].get("depends_on", []):
            visit(dependency)
        active.remove(identifier)
        visited.add(identifier)

    for identifier in by_id:
        visit(identifier)
    return config


class GitHub:
    def __init__(self, timeout=30, runner=subprocess.run):
        if not 0 < timeout <= 30:
            raise ValueError("Timeout must be within 30 seconds")
        self.timeout, self.runner = timeout, runner

    def api(self, endpoint, method="GET", payload=None):
        args = ["gh", "api", "--hostname", "github.com", "--method", method, endpoint]
        if payload is not None:
            args.extend(["--input", "-"])
        try:
            result = self.runner(args, input=json.dumps(payload) if payload is not None else None,
                                 text=True, capture_output=True, timeout=self.timeout)
        except subprocess.TimeoutExpired:
            raise OperationError(None, "request_timeout") from None
        except OSError:
            raise OperationError(None, "client_unavailable") from None
        if result.returncode:
            match = re.search(r"HTTP\s+(\d{3})", result.stderr or "")
            code = int(match.group(1)) if match else None
            raise OperationError(code, "permission_denied" if code in (401, 403) else "request_failed")
        try:
            return json.loads(result.stdout) if result.stdout.strip() else None
        except (json.JSONDecodeError, AttributeError):
            raise OperationError(None, "invalid_response") from None


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix="." + path.name, suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Engine:
    def __init__(self, config, state_path=".local/state.json", github=None):
        self.config = validate_config(config)
        self.state_path = Path(state_path)
        self.github = github or GitHub()
        self.state = {"schemaVersion": 1, "operations": {}}
        if self.state_path.exists():
            try:
                self.state = json.loads(self.state_path.read_text(encoding="utf-8"))
                if (self.state.get("schemaVersion") != 1 or not isinstance(self.state.get("operations"), dict)
                        or not all(isinstance(record, dict) for record in self.state["operations"].values())):
                    raise ValueError()
            except (ValueError, AttributeError, OSError):
                raise ValueError("Invalid local state; preserve it for recovery") from None

    def status(self):
        rows = []
        for op in self.config["operations"]:
            record = self.state["operations"].get(op["id"], {})
            status = "manual" if op["kind"] == "manual_pin" else "pending"
            reason = "manual_action_required" if status == "manual" else "not_applied"
            if record.get("fingerprint") == fingerprint(op):
                status = record.get("status", status)
                # Never copy arbitrary local diagnostics into public output.
                reason = record.get("reason", reason)
                if status not in {"pending", "manual", "applied", "blocked", "failed"}:
                    status, reason = "pending", "not_applied"
                if reason not in SAFE_REASONS:
                    reason = "request_failed"
            rows.append({"id": op["id"], "kind": op["kind"], "target": op["target"],
                         "status": status, "reason": reason})
        return rows

    def plan(self):
        return self.status()

    def _checkpoint(self, op, status, reason):
        self.state["operations"][op["id"]] = {"fingerprint": fingerprint(op), "status": status, "reason": reason}
        atomic_json(self.state_path, self.state)

    def _public_repository(self, target):
        repo = self.github.api("repos/" + target)
        if not isinstance(repo, dict) or repo.get("private") is not False:
            raise OperationError(None, "public_repository_required")
        return repo

    def _execute(self, op):
        kind, target, desired = (op[k] for k in ("kind", "target", "desired"))
        if kind == "create_repository":
            try:
                repo = self._public_repository(target)
            except OperationError as error:
                if error.code != 404:
                    raise
                self.github.api("user/repos", "POST", {"name": "github-studio", "private": False})
                repo = self._public_repository(target)
            return repo.get("full_name", "").lower() == target.lower()
        if kind == "user_profile":
            self.github.api("user", "PATCH", desired)
            observed = self.github.api("user")
            return isinstance(observed, dict) and observed.get("bio") == desired["bio"]
        self._public_repository(target)
        if kind == "star":
            endpoint = "user/starred/" + target
            self.github.api(endpoint, "PUT")
            self.github.api(endpoint)
            return True
        endpoint = "repos/" + target
        if kind == "repo_topics":
            endpoint += "/topics"
            self.github.api(endpoint, "PUT", {"names": desired["topics"]})
            observed = self.github.api(endpoint)
            return isinstance(observed, dict) and sorted(observed.get("names", [])) == sorted(desired["topics"])
        self.github.api(endpoint, "PATCH", desired)
        observed = self.github.api(endpoint)
        return isinstance(observed, dict) and all((observed.get(key) or "") == value for key, value in desired.items())

    def apply(self, retry_blocked=False, report=None):
        account = self.github.api("user")
        if not isinstance(account, dict) or account.get("login") != "hrniux":
            raise OperationError(None, "account_mismatch")
        statuses = {row["id"]: row["status"] for row in self.status()}
        remaining = list(self.config["operations"])
        while remaining:
            progressed = False
            for op in list(remaining):
                identifier = op["id"]
                current = statuses[identifier]
                if op["kind"] == "manual_pin":
                    self._checkpoint(op, "manual", "manual_action_required")
                elif current == "applied" or (current == "blocked" and not retry_blocked):
                    pass
                elif any(statuses[dependency] != "applied" for dependency in op.get("depends_on", [])):
                    continue
                else:
                    try:
                        if not self._execute(op):
                            raise OperationError(None, "verification_mismatch")
                        self._checkpoint(op, "applied", "verified")
                        statuses[identifier] = "applied"
                    except OperationError as error:
                        status = "blocked" if error.code in (401, 403) else "failed"
                        reason = "permission_denied" if status == "blocked" else error.reason
                        self._checkpoint(op, status, reason if reason in SAFE_REASONS else "request_failed")
                        statuses[identifier] = status
                    except (TypeError, ValueError, KeyError):
                        self._checkpoint(op, "failed", "invalid_response")
                        statuses[identifier] = "failed"
                remaining.remove(op)
                progressed = True
            if not progressed:
                for op in remaining:
                    self._checkpoint(op, "pending", "dependency_incomplete")
                break
        rows = self.status()
        if report:
            atomic_json(report, rows)
        return rows


SAFE_REASONS = {"not_applied", "manual_action_required", "permission_denied", "request_failed",
                "request_timeout", "client_unavailable", "invalid_response", "public_repository_required",
                "verification_mismatch", "verified", "dependency_incomplete"}
