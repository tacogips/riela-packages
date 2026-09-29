# Expected results

Run workflow validate/inspect, then run the repository compact-workflow
regression with the paired Riela source build. The full entry path requires a
resolved kaiba client for its memory add-ons; the deterministic regression
starts at `fable-design` to isolate the authored graph and uses the bundled
`mock-scenario.json`. Mock calls do not invoke models, commit or push.

Expect completed and exitCode 0. `fable-design` precedes independent design and
plan review gates, then plan checkpoint and commit. `dispatch-plans` starts
native branches that pass implementation progress, test-integrity and
adversarial gates before branch evidence. The parent wave-outcome gate
terminates blocked-only runs or continues successful evidence through
reconciliation and Fable integration review. Revisions return to the correct
author/worker; dependency waves repeat only after acceptance. Fable goal review
precedes E2E evidence, docs, completion and final Git steps.
