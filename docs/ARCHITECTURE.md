# Ledger architecture

One bounded graph turns a ticker into a cited report.

```mermaid
flowchart LR
    START((Ticker)) --> GRAPH((LangGraph))
    GRAPH --> DATA((SEC + market))
    DATA --> MATH((Python))
    MATH --> PEERS((Verified peers))
    PEERS --> END((Cited report))
    MODEL((Optional model)) -.-> PEERS
    MODEL -.-> END
```

- **LangGraph** moves shared research state through explicit nodes.
- **Python** owns every figure and the valuation verdict.
- **The model is optional:** candidate peers and prose only.
- **The end state is auditable:** evidence basis, citations, and trace.

Open the [visual architecture](ARCHITECTURE.html).
