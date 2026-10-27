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


def test_published_results_match_a_fresh_run():
    """results.json is the artefact the docs cite. It may not drift from the code it describes."""
    published = json.loads((ROOT / "data" / "gold" / "results.json").read_text(encoding="utf-8"))
    fresh = bench.full_report()
    assert published["accuracy"]["fields"] == fresh["accuracy"]["fields"]
    assert published["stability"]["transforms"].keys() == fresh["stability"]["transforms"].keys()
    for name, t in fresh["stability"]["transforms"].items():
        for k in ("mean_fact_retention", "max_abs_cosine_delta", "ranking_inversion_rate",
                  "competence_preserved_all", "fixtures_applied"):
            assert published["stability"]["transforms"][name][k] == t[k], (name, k)


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
