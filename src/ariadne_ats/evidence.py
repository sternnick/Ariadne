"""The evidence model: facts, spans, confidence, and the two hashes that make M-2 possible.

WHY TWO HASHES (Guard 2 — the design decision this module exists to carry)
--------------------------------------------------------------------------
A2 has to answer: *does the score move when only the presentation moves?* ([EV-02] measured a 29.6 %
reversal rate for this class of system). To measure that, the model must be able to say, mechanically,
**"these two documents carry the same competence and different surfaces."**

So every ledger carries two digests:

* `surface_hash` — a digest of the **raw text as it arrived**, before normalisation. It changes when
  anything changes: order, headings, markers, whitespace — and also glyph-level damage (a ligature, a
  soft hyphen) that normalisation repairs. That is deliberate: "what arrived" and "what it means" are
  different questions, and a model that hashed the *repaired* text could not tell a clean document
  from a damaged one that happened to repair cleanly.
* `competence_hash` — a digest of the **fact set only**: sorted `(kind, normalised_value)` pairs. It is
  order-insensitive and span-insensitive, so reordering sections, renaming `EXPERIENCE` to
  `WORK HISTORY`, or re-flowing a column leaves it identical.

A competence-preserving perturbation is therefore *defined*, not asserted: same `competence_hash`,
different `surface_hash`. `Ledger.delta()` reports exactly that, plus which fact ids appeared,
disappeared or changed value. If a perturbation was supposed to preserve competence and
`competence_changed` is True, the *fixture* is wrong — which is the failure mode that would otherwise
silently corrupt an A2 result.

What this model deliberately does NOT do
----------------------------------------
It stores facts the user's document asserts — employers, titles, dates, skills, bullets, numbers. It
does not infer traits, seniority, potential, demographics or any attribute of the person; that is
forbidden by `AGENT_CONTRACT` C9 and enforced by `tests/test_no_profiling.py`. Fit-to-JD scoring is a
comparison of *document* terms, not a profile (see the docstring of that test and `docs/09` §1.2).

Fact identity is content-derived, not positional: `id = sha1(kind + normalised value + occurrence)`.
A fact that moves keeps its id; a fact that changes value gets a new one, which is what makes the delta
trustworthy.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Iterable

from . import fields as _fields
from .errors import Code, ParseReport, Severity
from .segment import Section, segment
from .textutil import normalize

SCHEMA_VERSION = "1.7.0"

# Fact kinds are deliberately narrow and document-shaped: each one is something the document itself
# asserts, extracted by a named rule in `fields.py` or not emitted at all. `name` and `employer` were
# added 2026-10-27: the resume schema and `to_resume_json()` already named those fields while the
# ledger never produced them, which is how `basics.name` came to be a permanent empty string. The
# schema enum in schemas/resume.schema.json is the same list, and tests/test_schemas.py enforces it.
KINDS = ("contact", "name", "summary", "skill", "role", "employer", "date", "bullet",
         "education", "language", "other")

_NUMBER_RE = re.compile(r"\b\d+(?:[.,]\d+)?%?\b")
_YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")


def _sha(text: str, n: int = 16) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:n]


def _norm_value(value: str) -> str:
    """Normalise a fact value for identity and for the competence digest.

    Case, surrounding whitespace and runs of whitespace are ignored; nothing else is. That is
    deliberately conservative: over-normalising would make genuinely different facts collide, and a
    collision in `competence_hash` would make a real change look like a presentation change.
    """
    return re.sub(r"\s+", " ", value.strip().lower())


@dataclass(frozen=True)
class Fact:
    id: str
    kind: str
    value: str
    section: str
    span: tuple[int, int]
    confidence: float
    derived_from: str = "text"          # text | table-cell | bullet
    numbers: tuple[str, ...] = ()

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "kind": self.kind,
            "value": self.value,
            "section": self.section,
            "span": {"start": self.span[0], "end": self.span[1]},
            "confidence": round(self.confidence, 3),
            "derived_from": self.derived_from,
            "numbers": list(self.numbers),
        }


@dataclass
class LedgerDelta:
    added: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)
    changed: list[str] = field(default_factory=list)
    surface_changed: bool = False
    competence_changed: bool = False

    @property
    def competence_preserved(self) -> bool:
        return not self.competence_changed

    def as_dict(self) -> dict:
        return {
            "added": self.added,
            "removed": self.removed,
            "changed": self.changed,
            "surface_changed": self.surface_changed,
            "competence_changed": self.competence_changed,
            "competence_preserved": self.competence_preserved,
        }


@dataclass
class Ledger:
    facts: list[Fact] = field(default_factory=list)
    issues: list[dict] = field(default_factory=list)
    surface_hash: str = ""
    competence_hash: str = ""
    text: str = ""
    source: str = ""
    method: str = ""
    layout: dict = field(default_factory=dict)
    sections: list[dict] = field(default_factory=list)
    work: list[dict] = field(default_factory=list)
    basics: dict = field(default_factory=dict)
    perturbation_of: str | None = None

    # ---- construction -----------------------------------------------------------------------
    @classmethod
    def build(cls, text: str, sections: Iterable[Section], report: ParseReport,
              source: str = "", method: str = "", layout: dict | None = None,
              perturbation_of: str | None = None) -> "Ledger":
        norm = normalize(text)
        sec_list = list(sections)
        facts: list[Fact] = []
        counts: dict[tuple[str, str], int] = {}
        sec_dicts: list[dict] = []
        work: list[dict] = []
        basics: dict = {"name": ""}

        # The contact block is read first and is the ONLY place a contact may come from: an email
        # inside a REFERENCES block belongs to the reference (data/gold/cv-19 is that test).
        block = _fields.contact_block(sec_list)
        block_conf = min((s.confidence for s in sec_list
                          if s.kind in ("preamble", "contact", "unstructured")), default=0.5)
        if block:
            for hit in _fields.contacts(block, confidence=block_conf):
                facts.append(cls._fact("contact", hit.value, "contact", norm, counts, 0,
                                       hit.confidence, derived=hit.derived_from + ":" + hit.channel))
            name = _fields.person_name(block, confidence=block_conf)
            if name:
                facts.append(cls._fact("name", name.value, "contact", norm, counts, 0,
                                       name.confidence, derived=name.derived_from))
                basics["name"] = name.value
            for chan, key in (("email", "email"), ("phone", "phone"), ("url", "url")):
                vals = [f.value for f in facts
                        if f.kind == "contact" and f.derived_from.endswith(":" + chan)]
                if vals:
                    basics[key] = vals[0]
                    if chan == "url" and len(vals) > 1:
                        basics["profiles"] = [{"url": v} for v in vals[1:]]

        cursor = 0
        for sec in sec_list:
            sec_dicts.append(sec.as_dict())

            if sec.kind == "summary":
                s = _fields.summary_statement(sec_list, confidence=sec.confidence)
                if s and not any(f.kind == "summary" for f in facts):
                    facts.append(cls._fact("summary", s.value, sec.kind, norm, counts, cursor,
                                           s.confidence))
                    basics.setdefault("summary", s.value)

            roles: list[_fields.RoleHit] = []
            if sec.kind == "experience":
                roles = _fields.role_lines(sec.body, report, confidence=sec.confidence)
                for r in roles:
                    facts.append(cls._fact("role", r.title, sec.kind, norm, counts, cursor,
                                           sec.confidence, derived="role-line"))
                    facts.append(cls._fact("employer", r.employer, sec.kind, norm, counts, cursor,
                                           sec.confidence, derived="role-line"))

            for item in sec.bullets:
                facts.append(cls._fact("bullet", item, sec.kind, norm, counts, cursor, sec.confidence))
            if sec.kind == "skills":
                for item in re.split(r"[,;/|\t]|\n", sec.body):
                    item = item.strip(" \t*-\u00b7\u2022")
                    # The floor is about kind, not size: the skill "C" is one letter and has to
                    # survive. Audit P2 (the invisible "C") had recurred here, in a second function,
                    # and the gold set caught it on cv-10. A fragment with no letter in it is noise.
                    if 1 <= len(item) <= 60 and any(ch.isalpha() for ch in item):
                        facts.append(cls._fact("skill", item, sec.kind, norm, counts, cursor,
                                               sec.confidence))
            if sec.kind in ("experience", "education"):
                for line in sec.body.split("\n"):
                    for y in _YEAR_RE.findall(line):
                        facts.append(cls._fact("date", y, sec.kind, norm, counts, cursor, sec.confidence))

            if sec.kind == "experience":
                if roles:
                    for r in roles:
                        entry = {
                            "name": r.employer,
                            "position": r.title,
                            "highlights": list(r.bullets),
                            "custom": {"ariadne.factIds": [
                                f.id for f in facts
                                if f.kind in ("role", "employer")
                                and f.section == sec.kind and f.value in (r.title, r.employer)]},
                        }
                        if r.start:
                            entry["startDate"] = r.start.strip(" ./")
                        if r.end:
                            entry["endDate"] = r.end.strip(" ./")
                        work.append(entry)
                elif sec.bullets:
                    report.add(Code.ROLE_LINE_AMBIGUOUS, Severity.DEGRADED,
                               f"{len(sec.bullets)} bullet(s) under '{sec.heading or sec.kind}' with no "
                               "role line recognised; they stay facts but cannot be attached to an "
                               "employer")
                    work.append({"name": "", "position": "", "highlights": list(sec.bullets),
                                 "custom": {"ariadne.unassigned": True}})
            cursor += len(sec.body) + len(sec.heading) + 2

        seen: set[str] = set()
        uniq: list[Fact] = []
        for f in facts:
            if f.id in seen:
                continue
            seen.add(f.id)
            uniq.append(f)

        return cls(
            facts=uniq,
            issues=report.as_list(),
            surface_hash=_sha(text),
            competence_hash=cls._competence_digest(uniq),
            text=norm,
            source=source,
            method=method,
            layout=layout or {},
            sections=sec_dicts,
            work=work,
            basics=basics,
            perturbation_of=perturbation_of,
        )

    @staticmethod
    def _fact(kind: str, value: str, section: str, text: str, counts: dict, cursor: int,
              base_conf: float, derived: str = "") -> Fact:
        nv = _norm_value(value)
        key = (kind, nv)
        counts[key] = counts.get(key, 0) + 1
        fid = _sha(f"{kind}|{nv}|{counts[key]}")
        idx = text.lower().find(nv)
        span = (idx, idx + len(value)) if idx >= 0 else (cursor, cursor + len(value))
        numbers = tuple(_NUMBER_RE.findall(value))
        # A fact carrying numbers is more consequential (a wrong number is a false claim), so it takes
        # a 5 % penalty: under a degraded layout the number itself may be a merged-column artefact.
        # This is a heuristic about *consequence*, not a probability of being right — the measured
        # accuracy per field lives in data/gold/results.json, and the two must not be confused
        # (docs/05 5.1, docs/02 2.6).
        conf = base_conf if not numbers else round(base_conf * 0.95, 3)
        return Fact(fid, kind, value.strip(), section, span, conf,
                    derived or ("bullet" if kind == "bullet" else "text"), numbers)


    @staticmethod
    def _competence_digest(facts: Iterable[Fact]) -> str:
        pairs = sorted(f"{f.kind}|{_norm_value(f.value)}" for f in facts)
        return _sha("\n".join(pairs))

    # ---- comparison -------------------------------------------------------------------------
    def delta(self, other: "Ledger") -> LedgerDelta:
        mine = {f.id: _norm_value(f.value) for f in self.facts}
        theirs = {f.id: _norm_value(f.value) for f in other.facts}
        added = sorted(set(theirs) - set(mine))
        removed = sorted(set(mine) - set(theirs))
        changed = sorted(k for k in set(mine) & set(theirs) if mine[k] != theirs[k])
        return LedgerDelta(
            added=added,
            removed=removed,
            changed=changed,
            surface_changed=self.surface_hash != other.surface_hash,
            competence_changed=self.competence_hash != other.competence_hash,
        )

    # ---- serialisation ----------------------------------------------------------------------
    def to_resume_json(self, basics: dict | None = None) -> dict:
        """JSON Resume 1.7.0 shape, with provenance in the spec-sanctioned `custom` object.

        One `work[]` entry per recognised role line, each carrying its own highlights and its own
        dates. Before 2026-10-27 this function emitted exactly one work entry for every document,
        with `name` always `""`, `position` taken from the first role fact, and every skill in the
        document copied into that one entry's `keywords` - a three-employer CV rendered as one
        employer with no name. `work` is now built where the roles are recognised (`build`) and an
        empty `position` there is accompanied by a `ROLE_LINE_AMBIGUOUS` issue, never silent.
        """
        merged = dict(self.basics)
        if basics:
            merged.update(basics)
        return {
            "$schema": "https://raw.githubusercontent.com/jsonresume/resume-schema/v1.7.0/schema.json",
            "basics": merged,
            "work": [dict(w) for w in self.work],
            "skills": [{"name": x.value} for x in self.facts if x.kind == "skill"],
            "custom": {
                "ariadne.provenance": {
                    "schemaVersion": SCHEMA_VERSION,
                    "source": self.source,
                    "method": self.method,
                    "surfaceHash": self.surface_hash,
                    "competenceHash": self.competence_hash,
                    "perturbationOf": self.perturbation_of,
                    "layout": self.layout,
                    "sections": self.sections,
                    "issues": self.issues,
                    "facts": [x.as_dict() for x in self.facts],
                    "confidenceIsHeuristic": True,
                    "accuracySource": "data/gold/results.json",
                }
            },
        }

    def summary(self) -> dict:
        return {
            "source": self.source,
            "method": self.method,
            "facts": len(self.facts),
            "by_kind": {k: sum(1 for f in self.facts if f.kind == k) for k in KINDS if any(f.kind == k for f in self.facts)},
            "surface_hash": self.surface_hash,
            "competence_hash": self.competence_hash,
            "issues": [i["code"] for i in self.issues],
            "min_confidence": min((f.confidence for f in self.facts), default=0.0),
            "work_entries": len(self.work),
            "note": "confidence is a layout/section heuristic, not a measured probability; measured "
                    "field accuracy is in data/gold/results.json (docs/02 2.6)",
        }


def build_ledger(path: str, perturbation_of: str | None = None) -> Ledger:
    """Extract → analyse layout → segment → ledger. The one deterministic pipeline."""
    from pathlib import Path

    from .extract import extract
    from .layout import analyze

    ex = extract(path)
    report = ex.report
    layout_report, report = analyze(ex.text, report)
    sections = segment(ex.text, report, layout_report.reading_order_confidence)
    return Ledger.build(
        text=ex.text,
        sections=sections,
        report=report,
        source=str(Path(path).name),
        method=ex.method,
        layout=layout_report.as_dict(),
        perturbation_of=perturbation_of,
    )


__all__ = ["Fact", "Ledger", "LedgerDelta", "build_ledger", "SCHEMA_VERSION", "KINDS", "Code"]
