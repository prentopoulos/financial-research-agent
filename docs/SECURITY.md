# Security and agent access boundary

## Access triangle

The project follows the lethal-trifecta rule: a single agent session may have at most two of these
capabilities.

1. Untrusted or externally supplied input.
2. Sensitive/private data or secrets.
3. A communication path that can send data out.

```mermaid
flowchart TD
    I[Untrusted input] --- A[Maximum two]
    S[Sensitive data] --- A
    E[External egress] --- A
    A --> R{All three enabled?}
    R -->|Yes| X[Reject the session]
    R -->|No| Y[Run within the declared boundary]
```

Ledger’s model step is declared as:

| Capability | State | Enforcement |
|---|---|---|
| External input | Enabled, bounded | Server ticker regex; client character filter; structured public records only |
| Sensitive data | Disabled | No user files, memory, database, private portfolio, or environment values enter graph/model state |
| External egress | Enabled | One configured OpenAI-compatible HTTPS endpoint; no arbitrary URL or tool selection |

`backend/app/security.py` rejects any future runtime profile enabling all three. Remote model endpoints
must use HTTPS; HTTP is allowed only for localhost model servers.

## Model boundary

- The key is read from `OPENAI_API_KEY` and used only in the Authorization header.
- Keys and raw environment variables never enter LangGraph state, prompts, reports, or logs.
- Model input is assembled from an allowlisted public evidence packet.
- The model returns JSON only. Output shape, counts, and peer tickers are validated.
- Peer tickers are resolved against the SEC index and recalculated from source data.
- Python owns financial calculations and the verdict.
- The model has no browser, shell, filesystem, email, database, trading, or write tools.
- Provider errors are filtered before being returned to the UI.

## LangSmith boundary

Tracing is disabled by default. Enabling `LANGSMITH_TRACING=true` sends workflow traces to the
LangSmith account identified by `LANGSMITH_API_KEY`. The current workflow contains public research
data only, but traces can include graph inputs and outputs. Do not enable it after adding private
portfolio data, user documents, or sensitive memory until the trace payload is explicitly redacted or
those inputs are isolated from the traced graph.

## Future changes that require redesign

Before adding private portfolios, uploaded documents, persistent memory, email/Slack, brokerage APIs,
or arbitrary web browsing, create a separate agent boundary. A sensitive-data agent may not also take
untrusted input and communicate externally. Remove one capability, use a reviewed one-way handoff, and
add injection, denied-disclosure, retention, and destination tests before enabling the feature.

## Disable and recover

- Remove `OPENAI_API_KEY` to stop all paid model calls; deterministic mode remains available.
- Set `LANGSMITH_TRACING=false` to stop observability egress.
- Stop the local process or Docker container to disable the service.
- Rotate either provider key in its owner account if it may have been exposed.
