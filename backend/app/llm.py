from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any

import httpx

from .settings import load_local_env
from .security import PUBLIC_RESEARCH_MODEL_BOUNDARY, validate_model_endpoint


load_local_env()


@dataclass(frozen=True)
class TokenUsage:
    input_tokens: int = 0
    output_tokens: int = 0

    def __add__(self, other: "TokenUsage") -> "TokenUsage":
        return TokenUsage(
            input_tokens=self.input_tokens + other.input_tokens,
            output_tokens=self.output_tokens + other.output_tokens,
        )


class ModelError(RuntimeError):
    pass


class ModelClient:
    """Small OpenAI-compatible chat client used only for peer choice and prose."""

    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.model = os.getenv("OPENAI_MODEL", "gpt-5-mini").strip() or "gpt-5-mini"
        self.base_url = validate_model_endpoint(os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"))
        self.provider = os.getenv("MODEL_PROVIDER", "OpenAI-compatible").strip() or "OpenAI-compatible"

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    async def complete_json(self, *, system: str, user: dict[str, Any]) -> tuple[dict[str, Any], TokenUsage]:
        if not self.enabled:
            raise ModelError("No OPENAI_API_KEY is configured.")
        PUBLIC_RESEARCH_MODEL_BOUNDARY.enforce()

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": json.dumps(user, separators=(",", ":"), ensure_ascii=False)},
            ],
        }
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        try:
            async with httpx.AsyncClient(timeout=45, follow_redirects=True) as client:
                response = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
        except httpx.HTTPError as exc:
            raise ModelError(f"Model provider could not be reached: {exc}") from exc

        if response.status_code >= 400:
            raise ModelError(
                f"Model provider returned HTTP {response.status_code}. Check the configured key, model name, and account credits."
            )

        try:
            body = response.json()
            content = body["choices"][0]["message"]["content"]
            if not isinstance(content, str):
                raise TypeError("message content was not text")
            cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip(), flags=re.IGNORECASE)
            result = json.loads(cleaned)
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise ModelError("Model provider did not return the requested JSON object.") from exc

        if not isinstance(result, dict):
            raise ModelError("Model provider returned JSON, but it was not an object.")

        usage = body.get("usage") or {}
        return result, TokenUsage(
            input_tokens=int(usage.get("prompt_tokens") or usage.get("input_tokens") or 0),
            output_tokens=int(usage.get("completion_tokens") or usage.get("output_tokens") or 0),
        )

    async def choose_peers(self, *, ticker: str, company_name: str, sic: str, sic_description: str) -> tuple[list[str], TokenUsage]:
        result, usage = await self.complete_json(
            system=(
                "You select public-company comparables for a financial research workflow. Return JSON only as "
                '{"peers":["TICKER1","TICKER2"]}. Choose exactly two actively traded U.S. operating companies '
                "with similar products, customers, and economics. Do not include the subject, ETFs, funds, indexes, "
                "or private companies. Do not add commentary."
            ),
            user={"ticker": ticker, "company_name": company_name, "sec_sic": sic, "sec_industry": sic_description},
        )
        peers = normalize_peer_tickers(result.get("peers"), exclude=ticker)
        if len(peers) < 2:
            raise ModelError("Model did not return two usable peer tickers.")
        return peers[:2], usage

    async def write_memo(self, context: dict[str, Any]) -> tuple[dict[str, Any], TokenUsage]:
        result, usage = await self.complete_json(
            system=(
                "You write concise public-equity research prose from a closed JSON evidence set. Return JSON only "
                'with keys "summary" (string), "thesis" (array of exactly four strings), and "risks" (array of '
                "exactly four strings). Never change the supplied verdict, calculate new numbers, invent events, "
                "or claim to have read filing text. Use only supplied facts. Frame unsupported industry concerns as "
                "questions to verify in the cited filing. Avoid investment instructions and price targets."
            ),
            user=context,
        )
        summary = result.get("summary")
        thesis = result.get("thesis")
        risks = result.get("risks")
        if not isinstance(summary, str) or not summary.strip():
            raise ModelError("Model memo omitted its summary.")
        if not isinstance(thesis, list) or len(thesis) != 4 or not all(isinstance(item, str) and item.strip() for item in thesis):
            raise ModelError("Model memo must contain exactly four thesis statements.")
        if not isinstance(risks, list) or len(risks) != 4 or not all(isinstance(item, str) and item.strip() for item in risks):
            raise ModelError("Model memo must contain exactly four risk statements.")
        return {"summary": summary.strip(), "thesis": [item.strip() for item in thesis], "risks": [item.strip() for item in risks]}, usage


def normalize_peer_tickers(value: Any, *, exclude: str) -> list[str]:
    if not isinstance(value, list):
        return []
    normalized: list[str] = []
    for item in value:
        ticker = str(item).strip().upper()
        if not re.fullmatch(r"[A-Z][A-Z0-9.-]{0,7}", ticker) or ticker == exclude.upper() or ticker in normalized:
            continue
        normalized.append(ticker)
    return normalized
