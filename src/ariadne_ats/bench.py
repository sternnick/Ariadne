"""Measurement: field accuracy against `data/gold/`, and stability under perturbation.

This module exists because the repository had eight documentation gates and no number. A green CI run
proved that claims were dated and linked; it proved nothing about whether the parser reads a CV. The
unknowns this closes are M-1 (field-level parse quality) and the measurable half of M-2 (stability of
the comparative number under presentation-only change), both in docs/08 §8.3.

WHAT IS COUNTED (the definition is the claim, so it is here in words)
--------------------------------------------------------------------
* A value counts as **extracted** when its normalised form (NFKC, casefold, whitespace collapsed,
  surrounding punctuation stripped) equals the normalised expected form. Set semantics: a value is
  extracted or it is not; emitting it twice does not score twice, and `data/gold` says so in
  `matching_rule`.
* **precision** = TP / (TP + FP) and **recall** = TP / (TP + FN), micro-averaged over every fixture
  that contributes to the field. A fixture with no expected value for a field contributes nothing
  *unless* the parser emits something there, in which case every emission is a false positive: that
  is what makes an abstention rule falsifiable instead of free.
* **forbidden** values are labelled cases where emitting anything is wrong (a reference's email, a
  year inside prose, an employer named in a bullet). They are counted separately from FP because they
  are a different kind of failure: not "we missed it" but "we invented it".
* **stability**: for each fixture and each transform in `perturb.TRANSFORMS`, the same ledger is
  rebuilt from the perturbed text. Three things are reported, never blended into one number:
  whether competence was actually preserved (a broken fixture, not a broken parser), the fact-level
  Jaccard retention, and the **ranking inversion rate**: the share of fixture pairs whose order by
  cosine against one fixed advertisement flips. The inversion rate is the figure comparable to the
  29.6 % matched-pair reversal rate in [EV-02]; it is not the same experiment.

What this module must never do: turn `confidence` into an accuracy claim. `Fact.confidence` is a
heuristic about section and layout quality; the measured accuracy per field is this file's output, and
the two are kept in separate places on purpose.
"""
from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

from .evidence import Ledger, build_ledger
from .jd import build_jd
from .lexical import Tfidf
from .perturb import TRANSFORMS

ROOT = Path(__file__).resolve().parent.parent.parent
GOLD = ROOT / "data" / "gold"

# The gold manifest names fields; the ledger names fact kinds. One place maps them.
FIELD_KIND = {"employer": "employer", "title": "role", "date": "date", "skill": "skill",
              "contact": "contact", "name": "name"}
FIELDS = list(FIELD_KIND)

# CLI-level stop list for the stability cosine, so "the/and/of" do not carry a ranking.
_STOP = set("""a an and are as at be been but by for from has have he her his i if in into is it its
of on or our she that the their them then there these they this to was we were what when which who
will with you your""".split())

_PUNCT = " \t\r\n.,;:|-/()\u2019'\"\u2013\u2014[]{}"


def norm_value(value: str) -> str:
    """The matching rule, in one function so the scorer and the manifest cannot disagree."""
    v = unicodedata.normalize("NFKC", value).casefold()
    v = re.sub(r"\s+", " ", v).strip(_PUNCT)
    return v.strip()


@dataclass
class FieldScore:
    tp: int = 0
    fp: int = 0
    fn: int = 0
    fixtures: int = 0
    exact: int = 0
    forbidden: int = 0
    misses: list[str] = field(default_factory=list)
    extras: list[str] = field(default_factory=list)

    @property
    def precision(self) -> float:
        return round(self.tp / (self.tp + self.fp), 3) if (self.tp + self.fp) else 1.0

    @property
    def recall(self) -> float:
        return round(self.tp / (self.tp + self.fn), 3) if (self.tp + self.fn) else 1.0

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return round(2 * p * r / (p + r), 3) if (p + r) else 0.0

    def as_dict(self) -> dict:
        return {"tp": self.tp, "fp": self.fp, "fn": self.fn, "fixtures": self.fixtures,
                "exact_match_fixtures": self.exact, "forbidden_violations": self.forbidden,
                "precision": self.precision, "recall": self.recall, "f1": self.f1,
                "misses": self.misses[:40], "extras": self.extras[:40]}


