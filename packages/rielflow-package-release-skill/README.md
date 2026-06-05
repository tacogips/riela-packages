# rielflow-package-release-skill

Skill package for Rielflow package registry maintainers.

The useful artifact is:

- `skills/agents/AGENTS.md`
- `skills/codex/rielflow-package-release/SKILL.md`
- `skills/claude/rielflow-package-release/SKILL.md`

The package also includes `scripts/update-package-digests.ts` inside its marker
workflow so installed projects can refresh package checksum and integrity fields
without relying on this repository's local `.agents` checkout.
