"""How a job description becomes requirements, including every way the cue vocabulary can mislead.

`jd.py` classifies with vocabulary, not a model, so the interesting cases are the ones where the
vocabulary is present and means the opposite, is present twice, or is absent. Each case here is also
labelled in `data/gold/manifest.json`; this file is the unit-level counterpart, so a regression names
the rule instead of a corpus number.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from ariadne_ats.errors import Code  # noqa: E402
from ariadne_ats.jd import build_jd  # noqa: E402

GOLD = ROOT / "data" / "gold"


def jd(text: str, report=None):
    from ariadne_ats.errors import ParseReport
    doc = build_jd(text, source="test", report=report if report is not None else ParseReport())
    return doc


def weights(doc):
    return [r.weight for r in doc.requirements]


def test_plain_obligation_vocabulary():
    doc = jd("REQUIREMENTS\n* You have production experience with Kubernetes\n* Linux is required\n")
    assert weights(doc) == ["must", "must"]


def test_preference_vocabulary_is_not_an_obligation():
    doc = jd("NICE TO HAVE\n* Experience with service meshes is desirable\n")
    assert weights(doc) == ["nice"]


def test_a_negated_cue_is_not_evidence_of_a_requirement():
    """The bug this line exists for: 'required' inside a negation used to classify as must."""
    doc = jd("REQUIREMENTS\n* A computer science degree is not required\n")
    assert weights(doc) == ["unknown"]
    assert Code.REQUIREMENT_NEGATED_CUE.value in doc.issue_codes


def test_negation_separated_from_the_cue_by_several_words_is_still_caught():
    doc = jd("REQUIREMENTS\n* No prior fintech experience required\n")
    assert weights(doc) == ["unknown"]


def test_contradictory_cues_resolve_to_unknown_not_to_evaluation_order():
    doc = jd("REQUIREMENTS\n* SQL is desirable but required for this role\n")
    assert weights(doc) == ["unknown"]
    assert Code.REQUIREMENT_AMBIGUOUS_CUES.value in doc.issue_codes


def test_a_requirement_with_no_cue_word_is_kept_as_unknown_inside_a_requirements_section():
    doc = jd("REQUIREMENTS\n* Linux at the command line\n")
    assert weights(doc) == ["unknown"]


def test_a_requirement_with_no_cue_word_outside_a_requirements_section_is_dropped():
    doc = jd("PERKS\n* Free fruit on Wednesdays in the kitchen area\n")
    assert doc.requirements == []


def test_a_repeated_requirement_is_one_requirement():
    doc = jd("REQUIREMENTS\n* You have run Prometheus in production\n\nWHAT YOU BRING\n"
             "* You have run Prometheus in production\n")
    assert len(doc.requirements) == 1


def test_a_short_all_caps_line_is_a_section_label_not_an_ask():
    doc = jd("WHAT YOU WILL NEED\n* You have written infrastructure as code with Terraform\n")
    assert [r.text for r in doc.requirements] == \
        ["You have written infrastructure as code with Terraform"]


@pytest.mark.parametrize("fixture,expected", [
    ("jd-01-cloud.txt", {"must": 3, "nice": 2, "unknown": 0}),
    ("jd-02-negations.txt", {"must": 1, "nice": 1, "unknown": 2}),
    ("jd-03-conflicts.txt", {"must": 1, "nice": 1, "unknown": 2}),
    ("jd-04-no-cues.txt", {"must": 0, "nice": 0, "unknown": 3}),
    ("jd-05-duplicates.txt", {"must": 1, "nice": 0, "unknown": 1}),
])
def test_labelled_job_description_fixtures(fixture, expected):
    doc = build_jd((GOLD / fixture).read_text(encoding="utf-8"), source=fixture)
    counts = {"must": 0, "nice": 0, "unknown": 0}
    for r in doc.requirements:
        counts[r.weight] += 1
    assert counts == expected, f"{fixture}: {counts}"


def test_non_english_advertisements_yield_their_requirements_but_not_all_their_weights():
    """The limitation, restated at its true size after the 2026-10-27 fixes (jd-06, jd-07).

    Before: a German advertisement produced **no requirements at all**, because the heading vocabulary
    was English and the section was never found. That is fixed, and the honest residue is narrower -
    the requirements are extracted, and the ones with a cue word are weighted, while a requirement
    phrased *without* a cue word ("Sie haben X eingesetzt", "Vous avez une expérience …") stays
    `unknown`. That is the same abstention the English rule makes, and the fixture labels record it.

    Both halves are asserted so that a vocabulary change has to change this claim with it.
    """
    for name in ("jd-06-german.txt", "jd-07-french.txt"):
        doc = build_jd((GOLD / name).read_text(encoding="utf-8"), source=name)
        assert len(doc.requirements) == 3, f"{name}: requirements lost again"
        assert "NO_SECTIONS_FOUND" not in doc.issue_codes, f"{name}: the heading vocabulary regressed"
        weights = sorted(r.weight for r in doc.requirements)
        assert "unknown" in weights, f"{name}: cue-less requirement phrasing is being guessed now"
        assert set(weights) & {"must", "nice"}, f"{name}: the cue vocabulary stopped matching at all"


def test_english_advertisement_weighting_is_unchanged_by_the_cue_extension():
    doc = build_jd((GOLD / "jd-01-cloud.txt").read_text(encoding="utf-8"), source="jd-01")
    assert [r.weight for r in doc.requirements] == ["must", "must", "must", "nice", "nice"]
