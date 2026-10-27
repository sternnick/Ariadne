"""Job-description model: requirements, extracted deterministically.

A JD is not a document to be judged; it is a **list of asks**. This module turns prose into a list of
requirements with spans and confidence, so that A3 can map each one to evidence (or to `not_applicable`)
instead of diffing two blobs of text.

Extraction rules are deliberately lexical and boring:

* a bullet/line is a requirement if it contains a modal of obligation ("must", "required", "essential")
  or sits under a requirements-style heading;
* a line is *preferred* if it contains "nice to have", "preferred", "plus", "bonus";
* a skill term is any comma/slash-separated item in a requirements bullet, kept verbatim.

Nothing is inferred about the candidate. Nothing is inferred about the employer beyond the words they
wrote. There is no seniority model, no culture model, and no scoring here — that is A2/A3, and the
constraints on it live in `docs/03` and `AGENT_CONTRACT` C9.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field

from .errors import Code, ParseReport, Severity
from .segment import segment
from .textutil import normalize

MUST_CUES = ("must", "required", "requirement", "essential", "you have", "you will need", "minimum")
NICE_CUES = ("nice to have", "preferred", "bonus", "plus", "desirable", "advantageous")
REQUIREMENT_HEADINGS = ("requirements", "qualifications", "what you", "must have", "skills",
                        "experience", "about you", "you have", "nice to have", "benefits")

# A cue inside a negation is not evidence of a requirement. "A degree is not required" contains the
# cue word `required`, and until 2026-10-27 it was classified `must` — measured, not theorised, by
# data/gold/jd-02-negations.txt. The mask covers the words between the negator and the cue so
# "No prior fintech experience required" is caught as well as "is not required".
_NEGATED_CUE_RE = re.compile(
    r"\b(?:not|no|never|without|nor)\b[\w'\s]{0,28}?\b(?:must|required|requirement|essential|"
    r"necessary|experience)\b",
    re.I,
)


@dataclass
class Requirement:
    id: str
    text: str
    weight: str          # "must" | "nice" | "unknown"
    section: str
    span: tuple[int, int]
    confidence: float

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "text": self.text,
            "weight": self.weight,
            "section": self.section,
            "span": {"start": self.span[0], "end": self.span[1]},
            "confidence": round(self.confidence, 3),
        }


@dataclass
class JobDescription:
    requirements: list[Requirement] = field(default_factory=list)
    text: str = ""
    surface_hash: str = ""
    issue_codes: list[str] = field(default_factory=list)
    source: str = ""

    def to_jd_json(self) -> dict:
        return {
            "$schema": "https://ariadne.local/schemas/jd.schema.json",
            "requirements": [r.as_dict() for r in self.requirements],
            "custom": {
                "ariadne.provenance": {
                    "schemaVersion": "1.0.0",
                    "source": self.source,
                    "surfaceHash": self.surface_hash,
                    "counts": {
                        "must": sum(1 for r in self.requirements if r.weight == "must"),
                        "nice": sum(1 for r in self.requirements if r.weight == "nice"),
                        "unknown": sum(1 for r in self.requirements if r.weight == "unknown"),
                    },
                    "issues": self.issue_codes,
                }
            },
        }


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _cue_evidence(line: str) -> tuple[bool, bool, bool]:
    """(unnegated must cue?, unnegated nice cue?, any cue appeared negated?)."""
    low = line.lower()
    masked = _NEGATED_CUE_RE.sub(lambda m: " " * len(m.group(0)), low)
    must = any(c in masked for c in MUST_CUES)
    nice = any(c in masked for c in NICE_CUES)
    return must, nice, bool(_NEGATED_CUE_RE.search(low))


def _weight(line: str) -> tuple[str, str]:
    """Weight the line, plus the reason when the reason is 'we could not tell'.

    Two cues of different families in one sentence, or a cue the sentence then denies, is a
    contradiction, and the answer to a contradiction is `unknown` — not whichever cue the loop happened
    to test first. Until 2026-10-27 `NICE_CUES` were tested first, so "SQL is desirable but required"
    silently became `nice` and "is required, though not essential" became `must`; `jd-03-conflicts.txt`
    is the labelled case.
    """
    must, nice, negated = _cue_evidence(line)
    if must and nice:
        return "unknown", "contradictory cues"
    if negated:
        return "unknown", "negated cue"
    if must:
        return "must", ""
    if nice:
        return "nice", ""
    return "unknown", "no cue"


def build_jd(text: str, source: str = "", report: ParseReport | None = None) -> JobDescription:
    report = report or ParseReport()
    norm = normalize(text)
    sections = segment(norm, report)
    out: list[Requirement] = []
    seen: set[str] = set()

    for sec in sections:
        in_req_section = any(h in sec.heading.lower() for h in REQUIREMENT_HEADINGS) or sec.kind in (
            "skills", "experience")
        for line in sec.body.split("\n"):
            raw = line.strip(" \t*-")
            if len(raw) < 12:
                continue
            if raw.isupper() and len(raw.split()) <= 4:
                continue        # a short ALL-CAPS line is a section label, not an ask (jd-01)
            weight, reason = _weight(raw)
            if reason == "contradictory cues":
                report.add(Code.REQUIREMENT_AMBIGUOUS_CUES, Severity.NOTE,
                           f"'{raw[:60]}' carries both obligation and preference cues; weight left "
                           "unknown rather than resolved by evaluation order")
            elif reason == "negated cue":
                report.add(Code.REQUIREMENT_NEGATED_CUE, Severity.NOTE,
                           f"'{raw[:60]}' denies a requirement cue; weight left unknown")
            if weight == "unknown" and not in_req_section:
                continue
            rid = _sha(re.sub(r"\s+", " ", raw.lower()))[:12]
            if rid in seen:
                continue
            seen.add(rid)
            idx = norm.find(raw)
            out.append(Requirement(rid, raw, weight, sec.kind, (max(0, idx), max(0, idx) + len(raw)),
                                   sec.confidence * (1.0 if weight != "unknown" else 0.7)))

    if not out:
        report.add(Code.NO_SECTIONS_FOUND, Severity.DEGRADED,
                   "no requirement-shaped lines found; the JD may not use obligation language")
    return JobDescription(out, norm, _sha(text), report.codes(), source)


__all__ = ["Requirement", "JobDescription", "build_jd"]