def load_manifest(path: Path | None = None) -> dict:
    return json.loads((path or (GOLD / "manifest.json")).read_text(encoding="utf-8"))


def validate_manifest(manifest: dict, gold_dir: Path | None = None) -> list[str]:
    """Annotation integrity: every labelled value must actually be in the file it labels.

    An expected value that does not occur in the fixture is a transcription error in the manifest, and
    a forbidden value that does not occur tests nothing at all. Both are silent, so they are checked
    rather than trusted. This is what would have caught the Greek typo in the first annotation pass.
    """
    gold_dir = gold_dir or GOLD
    problems: list[str] = []
    for fx in manifest["fixtures"]:
        path = gold_dir / fx["file"]
        if not path.is_file():
            problems.append(f"{fx['id']}: missing fixture {fx['file']}")
            continue
        text = norm_value(path.read_text(encoding="utf-8", errors="replace"))
        for field_name, values in fx.get("expect", {}).items():
            if field_name not in FIELDS:
                problems.append(f"{fx['id']}: unknown field '{field_name}'")
            for v in values:
                if norm_value(v) not in text:
                    problems.append(f"{fx['id']}.{field_name}: expected value {v!r} is not in the fixture text")
        for field_name, values in fx.get("forbid", {}).items():
            for v in values:
                if norm_value(v) not in text:
                    problems.append(f"{fx['id']}.forbid.{field_name}: {v!r} does not occur in the "
                                    "fixture, so forbidding it tests nothing")
    for fx in manifest.get("job_descriptions", []):
        if not (gold_dir / fx["file"]).is_file():
            problems.append(f"{fx['id']}: missing fixture {fx['file']}")
    return problems


def emitted_fields(ledger: Ledger) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {k: set() for k in FIELDS}
    for f in ledger.facts:
        for field_name, kind in FIELD_KIND.items():
            if f.kind == kind:
                out[field_name].add(norm_value(f.value))
    return out


def score_corpus(manifest: dict | None = None, gold_dir: Path | None = None) -> dict:
    """Per-field accuracy, per-fixture detail, forbidden-emission report, and per-language recall."""
    manifest = manifest or load_manifest(gold_dir and None)
    gold_dir = gold_dir or GOLD
    scores = {k: FieldScore() for k in FIELDS}
    per_fixture: list[dict] = []
    by_language: dict[str, dict[str, FieldScore]] = {}
    violations: list[str] = []

    for fx in manifest["fixtures"]:
        ledger = build_ledger(gold_dir / fx["file"])
        got = emitted_fields(ledger)
        row: dict[str, object] = {"id": fx["id"], "language": fx["language"], "fields": {}}
        lang = by_language.setdefault(fx["language"], {k: FieldScore() for k in FIELDS})
        for field_name in FIELDS:
            expected = {norm_value(v) for v in fx.get("expect", {}).get(field_name, [])}
            forbidden = {norm_value(v) for v in fx.get("forbid", {}).get(field_name, [])}
            actual = got[field_name]
            hits = expected & actual
            extra = actual - expected
            bad = actual & forbidden
            for bucket in (scores[field_name], lang[field_name]):
                counted = bool(expected) or bool(actual)
                if counted:
                    bucket.fixtures += 1
                    bucket.exact += 1 if actual == expected else 0
                bucket.tp += len(hits)
                bucket.fp += len(extra - forbidden)
                bucket.fn += len(expected - actual)
                if bad:
                    bucket.forbidden += len(bad)
            for v in sorted(extra):
                if v in forbidden:
                    violations.append(f"{fx['id']}.{field_name}: emitted forbidden value {v!r}")
                    scores[field_name].forbidden += 0
            scores[field_name].misses += [f"{fx['id']}:{v}" for v in sorted(expected - actual)]
            scores[field_name].extras += [f"{fx['id']}:{v}" for v in sorted(extra)]
            row["fields"][field_name] = {
                "expected": len(expected), "emitted": len(actual), "missed": sorted(expected - actual),
                "extra": sorted(extra), "forbidden_emitted": sorted(bad),
            }
        row["issues"] = [i["code"] for i in ledger.issues]
        row["facts"] = ledger.summary()["by_kind"]
        per_fixture.append(row)

    return {
        "fields": {k: scores[k].as_dict() for k in FIELDS},
        "languages": {lang: {k: s[k].as_dict() for k in FIELDS} for lang, s in sorted(by_language.items())},
        "per_fixture": per_fixture,
        "forbidden_violations": violations,
        "fixtures": len(manifest["fixtures"]),
    }


