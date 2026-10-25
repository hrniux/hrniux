#!/usr/bin/env python3
"""Run explicitly configured public GitHub changes. Only apply performs remote writes."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from studio.operations import Engine, OperationError, validate_paths


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["plan", "apply", "status", "audit"])
    parser.add_argument("--config", default="config/operations.json")
    parser.add_argument("--state", default=".local/state.json")
    parser.add_argument("--json", action="store_true", help="Print public JSON results")
    parser.add_argument("--retry-blocked", action="store_true")
    parser.add_argument("--report", help="Write a sanitized public report (apply or audit)")
    args = parser.parse_args(argv)
    if args.retry_blocked and args.command != "apply":
        parser.error("--retry-blocked requires apply")
    if args.report is not None and args.command not in {"apply", "audit"}:
        parser.error("--report requires apply or audit")
    try:
        validate_paths(args.config, args.state, args.report)
        config = json.loads(Path(args.config).read_text(encoding="utf-8"))
        engine = Engine(config, args.state)
        if args.command == "apply":
            result = engine.apply(args.retry_blocked, args.report)
        elif args.command == "audit":
            result = engine.audit(args.report)
        else:
            result = engine.status()
        rows = result["operations"] if args.command == "audit" else result
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            for row in rows:
                status = row["remote_status"] if args.command == "audit" else row["status"]
                history = f' (local: {row["local_status"]})' if args.command == "audit" else ""
                print(f'{status:11} {row["id"]} {row["kind"]} {row["target"]}: {row["reason"]}{history}')
        if args.command == "audit":
            return 1 if result["counts"]["unavailable"] else 0
        return 1 if args.command == "apply" and any(row["status"] == "failed" for row in rows) else 0
    except OperationError as error:
        print("Execution stopped: " + error.reason, file=sys.stderr)
    except (OSError, ValueError):
        print("Invalid configuration or local state; no further operations attempted", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
