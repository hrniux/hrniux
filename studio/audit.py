"""Public remote observations, independent of local write history."""
from datetime import datetime, timezone

from studio.operations import OperationError, atomic_json, fingerprint


STATUSES = ("matches", "differs", "missing", "unavailable", "manual")
READ_REASONS = {"request_failed", "permission_denied", "request_timeout", "client_unavailable", "invalid_response"}


def audit(engine, report=None):
    # Cache successful responses and errors only within this invocation.
    cache = {}

    def read(endpoint):
        if endpoint not in cache:
            try:
                cache[endpoint] = engine.github.api(endpoint)
            except OperationError as error:
                cache[endpoint] = error
        value = cache[endpoint]
        if isinstance(value, OperationError):
            raise value
        return value

    def unavailable(reason="invalid_response"):
        raise OperationError(None, reason)

    def public_repository(target):
        repo = read("repos/" + target)
        if not isinstance(repo, dict):
            unavailable()
        if repo.get("private") is not False:
            unavailable("public_repository_required")
        name = repo.get("full_name")
        if not isinstance(name, str) or name.lower() != target.lower():
            unavailable("repository_identity_mismatch")
        return repo

    account_error = None
    try:
        account = read("user")
        if not isinstance(account, dict) or account.get("login") != "hrniux":
            unavailable("account_mismatch")
    except OperationError as error:
        account_error = error

    def observe(op):
        kind, target, desired = (op[key] for key in ("kind", "target", "desired"))
        if kind == "manual_pin":
            return "manual", "manual_action_required"
        if account_error is not None:
            raise account_error
        if kind == "user_profile":
            observed = read("user")
            if "bio" not in observed or (observed["bio"] is not None and not isinstance(observed["bio"], str)):
                unavailable()
            matches = (observed["bio"] or "") == desired["bio"]
        else:
            observed = public_repository(target)
            if kind == "create_repository":
                matches = True
            elif kind == "star":
                if read("user/starred/" + target) is not None:
                    unavailable()
                matches = True
            elif kind == "repo_topics":
                observed = read("repos/" + target + "/topics")
                if not (isinstance(observed, dict) and isinstance(observed.get("names"), list)
                        and all(isinstance(name, str) for name in observed["names"])):
                    unavailable()
                matches = set(observed["names"]) == set(desired["topics"])
            else:
                if any(key not in observed or (observed[key] is not None and not isinstance(observed[key], str))
                       for key in desired):
                    unavailable()
                matches = all((observed[key] or "") == value for key, value in desired.items())
        return ("matches", "observed_match") if matches else ("differs", "observed_difference")

    rows = []
    for op, local in zip(engine.config["operations"], engine.status()):
        try:
            remote_status, reason = observe(op)
        except OperationError as error:
            # An account read failure can never prove a repository is missing.
            remote_status = "missing" if error.code == 404 and error is not account_error else "unavailable"
            if remote_status == "missing":
                reason = "not_found"
            elif error.code in (401, 403):
                reason = "permission_denied"
            elif error.reason in READ_REASONS | {"account_mismatch", "public_repository_required", "repository_identity_mismatch"}:
                reason = error.reason
            else:
                reason = "request_failed"
        rows.append({"id": op["id"], "kind": op["kind"], "target": op["target"],
                     "local_status": local["status"], "remote_status": remote_status, "reason": reason})
    result = {"schemaVersion": 1, "checked_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
              "config_fingerprint": fingerprint(engine.config),
              "counts": {status: sum(row["remote_status"] == status for row in rows) for status in STATUSES},
              "operations": rows}
    if report is not None:
        atomic_json(report, result)
    return result
