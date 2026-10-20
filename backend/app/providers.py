from __future__ import annotations

import os
from datetime import UTC, datetime
from typing import Any

import httpx

from .settings import load_local_env


load_local_env()


SEC_BASE = "https://data.sec.gov"
SEC_WWW = "https://www.sec.gov"
YAHOO_BASE = "https://query1.finance.yahoo.com"


class DataProviderError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


class PublicDataClient:
    def __init__(self) -> None:
        identity = os.getenv("SEC_USER_AGENT", "Ledger Research research@example.com")
        self.client = httpx.AsyncClient(
            timeout=25,
            follow_redirects=True,
            headers={"User-Agent": identity, "Accept-Encoding": "gzip, deflate"},
        )

    async def close(self) -> None:
        await self.client.aclose()

    async def __aenter__(self) -> "PublicDataClient":
        return self

    async def __aexit__(self, exc_type, exc, traceback) -> None:
        await self.close()

    async def _json(self, url: str) -> dict[str, Any]:
        response = await self.client.get(url)
        if response.status_code >= 400:
            raise DataProviderError(f"{url} returned HTTP {response.status_code}")
        try:
            return response.json()
        except ValueError as exc:
            raise DataProviderError(f"{url} did not return JSON") from exc

    async def resolve_company(self, ticker: str) -> dict[str, Any]:
        data = await self._json(f"{SEC_WWW}/files/company_tickers.json")
        match = next((row for row in data.values() if row["ticker"].upper() == ticker.upper()), None)
        if not match:
            raise DataProviderError(f"Ticker {ticker} was not found in the SEC company index.")
        return {
            "ticker": match["ticker"].upper(),
            "name": match["title"],
            "cik": str(match["cik_str"]).zfill(10),
        }

    async def company_facts(self, cik: str) -> dict[str, Any]:
        return await self._json(f"{SEC_BASE}/api/xbrl/companyfacts/CIK{cik}.json")

    async def submissions(self, cik: str) -> dict[str, Any]:
        return await self._json(f"{SEC_BASE}/submissions/CIK{cik}.json")

    async def market_chart(self, ticker: str) -> dict[str, Any]:
        url = f"{YAHOO_BASE}/v8/finance/chart/{ticker}?range=1y&interval=1d&events=div%2Csplits"
        return await self._json(url)
