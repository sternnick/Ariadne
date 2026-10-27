"""A1 acceptance: parser behaviour over the five synthetic fixtures.

Each fixture exists to exercise a *named* failure mode. A test that only asserts "it parsed" would
pass on a parser that silently returns plausible garbage, so every assertion here is either a typed
failure code or a specific structural property.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from ariadne_ats.errors import Code, ParseFailure
from ariadne_ats.evidence import build_ledger
from ariadne_ats.extract import extract
from ariadne_ats.layout import analyze


# ---------------------------------------------------------------- clean single column
def test_clean_fixture_parses_without_degradation(fixtures):
    ex = extract(fixtures["clean"])
    assert ex.method == "stdlib-text"
    layout, report = analyze(ex.text, ex.report)
    assert layout.columns_suspected is False
    assert layout.table_rows == 0
    assert report.degraded == []
    assert layout.reading_order_confidence == 1.0


def test_clean_fixture_segments_into_expected_sections(fixtures):
    led = build_ledger(fixtures["clean"])
    kinds = [s["kind"] for s in led.sections]
    assert kinds[:1] == ["preamble"]
    for expected in ("summary", "experience", "skills", "education"):
        assert expected in kinds, f"{expected} missing from {kinds}"
    assert all(s["confidence"] >= 0.5 for s in led.sections)
    assert led.summary()["by_kind"]["bullet"] >= 4


# ---------------------------------------------------------------- two column
def test_two_column_fixture_is_flagged_and_degrades_confidence(fixtures):
    ex = extract(fixtures["two_column"])
    layout, report = analyze(ex.text, ex.report)
    assert layout.columns_suspected is True
    assert layout.column_ratio > 0.30
    assert Code.MULTICOLUMN_FLATTENED.value in report.codes()
    assert layout.reading_order_confidence < 1.0


def test_two_column_facts_have_lower_confidence_than_clean(fixtures):
    clean = build_ledger(fixtures["clean"])
    damaged = build_ledger(fixtures["two_column"])
    assert clean.facts and damaged.facts
    assert max(f.confidence for f in damaged.facts) < max(f.confidence for f in clean.facts)


# ---------------------------------------------------------------- table-heavy DOCX
def test_table_docx_reports_table_structure(table_docx: Path):
    led = build_ledger(table_docx)
    assert led.method == "stdlib-docx"
    assert Code.TABLE_STRUCTURE.value in [i["code"] for i in led.issues]
    # Tables still yield content: we flag the risk, we do not refuse the document.
    assert led.facts, "table-only CV produced no facts at all"


def test_table_docx_text_is_emitted_in_document_order(table_docx: Path):
    ex = extract(table_docx)
    assert ex.tables == 2
    assert "Senior Engineer" in ex.text and "python, go" in ex.text
    # Document order, not visual order: the flag exists precisely because the two may differ.
    assert ex.text.index("Senior Engineer") < ex.text.index("python")


# ---------------------------------------------------------------- malformed
def test_malformed_docx_fails_with_a_named_code(fixtures):
    with pytest.raises(ParseFailure) as excinfo:
        extract(fixtures["malformed"])
    assert excinfo.value.code is Code.CORRUPT_DOCUMENT
    assert "not a readable DOCX" in str(excinfo.value)


def test_unsupported_legacy_format_is_refused_not_guessed(tmp_path: Path):
    legacy = tmp_path / "cv.doc"
    legacy.write_bytes(b"\xd0\xcf\x11\xe0binary word document")
    with pytest.raises(ParseFailure) as excinfo:
        extract(legacy)
    assert excinfo.value.code is Code.UNSUPPORTED_FORMAT
    assert "convert to .docx" in str(excinfo.value)


def test_empty_file_is_a_typed_failure_not_an_empty_document(tmp_path: Path):
    empty = tmp_path / "empty.txt"
    empty.write_text("")
    with pytest.raises(ParseFailure) as excinfo:
        extract(empty)
    assert excinfo.value.code is Code.EMPTY_INPUT


# ---------------------------------------------------------------- image-only PDF
def test_image_only_pdf_never_returns_a_silent_empty_parse(fixtures):
    """Two acceptable outcomes, both typed:
    * no PDF backend in this environment -> PDF_BACKEND_MISSING
    * backend present, no text layer     -> NO_TEXT_LAYER
    What must never happen is an empty string being treated as a successful parse.
    """
    with pytest.raises(ParseFailure) as excinfo:
        extract(fixtures["image_pdf"])
    assert excinfo.value.code in (Code.PDF_BACKEND_MISSING, Code.NO_TEXT_LAYER)


def test_pdf_with_text_layer_extracts(fixtures, tmp_path: Path):
    """If a backend exists, a text PDF must extract.

    Two modes, because "skipped" is a word CI should only be able to say honestly:

    * default: `importorskip`, since the runtime dependency list is empty by policy and a contributor
      who has not installed the optional extra is not doing anything wrong;
    * `ARIADNE_REQUIRE_PDF_BACKEND=1` (what the `pytest-pdf` job sets): the backend is *required* and
      a missing one is a failure. Without that switch a broken optional import and a passing run look
      identical in the log, which is how a permanent skip can masquerade as coverage.
    """
    import os

    if os.environ.get("ARIADNE_REQUIRE_PDF_BACKEND") == "1":
        import pymupdf  # noqa: F401  - ImportError is the failure this mode exists to surface
    else:
        pymupdf = pytest.importorskip("pymupdf")
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((72, 72), "JANE DOE\nSUMMARY\nBackend engineer")
    out = tmp_path / "text.pdf"
    doc.save(out)
    doc.close()
    ex = extract(out)
    assert "JANE DOE" in ex.text
    assert ex.method.startswith("pdf-")


# ---------------------------------------------------------------- segmentation behaviour
def test_repeated_heading_keeps_every_block(fixtures):
    """Fixes audit P5: the old detector silently dropped the second occurrence."""
    text = "SUMMARY\nfirst block\nEXPERIENCE\nrole\nSUMMARY\nsecond block\n"
    from ariadne_ats.errors import ParseReport
    from ariadne_ats.segment import segment

    report = ParseReport()
    sections = segment(text, report)
    summaries = [s for s in sections if s.kind == "summary"]
    assert len(summaries) == 2, "a repeated heading must produce two segments, not one"
    assert "first block" in summaries[0].body
    assert "second block" in summaries[1].body
    assert Code.SECTION_REPEATED.value in report.codes()


def test_no_headings_is_degraded_not_invented():
    from ariadne_ats.errors import ParseReport
    from ariadne_ats.segment import segment

    report = ParseReport()
    sections = segment("just some text\nwith no headings at all\n", report)
    assert len(sections) == 1
    assert sections[0].kind == "unstructured"
    assert sections[0].confidence <= 0.25
    assert Code.NO_SECTIONS_FOUND.value in report.codes()


def test_unmarked_achievement_is_recognised_as_a_bullet():
    """Fixes audit P4: markers disappear when a layout is flattened."""
    from ariadne_ats.segment import bullets

    assert bullets("Led a team of nine engineers to ship the platform") == [
        "Led a team of nine engineers to ship the platform"
    ]
    assert bullets("Some ordinary prose sentence that is not an achievement") == []
