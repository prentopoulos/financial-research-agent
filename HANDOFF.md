# Handoff

Updated: 2026-10-21.

## Checkpoint

Project workflow, OpenSpec, build-safety, AI-ops, financial-review, and showcase skills are installed.
Phase 1 MVP is implemented and published to the owner's private GitHub repository; no deployment exists.

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
- Separate Explore mode using one OpenAI Responses web search, validated public citations, a locked
  report verdict, and independently filterable LangSmith traces.
- Expandable chat spotlight with Return and Escape controls that preserves the active conversation.
- Markdown and formatted PDF exports with a shared legacy-prose guard and clickable PDF sources.
- Branded system-architecture, research-data-flow, and access-triangle diagrams with self-contained
  HTML sources, SVG documentation exports, and a regenerated README.
- Docker packaging and a private editable desktop/mobile design source.

## Verification

- `npm run typecheck`: pass.
- `npm run lint`: pass.
- Python unit tests: pass (21).
- `npm run build`: pass.
- Diagram Design self-check: pass for all three HTML/SVG diagrams.
- PDF visual review: pass across all three pages; headings, list items, margins, links, and the evidence
  appendix render without overlap or orphaned sections.
- Live NVDA run: pass using FY2026 SEC facts and 2026-10-19 market price.
- Live AAPL and JPM cross-sector runs: pass with SEC-validated peers and no failed workflow steps.
- Live XNDU run: pass using an F-1 plus 6-K TTM basis and quantum peers.
- Live QNT run: pass using annualized 10-Q interim figures, aggregated share classes, and Low confidence.
- Browser review: pass at desktop and 390 x 844.
- Live NVDA Explore question: pass with current web search, validated source links, a locked report
  verdict, and the `gpt-5-mini · live sources verified` label.
- Sidebar scroll sync: pass for Conclusion, Financials, Risks, and the bottom-of-page Sources state.
- The report section indicator ends at Sources; Trace remains a separate evidence-rail tab.
- Semantic screen check: pass; desktop/mobile layouts and the design-system instance were verified.
- Three-perspective design review: complete; accessibility, mobile navigation, export depth, error recovery, and typography findings were applied.

## Next action

Add full filing-text retrieval only after chunk-level citation and injection evaluations are defined.
Durable cross-run memory still requires authentication, retention, deletion, and isolation.
