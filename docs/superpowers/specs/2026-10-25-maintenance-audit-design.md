# GitHub Studio maintenance audit design

User's existing instruction delegates all choices, publishes permitted reversible changes, queues denied operations, and forbids further questions. Scope this iteration to concrete reliability defects and clearer verification entrances.

## Requirements
1. Add a read-only audit CLI alongside plan/status/apply. It queries current remote public values and reports matches/differs/missing/unavailable/manual, with UTC timestamp, config fingerprint and each row's historical local_status. It never writes remote APIs or changes the state/checkpoint. It may atomically save an explicit report path.
2. Metadata and topics compare only desired fields (topics order-insensitive); profile bio uses the guarded hrniux account; Star GET204 is matches, GET404 is missing, GET403 is unavailable. Create target GET404 is missing. Other metadata GET404 is missing, not inaccessible proof. Missing/private/canonical mismatch data cannot produce matches. Pins remain manual. Cache repeated GETs within one audit, not across runs. Reports contain configured public target/id/kind and bounded reason categories, no raw account data, API bodies or stderr. A permission-denied observation is not a successful write and must not change blocked into applied.
3. Malformed checkpoint status/reason types and invalid records cause a controlled error before any API call, preserve original file bytes and emit no traceback/diagnostic content.
4. Configuration, checkpoint, and explicit report paths must not alias (resolved paths, symlinks, hardlinks) before any remote calls or file mutation. Guard CLI config/state/report and Engine apply/audit state/report. Return controlled exit2. No state/report overwrite on rejection.
5. Existing 45-op config and current38blocked/6manual/1pending checkpoint remain unchanged. Default retry-blocked semantics unchanged. No known-denied writes are retried this iteration.
6. Add clear expected outcomes to profile; direct Spring links to Task API/tests. Add short first-run section and core-source links to underwriting README; synchronize seven Maven commands in three existing docs. Do not change business code or merge DraftPR#2, still mark it accurately.
7. Preserve public-only scope; no new schedules, no fabricated results or platform claims. Python standard library only, Mac/Linux compatibility.

## Interfaces
python3 scripts/studio.py audit --config config/operations.json --state reports/resume-state.json --json --report reports/remote-audit.json
Audit report envelope schemaVersion=1, checked_at_utc, config_fingerprint, counts and operations array.
Each operation row id/kind/target/local_status/remote_status/reason; actual values limited to desired metadata fields only if needed, safest omit values.
Read-only audit may emit unavailable rows with exit1 for errors; matches/differs/missing/manual are observations, not command failures. Existing apply/plan/status behavior remains.
Report overwrite guard runs regardless of command/API readiness.

## Verification
TDD for audit observations and zero mutations/state preservation; stale blocked+remote matches remains blocked. Test missing/403/wrongaccount/private/canonical mismatch and cached duplicate reads. TDD malformed state containers and CLI controlled errors; normal/symlink/hardlink path aliases and byte preservation before API call. Full existing/new unittest suite; real read-only audit and report/checkpoint hash comparison; document edited source links/commands and actual expected scenarios. Fresh reviewer before publishing, then remote content hashes verified.
