# Ledger Financial Research Agent

Evidence-first public-company research using live SEC filings and market prices.

Read `HANDOFF.md` for recovery state and `PROJECT.md` for scope and gates. Use
`.agents/skills/financial-research-agent-build-safety/SKILL.md` for architecture, provider,
data, cost, telemetry, and release changes. Use the sibling AI-ops and financial-review skills
when model behavior, retrieval, numerical outputs, or investment conclusions change.

## Current scope

- Phase 1 is a local MVP for SEC-reporting U.S. tickers.
- Live SEC Company Facts and filing metadata are the source of financial statements.
- Live market prices come from Yahoo's chart endpoint; calculations run in Python.
- LangGraph coordinates retrieval, calculations, comparison, and memo composition.
- Optional BYO model synthesis and optional LangSmith tracing are enabled by owner-supplied keys.
- Completed reports support a read-only, report-scoped conversational analyst with verified evidence IDs.
- AWS deployment, PostgreSQL memory, authentication, private portfolios, and trading are deferred.

## Constitution — version 1.1.0

- Never present generated copy or cached values as primary-source facts.
- Every reported figure must keep its period, unit, source, and retrieval time.
- Python owns calculations; language models may explain results but may not invent or recompute them.
- A failed or incomplete provider response must produce an explicit unavailable/error state.
- The product must remain a research aid and must not execute trades or present personal investment advice.
- No simulated company or market data may appear in product flows or verification screenshots.
- UI must preserve keyboard focus, semantic structure, reduced-motion behavior, and mobile readability.
- No agent session may combine untrusted input, sensitive/private data, and external egress; at most
  two capabilities may be active in the same boundary.

## Local development

Use Node 22+, Python 3.13, npm, and the checked-in lockfile. Copy `.env.example` to `.env`
and set a truthful SEC contact in `SEC_USER_AGENT`. Then run:

```powershell
py -3.13 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
npm install
npm run dev
```

Gate: `npm run check` followed by `openspec validate --all --strict`.

GitHub publication is owner-authorized for this MVP. Deployment, paid provider calls, credential
changes, and merges into a future protected main branch require the owner's approval.
