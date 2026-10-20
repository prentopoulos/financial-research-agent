from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
from statistics import median
from typing import Any, Iterable

from .inline_xbrl import InlineDocument, extract_inline_document_set
from .models import Financials, Peer, Valuation


TAG_CANDIDATES = {
    "revenue": ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues", "SalesRevenueNet", "Revenue"],
    "gross_profit": ["GrossProfit"],
    "operating_income": ["OperatingIncomeLoss", "ProfitLossFromOperatingActivities"],
    "net_income": ["NetIncomeLoss", "ProfitLoss"],
    "operating_cash": ["NetCashProvidedByUsedInOperatingActivities", "CashFlowsFromUsedInOperatingActivities"],
    "capex": ["PaymentsToAcquireProductiveAssets", "PaymentsToAcquirePropertyPlantAndEquipment", "PurchaseOfPropertyPlantAndEquipment"],
    "cash": ["CashAndCashEquivalentsAtCarryingValue", "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents", "CashAndCashEquivalents"],
    "debt_current": ["ShortTermBorrowings", "LongTermDebtCurrent", "CurrentBorrowings"],
    "debt_long": ["LongTermDebtNoncurrent", "LongTermDebt", "NoncurrentBorrowings"],
    "shares": ["CommonStockSharesOutstanding", "EntityCommonStockSharesOutstanding", "SharesOutstanding"],
}

ANNUAL_FORMS = {"10-K", "20-F", "40-F"}
PROSPECTUS_FORMS = {"S-1", "S-1/A", "F-1", "F-1/A", "424B3", "424B4"}
INTERIM_FORMS = {"10-Q", "6-K", *PROSPECTUS_FORMS}


@dataclass(frozen=True)
class _Component:
    start: str
    end: str
    coefficient: float = 1.0


@dataclass(frozen=True)
class _Basis:
    kind: str
    label: str
    source_form: str
    source_url: str | None
    fiscal_year: int
    end: str
    components: tuple[_Component, ...]
    revenue: float
    previous_revenue: float | None
    limited_history: bool