def score_jd(manifest: dict | None = None, gold_dir: Path | None = None) -> dict:
    """Requirement extraction, measured: how many asks, and with which weight, per fixture."""
    manifest = manifest or load_manifest()
    gold_dir = gold_dir or GOLD
    rows = []
    totals = {"must": 0, "nice": 0, "unknown": 0}
    expected_totals = {"must": 0, "nice": 0, "unknown": 0}
    wrong = 0
    for fx in manifest.get("job_descriptions", []):
        doc = build_jd((gold_dir / fx["file"]).read_text(encoding="utf-8"), source=fx["file"])
        counts = {"must": 0, "nice": 0, "unknown": 0}
        for r in doc.requirements:
            counts[r.weight] += 1
        rows.append({"id": fx["id"], "note": fx.get("note", ""), "expected_weights": fx["expect_weights"],
                     "actual_weights": counts, "requirements": len(doc.requirements),
                     "expected_requirements": fx.get("expect_requirements", len(doc.requirements)),
                     "match": counts == fx["expect_weights"]})
        for k in totals:
            totals[k] += counts[k]
            expected_totals[k] += fx["expect_weights"][k]
            wrong += abs(counts[k] - fx["expect_weights"][k])
    fixtures = len(rows) or 1
    return {"fixtures": len(rows), "per_fixture": rows, "actual_weights": totals,
            "expected_weights": expected_totals,
            "weight_cue_accuracy": round(1 - wrong / max(1, sum(expected_totals.values()) * 1.0), 3),
            "fixtures_exactly_matching": round(sum(1 for r in rows if r["match"]) / fixtures, 3)}


