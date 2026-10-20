# Ledger Financial Research Agent

Owner: Peter. Created: 2026-10-19.

## 1. Purpose

Build an evidence-first research agent that retrieves public-company filings and live market data,
calculates financial and valuation metrics, compares peers, and returns a cited investment memo.
It is a research aid, not a trading system or personal investment adviser.

## 2. Scope

Phase 1 delivers a working research MVP for SEC-reporting U.S. companies. It includes live SEC and
market retrieval, deterministic calculations, model-assisted and SEC-validated peer selection,
optional grounded prose through an owner-supplied OpenAI-compatible key, report export, loading and
error states, and optional LangSmith tracing. PostgreSQL memory, AWS, authentication, portfolios, and
trading are deferred.

## 3. Evidence of completion

- `npm run check` passes.
- A live NVDA run completes without fixtures and cites the latest available SEC filing.
- Revenue, margins, FCF, P/E, P/S, and FCF yield are computed from retrieved values.
- Desktop and 390px mobile layouts are visually inspected.
- Editable desktop and mobile designs exist in the linked private design source file.
- `openspec validate --all --strict` exits successfully or reports an explicit empty-spec state.

Read [AI_OPS.md](AI_OPS.md) and the
[AI-ops skill](.agents/skills/financial-research-agent-ai-ops/SKILL.md) for model, retrieval,
evaluation, runtime-state, monitoring, or provider changes.

## 4. Stack

- Frontend: React, TypeScript, Vite, tokenized CSS, Lucide icons.
- API: Python 3.13, FastAPI, Pydantic, httpx.
- Orchestration: LangGraph.
- Data: SEC EDGAR Company Facts/submissions and Yahoo Finance chart data.
- Packaging: npm lockfile, Python requirements, Dockerfile, docker-compose.
- Design: private design source file `PRIVATE_DESIGN_SOURCE_REMOVED` with editable desktop/mobile screens.

Gate: `npm run check`.
The repository is prepared for an owner-authorized GitHub remote. Follow [WORKFLOW.md](WORKFLOW.md)
for future phase work.

## 5. Constitution

**Version 1.1.0** · Ratified 2026-10-19 · Last amended 2026-10-20

- Never present generated copy or cached values as primary-source facts.
- Every reported figure must keep its period, unit, source, and retrieval time.
- Python owns calculations; language models may explain results but may not invent or recompute them.
- A failed or incomplete provider response must produce an explicit unavailable/error state.
- The product must remain a research aid and must not execute trades or present personal investment advice.
- No simulated company or market data may appear in product flows or verification screenshots.
- UI must preserve keyboard focus, semantic structure, reduced-motion behavior, and mobile readability.
- No agent session may combine untrusted input, sensitive/private data, and external egress; at most
  two capabilities may be active in the same boundary.

Amendments require the owner, a reason, a semantic version bump, and matching copies in
`AGENTS.md` and `openspec/config.yaml`.

| Version | Date | Reason | Owner |
|---|---|---|---|
| 1.0.0 | 2026-10-19 | Ratified at setup | Peter |
| 1.1.0 | 2026-10-20 | Add BYO model, LangSmith, and enforced access-triangle boundary | Peter |

## 6. Phases and gates

| Phase | Deliverable | Status |
|---|---|---|
| 1 | Live SEC/market-data MVP, responsive dashboard, private design source designs, local checks | Complete |
| 2 | Durable run memory and evaluation corpus | Planned |
| 3 | Production deployment design and hardened observability | Planned |

### ⛔ Before deployment

- [ ] Owner chooses AWS account, region, budget, secrets path, and public/private access.
- [ ] Security, privacy, evaluation, rollback, and cost gates pass.

### ⛔ Before paid model use

- [ ] Owner chooses provider/model and approves a spend ceiling.
- [ ] Offline calculation and citation evaluations remain authoritative.

### ⛔ Before external writes

- [ ] Owner explicitly authorizes any message, alert, portfolio update, or trade-like action.
