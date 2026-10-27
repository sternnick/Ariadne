"""The benchmark is itself a claim, so the benchmark is tested.

Three failure classes are in scope here, and none of them is "the parser is wrong":

1. the scorer agrees with arithmetic on cases where the arithmetic is known;
2. the annotation cannot silently drift away from the text it annotates;
3. the published floors still hold on this checkout, so `ariadne bench` and CI say the same thing a
   contributor's `pytest` says.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from ariadne_ats import bench

SCRIPTS = ROOT / "scripts"


def load_gate():
    spec = importlib.util.spec_from_file_location("bench_gate", SCRIPTS / "bench.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_scorer_counts_arithmetic_we_can_do_by_hand():
    """A perfect extractor scores 1.0 everywhere; a shifted one loses recall and gains false positives."""
    scores = {"employer": bench.FieldScore()}
    s = scores["employer"]
    s.tp, s.fp, s.fn, s.fixtures = 3, 0, 0, 1
    assert (s.precision, s.recall, s.f1) == (1.0, 1.0, 1.0)
    shifted = bench.FieldScore(tp=2, fp=1, fn=1, fixtures=1)
    assert shifted.precision == 0.667 and shifted.recall == 0.667


def test_matching_rule_normalises_before_comparing():
    assert bench.norm_value("  Acme\u00a0Corp, ") == bench.norm_value("acme corp")
    assert bench.norm_value("D\u00e9veloppeur") == "d\u00e9veloppeur"


def test_annotation_agrees_with_the_text_it_annotates():
    """An expected value that is not in its fixture is a transcription error, and a forbidden value
    that does not occur in the fixture forbids nothing."""
    assert bench.validate_manifest(bench.load_manifest()) == []


def test_gold_corpus_meets_its_own_floors():
    report = bench.full_report()
    fails, _notes = load_gate().check(report, ROOT / "data" / "gold" / "thresholds.json")
    assert not fails, "\n".join(fails)


def _without_stamp(report: dict) -> dict:
    return {k: v for k, v in report.items() if k != "generated"}


def test_published_results_match_a_fresh_run():
    """`results.json` is the artefact the docs cite, so it may not drift from the code it describes.

    Compared structurally, everything except the timestamp. An earlier version of this test compared
    only the per-field accuracy table and the stability numbers, and that hole was paid for: the
    committed artefact carried `by_kind` fact counts generated while `KINDS` still omitted `name` and
    `employer`, so the published file under-reported what the parser emitted while every headline
    number in it was correct. A partial equality check is how a stale artefact survives a green build.
    """
    published = json.loads((ROOT / "data" / "gold" / "results.json").read_text(encoding="utf-8"))
    fresh = bench.full_report()
    a, b = _without_stamp(published), _without_stamp(fresh)
    assert a == b, _first_difference(a, b)


def _first_difference(a, b, path="$") -> str:
    """Name the first place the published artefact and a fresh run disagree. A dict-vs-dict assert in
    pytest would dump both trees; the artefact is 60 KB and the reader wants one line."""
    if type(a) is not type(b):
        return f"{path}: published {type(a).__name__}, fresh {type(b).__name__}"
    if isinstance(a, dict):
        for k in sorted(set(a) | set(b), key=str):
            if k not in a:
                return f"{path}.{k}: missing from the published artefact"
            if k not in b:
                return f"{path}.{k}: absent from a fresh run (was the artefact hand-edited?)"
            if a[k] != b[k]:
                return _first_difference(a[k], b[k], f"{path}.{k}")
    elif isinstance(a, list):
        if len(a) != len(b):
            return f"{path}: published {len(a)} items, fresh {len(b)}"
        for i, (x, y) in enumerate(zip(a, b)):
            if x != y:
                return _first_difference(x, y, f"{path}[{i}]")
    else:
        return f"{path}: published {a!r}, fresh {b!r}"
    return f"{path}: differs (no scalar found; structural comparison)"


def test_the_two_runs_that_should_be_identical_are_byte_identical():
    """Determinism claim in README: same tree, same numbers. Only the stamp may differ."""
    import copy

    first = copy.deepcopy(bench.full_report())
    second = copy.deepcopy(bench.full_report())
    first.pop("generated", None)
    second.pop("generated", None)
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_perturbations_really_do_preserve_competence():
    """If a transform changes a fact, the measurement is measuring a different document."""
    for name, t in bench.stability()["transforms"].items():
        assert t["broken_fixtures"] == [], f"{name} is not competence-preserving"


def test_ranking_inversion_is_zero_for_a_permutation_only_transform():
    """Cosine over a bag of terms cannot reorder a document: reordering sections must invert nothing.
    If this ever fails, the comparison layer has grown order-sensitivity somewhere unannounced."""
    assert bench.stability()["transforms"]["reorder_sections"]["ranking_inversion_rate"] == 0.0


def test_version_matches_pyproject():
    import ariadne_ats

    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert f'version = "{ariadne_ats.__version__}"' in pyproject, (
        "ariadne --version and the installed distribution must report the same number (D-004 class)")


def test_bench_cli_exits_zero_on_a_green_corpus():
    assert load_gate().main(["--check"]) == 0


def _gate():
    """The gate itself, imported from scripts/ - the ratchet lives in the CLI, and a test that
    re-implements it would be testing a copy."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("ariadne_gate", ROOT / "scripts" / "bench.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, ROOT / "data" / "gold" / "thresholds.json"


def test_the_gate_notices_a_deliberate_regression():
    """A ratchet nobody has seen fail is a decoration.

    Two mutations, both in-memory and both reverted by the fixture: one that costs recall (a field rule
    stops firing) and one that costs precision (a rule invents a value). Each must produce a named
    failure from the same `check` the CLI runs, so a green gate is known to be able to go red.
    """
    from ariadne_ats import fields

    gate, thresholds = _gate()
    baseline = gate.check(bench.full_report(), thresholds)
    assert baseline[0] == [], f"the gate is red before the mutation: {baseline[0]}"

    from ariadne_ats import fields as _f
    _original = _f.role_lines
    _f.role_lines = lambda *a, **k: []
    try:
        failures, _ = gate.check(bench.full_report(), thresholds)
    finally:
        _f.role_lines = _original
    assert failures, "a parser that emits no roles at all passed the ratchet: the floors are not gating"
    assert any("employer" in f or "title" in f for f in failures)


def test_the_gate_notices_invented_values(monkeypatch):
    from ariadne_ats import fields

    gate, thresholds = _gate()
    original = fields.person_name

    def invented(text, confidence=0.75):
        hit = original(text, confidence)
        if hit is None:
            return None
        hit.value = hit.value + " Extra"       # a value that is no longer in the document
        return hit

    monkeypatch.setattr(fields, "person_name", invented)
    failures, _ = gate.check(bench.full_report(), thresholds)
    assert failures, "inventing part of a name did not move the ratchet; precision is not being measured"
    assert any("name" in f for f in failures)
