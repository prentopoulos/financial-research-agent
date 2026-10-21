from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .models import ResearchReport


def _money(value: float | None) -> str:
    if value is None:
        return "Unavailable"
    absolute = abs(value)
    for scale, suffix in ((1_000_000_000_000, "T"), (1_000_000_000, "B"), (1_000_000, "M")):
        if absolute >= scale:
            return f"${value / scale:,.1f}{suffix}"
    return f"${value:,.2f}"


def _percent(value: float | None) -> str:
    return "Unavailable" if value is None else f"{value:.1%}"


def _multiple(value: float | None) -> str:
    return "Unavailable" if value is None else f"{value:.1f}×"


@dataclass(frozen=True)
class OntologyFact:
    fact_id: str
    category: str
    label: str
    value: str
    source_ids: tuple[str, ...] = ()

    def as_prompt(self) -> dict[str, object]:
        return {
            "fact_id": self.fact_id,
            "category": self.category,
            "label": self.label,
            "value": self.value,
            "source_ids": list(self.source_ids),
        }


@dataclass(frozen=True)
class ReportOntology:
    ticker: str
    company_name: str
    facts: tuple[OntologyFact, ...]

    @property
    def by_id(self) -> dict[str, OntologyFact]:
        return {fact.fact_id: fact for fact in self.facts}

    def prompt_packet(self) -> dict[str, object]:
        return {
            "ontology_version": "ledger-report-v1",
            "objects": ["Company", "ReportRun", "FinancialMetric", "ValuationMetric", "Peer", "Claim", "Source"],
            "links": [
                "ReportRun ABOUT Company",
                "FinancialMetric REPORTED_ON ReportRun",
                "ValuationMetric CALCULATED_FOR Company",
                "Company COMPARED_WITH Peer",
                "Claim SUPPORTED_BY FinancialMetric|ValuationMetric|Source",
            ],
            "rules": [
                "Python-calculated values and verdict are immutable.",
                "Missing values remain unavailable.",
                "Answers may cite only listed fact_id values.",
                "No actions, forecasts, price targets, or personal advice.",
            ],
            "facts": [fact.as_prompt() for fact in self.facts],
        }


def _source_ids(report: ResearchReport, *needles: str) -> tuple[str, ...]:
    matches = []
    for index, citation in enumerate(report.citations, start=1):
        haystack = f"{citation.label} {citation.source}".lower()
        if any(needle.lower() in haystack for needle in needles):
            matches.append(f"source.{index}")
    return tuple(matches)


def _subject_source_ids(report: ResearchReport, *, financial_only: bool = False, price_only: bool = False) -> tuple[str, ...]:
    matches: list[str] = []
    for index, citation in enumerate(report.citations, start=1):
        label = citation.label.lower()
        if price_only:
            include = label == "market price history"
        elif financial_only:
            include = label.startswith("financial basis source") or label == "sec company facts"
        else:
            include = label.startswith("financial basis source") or label.startswith("latest available filing") or label in {"sec company facts", "sec filing history"}
        if include:
            matches.append(f"source.{index}")
    return tuple(matches)


