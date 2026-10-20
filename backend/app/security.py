from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse


class SecurityBoundaryError(RuntimeError):
    pass


@dataclass(frozen=True)
class AccessTriangle:
    """Enforce that an agent session never holds all three exfiltration capabilities."""

    untrusted_input: bool
    sensitive_data: bool
    external_egress: bool

    def enforce(self) -> None:
        enabled = sum((self.untrusted_input, self.sensitive_data, self.external_egress))
        if enabled > 2:
            raise SecurityBoundaryError(
                "Agent access boundary rejected: untrusted input, sensitive data, and external egress cannot coexist."
            )


PUBLIC_RESEARCH_MODEL_BOUNDARY = AccessTriangle(
    untrusted_input=True,
    sensitive_data=False,
    external_egress=True,
)


def validate_model_endpoint(base_url: str) -> str:
    parsed = urlparse(base_url)
    local_hosts = {"localhost", "127.0.0.1", "::1"}
    if parsed.scheme not in {"https", "http"} or not parsed.hostname:
        raise SecurityBoundaryError("OPENAI_BASE_URL must be an absolute HTTP(S) URL.")
    if parsed.scheme != "https" and parsed.hostname not in local_hosts:
        raise SecurityBoundaryError("Remote model endpoints must use HTTPS.")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise SecurityBoundaryError("OPENAI_BASE_URL cannot contain credentials, a query string, or a fragment.")
    return base_url.rstrip("/")
