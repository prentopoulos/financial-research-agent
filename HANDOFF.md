# Handoff

Updated: 2026-10-20.

## Checkpoint

Project workflow, OpenSpec, build-safety, AI-ops, financial-review, and showcase skills are installed.
Phase 1 MVP implementation is being finalized for an owner-authorized GitHub push; no deployment exists.

## Implemented

- React/Vite research dashboard with responsive desktop and mobile layouts.
- FastAPI + LangGraph workflow using live SEC and market-price data.
- Optional BYO OpenAI-compatible model for validated peer selection and grounded prose.
- Optional LangSmith tracing, disabled in the template and enabled in the owner's ignored local environment.
- 20-F/40-F, prospectus, TTM, issuer-extension XBRL, and recent-listing financial bases.
- Runtime enforcement of the two-of-three agent access boundary.
- Python financial calculations, AMD/Intel comparison, deterministic cited memo, Markdown export.
- Loading, provider failure, trace timing, and zero-cost reporting states.
- Scroll-synced sidebar navigation, including correct activation of the final Sources section.
- Report-scoped Ask Ledger panel with a typed virtual ontology, verified evidence IDs, source links,
  prompt-injection/secret guards, a deterministic no-credit fallback, and ephemeral bounded memory.
- Docker packaging and a private editable desktop/mobile design source.

## Verification

- `npm run typecheck`: pass.
- `npm run lint`: pass.
- Python unit tests: pass (16).
- `npm run build`: pass.
- Live NVDA run: pass using FY2026 SEC facts and 2026-10-19 market price.
- Live AAPL and JPM cross-sector runs: pass with SEC-validated peers and no failed workflow steps.
- Live XNDU run: pass using an F-1 plus 6-K TTM basis and quantum peers.
- Live QNT run: pass using annualized 10-Q interim figures, aggregated share classes, and Low confidence.
- Browser review: pass at desktop and 390 x 844.
- Sidebar scroll sync: pass for Conclusion, Financials, Risks, and the bottom-of-page Sources state.
- Semantic screen check: pass; desktop/mobile layouts and the design-system instance were verified.
- Three-perspective design review: complete; accessibility, mobile navigation, export depth, error recovery, and typography findings were applied.

## Next action

Extend the chat to full filing-text retrieval only after chunk-level citation and injection evaluations
are defined. Durable cross-run memory still requires authentication, retention, deletion, and isolation.
