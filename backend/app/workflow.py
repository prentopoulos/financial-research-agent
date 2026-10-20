from __future__ import annotations

import asyncio
import time
import uuid
from datetime import UTC, datetime
from statistics import median
from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from .analysis import as_peer, calculate_valuation, extract_financials, extract_market, verdict_for
from .llm import ModelClient, ModelError, TokenUsage
from .models import Citation, ModelRun, ResearchReport, TraceStep
from .providers import PublicDataClient, utc_now


PEER_COHORTS: list[tuple[range, list[str]]] = [
    (range(3570, 3580), ["MSFT", "ORCL", "ADBE"]),
    (range(3670, 3680), ["NVDA", "AMD", "INTC"]),
    (range(2830, 2840), ["JNJ", "PFE", "MRK"]),
    (range(2910, 2920), ["XOM", "CVX", "COP"]),
    (range(3710, 3720), ["F", "GM", "TSLA"]),
    (range(4510, 4520), ["DAL", "UAL", "AAL"]),
    (range(4810, 4820), ["T", "VZ", "TMUS"]),
    (range(5410, 5420), ["WMT", "COST", "KR"]),
    (range(5810, 5820), ["MCD", "SBUX", "YUM"]),
    (range(6020, 6030), ["JPM", "BAC", "WFC"]),
    (range(7370, 7380), ["MSFT", "ORCL", "GOOGL"]),
]


class ResearchState(TypedDict, total=False):
    ticker: str
    run_id: str
    company: dict[str, Any]
    company_facts: dict[str, Any]
    submissions: dict[str, Any]
    chart: dict[str, Any]
    subject: dict[str, Any]
    peer_tickers: list[str]
    peers: list[dict[str, Any]]
    citations: list[dict[str, Any]]
    trace: list[dict[str, Any]]
    report: dict[str, Any]
    model_usage: TokenUsage
    model_used: bool
    fallback_reason: str


def timed(name: str):
    def decorator(fn):
        async def wrapper(state: ResearchState) -> ResearchState:
            started = time.perf_counter()
            try:
                update = await fn(state)
                elapsed = round((time.perf_counter() - started) * 1000)
                detail = update.pop("_detail")
                trace = [*state.get("trace", []), TraceStep(name=name, status="completed", latency_ms=elapsed, detail=detail).model_dump()]
                return {**update, "trace": trace}
            except Exception as exc:
                elapsed = round((time.perf_counter() - started) * 1000)
                state["trace"] = [*state.get("trace", []), TraceStep(name=name, status="failed", latency_ms=elapsed, detail=str(exc)).model_dump()]
                raise
        return wrapper
    return decorator


def fallback_peer_tickers(sic: str, subject: str) -> list[str]:
    try:
        sic_number = int(sic)
    except (TypeError, ValueError):
        sic_number = 0

    cohort = next((tickers for sic_range, tickers in PEER_COHORTS if sic_number in sic_range), None)
    if cohort is None:
        if 1000 <= sic_number < 4000:
            cohort = ["HON", "GE", "CAT"]
        elif 4000 <= sic_number < 5000:
            cohort = ["UPS", "FDX", "UNP"]
        elif 5000 <= sic_number < 6000:
            cohort = ["WMT", "COST", "TGT"]
        elif 6000 <= sic_number < 7000:
            cohort = ["JPM", "BAC", "C"]
        elif 7000 <= sic_number < 9000:
            cohort = ["MSFT", "GOOGL", "META"]
        else:
            cohort = ["MSFT", "JPM", "WMT"]
    return [ticker for ticker in cohort if ticker != subject.upper()][:2]


@timed("Resolve company")
async def resolve_company(state: ResearchState) -> ResearchState:
    async with PublicDataClient() as client:
        company = await client.resolve_company(state["ticker"])
    return {"company": company, "_detail": f"Matched {company['ticker']} to SEC CIK {company['cik']}."}


