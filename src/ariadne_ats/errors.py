"""Typed failures. A parser that cannot resolve a layout says so with a code, not a guess.

Every degradation is a `ParseIssue` with a machine-readable `Code` and a severity:

* `BLOCKING` — no usable document model was produced. The caller must not proceed.
* `DEGRADED` — a model was produced, but a named assumption was violated (e.g. columns were
  flattened). Downstream confidence must be reduced, and the caller must surface it.
* `NOTE`  — a transformation was applied and is recorded for audit (e.g. ligatures folded).

Why codes instead of exceptions for everything: a résumé that parsed *badly* is a useful result. The
distinction that matters to a user is "we could not read this" versus "we read it and it is damaged",
and both must be visible (AGENT_CONTRACT C7.7).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Code(str, Enum):
    OK = "OK"

    # input-level
    EMPTY_INPUT = "EMPTY_INPUT"
    UNSUPPORTED_FORMAT = "UNSUPPORTED_FORMAT"
    CORRUPT_DOCUMENT = "CORRUPT_DOCUMENT"

    # extraction
    PDF_BACKEND_MISSING = "PDF_BACKEND_MISSING"
    OCR_BACKEND_MISSING = "OCR_BACKEND_MISSING"
    NO_TEXT_LAYER = "NO_TEXT_LAYER"
    LOW_TEXT_YIELD = "LOW_TEXT_YIELD"

    # layout
    MULTICOLUMN_FLATTENED = "MULTICOLUMN_FLATTENED"
    TABLE_STRUCTURE = "TABLE_STRUCTURE"
    HEADER_FOOTER_BAND = "HEADER_FOOTER_BAND"
    LIGATURE_FOLDED = "LIGATURE_FOLDED"
    SOFT_HYPHEN_FOLDED = "SOFT_HYPHEN_FOLDED"

    # segmentation
    NO_SECTIONS_FOUND = "NO_SECTIONS_FOUND"
    SECTION_UNRECOGNISED = "SECTION_UNRECOGNISED"
    SECTION_REPEATED = "SECTION_REPEATED"
    SECTION_AMBIGUOUS_HEADING = "SECTION_AMBIGUOUS_HEADING"


class Severity(str, Enum):
    BLOCKING = "blocking"
    DEGRADED = "degraded"
    NOTE = "note"


@dataclass(frozen=True)
class ParseIssue:
    code: Code
    severity: Severity
    detail: str
    span: tuple[int, int] | None = None

    def as_dict(self) -> dict:
        d = {"code": self.code.value, "severity": self.severity.value, "detail": self.detail}
        if self.span:
            d["span"] = {"start": self.span[0], "end": self.span[1]}
        return d


class ParseFailure(Exception):
    """Raised only when no document model can be produced at all."""

    def __init__(self, issue: ParseIssue):
        super().__init__(f"{issue.code.value}: {issue.detail}")
        self.issue = issue

    @property
    def code(self) -> Code:
        return self.issue.code


@dataclass
class ParseReport:
    """Collected issues plus the counts a caller needs to judge the result."""

    issues: list[ParseIssue] = field(default_factory=list)

    def add(self, code: Code, severity: Severity, detail: str, span: tuple[int, int] | None = None) -> None:
        self.issues.append(ParseIssue(code, severity, detail, span))

    @property
    def blocking(self) -> list[ParseIssue]:
        return [i for i in self.issues if i.severity is Severity.BLOCKING]

    @property
    def degraded(self) -> list[ParseIssue]:
        return [i for i in self.issues if i.severity is Severity.DEGRADED]

    @property
    def ok(self) -> bool:
        return not self.blocking

    def codes(self) -> list[str]:
        return [i.code.value for i in self.issues]

    def as_list(self) -> list[dict]:
        return [i.as_dict() for i in self.issues]
