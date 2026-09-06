# Expected results

Run workflow validate/inspect, then workflow run fable-and-improve-opus with its bundled mock-scenario.json, isolated --session-store and --artifact-root. Use the paired Riela source build. Mock calls do not invoke models, commit or push.

Expect completed and exitCode 0. fable-design precedes plan-checkpoint and plan-git-commit. dispatch-plans starts native implementation/review branches; branch-evidence ends each branch before the parent reconcile-implementations and integration-review. Revisions return to their owning worker; dependency waves repeat only after integration acceptance. Final Git steps and base-branch-integrate precede knowledge self-review and final-output. Existing Claude models remain unchanged.
