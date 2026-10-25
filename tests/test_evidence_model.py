"""A1 acceptance: the evidence model expresses perturbation deltas (Guard 2).

If these tests pass, A2 can measure score stability: a competence-preserving perturbation is
*detectable as such* by the model alone (same `competence_hash`, different `surface_hash`), and the
delta names exactly which fact ids changed.

If they fail, M-2 cannot be closed later — which is why they are A1's gate and not A2's.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from ariadne_ats import perturb
from ariadne_ats.errors import ParseReport
from ariadne_ats.evidence import Ledger, build_ledger
from ariadne_ats.layout import analyze
from ariadne_ats.segment import segment


def ledger_for(text: str, name: str = "synthetic") -> Ledger:
    report = ParseReport()
    lay, report = analyze(text, report)
    sections = segment(text, report, lay.reading_order_confidence)
    return Ledger.build(text, sections, report, source=name, method="text", layout=lay.as_dict())


@pytest.fixture(scope="module")
def base_text(fixtures) -> str:
    return fixtures["clean"].read_text(encoding="utf-8")


def test_perturbations_preserve_competence_and_change_surface(base_text):
    """The definition M-2 depends on, asserted for every transform."""
    base = ledger_for(base_text, "base")
    assert base.facts, "fixture produced no facts; the perturbation test would be vacuous"

    for name, transform in perturb.TRANSFORMS.items():
        changed = transform(base_text)
        assert changed != base_text, f"transform {name} was a no-op; the test would pass vacuously"

        other = ledger_for(changed, f"base+{name}")
        delta = base.delta(other)

        assert delta.surface_changed, f"{name}: surface_hash did not change"
        assert delta.competence_preserved, (
            f"{name}: competence changed ({len(delta.added)} added, {len(delta.removed)} removed, "
            f"{len(delta.changed)} changed). The transform is supposed to touch presentation only, so "
            "this is a fixture bug, not a stability result."
        )
        assert other.competence_hash == base.competence_hash


def test_a_real_content_change_does_change_competence(base_text):
    """The counter-test: if everything preserved competence, the hash would prove nothing."""
    base = ledger_for(base_text)
    edited = base_text.replace("python, kubernetes", "python, kubernetes, rust")
    other = ledger_for(edited)
    delta = base.delta(other)
    assert delta.competence_changed
    assert delta.added or delta.removed or delta.changed


def test_fact_ids_are_stable_across_reordering(base_text):
    """A fact that moves keeps its id, so a delta can distinguish 'moved' from 'changed'."""
    base = ledger_for(base_text)
    moved = ledger_for(perturb.reorder_sections(base_text))
    assert {f.id for f in moved.facts} == {f.id for f in base.facts}


def test_numbers_are_captured_on_the_facts_that_carry_them(base_text):
    led = ledger_for(base_text)
    numbered = [f for f in led.facts if f.numbers]
    assert numbered, "no fact captured a number; the anti-hallucination checker would have nothing to check"
    joined = " ".join(n for f in numbered for n in f.numbers)
    assert any("%" in n or any(ch.isdigit() for ch in n) for n in joined.split())


def test_delta_is_serialisable_and_names_its_hashes(base_text):
    base = ledger_for(base_text)
    d = base.delta(ledger_for(perturb.change_markers(base_text))).as_dict()
    assert set(d) == {"added", "removed", "changed", "surface_changed", "competence_changed", "competence_preserved"}
    assert d["competence_preserved"] is True


def test_resume_json_carries_provenance_in_custom(base_text):
    """JSON Resume 1.7.0 base + provenance in the spec-sanctioned `custom` object (implication 16)."""
    led = ledger_for(base_text)
    doc = led.to_resume_json()
    assert doc["$schema"].endswith("v1.7.0/schema.json")
    prov = doc["custom"]["ariadne.provenance"]
    assert prov["competenceHash"] == led.competence_hash
    assert prov["surfaceHash"] == led.surface_hash
    assert len(prov["facts"]) == len(led.facts)
    for fact in prov["facts"]:
        assert set(fact) >= {"id", "kind", "value", "span", "confidence"}
        assert fact["span"]["end"] >= fact["span"]["start"]
        assert 0.0 < fact["confidence"] <= 1.0


def test_confidence_is_reduced_by_layout_damage(fixtures):
    """A fact cut from a flattened two-column extraction must not carry full confidence."""
    clean = ledger_for(fixtures["clean"].read_text(encoding="utf-8"))
    damaged_text = fixtures["two_column"].read_text(encoding="utf-8")
    damaged = ledger_for(damaged_text)
    assert damaged.layout["columns_suspected"] is True
    assert damaged.layout["reading_order_confidence"] < 1.0
    assert min(f.confidence for f in damaged.facts) < min(f.confidence for f in clean.facts)


def test_build_ledger_from_file(fixtures, table_docx: Path):
    """The pipeline entry point works end to end on a real DOCX, with tables flagged."""
    led = build_ledger(table_docx)
    assert led.method == "stdlib-docx"
    assert any(i["code"] == "TABLE_STRUCTURE" for i in led.issues)
    assert led.facts, "table-based CV produced no facts"
    assert led.summary()["facts"] == len(led.facts)