@timed("Retrieve primary data")
async def retrieve_data(state: ResearchState) -> ResearchState:
    cik = state["company"]["cik"]
    async with PublicDataClient() as client:
        facts, submissions, chart = await asyncio.gather(
            client.company_facts(cik),
            client.submissions(cik),
            client.market_chart(state["ticker"]),
        )
    company = {
        **state["company"],
        "sic": str(submissions.get("sic") or ""),
        "sic_description": str(submissions.get("sicDescription") or "Unclassified"),
        "exchange": (submissions.get("exchanges") or ["U.S."])[0],
    }
    return {
        "company": company,
        "company_facts": facts,
        "submissions": submissions,
        "chart": chart,
        "_detail": "Loaded SEC Company Facts, filing metadata, and one year of market prices.",
    }


@timed("Calculate fundamentals")
async def calculate_subject(state: ResearchState) -> ResearchState:
    financials, shares = extract_financials(state["company_facts"])
    price, as_of = extract_market(state["chart"])
    valuation = calculate_valuation(financials, shares, price, as_of)
    subject = as_peer(state["ticker"], state["company"]["name"], financials, valuation)
    return {
        "subject": {"financials": financials.model_dump(), "valuation": valuation.model_dump(), "peer": subject.model_dump()},
        "_detail": f"Calculated GAAP margins and valuation from FY {financials.fiscal_year} facts.",
    }


@timed("Select comparable peers")
async def select_peers(state: ResearchState) -> ResearchState:
    model = ModelClient()
    fallback = fallback_peer_tickers(state["company"].get("sic", ""), state["ticker"])
    if not model.enabled:
        return {
            "peer_tickers": fallback,
            "fallback_reason": "No OPENAI_API_KEY configured; used the SEC industry fallback.",
            "_detail": f"Selected {', '.join(fallback)} from the SEC industry fallback; no model credits used.",
        }

    try:
        selected, usage = await model.choose_peers(
            ticker=state["ticker"],
            company_name=state["company"]["name"],
            sic=state["company"].get("sic", ""),
            sic_description=state["company"].get("sic_description", ""),
        )
        candidates = list(dict.fromkeys([*selected, *fallback]))
        return {
            "peer_tickers": candidates,
            "model_usage": state.get("model_usage", TokenUsage()) + usage,
            "model_used": True,
            "_detail": f"{model.model} proposed {', '.join(selected)}; SEC validation follows.",
        }
    except ModelError as exc:
        return {
            "peer_tickers": fallback,
            "fallback_reason": str(exc),
            "_detail": f"Model peer selection was unavailable; used SEC industry fallback ({exc}).",
        }


async def _peer_snapshot(client: PublicDataClient, ticker: str) -> dict[str, Any]:
    company = await client.resolve_company(ticker)
    facts, chart = await asyncio.gather(client.company_facts(company["cik"]), client.market_chart(ticker))
    financials, shares = extract_financials(facts)
    price, as_of = extract_market(chart)
    valuation = calculate_valuation(financials, shares, price, as_of)
    return as_peer(ticker, company["name"], financials, valuation).model_dump()


@timed("Compare peers")
async def compare_peers(state: ResearchState) -> ResearchState:
    candidates = state.get("peer_tickers", [])
    async with PublicDataClient() as client:
        results = await asyncio.gather(
            *[_peer_snapshot(client, ticker) for ticker in candidates],
            return_exceptions=True,
        )
    peers = [result for result in results if isinstance(result, dict)][:2]
    rows = [state["subject"]["peer"], *peers]
    skipped = len(results) - len(peers)
    suffix = f" {skipped} candidate(s) could not be validated and were omitted." if skipped else ""
    return {"peers": rows, "_detail": f"Compared {len(rows)} SEC-validated companies on growth, margins, earnings, sales, and cash flow.{suffix}"}


