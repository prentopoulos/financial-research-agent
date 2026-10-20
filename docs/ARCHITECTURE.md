# Ledger architecture

Live public data enters once. Python calculates the numbers. Ledger returns a cited research memo.

## System map

```mermaid
flowchart LR
    R[Researcher] -->|Ticker| UI[Ledger]
    UI --> API[Research API]
    SEC[SEC filings] --> API
    MKT[Market prices] --> API
    API --> PY[Python engine]
    PY --> OUT[Cited report]
    OUT --> UI
    MODEL[Optional model] -. candidate peers + prose .-> API
```

The model is optional. It may suggest peers and write prose from minimized public evidence, but it
does not calculate figures or change the valuation verdict.

## One research run

```mermaid
flowchart LR
    A[01 Resolve] --> B[02 Retrieve]
    B --> C[03 Calculate]
    C --> D[04 Select peers]
    D --> E[05 Verify peers]
    E --> F[06 Publish]
```

- **Resolve:** match the ticker to an SEC company.
- **Retrieve:** load filings, company facts, and market history.
- **Calculate:** normalize periods and calculate metrics in Python.
- **Select:** use the configured model or an SEC-industry fallback.
- **Verify:** retrieve and calculate every peer independently.
- **Publish:** return the memo, citations, evidence basis, and run trace.

## Trust contract

| Concern | Owner | Rule |
| --- | --- | --- |
| Figures and verdict | Python | Deterministic and testable outside the language layer |
| Narrative and peer suggestions | Optional model | Public, minimized evidence only; output is validated |
| Missing or failed data | API | Remains unavailable or becomes an explicit error |

The runtime keeps private data out of the research session. Ledger has no trading, messaging,
background-write, or database capability in the local MVP.

For the visual version, open [`ARCHITECTURE.html`](ARCHITECTURE.html).
