"""Field extraction: what a rule does, and what it refuses to do.

These are the unit-level counterparts of the gold benchmark (`scripts/bench.py`). The benchmark says
how often the rules are right over a corpus; these say why, on the smallest case that separates a
correct rule from one that passes by accident. The three properties that matter here are:

* a rule that abstains must abstain *silently-but-visibly* - no fact, plus an issue that names why;
* a value that is emitted must be a substring of the document, never a reconstruction of it;
* a heading recognised in one language must be recognised in the same language when it is written in
  capitals, because Greek and Czech capitalisation deletes accents and an all-caps CV is a style,
  not a different document.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from ariadne_ats import fields
from ariadne_ats.errors import Code, ParseReport
from ariadne_ats.evidence import build_ledger
from ariadne_ats.textutil import normalize


# ------------------------------------------------------------------ role lines
def test_role_line_yields_title_and_employer():
    report = ParseReport()
    hits = fields.role_lines("Senior Engineer, Acme Corp 2019-2024\n* Led something", report)
    assert [(h.title, h.employer, h.start, h.end) for h in hits] == [
        ("Senior Engineer", "Acme Corp", "2019", "2024")]
    assert hits[0].bullets == ["Led something"]
    assert report.codes() == []


def test_role_line_with_an_open_end_records_present_not_a_year():
    hits = fields.role_lines("Lead SRE, Fjord Netverk 2016 - present")
    assert hits[0].end.lower() == "present"
    assert hits[0].start == "2016"


@pytest.mark.parametrize("line", [
    "DevOps Engineer, Rheinhanda GmbH 03/2019 - heute",
    "Développeuse senior, Lumineo SAS 2018 - Présent",
    "Ingeniera de soporte, Mareterra SL 2019 - Actualidad",
    "Príomhinnealtóir, Coho Networks 2018 - inniu",
    "Operations Engineer, Van Dijk Logistiek 2013/2019",
])
def test_date_span_forms_the_fixtures_actually_use(line):
    hits = fields.role_lines(line)
    assert len(hits) == 1, line
    assert hits[0].start and hits[0].employer


def test_a_date_bearing_line_with_one_segment_abstains_with_a_reason():
    """The honest output for an unreadable role line is nothing, plus an issue that says why."""
    report = ParseReport()
    hits = fields.role_lines("Confidential client 2019-2024", report)
    assert hits == []
    assert Code.ROLE_LINE_AMBIGUOUS.value in report.codes()


def test_key_value_role_line_is_labelled_not_guessed():
    line = "Role: Senior Platform Engineer   Company: Saxen AB          Period: 2020-2025"
    hits = fields.role_lines(line)
    assert [(h.title, h.employer) for h in hits] == [("Senior Platform Engineer", "Saxen AB")]


def test_bullets_are_not_role_lines_even_when_they_name_an_employer():
    report = ParseReport()
    body = "Delivery Lead, Kestrel Digital 2020-2025\n* Ran the programme for Halcyon Bank 2019-2020"
    hits = fields.role_lines(body, report)
    assert [h.employer for h in hits] == ["Kestrel Digital"]


# ------------------------------------------------------------------ contacts
def test_contact_reads_the_channels_and_nothing_else():
    block = "Sofia Rossi\nsofia.rossi@example.it\n+39 340 1122334\ngithub.com/srossi\nVia Roma 12, 2012 Milano"
    got = {h.value for h in fields.contacts(block)}
    assert got == {"sofia.rossi@example.it", "+39 340 1122334", "github.com/srossi"}


def test_a_reference_email_is_not_the_candidate_s_contact():
    """Contact comes from the contact block, so a REFERENCES section cannot leak into it."""
    ledger = build_ledger(ROOT / "data" / "gold" / "cv-19-adversarial.txt")
    contacts = {f.value for f in ledger.facts if f.kind == "contact"}
    assert "grace.adeyemi@example.com" in contacts
    assert "a.dada@example.com" not in contacts


def test_tab_separated_contact_block_still_splits():
    got = {h.value for h in fields.contacts("anna.k@example.de\tBerlin\t+49 30 123456")}
    assert got == {"anna.k@example.de", "+49 30 123456"}


# ------------------------------------------------------------------ names
@pytest.mark.parametrize("line,expected", [
    ("Séamus Ó Briain", "Séamus Ó Briain"),      # single-letter Irish prefix is part of the name
    ("Pieter de Vries", "Pieter de Vries"),      # lower-case particle
    ("MARIA GONZALEZ", "MARIA GONZALEZ"),        # an all-caps CV is a formatting choice
])
def test_name_rule_accepts_the_shapes_real_names_use(line, expected):
    hit = fields.person_name(line)
    assert hit and hit.value == expected


@pytest.mark.parametrize("line", [
    "SENIOR SECURITY ENGINEER",                  # a headline, not a name (cv-24)
    "Madrid",                                    # one token: a location
    "Berlin | Munich",                           # a separator means a data row
])
def test_name_rule_abstains_rather_than_guess(line):
    assert fields.person_name(line) is None


# ------------------------------------------------------------------ headings, tabs, folding
@pytest.mark.parametrize("line,kind", [
    ("ΔΕΞΙΟΤΗΤΕΣ", "skills"),        # capitalised Greek has no accents left to match on
    ("Δεξιότητες", "skills"),
    ("EXPÉRIENCE PROFESSIONNELLE", "experience"),
    ("expérience professionnelle", "experience"),
    ("BERUFSERFAHRUNG", "experience"),
    ("TAITHÍ OIBRE", "experience"),
])
def test_heading_recognition_survives_case_and_accent(line, kind):
    from ariadne_ats.textutil import heading_kind

    assert heading_kind(line)[0] == kind


def test_normalize_keeps_the_tab_because_a_tab_is_a_column_boundary():
    assert normalize("Title\tAcme\t2019 - 2024") == "Title\tAcme\t2019 - 2024"
    assert normalize("a  \t b") == "a\tb"
    assert normalize(normalize("a\tb  c")) == "a\tb c"          # idempotent


def test_a_tab_separated_role_line_is_recoverable_after_normalize():
    """The audit's P3 lesson, in the extractor: the detector and the field rules must not disagree
    about what text is. Collapsing tabs made cv-03 unreadable until the gold set scored it."""
    ledger = build_ledger(ROOT / "data" / "gold" / "cv-03-two-column-tabs.txt")
    assert {f.value for f in ledger.facts if f.kind == "employer"} == {"KfW Tech", "Berlino Systems"}


def test_every_emitted_fact_value_appears_in_the_source_text():
    """No rule may reconstruct a value. A fact that is not a substring of the document is inferred,
    and inference about a person is what AGENT_CONTRACT C9 forbids; this checks the weaker, checkable
    half of that claim over every gold fixture."""
    for path in sorted((ROOT / "data" / "gold").glob("cv-*.txt")):
        raw = normalize(path.read_text(encoding="utf-8", errors="replace"))
        for fact in build_ledger(path).facts:
            assert fact.value.casefold() in raw.casefold(), f"{path.name}: {fact.kind} {fact.value!r}"


def test_work_entries_are_the_roles_and_never_an_empty_claim():
    ledger = build_ledger(ROOT / "data" / "gold" / "cv-01-single-column.txt")
    assert [(w["position"], w["name"]) for w in ledger.work] == [
        ("Data Engineer", "Norddata"), ("Junior Analyst", "Bisel SA")]
    assert ledger.basics["name"] == "MARIA GONZALEZ"
    assert ledger.basics["email"] == "maria.gonzalez@example.org"


def test_an_unassigned_bullet_block_reports_why_it_has_no_employer():
    """An empty position must always arrive with a reason attached, never silently."""
    for path in sorted((ROOT / "data" / "gold").glob("cv-*.txt")):
        ledger = build_ledger(path)
        for entry in ledger.work:
            if entry["position"] == "":
                assert entry["custom"].get("ariadne.unassigned") is True
                assert Code.ROLE_LINE_AMBIGUOUS.value in [i["code"] for i in ledger.issues], path.name
