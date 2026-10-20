---
name: financial-research-agent-build-safety
description: Review Ledger architecture, dependencies, provider contracts, data handling, cost controls, telemetry, and release readiness.
---

# Ledger build safety

Load only the relevant preserved workflow from `agent-builder/`. Apply these project rules first:

- SEC and market adapters keep provider attribution, timeouts, periods, units, and retrieval times.
- Calculations stay deterministic and testable outside the language layer.
- Missing data remains missing; no fallback may look like a retrieved fact.
- Secrets stay in environment/runtime secret storage and out of logs, reports, and Git.
- Deployment, paid models, external writes, and trading remain owner gates.

Read the sibling AI-ops skill for model, retrieval, state, evaluation, and observability changes.
Read the financial-review skill for ratios, peer comparisons, conclusions, and report claims.
Finish with `npm run check` and the relevant live failure-path evidence.
