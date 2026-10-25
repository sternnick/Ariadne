"""Layout-damage detection: what the extraction destroyed, named and measured.

This is the module that makes the product's central claim testable. It never repairs layout — it
*reports* it, because a silent repair is how a two-column CV becomes a plausible-looking wrong
document. Every finding is a `ParseIssue` with a code.

Signals are read from the **raw** extraction, before `normalize()` collapses whitespace. That ordering
is the whole point: an earlier version of this codebase ran the multi-column detector on normalised
text, where tabs and multi-space runs no longer exist, so the detector could only ever answer "single
column" (audit P3). The detector and the normaliser must not disagree about what text is.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .errors import Code, ParseReport, Severity

_LIGATURES = "\ufb00\ufb01\ufb02\ufb03\ufb04\ufb05\ufb06"
_SOFT_HYPHEN = "\u00ad"
# Two runs of non-space text separated by a wide gap, or by a tab: a visual column boundary that
# survived extraction.
_SPLIT_RE = re.compile(r"\S(?:[^\t\n]{0,60}?)(?:\t| {3,})\S")
_TABLE_ROW_RE = re.compile(r"(?:\S(?:[^\t\n]{0,40}?)(?:\t| {3,})){2,}\S")

# A page header/footer repeats verbatim across pages; a body line does not.
MIN_REPEAT_PAGES = 2


@dataclass
class LayoutReport:
    columns_suspected: bool = False
    column_ratio: float = 0.0
    table_rows: int = 0
    header_footer_lines: list[str] = field(default_factory=list)
    ligatures_found: int = 0
    soft_hyphens_found: int = 0
    reading_order_confidence: float = 1.0

    def as_dict(self) -> dict:
        return {
            "columns_suspected": self.columns_suspected,
            "column_ratio": round(self.column_ratio, 3),
            "table_rows": self.table_rows,
            "header_footer_lines": self.header_footer_lines,
            "ligatures_found": self.ligatures_found,
            "soft_hyphens_found": self.soft_hyphens_found,
            "reading_order_confidence": round(self.reading_order_confidence, 3),
        }


def _split_lines(text: str) -> list[str]:
    return [ln for ln in text.split("\n") if ln.strip()]


def _header_footer_candidates(pages: list[list[str]]) -> list[str]:
    """Lines that appear on >= MIN_REPEAT_PAGES pages at the same edge position."""
    if len(pages) < MIN_REPEAT_PAGES:
        return []
    seen: dict[str, int] = {}
    for lines in pages:
        edges = lines[:2] + lines[-2:]
        for ln in edges:
            key = re.sub(r"\s+", " ", ln.strip())
            if 0 < len(key) <= 80:
                seen[key] = seen.get(key, 0) + 1
    return sorted(k for k, n in seen.items() if n >= MIN_REPEAT_PAGES)


def analyze(raw_text: str, report: ParseReport | None = None) -> tuple[LayoutReport, ParseReport]:
    """Inspect the raw extraction. Never mutates the text."""
    report = report or ParseReport()
    out = LayoutReport()
    lines = _split_lines(raw_text)

    if len(lines) >= 8:
        hits = sum(1 for ln in lines if _SPLIT_RE.search(ln))
        out.column_ratio = hits / len(lines)
        # 0.30 is a working threshold, not a measured constant: it is deliberately conservative so
        # that a false positive degrades confidence rather than blocking a parse.
        out.columns_suspected = out.column_ratio > 0.30
        if out.columns_suspected:
            out.reading_order_confidence -= 0.4
            report.add(Code.MULTICOLUMN_FLATTENED, Severity.DEGRADED,
                       f"{hits}/{len(lines)} lines ({out.column_ratio:.0%}) contain a wide gap or tab; "
                       "reading order is document order and may interleave columns")

    out.table_rows = sum(1 for ln in lines if _TABLE_ROW_RE.search(ln))
    if out.table_rows >= 3:
        out.reading_order_confidence -= 0.2
        report.add(Code.TABLE_STRUCTURE, Severity.DEGRADED,
                   f"{out.table_rows} row(s) look tabular; cell-to-field mapping is positional")

    pages = [p.split("\n") for p in raw_text.split("\f")]
    out.header_footer_lines = _header_footer_candidates(pages)
    if out.header_footer_lines:
        out.reading_order_confidence -= 0.2
        report.add(Code.HEADER_FOOTER_BAND, Severity.DEGRADED,
                   f"{len(out.header_footer_lines)} line(s) repeat at page edges: {out.header_footer_lines[:3]}")

    out.ligatures_found = sum(raw_text.count(ch) for ch in _LIGATURES)
    if out.ligatures_found:
        report.add(Code.LIGATURE_FOLDED, Severity.NOTE,
                   f"{out.ligatures_found} ligature glyph(s) present; folded to ASCII by normalize()")

    out.soft_hyphens_found = raw_text.count(_SOFT_HYPHEN)
    if out.soft_hyphens_found:
        report.add(Code.SOFT_HYPHEN_FOLDED, Severity.NOTE,
                   f"{out.soft_hyphens_found} soft hyphen(s) removed by normalize()")

    out.reading_order_confidence = max(0.05, min(1.0, out.reading_order_confidence))
    return out, report
