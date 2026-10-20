---
name: next-phase
description: Start or resume a bounded Ledger Financial Research Agent OpenSpec phase, implement authorized tasks, verify evidence, and stop at a clean checkpoint.
---

# Ledger next phase

Read `PROJECT.md`, `WORKFLOW.md`, `HANDOFF.md`, `AI_OPS.md`, and the active OpenSpec change.
Recover unfinished work before proposing anything new. Select the next planned phase, resolve only
material owner calls, and keep non-goals explicit.

Use the sibling build-safety skill for architecture, provider, data, cost, and release boundaries.
Use the financial-review skill whenever calculations, comparison policy, or investment conclusions
change. Use the AI-ops skill for retrieval, orchestration, prompts/models, memory, evaluation,
monitoring, and release recovery.

Implement only authorized tasks. Run `npm run check`, one live smoke test for data changes, and
`openspec validate --all --strict`. Update `HANDOFF.md` with actual evidence. Deployment, paid
providers, external writes, and merges remain owner gates.
