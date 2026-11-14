# riela-package-release-skill

Skill package for Riela package registry maintainers.

The useful artifact is:

- `skills/agents/AGENTS.md`
- `skills/codex/riela-package-release/SKILL.md`
- `skills/claude/riela-package-release/SKILL.md`

The package also includes `scripts/update-package-digests.ts` inside its marker
workflow so installed projects can refresh package checksum and integrity fields
without relying on this repository's local `.agents` checkout.
