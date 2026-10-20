# Workflow

Phase work uses one OpenSpec change and one branch per phase. Read `PROJECT.md`, `HANDOFF.md`,
`AI_OPS.md`, and the active change before implementation.

1. Recover the current checkpoint from `HANDOFF.md` and Git status.
2. Confirm which planned phase is being implemented and keep its non-goals explicit.
3. Create or update the OpenSpec proposal, design, specs, and tasks.
4. Run the constitution/gate check before implementation.
5. Implement small coherent tasks, preserving live-data and evidence contracts.
6. Run `npm run check` and `openspec validate --all --strict`.
7. For financial changes, run the financial-review skill and one live smoke test.
8. For UI changes, inspect desktop and 390px mobile states and update the private design source when the visual contract changes.
9. Update `HANDOFF.md` with actual behavior, evidence, and the next action.

No Git remote is configured. Do not push or open PRs. If a remote is added later, phase branches
use draft PRs, code review, required checks, and the owner's explicit merge approval.

The following always require the owner's decision: deployment, paid provider/model use, persistent
credentials, external messages or writes, production data retention, and any trade-like action.
