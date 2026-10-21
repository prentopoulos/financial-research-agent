from __future__ import annotations

import re

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .chat import run_report_chat
from .explore import run_market_explore
from .llm import ModelError
from .models import ChatRequest, ChatResponse, ResearchReport
from .providers import DataProviderError
from .report_store import ReportStore
from .security import SecurityBoundaryError
from .workflow import run_research


app = FastAPI(title="Ledger Financial Research Agent", version="0.1.0")
report_store = ReportStore()
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
        report = await run_research(ticker)
        report_store.put(report)
        return report
    except DataProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Research run failed: {exc}") from exc


@app.post("/api/research/{run_id}/chat", response_model=ChatResponse)
async def chat(run_id: str, request: ChatRequest) -> ChatResponse:
    try:
        report = report_store.get_for_chat(run_id)
        return await run_report_chat(report, request)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="This report session expired. Run the ticker again to continue.") from exc
    except SecurityBoundaryError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ModelError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc


@app.post("/api/research/{run_id}/explore", response_model=ChatResponse)
async def explore(run_id: str, request: ChatRequest) -> ChatResponse:
    try:
        report = report_store.get_for_chat(run_id)
        return await run_market_explore(report, request)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="This report session expired. Run the ticker again to continue.") from exc
    except SecurityBoundaryError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ModelError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc


app.mount("/", StaticFiles(directory="dist", html=True, check_dir=False), name="web")