def _latest_filing(submissions: dict[str, Any]) -> tuple[str, str, str] | None:
    recent = submissions.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    for index, form in enumerate(forms):
        if form in {"10-K", "10-Q"}:
            accession = recent["accessionNumber"][index]
            document = recent["primaryDocument"][index]
            filing_date = recent["filingDate"][index]
            return accession, document, filing_date
    return None


def deterministic_memo(verdict: str, financials: dict[str, Any], valuation: dict[str, Any], premium: float | None) -> dict[str, Any]:
    summaries = {
        "Expensive": "Reported operating quality is offset by a substantial peer-multiple premium. The valuation leaves less room for slower growth or weaker execution.",
        "Undervalued": "Reported growth and cash generation exceed the selected peer set without a matching valuation premium. On this narrow relative screen, the shares appear discounted.",
        "Fairly valued": "The current valuation broadly reflects the company’s reported growth and margin position versus the selected peers. Future returns depend more on operating execution than multiple expansion.",
        "Insufficient evidence": "The available primary-source facts or validated peers are not complete enough for a defensible relative valuation conclusion.",
    }
    thesis = [
        f"Revenue changed {financials['revenue_growth']:.1%} in fiscal {financials['fiscal_year']} based on SEC-reported annual facts." if financials["revenue_growth"] is not None else "Annual revenue growth could not be calculated from comparable SEC facts.",
        f"Gross margin was {financials['gross_margin']:.1%} and operating margin was {financials['operating_margin']:.1%}." if financials["gross_margin"] is not None and financials["operating_margin"] is not None else "One or more reported margin facts were unavailable.",
        f"Free cash flow was approximately ${financials['free_cash_flow'] / 1_000_000_000:.1f}B after reported capital spending." if financials["free_cash_flow"] is not None else "Comparable operating cash flow and capital-spending facts were not both available.",
        f"The stock trades at {valuation['price_to_sales']:.1f}× sales, {premium:.1f}× the selected peer median." if premium is not None else "The relative sales multiple could not be calculated with the available facts.",
    ]
    risks = [
        "Review the latest filing’s Risk Factors section for company-specific operating and regulatory exposures.",
        "A high earnings or sales multiple increases downside sensitivity if growth or margins weaken.",
        "One fiscal-year comparison may not represent the durability of demand, pricing, or cash generation.",
        "Peer multiples are a screening tool, not intrinsic value; business mix and accounting comparability can differ materially.",
    ]
    return {"summary": summaries[verdict], "thesis": thesis, "risks": risks}


