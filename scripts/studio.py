#!/usr/bin/env python3
"""Run explicitly configured public GitHub changes. Only apply performs writes."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from studio.operations import Engine, OperationError


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["plan", "apply", "status"])
    parser.add_argument("--config", default="config/operations.json")
    parser.add_argument("--state", default=".local/state.json")
    parser.add_argument("--json", action="store_true", help="Print public JSON results")
    parser.add_argument("--retry-blocked", action="store_true")
    parser.add_argument("--report", help="Write a sanitized public report (apply only)")
    args = parser.parse_args(argv)
    if args.command != "apply" and (args.report or args.retry_blocked):
        parser.error("--report and --retry-blocked require apply")
    try:
        config = json.loads(Path(args.config).read_text(encoding="utf-8"))
        engine = Engine(config, args.state)
        rows = engine.apply(args.retry_blocked, args.report) if args.command == "apply" else engine.status()
        if args.json:
            print(json.dumps(rows, ensure_ascii=False, indent=2))
        else:
            for row in rows:
                print(f'{row["status"]:8} {row["id"]} {row["kind"]} {row["target"]}: {row["reason"]}')
        return 1 if args.command == "apply" and any(row["status"] == "failed" for row in rows) else 0
    except OperationError as error:
        print("Execution stopped: " + error.reason, file=sys.stderr)
    except (OSError, ValueError):
        print("Invalid configuration or local state; no further operations attempted", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