def build_report_ontology(report: ResearchReport) -> ReportOntology:
    sec_sources = _subject_source_ids(report)
    financial_sources = _subject_source_ids(report, financial_only=True) or sec_sources
    price_sources = _subject_source_ids(report, price_only=True)
    all_sources = tuple(f"source.{index}" for index in range(1, len(report.citations) + 1))
    valuation_sources = tuple(dict.fromkeys((*financial_sources, *price_sources)))

    facts: list[OntologyFact] = [
        OntologyFact("company.identity", "company", "Company", f"{report.company_name} ({report.ticker}), {report.exchange}"),
        OntologyFact("report.verdict", "conclusion", "Screening verdict", report.verdict, valuation_sources),
        OntologyFact("report.confidence", "conclusion", "Confidence", report.confidence, financial_sources),
        OntologyFact("report.summary", "conclusion", "Conclusion", report.summary, all_sources),
        OntologyFact("financial.basis", "financials", "Evidence basis", f"{report.financials.source_form} · {report.financials.basis_label}", financial_sources),
        OntologyFact("financial.revenue", "financials", "Revenue", _money(report.financials.revenue), financial_sources),
        OntologyFact("financial.revenue_growth", "financials", "Revenue growth", _percent(report.financials.revenue_growth), financial_sources),
        OntologyFact("financial.gross_margin", "financials", "Gross margin", _percent(report.financials.gross_margin), financial_sources),
        OntologyFact("financial.operating_margin", "financials", "Operating margin", _percent(report.financials.operating_margin), financial_sources),
        OntologyFact("financial.net_margin", "financials", "Net margin", _percent(report.financials.net_margin), financial_sources),
        OntologyFact("financial.free_cash_flow", "financials", "Free cash flow", _money(report.financials.free_cash_flow), financial_sources),
        OntologyFact("financial.cash", "financials", "Cash", _money(report.financials.cash), financial_sources),
        OntologyFact("financial.debt", "financials", "Debt", _money(report.financials.debt), financial_sources),
        OntologyFact("valuation.price", "valuation", "Share price", _money(report.valuation.price), price_sources),
        OntologyFact("valuation.market_cap", "valuation", "Market capitalization", _money(report.valuation.market_cap), valuation_sources),
        OntologyFact("valuation.pe", "valuation", "Price to earnings", _multiple(report.valuation.pe), valuation_sources),
        OntologyFact("valuation.price_to_sales", "valuation", "Price to sales", _multiple(report.valuation.price_to_sales), valuation_sources),
        OntologyFact("valuation.fcf_yield", "valuation", "Free-cash-flow yield", _percent(report.valuation.fcf_yield), valuation_sources),
        OntologyFact("valuation.as_of", "valuation", "Market price date", report.valuation.as_of, price_sources),
        OntologyFact("report.methodology", "methodology", "Methodology", report.methodology, all_sources),
    ]

    for index, claim in enumerate(report.thesis, start=1):
        facts.append(OntologyFact(f"thesis.{index}", "thesis", f"Investment case {index}", claim, all_sources))
    for index, risk in enumerate(report.risks, start=1):
        facts.append(OntologyFact(f"risk.{index}", "risks", f"Risk {index}", risk, sec_sources))
    for peer in report.peers:
        prefix = f"peer.{peer.ticker.lower()}"
        peer_sources = valuation_sources if peer.ticker == report.ticker else (_source_ids(report, peer.ticker) or all_sources)
        facts.extend([
            OntologyFact(f"{prefix}.identity", "peers", f"{peer.ticker} company", peer.name, peer_sources),
            OntologyFact(f"{prefix}.market_cap", "peers", f"{peer.ticker} market cap", _money(peer.market_cap), peer_sources),
            OntologyFact(f"{prefix}.revenue_growth", "peers", f"{peer.ticker} revenue growth", _percent(peer.revenue_growth), peer_sources),
            OntologyFact(f"{prefix}.gross_margin", "peers", f"{peer.ticker} gross margin", _percent(peer.gross_margin), peer_sources),
            OntologyFact(f"{prefix}.pe", "peers", f"{peer.ticker} P/E", _multiple(peer.pe), peer_sources),
            OntologyFact(f"{prefix}.price_to_sales", "peers", f"{peer.ticker} P/S", _multiple(peer.price_to_sales), peer_sources),
            OntologyFact(f"{prefix}.fcf_yield", "peers", f"{peer.ticker} FCF yield", _percent(peer.fcf_yield), peer_sources),
        ])
    for index, citation in enumerate(report.citations, start=1):
        facts.append(OntologyFact(f"source.{index}", "sources", citation.label, f"{citation.source}; retrieved {citation.retrieved_at[:10]}", (f"source.{index}",)))

    return ReportOntology(ticker=report.ticker, company_name=report.company_name, facts=tuple(facts))


def facts_for_question(ontology: ReportOntology, question: str) -> list[OntologyFact]:
    text = question.lower()
    categories: set[str] = set()
    keyword_groups = {
        "financials": ("revenue", "growth", "margin", "cash", "debt", "financial", "profit", "flow"),
        "valuation": ("valuation", "valued", "price", "p/e", "pe ", "p/s", "multiple", "yield", "market cap", "undervalued", "expensive", "fair"),
        "peers": ("peer", "compare", "comparison", "competitor", "versus", " vs"),
        "risks": ("risk", "downside", "break", "concern"),
        "sources": ("source", "filing", "evidence", "cite", "where", "document"),
        "methodology": ("method", "calculate", "reliable", "confidence", "basis", "limitation"),
        "thesis": ("thesis", "case", "why", "strength", "reason"),
    }
    for category, keywords in keyword_groups.items():
        if any(keyword in text for keyword in keywords):
            categories.add(category)
    if not categories:
        categories = {"conclusion", "financials", "valuation"}
    if "peers" in categories:
        peer_facts = [fact for fact in ontology.facts if fact.category == "peers"]
        valuation_facts = [fact for fact in ontology.facts if fact.fact_id in {"report.verdict", "report.confidence", "valuation.price_to_sales"}]
        return [*valuation_facts, *peer_facts][:32]
    selected = [fact for fact in ontology.facts if fact.category in categories]
    return selected[:18]


def validated_facts(ontology: ReportOntology, fact_ids: Iterable[str]) -> list[OntologyFact]:
    known = ontology.by_id
    result: list[OntologyFact] = []
    for fact_id in fact_ids:
        fact = known.get(str(fact_id))
        if fact and fact not in result:
            result.append(fact)
    return result[:10]
