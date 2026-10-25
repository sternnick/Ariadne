"""Section segmentation with a confidence value per section.

Fixes two measured defects from the audit in the same place they were found:

* **P5** — the old `detect_sections` kept only the *first* heading of each kind, so a CV with
  `SUMMARY / EXPERIENCE / SUMMARY` lost its second summary block silently. Here every heading starts a
  segment, repeats are recorded (`SECTION_REPEATED`), and nothing is discarded.
* **P4** — bullets are recognised from markers *or* from an achievement shape, because markers
  routinely disappear when a layout is flattened.

Confidence is a *judgement*, not a measurement, and says so: an exact vocabulary heading is 0.9, a
fuzzy heading 0.6, text before the first heading 0.5, a document with no headings 0.25. Each is
multiplied by the layout's reading-order confidence, because a segment cut from a flattened
two-column document is worth less even when its heading is perfect. There is no source that validates
these numbers; they are engineering defaults, and A2's stability work is what will calibrate them.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .errors import Code, ParseReport, Severity
from .textutil import SECTION_HEADINGS, normalize

_MARKERS = ("*", "-", "\u2022", "\u25cf", "\u25aa", "\u25e6", "\u00b7")
_ACHIEVEMENT_RE = re.compile(
    r"^(?:led|built|shipped|designed|reduced|increased|improved|delivered|managed|owned|created|"
    r"migrated|automated|launched|scaled|cut|saved|grew|ran|drove)\b", re.I)

EXACT_CONFIDENCE = 0.9
FUZZY_CONFIDENCE = 0.6
PREAMBLE_CONFIDENCE = 0.5
UNSTRUCTURED_CONFIDENCE = 0.25


@dataclass
class Section:
    kind: str            # canonical name: summary, skills, experience, education, projects, other
    heading: str         # the literal heading line, as extracted ("" for the preamble)
    body: str
    start: int           # character offset of the heading within the normalised text
    confidence: float
    bullets: list[str] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "kind": self.kind,
            "heading": self.heading,
            "chars": len(self.body),
            "start": self.start,
            "confidence": round(self.confidence, 3),
            "bullets": len(self.bullets),
            "issues": self.issues,
        }


def _classify(line: str) -> tuple[str | None, float]:
    """Return (canonical kind, base confidence) for a candidate heading line."""
    raw = line.strip()
    if not raw or len(raw) > 46:
        return None, 0.0
    plain = raw.strip(" :#*_-\t").lower()
    if not plain or len(plain.split()) > 4:
        return None, 0.0
    for kind, names in SECTION_HEADINGS.items():
        if plain in names:
            return kind, EXACT_CONFIDENCE
    if len(plain.split()) <= 3 and raw[:1].isupper():
        for kind, names in SECTION_HEADINGS.items():
            if any(w in plain for w in names if len(w) > 5):
                return kind, FUZZY_CONFIDENCE
    return None, 0.0


def bullets(body: str) -> list[str]:
    out: list[str] = []
    for line in body.split("\n"):
        s = line.strip()
        if not s:
            continue
        if s.startswith(_MARKERS):
            body_text = s.lstrip("".join(_MARKERS) + " ").strip()
            if len(body_text) > 8:
                out.append(body_text)
        elif _ACHIEVEMENT_RE.match(s) and len(s) > 20:
            # Marker lost in extraction but the shape is an achievement. Recorded, not invented.
            out.append(s)
    return out


def segment(text: str, report: ParseReport | None = None,
            reading_order_confidence: float = 1.0) -> list[Section]:
    report = report or ParseReport()
    text = normalize(text)
    lines = text.split("\n")

    heads: list[tuple[int, str, str, float]] = []  # (line index, kind, heading, base confidence)
    for i, line in enumerate(lines):
        kind, conf = _classify(line)
        if kind:
            heads.append((i, kind, line.strip(), conf))

    if not heads:
        report.add(Code.NO_SECTIONS_FOUND, Severity.DEGRADED,
                   "no heading matched the vocabulary; whole document treated as one block")
        return [Section("unstructured", "", text, 0, UNSTRUCTURED_CONFIDENCE * reading_order_confidence,
                        bullets(text), ["NO_SECTIONS_FOUND"])]

    sections: list[Section] = []
    if heads[0][0] > 0:
        pre = "\n".join(lines[:heads[0][0]]).strip()
        if pre:
            sections.append(Section("preamble", "", pre, 0,
                                    PREAMBLE_CONFIDENCE * reading_order_confidence, bullets(pre)))

    seen: dict[str, int] = {}
    for n, (idx, kind, heading, base) in enumerate(heads):
        end = heads[n + 1][0] if n + 1 < len(heads) else len(lines)
        body = "\n".join(lines[idx + 1:end]).strip()
        start = len("\n".join(lines[:idx]))
        issues: list[str] = []
        conf = base * reading_order_confidence
        seen[kind] = seen.get(kind, 0) + 1
        if seen[kind] > 1:
            issues.append(Code.SECTION_REPEATED.value)
            conf *= 0.8
            report.add(Code.SECTION_REPEATED, Severity.NOTE,
                       f"heading '{heading}' repeats ({seen[kind]}×); each occurrence kept as its own segment")
        if base == FUZZY_CONFIDENCE:
            issues.append(Code.SECTION_AMBIGUOUS_HEADING.value)
            report.add(Code.SECTION_UNRECOGNISED, Severity.NOTE,
                       f"heading '{heading}' matched fuzzily; treated as {kind}")
        sections.append(Section(kind, heading, body, start, conf, bullets(body), issues))

    return sections