def safe_div(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return numerator / denominator


def _duration(row: dict[str, Any]) -> int | None:
    if not row.get("start") or not row.get("end"):
        return None
    try:
        return (date.fromisoformat(row["end"]) - date.fromisoformat(row["start"])).days + 1
    except (TypeError, ValueError):
        return None


def _heuristic_tag(field: str, tag: str) -> bool:
    compact = "".join(character for character in tag.lower() if character.isalnum())
    exclusions = ("cost", "remaining", "contractliability", "deferred", "segment", "geographic", "disaggregation", "percentage", "policy", "textblock")
    if field == "revenue":
        return not any(word in compact for word in exclusions) and compact.endswith(("revenue", "revenues", "revenuenet", "salesnet"))
    endings = {
        "gross_profit": ("grossprofit",),
        "operating_income": ("operatingincomeloss", "operatingprofitloss"),
        "net_income": ("netincomeloss", "profitloss"),
        "operating_cash": ("netcashprovidedbyusedinoperatingactivities", "cashflowsfromusedinoperatingactivities"),
        "capex": ("paymentstoacquirepropertyplantandequipment", "purchaseofpropertyplantandequipment"),
        "cash": ("cashandcashequivalents", "cashandcashequivalentsatcarryingvalue"),
        "debt_current": ("longtermdebtcurrent", "currentborrowings"),
        "debt_long": ("longtermdebtnoncurrent", "longtermdebt", "noncurrentborrowings"),
        "shares": ("commonstocksharesoutstanding", "entitycommonstocksharesoutstanding", "sharesoutstanding"),
    }
    return compact.endswith(endings[field])


def _field_rows(facts: dict[str, Any], inline_rows: list[dict[str, Any]], field: str, unit: str) -> list[dict[str, Any]]:
    candidates = TAG_CANDIDATES[field]
    rows: list[dict[str, Any]] = []
    for namespace, concepts in facts.get("facts", {}).items():
        for tag, concept in concepts.items():
            if tag in candidates:
                priority = candidates.index(tag)
            elif _heuristic_tag(field, tag):
                priority = 100
            else:
                continue
            for unit_name, values in concept.get("units", {}).items():
                if unit_name.lower() != unit.lower():
                    continue
                for value in values:
                    if value.get("val") is None or (value.get("segment") and field != "shares"):
                        continue
                    rows.append({**value, "namespace": namespace, "tag": tag, "unit": unit_name, "priority": priority, "source_url": None, "dimensional": bool(value.get("segment"))})

    for value in inline_rows:
        tag = str(value.get("tag", ""))
        if tag in candidates:
            priority = candidates.index(tag)
        elif _heuristic_tag(field, tag):
            priority = 100
        else:
            continue
        unit_name = str(value.get("unit", ""))
        if unit.lower() not in unit_name.lower():
            continue
        if value.get("dimensional") and field != "shares":
            continue
        rows.append({**value, "priority": priority})
    return rows


def _best(rows: Iterable[dict[str, Any]]) -> dict[str, Any] | None:
    candidates = list(rows)
    if not candidates:
        return None
    return sorted(candidates, key=lambda row: (-int(row.get("priority", 100)), row.get("filed", "")))[-1]


def _unique_periods(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    periods: dict[tuple[str | None, str | None], list[dict[str, Any]]] = {}
    for row in rows:
        periods.setdefault((row.get("start"), row.get("end")), []).append(row)
    selected = [_best(group) for group in periods.values()]
    return sorted((row for row in selected if row), key=lambda row: (row.get("end", ""), row.get("start", "")))


def _full_year_rows(rows: list[dict[str, Any]], forms: set[str]) -> list[dict[str, Any]]:
    return _unique_periods(row for row in rows if row.get("form") in forms and _duration(row) is not None and 300 <= (_duration(row) or 0) <= 400)


def _matching_prior(rows: list[dict[str, Any]], current: dict[str, Any]) -> dict[str, Any] | None:
    current_days = _duration(current)
    if current_days is None:
        return None
    current_end = date.fromisoformat(current["end"])
    matches = []
    for row in rows:
        days = _duration(row)
        if days is None or row.get("end") == current.get("end"):
            continue
        day_gap = (current_end - date.fromisoformat(row["end"])).days
        if 330 <= day_gap <= 400 and abs(days - current_days) <= 10:
            matches.append(row)
    return _best(matches)


def _ttm_from_annual(revenue_rows: list[dict[str, Any]], annual: dict[str, Any]) -> _Basis | None:
    annual_end = date.fromisoformat(annual["end"])
    ytd_rows = _unique_periods(
        row for row in revenue_rows
        if row.get("form") in INTERIM_FORMS
        and _duration(row) is not None
        and 120 <= (_duration(row) or 0) <= 285
        and date.fromisoformat(row["end"]) > annual_end
    )
    if not ytd_rows:
        return None
    current = ytd_rows[-1]
    prior = _matching_prior(revenue_rows, current)
    if not prior:
        return None
    revenue = float(annual["val"]) + float(current["val"]) - float(prior["val"])
    return _Basis(
        kind="ttm",
        label=f"Trailing 12 months through {current['end']}",
        source_form=f"{annual.get('form', 'annual')} + {current.get('form', 'interim')}",
        source_url=current.get("source_url") or annual.get("source_url"),
        fiscal_year=int(str(current["end"])[:4]),
        end=current["end"],
        components=(
            _Component(annual["start"], annual["end"], 1.0),
            _Component(current["start"], current["end"], 1.0),
            _Component(prior["start"], prior["end"], -1.0),
        ),
        revenue=revenue,
        previous_revenue=float(annual["val"]),
        limited_history=annual.get("form") in PROSPECTUS_FORMS,
    )


def _ttm_from_quarters(revenue_rows: list[dict[str, Any]]) -> _Basis | None:
    quarters = _unique_periods(
        row for row in revenue_rows
        if row.get("form") in INTERIM_FORMS and _duration(row) is not None and 70 <= (_duration(row) or 0) <= 110
    )
    if len(quarters) < 4:
        return None
    current = quarters[-4:]
    gaps = [(date.fromisoformat(right["end"]) - date.fromisoformat(left["end"])).days for left, right in zip(current, current[1:])]
    if any(gap < 65 or gap > 125 for gap in gaps):
        return None
    previous = quarters[-8:-4] if len(quarters) >= 8 else []
    return _Basis(
        kind="ttm",
        label=f"Trailing 12 months through {current[-1]['end']}",
        source_form="Four reported quarters",
        source_url=current[-1].get("source_url"),
        fiscal_year=int(str(current[-1]["end"])[:4]),
        end=current[-1]["end"],
        components=tuple(_Component(row["start"], row["end"]) for row in current),
        revenue=sum(float(row["val"]) for row in current),
        previous_revenue=sum(float(row["val"]) for row in previous) if len(previous) == 4 else None,
        limited_history=False,
    )


def _select_basis(revenue_rows: list[dict[str, Any]]) -> _Basis:
    annual = _full_year_rows(revenue_rows, ANNUAL_FORMS)
    prospectus = _full_year_rows(revenue_rows, PROSPECTUS_FORMS)
    base = annual[-1] if annual else prospectus[-1] if prospectus else None
    if base:
        ttm = _ttm_from_annual(revenue_rows, base)
        if ttm:
            return ttm
        peers = annual if annual else prospectus
        previous = peers[-2] if len(peers) >= 2 else None
        kind = "annual" if annual else "prospectus"
        form = str(base.get("form") or ("10-K" if annual else "Prospectus"))
        return _Basis(
            kind=kind,
            label=f"FY {base.get('fy') or str(base['end'])[:4]} reported in {form}",
            source_form=form,
            source_url=base.get("source_url"),
            fiscal_year=int(base.get("fy") or str(base["end"])[:4]),
            end=base["end"],
            components=(_Component(base["start"], base["end"]),),
            revenue=float(base["val"]),
            previous_revenue=float(previous["val"]) if previous else None,
            limited_history=kind == "prospectus",
        )

    ttm = _ttm_from_quarters(revenue_rows)
    if ttm:
        return ttm

    interim = _unique_periods(
        row for row in revenue_rows
        if row.get("form") in INTERIM_FORMS and _duration(row) is not None and 70 <= (_duration(row) or 0) <= 285
    )
    if not interim:
        raise ValueError("SEC filings were found, but no compatible annual, prospectus, or interim revenue period was available.")
    latest_end = interim[-1]["end"]
    latest = max((row for row in interim if row["end"] == latest_end), key=lambda row: _duration(row) or 0)
    days = _duration(latest) or 365
    factor = 365 / days
    prior = _matching_prior(revenue_rows, latest)
    prior_value = float(prior["val"]) * (365 / (_duration(prior) or days)) if prior else None
    months = max(1, round(days / 30.4))
    return _Basis(
        kind="interim_annualized",
        label=f"Annualized {months}-month interim period through {latest['end']}",
        source_form=str(latest.get("form") or "Interim filing"),
        source_url=latest.get("source_url"),
        fiscal_year=int(latest.get("fy") or str(latest["end"])[:4]),
        end=latest["end"],
        components=(_Component(latest["start"], latest["end"], factor),),
        revenue=float(latest["val"]) * factor,
        previous_revenue=prior_value,
        limited_history=True,
    )


def _flow_for_basis(rows: list[dict[str, Any]], basis: _Basis) -> float | None:
    total = 0.0
    for component in basis.components:
        row = _best(row for row in rows if row.get("start") == component.start and row.get("end") == component.end)
        if not row:
            return None
        total += float(row["val"]) * component.coefficient
    return total


def _latest_at_or_before(rows: list[dict[str, Any]], end: str) -> float | None:
    eligible = [row for row in rows if row.get("end", "") <= end and row.get("val") is not None]
    if not eligible:
        return None
    latest_end = max(row["end"] for row in eligible)
    row = _best(item for item in eligible if item["end"] == latest_end)
    return float(row["val"]) if row else None


def extract_financials(facts: dict[str, Any], inline_documents: list[InlineDocument] | None = None) -> tuple[Financials, float | None]:
    inline_rows = extract_inline_document_set(inline_documents or [])
    revenue_rows = _field_rows(facts, inline_rows, "revenue", "USD")
    basis = _select_basis(revenue_rows)

    def flow(field: str) -> float | None:
        return _flow_for_basis(_field_rows(facts, inline_rows, field, "USD"), basis)

    gross_profit = flow("gross_profit")
    operating_income = flow("operating_income")
    net_income = flow("net_income")
    operating_cash = flow("operating_cash")
    capex = flow("capex")
    cash_rows = _field_rows(facts, inline_rows, "cash", "USD")
    debt_current_rows = _field_rows(facts, inline_rows, "debt_current", "USD")
    debt_long_rows = _field_rows(facts, inline_rows, "debt_long", "USD")
    shares_rows = _field_rows(facts, inline_rows, "shares", "shares")

    cash = _latest_at_or_before(cash_rows, basis.end)
    debt_current = _latest_at_or_before(debt_current_rows, basis.end) or 0
    debt_long = _latest_at_or_before(debt_long_rows, basis.end) or 0
    latest_share_end = max((row.get("end", "") for row in shares_rows), default="")
    share_candidates = [row for row in shares_rows if row.get("end") == latest_share_end]
    consolidated_shares = _best(row for row in share_candidates if not row.get("dimensional"))
    if consolidated_shares:
        shares = float(consolidated_shares["val"])
    elif share_candidates:
        latest_filed = max(row.get("filed", "") for row in share_candidates)
        deduped = {
            (row.get("context_id") or str(row.get("segment")), float(row["val"])): float(row["val"])
            for row in share_candidates if row.get("filed", "") == latest_filed
        }
        shares = sum(deduped.values()) or None
    else:
        shares = None
    free_cash_flow = operating_cash - capex if operating_cash is not None and capex is not None else None

    financials = Financials(
        fiscal_year=basis.fiscal_year,
        period_end=basis.end,
        basis=basis.kind,
        basis_label=basis.label,
        source_form=basis.source_form,
        source_url=basis.source_url,
        limited_history=basis.limited_history,
        revenue=basis.revenue,
        revenue_growth=safe_div(basis.revenue - basis.previous_revenue, basis.previous_revenue) if basis.previous_revenue is not None else None,
        gross_margin=safe_div(gross_profit, basis.revenue),
        operating_margin=safe_div(operating_income, basis.revenue),
        net_margin=safe_div(net_income, basis.revenue),
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
