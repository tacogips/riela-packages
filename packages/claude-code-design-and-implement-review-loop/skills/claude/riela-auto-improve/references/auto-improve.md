# Auto-Improve Migration (Riela 0.2.0)

The old engine-owned supervision loop and its CLI flags were removed. Existing
run scripts must drop the flags, and operators must handle retries explicitly.

| Previous behavior | Current action |
| --- | --- |
| Start with `--auto-improve` | Start with `workflow run --output jsonl` and retain the session id. |
| Automatic stall/failure recovery | Inspect `session progress` and `session status --output json`; diagnose the failing step. |
| Targeted retry | Use `session rerun <session-id> <step-id>` only after checking side effects. |
| Continue an interrupted run | Use `session resume <session-id>` when the saved state allows it. |
| Paired nested supervisor | No equivalent in Riela 0.2.0. |

`--supervisor-mode` is a Codex execution setting, not the old auto-improve
monitor or repair loop. Never substitute it silently for removed supervision.
