from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from time import monotonic

from .models import ResearchReport


@dataclass
class ReportSession:
    report: ResearchReport
    expires_at: float
    chat_turns: int = 0


class ReportStore:
    """Small process-local store for public report runs; conversation text is never persisted."""

    def __init__(self, *, ttl_seconds: int = 1800, max_entries: int = 64, max_chat_turns: int = 24) -> None:
        self.ttl_seconds = ttl_seconds
        self.max_entries = max_entries
        self.max_chat_turns = max_chat_turns
        self._sessions: dict[str, ReportSession] = {}
        self._lock = RLock()

    def put(self, report: ResearchReport) -> None:
        now = monotonic()
        with self._lock:
            self._prune(now)
            if len(self._sessions) >= self.max_entries:
                oldest = min(self._sessions, key=lambda key: self._sessions[key].expires_at)
                self._sessions.pop(oldest, None)
            self._sessions[report.run_id] = ReportSession(report=report, expires_at=now + self.ttl_seconds)

    def get_for_chat(self, run_id: str) -> ResearchReport:
        now = monotonic()
        with self._lock:
            self._prune(now)
            session = self._sessions.get(run_id)
            if session is None:
                raise KeyError(run_id)
            if session.chat_turns >= self.max_chat_turns:
                raise RuntimeError("This report reached its 24-question session limit. Run the ticker again to start a new session.")
            session.chat_turns += 1
            return session.report

    def _prune(self, now: float) -> None:
        expired = [run_id for run_id, session in self._sessions.items() if session.expires_at <= now]
        for run_id in expired:
            self._sessions.pop(run_id, None)
