# Ledger architecture

## Runtime components

```mermaid
flowchart LR
    User[Researcher] --> Web[React and Vite client]
    Web -->|POST research ticker| API[FastAPI research API]
    API --> Graph[LangGraph workflow]
    Graph --> SEC[SEC EDGAR]
    Graph --> Market[Market chart API]
    Graph --> Calc[Python financial engine]
    Graph -. minimized public evidence .-> Model[Owner model account]
    Graph -. optional traces .-> Smith[Owner LangSmith account]
    Graph --> Report[Cited report and trace]
    Report --> Web
```

## Agent responsibilities

```mermaid
sequenceDiagram
    actor User
    participant API as FastAPI
    participant Graph as LangGraph
    participant Public as SEC + Market APIs
    participant Python as Calculation engine
    participant Model as BYO model

    User->>API: Analyze ticker
    API->>API: Validate ticker format
    API->>Graph: Start bounded run
    Graph->>Public: Resolve company and retrieve facts
    Public-->>Graph: Public structured records
    Graph->>Python: Select annual, TTM, prospectus, or interim basis
    Python->>Python: Normalize XBRL tags and calculate valuation
    Python-->>Graph: Deterministic metrics and verdict
    opt Model key configured
        Graph->>Model: Public company identity + minimized calculated evidence
        Model-->>Graph: Candidate peers and JSON prose
        Graph->>Public: Validate candidate tickers and retrieve their facts
    end
    Graph-->>API: Report, citations, trace, model usage
    API-->>User: Auditable research view
```

The model never calculates financial figures or changes the verdict. Invalid model output is rejected;
provider failure returns the deterministic memo. Candidate peers enter the table only after SEC
resolution and independent calculation.

## Filing compatibility

```mermaid
flowchart TD
    F[SEC Company Facts] --> A{Latest compatible basis}
    X[Bounded inline-XBRL filing fallback] --> A
    A -->|10-K / 20-F / 40-F| Y[Reported annual]
    A -->|Annual plus YTD or four quarters| T[Trailing 12 months]
    A -->|S-1 / F-1 / 424B| P[Prospectus annual]
    A -->|Recent listing with interim history| I[Annualized interim]
    I --> L[Low-confidence cap]
    P --> L
```

The inline-XBRL fallback reads a bounded set of SEC documents only when Company Facts has limited
history. It joins split document sets, excludes dimensional breakdowns from operating totals, sums
share-class facts when no consolidated share count exists, and never asks the language model to infer a
missing number.

## Data ownership

| Data | Owner/source | Persistence | Sent to model |
|---|---|---|---|
| Ticker | User | In-memory request only | Yes, normalized |
| Company facts | SEC | In-memory run only | Selected calculated fields only |
| Market price | Yahoo chart endpoint | In-memory run only | Selected calculated fields only |
| API keys | User environment | `.env`, Git-ignored | Never |
| Report | User | Browser memory / explicit Markdown export | Model prose becomes part of report |
| Trace | Local UI; optional LangSmith | No local database | Public run data only when enabled |

The MVP has no PostgreSQL memory, trading authority, messaging capability, or background scheduler.