def stability(manifest: dict | None = None, gold_dir: Path | None = None) -> dict:
    """The measurable half of M-2: what a presentation-only change does to facts and to a ranking."""
    manifest = manifest or load_manifest()
    gold_dir = gold_dir or GOLD
    anchor = (gold_dir / manifest["anchor_jd"]["file"]).read_text(encoding="utf-8")
    tf = Tfidf(stop=_STOP)

    base_texts = {fx["id"]: (gold_dir / fx["file"]).read_text(encoding="utf-8")
                  for fx in manifest["fixtures"]}
    base_ledgers = {fid: build_ledger_text(text) for fid, text in base_texts.items()}
    base_cosine = {fid: tf.compare(_norm_for_compare(t), anchor)["cosine"] for fid, t in base_texts.items()}

    per_transform: dict[str, dict] = {}
    for name, fn in TRANSFORMS.items():
        fixture_rows = []
        broken_fixtures = []
        cosines: dict[str, float] = {}
        retentions = []
        for fx in manifest["fixtures"]:
            text = base_texts[fx["id"]]
            perturbed = fn(text)
            if perturbed == text:
                fixture_rows.append({"id": fx["id"], "applied": False,
                                     "note": "transform found nothing to change in this fixture"})
                continue
            led = build_ledger_text(perturbed)
            delta = base_ledgers[fx["id"]].delta(led)
            a = {f"{f.kind}|{f.value.casefold()}" for f in base_ledgers[fx["id"]].facts}
            b = {f"{f.kind}|{f.value.casefold()}" for f in led.facts}
            retention = round(len(a & b) / len(a | b), 3) if (a | b) else 1.0
            cos = tf.compare(_norm_for_compare(perturbed), anchor)["cosine"]
            cosines[fx["id"]] = cos
            retentions.append(retention)
            if delta.competence_changed:
                broken_fixtures.append(fx["id"])
            fixture_rows.append({"id": fx["id"], "applied": True,
                                 "competence_preserved": delta.competence_preserved,
                                 "facts_added": len(delta.added), "facts_removed": len(delta.removed),
                                 "fact_retention": retention,
                                 "cosine_before": round(base_cosine[fx["id"]], 4),
                                 "cosine_after": round(cos, 4),
                                 "cosine_delta": round(cos - base_cosine[fx["id"]], 4)})
        applied = [r for r in fixture_rows if r.get("applied")]
        per_transform[name] = {
            "fixtures_applied": len(applied),
            "competence_preserved_all": all(r["competence_preserved"] for r in applied)
            and bool(applied),
            "broken_fixtures": broken_fixtures,
            "mean_fact_retention": round(sum(r["fact_retention"] for r in applied) / len(applied), 4)
            if applied else None,
            "max_abs_cosine_delta": round(max((abs(r["cosine_delta"]) for r in applied), default=0.0), 4),
            "ranking_inversion_rate": _inversion_rate(base_cosine, cosines),
            "per_fixture": fixture_rows,
        }
    return {"anchor_jd": manifest["anchor_jd"]["file"], "transforms": per_transform,
            "note": "ranking_inversion_rate is the share of fixture pairs whose order against the "
                    "anchor advertisement flips; it is the figure nearest to the 29.6 % matched-pair "
                    "reversal rate in [EV-02], and it is not the same experiment."}


def build_ledger_text(text: str) -> Ledger:
    """Ledger from a string (the perturbations live in memory, not on disk)."""
    from .errors import ParseReport
    from .layout import analyze
    from .segment import segment
    from .evidence import Ledger as _L

    report = ParseReport()
    layout_report, report = analyze(text, report)
    sections = segment(text, report, layout_report.reading_order_confidence)
    return _L.build(text=text, sections=sections, report=report, method="in-memory",
                     layout=layout_report.as_dict())


def _norm_for_compare(text: str) -> str:
    from .textutil import normalize

    return normalize(text)


def _inversion_rate(before: dict[str, float], after: dict[str, float]) -> float | None:
    ids = sorted(set(before) & set(after))
    pairs = [(a, b) for i, a in enumerate(ids) for b in ids[i + 1:]]
    if not pairs:
        return None
    flips = 0
    for a, b in pairs:
        d0 = before[a] - before[b]
        d1 = after[a] - after[b]
        if (d0 > 0 > d1) or (d0 < 0 < d1):
            flips += 1
    return round(flips / len(pairs), 4)


def full_report(manifest: dict | None = None, gold_dir: Path | None = None) -> dict:
    manifest = manifest or load_manifest()
    gold_dir = gold_dir or GOLD
    problems = validate_manifest(manifest, gold_dir)
    if problems:
        raise ValueError("gold manifest is not internally consistent:\n  " + "\n  ".join(problems))
    return {"schema": "1.0.0",
            "corpus": {"fixtures": len(manifest["fixtures"]),
                       "languages": sorted({f["language"] for f in manifest["fixtures"]}),
                       "fields": FIELDS,
                       "matching_rule": manifest.get("matching_rule", "")},
            "accuracy": score_corpus(manifest, gold_dir),
            "jd": score_jd(manifest, gold_dir),
            "stability": stability(manifest, gold_dir)}


__all__ = ["FIELDS", "FIELD_KIND", "norm_value", "load_manifest", "validate_manifest",
           "emitted_fields", "score_corpus", "score_jd", "stability", "full_report", "GOLD"]
