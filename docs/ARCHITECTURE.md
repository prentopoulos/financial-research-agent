# Ledger agent architecture

One ticker enters one bounded LangGraph run. Four visible steps produce one cited report.

```mermaid
flowchart LR
    IN((Ticker)) --> ORCH[LangGraph<br/>orchestrator]
    subgraph RUN[LangGraph research run]
        ORCH --> DATA(Evidence<br/>SEC + prices)
        DATA --> MATH(Python<br/>math + verdict)
        MATH --> PEERS(Peers<br/>verify tickers)
        PEERS --> WRITE(Write<br/>cite + explain)
    end
    WRITE --> OUT((Cited report))
    MODEL(Optional model) -.-> PEERS
    MODEL -.-> WRITE
```

- **Required path:** public evidence, Python calculations, verified peers, cited output.
- **Optional model:** suggests peers and helps write prose; it never owns the numbers.
- **Audit trail:** every result keeps its source, period, and retrieval time.

Open the [white system map](ARCHITECTURE.html).
