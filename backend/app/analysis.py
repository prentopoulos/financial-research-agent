from __future__ import annotations

from datetime import UTC, datetime
from statistics import median
from typing import Any, Iterable

from .models import Financials, Peer, Valuation


TAG_CANDIDATES = {
    "revenue": ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues", "SalesRevenueNet"],
    "gross_profit": ["GrossProfit"],
    "operating_income": ["OperatingIncomeLoss"],
    "net_income": ["NetIncomeLoss", "ProfitLoss"],
    "operating_cash": ["NetCashProvidedByUsedInOperatingActivities"],
    "capex": ["PaymentsToAcquireProductiveAssets", "PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsForAdditionsToPropertyPlantAndEquipment"],
    "cash": ["CashAndCashEquivalentsAtCarryingValue", "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents"],
    "debt_current": ["ShortTermBorrowings", "LongTermDebtCurrent"],
    "debt_long": ["LongTermDebtNoncurrent", "LongTermDebt"],
    "shares": ["CommonStockSharesOutstanding", "EntityCommonStockSharesOutstanding"],
}


def safe_div(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return numerator / denominator


def _values(facts: dict[str, Any], names: Iterable[str], unit: str) -> list[dict[str, Any]]:
    us_gaap = facts.get("facts", {}).get("us-gaap", {})
    combined: list[dict[str, Any]] = []
    for name in names:
        values = us_gaap.get(name, {}).get("units", {}).get(unit, [])
        combined.extend(values)
    combined.sort(key=lambda row: (row.get("end", ""), row.get("filed", "")))
    return combined


def _annual_values(facts: dict[str, Any], names: Iterable[str]) -> list[dict[str, Any]]:
    values = _values(facts, names, "USD")
    filtered = [row for row in values if row.get("form") == "10-K" and row.get("fp") == "FY" and row.get("val") is not None]
    deduped: dict[tuple[Any, Any], dict[str, Any]] = {}
    for row in filtered:
        key = (row.get("fy"), row.get("end"))
        incumbent = deduped.get(key)
        if not incumbent or row.get("filed", "") > incumbent.get("filed", ""):
            deduped[key] = row
    return sorted(deduped.values(), key=lambda row: (row.get("fy", 0), row.get("end", "")))


def _latest_at_or_before(rows: list[dict[str, Any]], end: str) -> float | None:
    eligible = [row for row in rows if row.get("end", "") <= end and row.get("val") is not None]
    return float(eligible[-1]["val"]) if eligible else None


def extract_financials(facts: dict[str, Any]) -> tuple[Financials, float | None]:
    revenue_rows = _annual_values(facts, TAG_CANDIDATES["revenue"])
    if not revenue_rows:
        raise ValueError("No annual revenue fact was available in SEC Company Facts.")
    latest = revenue_rows[-1]
    previous = next((row for row in reversed(revenue_rows[:-1]) if row.get("fy") != latest.get("fy") or row.get("end") != latest.get("end")), None)
    end = latest["end"]
    revenue = float(latest["val"])
    previous_revenue = float(previous["val"]) if previous else None

    def annual(field: str) -> float | None:
        rows = _annual_values(facts, TAG_CANDIDATES[field])
        exact = [row for row in rows if row.get("end") == end]
        return float(exact[-1]["val"]) if exact else None

    gross_profit = annual("gross_profit")
    operating_income = annual("operating_income")
    net_income = annual("net_income")
    operating_cash = annual("operating_cash")
    capex = annual("capex")

    cash_rows = _values(facts, TAG_CANDIDATES["cash"], "USD")
    debt_current_rows = _values(facts, TAG_CANDIDATES["debt_current"], "USD")
    debt_long_rows = _values(facts, TAG_CANDIDATES["debt_long"], "USD")
    shares_rows = _values(facts, TAG_CANDIDATES["shares"], "shares")
    shares_rows = [row for row in shares_rows if row.get("val") is not None]
    shares_rows.sort(key=lambda row: (row.get("end", ""), row.get("filed", "")))

    cash = _latest_at_or_before(cash_rows, end)
    debt_current = _latest_at_or_before(debt_current_rows, end) or 0
    debt_long = _latest_at_or_before(debt_long_rows, end) or 0
    shares = float(shares_rows[-1]["val"]) if shares_rows else None
    free_cash_flow = operating_cash - capex if operating_cash is not None and capex is not None else None

    financials = Financials(
        fiscal_year=int(latest.get("fy") or int(end[:4])),
        period_end=end,
        revenue=revenue,
        revenue_growth=safe_div(revenue - previous_revenue, previous_revenue) if previous_revenue is not None else None,
        gross_margin=safe_div(gross_profit, revenue),
        operating_margin=safe_div(operating_income, revenue),
        net_margin=safe_div(net_income, revenue),
        free_cash_flow=free_cash_flow,
        cash=cash,
        debt=debt_current + debt_long,
    )
    return financials, shares


def extract_market(chart: dict[str, Any]) -> tuple[float | None, str]:
    results = chart.get("chart", {}).get("result") or []
    if not results:
        error = chart.get("chart", {}).get("error", {}).get("description", "No market chart returned")
        raise ValueError(error)
    result = results[0]
    metadata = result.get("meta", {})
    price = metadata.get("regularMarketPrice")
    timestamp = metadata.get("regularMarketTime")
    if price is None:
        closes = result.get("indicators", {}).get("quote", [{}])[0].get("close", [])
        price = next((value for value in reversed(closes) if value is not None), None)
    as_of = datetime.fromtimestamp(timestamp, UTC).date().isoformat() if timestamp else datetime.now(UTC).date().isoformat()
    return float(price) if price is not None else None, as_of


def calculate_valuation(financials: Financials, shares: float | None, price: float | None, as_of: str) -> Valuation:
    market_cap = price * shares if price is not None and shares is not None else None
    net_income = financials.revenue * financials.net_margin if financials.revenue is not None and financials.net_margin is not None else None
    return Valuation(
        price=price,
        market_cap=market_cap,
        pe=safe_div(market_cap, net_income),
        price_to_sales=safe_div(market_cap, financials.revenue),
        fcf_yield=safe_div(financials.free_cash_flow, market_cap),
        as_of=as_of,
    )


def as_peer(ticker: str, name: str, financials: Financials, valuation: Valuation) -> Peer:
    return Peer(
        ticker=ticker,
        name=name,
        price=valuation.price,
        market_cap=valuation.market_cap,
        revenue_growth=financials.revenue_growth,
        gross_margin=financials.gross_margin,
        pe=valuation.pe,
        price_to_sales=valuation.price_to_sales,
        fcf_yield=valuation.fcf_yield,
    )


def verdict_for(subject: Peer, peers: list[Peer]) -> tuple[str, str]:
    comparable = [peer for peer in peers if peer.ticker != subject.ticker and peer.price_to_sales is not None]
    if subject.price_to_sales is None or subject.revenue_growth is None or not comparable:
        return "Insufficient evidence", "Low"
    median_ps = median(peer.price_to_sales for peer in comparable if peer.price_to_sales is not None)
    growth_lead = subject.revenue_growth - max((peer.revenue_growth or 0) for peer in comparable)
    premium = subject.price_to_sales / median_ps if median_ps else None
    if premium is not None and premium < 1.15 and growth_lead > 0.10:
        return "Undervalued", "Moderate"
    if premium is not None and premium > 2.5:
        return "Expensive", "Moderate"
    return "Fairly valued", "Moderate"
