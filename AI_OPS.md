# Ledger Financial Research Agent AI operations

Use this file with the
[AI-ops skill](.agents/skills/financial-research-agent-ai-ops/SKILL.md) whenever retrieval,
orchestration, model behavior, evaluation, state, monitoring, or release controls change.

| Capability | Status | Evidence / recheck trigger |
|---|---|---|
| SEC retrieval | Enabled | `backend/app/providers.py`; recheck on SEC contract changes |
| Market-price retrieval | Enabled | Yahoo chart adapter; recheck on endpoint/auth changes |
| Python calculations | Enabled | `analysis.py` and unit tests |
| LangGraph orchestration | Enabled | `workflow.py` |
| LLM synthesis | Optional | BYO OpenAI-compatible key; `llm.py`; deterministic fallback remains available |
| Report conversation | Enabled | Four-node LangGraph; immutable report ontology; evidence-ID verifier; max one model call per question |
| RAG over filings/transcripts | Deferred | Phase 2 design and evaluation required |
| Durable memory | Deferred | PostgreSQL schema and retention policy not chosen |
| LangSmith monitoring | Optional | Disabled by default; owner supplies key/project and enables tracing. Root runs are named `company-research` and `report-chat` with ticker and report metadata. |
| Messages or trades | Disabled | Outside constitution and current scope |

## Evaluation lanes

- Offline deterministic gate: `npm run check`.
- Live smoke test: run NVDA and confirm fiscal period, citation URLs, price date, ratios, and peer rows.
- Groundedness: each claim with a figure must map to a returned calculation or source record.
- Failure behavior: provider errors must produce an unavailable/error state without cached replacement data.
- Business outcome testing is deferred until a controlled user study has an approved decision-quality rubric.

## Runtime limits

- Provider timeout: 25 seconds per HTTP request.
- Peer fan-out: two SEC-validated peers; model suggestions fall back to an SEC-industry cohort.
- Automatic retries: none in Phase 1; surface failures explicitly.
- Model calls: at most two per research run plus one per chat question, each with a 45-second timeout.
- Chat budgets: 600-character question, eight recent messages, 24 questions per report, ten evidence IDs,
  1,800-character answer, and a 30-minute report-session lifetime.
- Model spend belongs to the owner-supplied provider account; tests never make paid calls.
- Secrets: environment only, never committed.
- Access triangle: a session may hold at most two of untrusted input, sensitive data, and external egress.
- Current model session has bounded public input plus egress and no sensitive-data access or write tools.
- Chat content is report-scoped, rejects links and common secret patterns, and is never stored durably.