@timed("Compose cited memo")
async def compose_report(state: ResearchState) -> ResearchState:
    subject = state["subject"]["peer"]
    peers = state["peers"]
    verdict, confidence = verdict_for(type("PeerLike", (), subject)(), [type("PeerLike", (), row)() for row in peers])
    financials = state["subject"]["financials"]
    valuation = state["subject"]["valuation"]
    peer_ps = [row["price_to_sales"] for row in peers if row["ticker"] != state["ticker"] and row["price_to_sales"] is not None]
    median_peer_ps = median(peer_ps) if peer_ps else None
    premium = valuation["price_to_sales"] / median_peer_ps if valuation["price_to_sales"] and median_peer_ps else None
    memo = deterministic_memo(verdict, financials, valuation, premium)

    model = ModelClient()
    usage = state.get("model_usage", TokenUsage())
    fallback_reason = state.get("fallback_reason")
    model_used = state.get("model_used", False)
    if model.enabled:
        try:
            model_memo, memo_usage = await model.write_memo({
                "ticker": state["ticker"],
                "company_name": state["company"]["name"],
                "sec_industry": state["company"].get("sic_description"),
                "verdict": verdict,
                "confidence": confidence,
                "financials": financials,
                "valuation": valuation,
                "validated_peers": peers,
                "relative_price_to_sales_premium": premium,
            })
            memo = model_memo
            usage += memo_usage
            model_used = True
        except ModelError as exc:
            fallback_reason = "; ".join(filter(None, [fallback_reason, str(exc)]))

    retrieved = utc_now()
    cik_plain = str(int(state["company"]["cik"]))
    filing = _latest_filing(state["submissions"])
    citations = [
        Citation(label="SEC Company Facts", url=f"https://data.sec.gov/api/xbrl/companyfacts/CIK{state['company']['cik']}.json", source="U.S. Securities and Exchange Commission", retrieved_at=retrieved),
        Citation(label="SEC filing history", url=f"https://data.sec.gov/submissions/CIK{state['company']['cik']}.json", source="U.S. Securities and Exchange Commission", retrieved_at=retrieved),
        Citation(label="Market price history", url=f"https://query1.finance.yahoo.com/v8/finance/chart/{state['ticker']}?range=1y&interval=1d", source="Yahoo Finance chart endpoint", retrieved_at=retrieved),
    ]
    if filing:
        accession, document, filing_date = filing
        accession_plain = accession.replace("-", "")
        citations.insert(0, Citation(label=f"Latest available filing ({filing_date})", url=f"https://www.sec.gov/Archives/edgar/data/{cik_plain}/{accession_plain}/{document}", source="U.S. Securities and Exchange Commission", retrieved_at=retrieved))

    model_run = ModelRun(
        enabled=model_used,
        provider=model.provider,
        name=model.model,
        input_tokens=usage.input_tokens,
        output_tokens=usage.output_tokens,
        fallback_reason=fallback_reason,
    )
    report = ResearchReport(
        run_id=state["run_id"],
        ticker=state["ticker"],
        company_name=state["company"]["name"],
        exchange=state["company"].get("exchange", "U.S."),
        generated_at=datetime.now(UTC).isoformat(),
        verdict=verdict,
        confidence=confidence,
        summary=memo["summary"],
        thesis=memo["thesis"],
        risks=memo["risks"],
        financials=financials,
        valuation=valuation,
        peers=peers,
        citations=citations,
        trace=[],
        model=model_run,
        methodology=(
            "Reported GAAP facts come from SEC Company Facts. Market capitalization uses the latest available share price and SEC-reported shares outstanding. "
            "Multiples are calculated in Python. The configured model may select candidate peers and write prose, but it cannot alter figures or the deterministic verdict."
        ),
    )
    detail = f"Generated grounded prose with {model.model}; figures and verdict remained deterministic." if model_used else "Generated the deterministic memo; no model credits were used."
    return {"report": report.model_dump(), "citations": [citation.model_dump() for citation in citations], "model_usage": usage, "model_used": model_used, "fallback_reason": fallback_reason or "", "_detail": detail}


def build_graph():
    graph = StateGraph(ResearchState)
    graph.add_node("resolve_company", resolve_company)
    graph.add_node("retrieve_data", retrieve_data)
    graph.add_node("calculate_subject", calculate_subject)
    graph.add_node("select_peers", select_peers)
    graph.add_node("compare_peers", compare_peers)
    graph.add_node("compose_report", compose_report)
    graph.add_edge(START, "resolve_company")
    graph.add_edge("resolve_company", "retrieve_data")
    graph.add_edge("retrieve_data", "calculate_subject")
    graph.add_edge("calculate_subject", "select_peers")
    graph.add_edge("select_peers", "compare_peers")
    graph.add_edge("compare_peers", "compose_report")
    graph.add_edge("compose_report", END)
    return graph.compile()


GRAPH = build_graph()


async def run_research(ticker: str) -> ResearchReport:
    result = await GRAPH.ainvoke({
        "ticker": ticker.upper(),
        "run_id": str(uuid.uuid4()),
        "trace": [],
        "model_usage": TokenUsage(),
        "model_used": False,
    })
    report = ResearchReport.model_validate(result["report"])
    report.trace = [TraceStep.model_validate(step) for step in result["trace"]]
    return report
