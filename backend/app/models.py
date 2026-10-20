from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class Citation(BaseModel):
    label: str
    url: str
    source: str
    retrieved_at: str


class Financials(BaseModel):
    fiscal_year: int
    period_end: str
    revenue: float | None = None
    revenue_growth: float | None = None
    gross_margin: float | None = None
    operating_margin: float | None = None
    net_margin: float | None = None
    free_cash_flow: float | None = None
    cash: float | None = None
    debt: float | None = None


class Valuation(BaseModel):
    price: float | None = None
    market_cap: float | None = None
    pe: float | None = None
    price_to_sales: float | None = None
    fcf_yield: float | None = None
    as_of: str


class Peer(BaseModel):
    ticker: str
    name: str
    price: float | None = None
    market_cap: float | None = None
    revenue_growth: float | None = None
    gross_margin: float | None = None
    pe: float | None = None
    price_to_sales: float | None = None
    fcf_yield: float | None = None


class TraceStep(BaseModel):
    name: str
    status: Literal["completed", "failed"]
    latency_ms: int = Field(ge=0)
    detail: str


class ModelRun(BaseModel):
    enabled: bool
    provider: str
    name: str
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    fallback_reason: str | None = None


class ResearchReport(BaseModel):
    run_id: str
    ticker: str
    company_name: str
    exchange: str
    generated_at: str
    verdict: Literal["Undervalued", "Fairly valued", "Expensive", "Insufficient evidence"]
    confidence: Literal["Low", "Moderate", "High"]
    summary: str
    thesis: list[str]
    risks: list[str]
    financials: Financials
    valuation: Valuation
    peers: list[Peer]
    citations: list[Citation]
    trace: list[TraceStep]
    model: ModelRun
    methodology: str
