from __future__ import annotations

import re

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .models import ResearchReport
from .providers import DataProviderError
from .workflow import run_research


app = FastAPI(title="Ledger Financial Research Agent", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/research/{ticker}", response_model=ResearchReport)
async def research(ticker: str) -> ResearchReport:
    ticker = ticker.strip().upper()
    if not re.fullmatch(r"[A-Z][A-Z0-9.-]{0,7}", ticker):
        raise HTTPException(status_code=422, detail="Enter a valid SEC-listed ticker symbol.")
    try:
        return await run_research(ticker)
    except DataProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Research run failed: {exc}") from exc


app.mount("/", StaticFiles(directory="dist", html=True, check_dir=False), name="web")
