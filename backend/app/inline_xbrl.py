from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from html.parser import HTMLParser
from typing import Any


@dataclass(frozen=True)
class InlineDocument:
    form: str
    filed: str
    url: str
    html: str


@dataclass
class _Context:
    identifier: str
    start: str | None = None
    end: str | None = None
    instant: str | None = None
    dimensional: bool = False


class _InlineParser(HTMLParser):
    """Extract consolidated numeric facts from an SEC inline-XBRL document."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.contexts: dict[str, _Context] = {}
        self.facts: list[dict[str, Any]] = []
        self._context: _Context | None = None
        self._context_field: str | None = None
        self._context_text: list[str] = []
        self._fact: dict[str, Any] | None = None
        self._fact_text: list[str] = []
        self._exclude_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        values = {key.lower(): value for key, value in attrs}
        if tag == "xbrli:context":
            identifier = values.get("id")
            if identifier:
                self._context = _Context(identifier=identifier)
        elif self._context and tag in {"xbrli:startdate", "xbrli:enddate", "xbrli:instant"}:
            self._context_field = tag.split(":", 1)[1]
            self._context_text = []
        elif self._context and tag in {"xbrldi:explicitmember", "xbrldi:typedmember"}:
            self._context.dimensional = True

        if tag == "ix:nonfraction":
            self._fact = values
            self._fact_text = []
        elif self._fact and tag == "ix:exclude":
            self._exclude_depth += 1

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if self._context and self._context_field and tag == f"xbrli:{self._context_field}":
            value = "".join(self._context_text).strip()
            if self._context_field == "startdate":
                self._context.start = value
            elif self._context_field == "enddate":
                self._context.end = value
            else:
                self._context.instant = value
            self._context_field = None
            self._context_text = []
        elif self._context and tag == "xbrli:context":
            self.contexts[self._context.identifier] = self._context
            self._context = None

        if self._fact and tag == "ix:exclude":
            self._exclude_depth = max(0, self._exclude_depth - 1)
        elif self._fact and tag == "ix:nonfraction":
            self._fact["text"] = "".join(self._fact_text).strip()
            self.facts.append(self._fact)
            self._fact = None
            self._fact_text = []
            self._exclude_depth = 0

    def handle_data(self, data: str) -> None:
        if self._context and self._context_field:
            self._context_text.append(data)
        if self._fact and not self._exclude_depth:
            self._fact_text.append(data)


def _numeric_value(text: str, *, scale: str | None, sign: str | None) -> float | None:
    normalized = text.replace("\u2212", "-").replace("\u2014", "").strip()
    negative = normalized.startswith("(") and normalized.endswith(")")
    normalized = re.sub(r"[^0-9.\-]", "", normalized)
    if normalized in {"", "-", "."}:
        return None
    try:
        value = float(normalized)
        if scale:
            value *= 10 ** int(scale)
        if sign == "-" or negative:
            value = -abs(value)
        return value
    except (ValueError, OverflowError):
        return None


def _rows_from_parser(
    parser: _InlineParser,
    document: InlineDocument,
    contexts: dict[str, _Context],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for fact in parser.facts:
        if str(fact.get("xsi:nil", "")).lower() == "true":
            continue
        context = contexts.get(str(fact.get("contextref", "")))
        if not context:
            continue
        value = _numeric_value(
            str(fact.get("text", "")),
            scale=fact.get("scale"),
            sign=fact.get("sign"),
        )
        if value is None:
            continue
        name = str(fact.get("name", ""))
        namespace, _, tag = name.partition(":")
        end = context.end or context.instant
        if not tag or not end:
            continue
        try:
            date.fromisoformat(end)
        except ValueError:
            continue
        rows.append(
            {
                "namespace": namespace,
                "tag": tag,
                "unit": str(fact.get("unitref", "")),
                "form": document.form,
                "filed": document.filed,
                "start": context.start,
                "end": end,
                "val": value,
                "source_url": document.url,
                "context_id": context.identifier,
                "dimensional": context.dimensional,
            }
        )
    return rows


def extract_inline_facts(document: InlineDocument) -> list[dict[str, Any]]:
    parser = _InlineParser()
    parser.feed(document.html)
    return _rows_from_parser(parser, document, parser.contexts)


def extract_inline_document_set(documents: list[InlineDocument]) -> list[dict[str, Any]]:
    """Parse an inline-XBRL document set whose contexts may live in a different HTML file."""
    parsed: list[tuple[InlineDocument, _InlineParser]] = []
    contexts: dict[str, _Context] = {}
    for document in documents:
        parser = _InlineParser()
        parser.feed(document.html)
        contexts.update(parser.contexts)
        parsed.append((document, parser))
    return [row for document, parser in parsed for row in _rows_from_parser(parser, document, contexts)]
