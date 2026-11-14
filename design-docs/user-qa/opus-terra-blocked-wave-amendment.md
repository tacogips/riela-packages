# User QA: Opus Terra blocked-wave amendment

Design: `design-docs/specs/design-opus-terra-blocked-wave-amendment.md`.

## Q1. Amendment bound (decided by default; confirm if desired)

Decision: keep `MAX_CHECKPOINT_AMENDMENTS = 2`, shared between dispatch
amendments and blocked-wave amendments, so a run gets 2 in total. Monja
needed 6 manual restarts, but each restart fixed one gap. A blocked-wave
amendment asks Opus to resolve every blocker in the wave at once.

Alternative: raise the bound to 3. That means changing the single constant in
`scripts/dispatch-wave.py`, plus `test_dispatch_amendment.py` (which expects
the exhausted round to be 2), README and EXPECTED_RESULTS.md. Not chosen: the
intake did not require it, and the existing tests pin 2.

## Q2. Mock scenario sequencing (resolved; no fallback)

The required scenario is blocked wave → amendment → redispatch → success.
It uses per-node response arrays, which the scenario adapter already
supports. Responses are consumed in visit order, and the last entry repeats
(`.agents/skills/riela-package-release/scripts/check-package-compat.ts:241-255`).
Existing fixtures already use array entries, for example
`packages/codex-deepdesign/workflows/codex-deepdesign/mock-scenario.json:32`.
The design D7 lists the array entries, the exact run command and the
required route assertions.

The earlier fallback is withdrawn. It ended the scenario at
`dispatch-plans: amendment_blocked`, which was invalid: a fixed response
would also end the initial dispatch.

If the installed riela rejects the scenario when it runs, the implementer
reports the capability gap as a blocker and asks for an acceptance amendment.
A blocked-terminal scenario or unit tests are never an acceptable substitute
for the success scenario.
