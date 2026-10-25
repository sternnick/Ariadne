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
                        "experience", "about you", "you have")


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


def _weight(line: str) -> str:
    low = line.lower()
    if any(cue in low for cue in NICE_CUES):
        return "nice"
    if any(cue in low for cue in MUST_CUES):
        return "must"
    return "unknown"


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
            weight = _weight(raw)
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
