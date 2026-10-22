from __future__ import annotations

import asyncio
import os
import time
from datetime import UTC, datetime
from typing import Any

import httpx

from .inline_xbrl import InlineDocument
from .settings import load_local_env


load_local_env()


SEC_BASE = "https://data.sec.gov"
SEC_WWW = "https://www.sec.gov"
YAHOO_BASE = "https://query1.finance.yahoo.com"

_COMPANY_INDEX_TTL_SECONDS = 6 * 60 * 60
_company_index: dict[str, dict[str, Any]] | None = None
_company_index_loaded_at = 0.0
_company_index_lock = asyncio.Lock()


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

    async def _text(self, url: str) -> str:
        response = await self.client.get(url)
        if response.status_code >= 400:
            raise DataProviderError(f"{url} returned HTTP {response.status_code}")
        return response.text

    async def resolve_company(self, ticker: str) -> dict[str, Any]:
        global _company_index, _company_index_loaded_at
        now = time.monotonic()
        if _company_index is None or now - _company_index_loaded_at >= _COMPANY_INDEX_TTL_SECONDS:
            async with _company_index_lock:
                now = time.monotonic()
                if _company_index is None or now - _company_index_loaded_at >= _COMPANY_INDEX_TTL_SECONDS:
                    data = await self._json(f"{SEC_WWW}/files/company_tickers.json")
                    _company_index = {
                        str(row.get("ticker", "")).upper(): row
                        for row in data.values()
                        if row.get("ticker")
                    }
                    _company_index_loaded_at = now
        match = _company_index.get(ticker.upper()) if _company_index else None
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

    async def financial_documents(self, cik: str, submissions: dict[str, Any]) -> list[InlineDocument]:
        """Fetch a bounded set of SEC financial filings for Company Facts fallback parsing."""
        recent = submissions.get("filings", {}).get("recent", {})
        rows: list[dict[str, str]] = []
        for index, form in enumerate(recent.get("form", [])):
            if form not in {"10-K", "10-Q", "20-F", "40-F", "6-K", "S-1", "S-1/A", "F-1", "F-1/A", "424B3", "424B4"}:
                continue
            rows.append(
                {
                    "form": form,
                    "filed": recent["filingDate"][index],
                    "accession": recent["accessionNumber"][index],
                    "primary": recent["primaryDocument"][index],
                }
            )

        selected: list[dict[str, str]] = []
        groups = [
            ({"10-K", "20-F", "40-F"}, 2),
            ({"10-Q"}, 2),
            ({"6-K"}, 4),
            ({"424B3", "424B4"}, 2),
            ({"S-1", "S-1/A", "F-1", "F-1/A"}, 2),
        ]
        for forms, limit in groups:
            selected.extend([row for row in rows if row["form"] in forms][:limit])

        unique: list[dict[str, str]] = []
        seen_accessions: set[str] = set()
        for row in selected:
            if row["accession"] not in seen_accessions:
                unique.append(row)
                seen_accessions.add(row["accession"])

        cik_plain = str(int(cik))
        documents: list[InlineDocument] = []
        for row in unique:
            accession_plain = row["accession"].replace("-", "")
            directory = f"https://www.sec.gov/Archives/edgar/data/{cik_plain}/{accession_plain}"
            try:
                index = await self._json(f"{directory}/index.json")
            except DataProviderError:
                continue
            names = [str(item.get("name", "")) for item in index.get("directory", {}).get("item", [])]
            extras = [
                name for name in names
                if name.lower().endswith((".htm", ".html"))
                and name != row["primary"]
                and any(marker in name.lower() for marker in ("_d2", "ex99", "exhibit99", "financial"))
            ]
            for name in [row["primary"], *extras[:2]]:
                if not name:
                    continue
                url = f"{directory}/{name}"
                try:
                    html = await self._text(url)
                except DataProviderError:
                    continue
                if "ix:nonfraction" not in html.lower():
                    continue
                documents.append(InlineDocument(form=row["form"], filed=row["filed"], url=url, html=html))
        return documents
