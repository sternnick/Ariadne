"""Guards on the sentences the software says out loud.

A user-facing string is a claim (AGENT_CONTRACT C8), and a claim that lives only in prose can be
deleted by a refactor that never touches a test. These tests bind the three disclaimers that keep the
output from over-reading itself to the code that prints them:

* a fact's `confidence` is a heuristic about section and layout quality, never a calibrated
  probability - the measured accuracy is a different artefact, in a different place;
* `compare` is document similarity, not a job-match score, and the output carries no field that could
  be read as a score, a rank or a verdict;
* the package exposes no scoring entry point at all, so "there is no score yet" stays true in the
  shape of the API, not just in the README.
"""
from __future__ import annotations

import io
import json
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import ariadne_ats  # noqa: E402
from ariadne_ats.cli import main  # noqa: E402
from ariadne_ats.evidence import build_ledger  # noqa: E402
from ariadne_ats.lexical import Tfidf  # noqa: E402

GOLD = ROOT / "data" / "gold"


def test_provenance_labels_confidence_as_a_heuristic_and_points_at_accuracy():
    doc = build_ledger(GOLD / "cv-01-single-column.txt").to_resume_json()
    prov = doc["custom"]["ariadne.provenance"]
    assert prov["confidenceIsHeuristic"] is True, (
        "confidence must be labelled as a heuristic; if it has been calibrated, that needs a "
        "DECISIONS entry and a labelled corpus, not a deleted flag")
    assert Path(prov["accuracySource"]).is_file(), (
        "the provenance block points at measured accuracy that does not exist")


def test_confidence_is_not_presented_as_an_accuracy():
    """Confidence and accuracy are different quantities and must not be conflated in any output."""
    ledger = build_ledger(GOLD / "cv-06-german.txt")
    summary = ledger.summary()
    assert "note" in summary and "heuristic" in summary["note"]
    for fact in ledger.facts:
        assert 0.0 < fact.confidence <= 1.0
        # A number-bearing fact takes the penalty; that is the heuristic, and it must be visible.
        if fact.numbers:
            assert fact.confidence < 0.95 or fact.section == ""


def test_compare_output_is_similarity_and_carries_no_verdict_field():
    tf = Tfidf(stop={"the", "and", "of", "a", "an", "to", "in"})
    out = tf.compare("python kubernetes pipelines", "python docker kubernetes")
    forbidden = {"score", "percent_match", "match_score", "rank", "verdict", "ats_score", "fit"}
    assert not (set(out) & forbidden), f"the comparison grew a score-shaped field: {set(out) & forbidden}"
    assert "cosine" in out and 0.0 <= out["cosine"] <= 1.0


def test_cli_compare_states_that_it_is_not_a_score(tmp_path, capsys):
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    a.write_text("python kubernetes terraform pipelines monitoring\n", encoding="utf-8")
    b.write_text("python terraform team player excellent communication\n", encoding="utf-8")
    assert main(["compare", str(a), str(b)]) == 0
    out = json.loads(capsys.readouterr().out)
    assert "note" in out, "compare() shipped without the sentence that bounds what it means"
    lowered = out["note"].lower()
    assert "similarity" in lowered and "not" in lowered
    assert not (set(out) & {"score", "rank", "verdict"})


def test_no_scoring_entry_point_exists_anywhere_in_the_public_surface():
    for name in ("score", "ScoreResult", "rank", "match", "suggest", "propose"):
        assert not hasattr(ariadne_ats, name), f"`ariadne_ats.{name}` exists; the README says it does not"


def test_bench_cli_prints_its_own_limit(tmp_path, capsys):
    err = io.StringIO()
    with redirect_stderr(err), redirect_stdout(io.StringIO()):
        assert main(["bench"]) == 0
    assert "synthetic" in err.getvalue().lower() and "not accuracy figures" in err.getvalue().lower()
