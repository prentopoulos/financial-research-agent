# Ledger

**Evidence-first public-company research from live SEC filings and market prices.**

Ledger turns a ticker into a cited research memo, a peer comparison, and a company-scoped
conversation. Python calculates every financial figure and the valuation verdict. A configured
model may select candidate peers, write clear prose, answer questions about the report, and search
the public web in Explore mode.

[Quick start](#quick-start) · [Workflow](#how-a-report-is-built) · [Ask Ledger](#ask-ledger) ·
[Architecture](#architecture) · [Security](#security-boundary) · [Observability](#langsmith-observability)

![Ledger system architecture](docs/diagrams/system-architecture.svg)

There is no simulated company data. Missing or weak evidence lowers confidence or stops the report.

## What it does

| Capability | Practical behavior |
|---|---|
| Live company evidence | Retrieves SEC Company Facts, filing metadata, and current market history |
| Deterministic analysis | Calculates growth, margins, cash flow, market value, and multiples in Python |
| Verified comparisons | Resolves peer tickers against SEC records and retrieves each peer independently |
| Research memo | Produces a cited conclusion, investment case, financial profile, valuation, and risks |
| Report conversation | Answers from the verified report snapshot and returns allow-listed evidence links |
| Explore conversation | Adds current public-web context through one cited OpenAI web search |
| Export | Downloads the validated memo as editable Markdown or a formatted PDF |
| Observability | Sends research and chat traces to LangSmith when explicitly enabled |

## Quick start

Prerequisites: Python 3.12+, Node.js 22+, and Git.

```powershell
git clone YOUR_GITHUB_REPOSITORY_URL
cd financial_research_agent
Copy-Item .env.example .env
```

Set a real SEC contact identity and, if wanted, your own model-provider key:

```dotenv
SEC_USER_AGENT="Ledger Research your-email@example.com"
OPENAI_API_KEY="your-provider-key"
OPENAI_MODEL="gpt-5-mini"
OPENAI_BASE_URL="https://api.openai.com/v1"
MODEL_PROVIDER="OpenAI"
```

The key belongs to your provider account, and that provider bills the usage. Ledger ships no shared
key or credits. Leave `OPENAI_API_KEY` blank to run deterministic report generation and common Report
chat questions without model charges.

Install and start:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
npm install
npm run dev
```

Open <http://127.0.0.1:5173>.

Docker is also supported:

```powershell
Copy-Item .env.example .env
docker compose up --build
```

Then open <http://127.0.0.1:8000>.

## How a report is built

![Ledger research data flow](docs/diagrams/research-data-flow.svg)

1. The API resolves the ticker against the SEC company index.
2. Providers retrieve public filing facts, filing history, and price history.
3. Python normalizes annual, quarterly, and trailing-period evidence.
4. Python calculates ratios and assigns the valuation verdict.
5. Candidate peers are resolved and recalculated from their own evidence.
6. The optional model writes prose around locked figures; the response is validated before display.
7. The browser receives a typed report with source URLs, periods, and retrieval times.

The model cannot alter figures, confidence rules, or the verdict. Invalid model prose falls back to a
deterministic memo. Export applies the same final guard so older in-memory text cannot leak internal
field names or unformatted raw values.

## Ask Ledger

Every completed report opens two conversation modes.

| Mode | Use it for | Evidence boundary |
|---|---|---|
| **Report** | Explain the verdict, figures, peers, risks, and methodology already on screen | Immutable server-held report snapshot; no browsing or tools |
| **Explore** | Ask about current news, commentary, industry changes, or a wider market narrative | Locked report plus one provider-hosted public-web search with validated citations |

The browser sends the report run ID, a public-company question, and at most eight recent messages. The
server rebuilds a typed virtual ontology from the verified report on every turn and checks every
evidence ID before returning a source link. Reports expire after 30 minutes, conversations reset when
the server restarts, and each run accepts at most 24 questions.

Use **Expand** to give the conversation the full workspace. **Return** or `Escape` restores the report
layout without clearing the thread, selected mode, suggestions, or draft question.

Report generation and Report chat work with providers exposing an OpenAI-compatible
`/chat/completions` endpoint. Explore uses OpenAI's `/responses` endpoint and built-in `web_search`, so
it requires the official OpenAI endpoint, a compatible model, and Responses permission.

## Export

Choose **Markdown** for an editable memo or **PDF** for a paginated research document with clickable
source links. Both formats use the same validated report snapshot and compact human-readable numbers.

The PDF uses a three-part editorial structure: conclusion and investment case, financial analysis and
risks, then methodology and the full evidence ledger. Text blocks are measured before pagination so
headings, numbered items, and source entries stay together.

## Which companies work?

Ledger accepts a ticker from the SEC company index, including formats such as `AAPL`, `NVDA`, `XNDU`,
`QNT`, and `BRK.B`. The evidence engine supports:

- 10-K, 20-F, and 40-F annual reporting;
- structured annual financials from S-1, F-1, 424B3, and 424B4 prospectuses;
- trailing-twelve-month figures from four reported quarters or annual-plus-YTD reconciliation;
- standard US-GAAP/IFRS concepts and conservatively matched issuer-extension concepts; and
- recent listings, using the latest comparable interim period with confidence capped at Low.

Annualized interim figures are calculations from reported periods. Funds, private companies, issuers
without usable consolidated XBRL facts, and symbols without market-price history may return an
evidence error instead of a report.

When a model is configured, it proposes two relevant peers. Every ticker is resolved against the SEC
index and its figures are retrieved independently before it enters the table. Without a model, Ledger
uses a small SEC-industry fallback cohort. Missing peers reduce confidence and are never replaced with
invented values.

## Architecture

Ledger uses three separate LangGraph workflows:

- `company-research` retrieves evidence, calculates figures, verifies peers, and writes the report;
- `report-chat` explains an immutable report through typed facts and allow-listed citations; and
- `market-explore` adds cited public-web context without changing the report.

FastAPI owns request guards and process-local report state. Python owns calculations and verdicts.
React renders the report and conversation. OpenAI is optional for report generation and Report chat,
and required for Explore. LangSmith is optional.

[Read the architecture notes](docs/ARCHITECTURE.md) ·
[Open the standalone diagram gallery](docs/ARCHITECTURE.html) ·
[Inspect the self-contained diagram sources](docs/diagrams/)

## Security boundary

Ledger enforces the access-triangle rule: one agent session may hold at most two of untrusted input,
sensitive data, and a path that can send data out.

![Ledger access-triangle security matrix](docs/diagrams/access-triangle-matrix.svg)

Current research and conversation sessions accept bounded external input and can call approved HTTPS
services. Sensitive-data access is absent. The runtime check in `backend/app/security.py` rejects a
three-capability profile. Keys stay outside graph state, and the model has no filesystem, database,
messaging, portfolio, account, or trading tools.

See [the security model](docs/SECURITY.md) for prompt-injection controls, tracing limits, recovery, and
the rules for any future private-data feature.

## LangSmith observability

Tracing is optional and disabled by default:

```dotenv
LANGSMITH_TRACING="true"
LANGSMITH_API_KEY="your-langsmith-key"
LANGSMITH_PROJECT="ledger-financial-research"
```

Research runs appear as `company-research`, report conversations as `report-chat`, and live web
questions as `market-explore`. Traces include workflow, ticker, report run ID, model configuration,
latency, verifier outcome, and token usage when the provider returns it. Model calls appear as nested
`openai-chat-completions` or `openai-responses-web-search` runs.

Tracing can include graph inputs and outputs. Keep the current public-data boundary or add explicit
redaction and isolation before introducing private portfolios, user files, or sensitive memory.

## Verify

```powershell
npm run check
openspec validate --all --strict
```

`npm run check` runs TypeScript checking, ESLint, Python unit tests, and the production build. Tests do
not call a paid model. Live smoke tests require SEC and market-network access.

## Project documents

- [Architecture](docs/ARCHITECTURE.md)
- [Conversational-agent research](docs/CONVERSATIONAL_AGENT_RESEARCH.md)
- [Security and access triangle](docs/SECURITY.md)
- [Design review](docs/DESIGN_REVIEW.md)
- [AI operations](AI_OPS.md)
- [Project handoff](HANDOFF.md)

Ledger is a research aid, not investment advice. Verify primary filings before making a decision.
