"""Build the binary fixtures at test time, from committed text and the standard library.

`table_heavy.docx` is produced with `zipfile` + XML: a DOCX is a zip, so this needs no dependency in CI
and keeps the repository free of opaque binary blobs whose provenance nobody can read.

`image_only.pdf` is committed as a 638-byte PDF (one drawn rectangle, no fonts, no text operators), so
the NO_TEXT_LAYER path can be exercised whether or not a PDF backend is installed.
"""
from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"

_DOCX_CT = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""

_DOCX_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""


def _para(text: str) -> str:
    return f'<w:p><w:r><w:t xml:space="preserve">{text}</w:t></w:r></w:p>'


def _table(rows: list[list[str]]) -> str:
    cells = "".join(
        "<w:tr>" + "".join(f"<w:tc>{_para(c)}</w:tc>" for c in row) + "</w:tr>" for row in rows
    )
    return f"<w:tbl>{cells}</w:tbl>"


def build_docx(path: Path, blocks: list[tuple[str, object]]) -> None:
    """blocks: ("p", "text") for a paragraph, ("t", [[cells], ...]) for a table, in document order."""
    body = ""
    for kind, payload in blocks:
        if kind == "p":
            body += _para(str(payload))
        elif kind == "t":
            body += _table(payload)  # type: ignore[arg-type]
        else:
            raise ValueError(f"unknown block kind: {kind}")
    document = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f"<w:body>{body}</w:body></w:document>"
    )
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", _DOCX_CT)
        zf.writestr("_rels/.rels", _DOCX_RELS)
        zf.writestr("word/document.xml", document)


@pytest.fixture(scope="session")
def table_docx(tmp_path_factory) -> Path:
    """A résumé whose experience and skills are expressed as tables, with real headings."""
    out = tmp_path_factory.mktemp("fixtures") / "table_heavy.docx"
    build_docx(out, [
        ("p", "JANE DOE"),
        ("p", "jane.doe@example.com"),
        ("p", "SUMMARY"),
        ("p", "Backend engineer with 8 years building payment systems."),
        ("p", "EXPERIENCE"),
        ("t", [["Role", "Employer", "Period"],
               ["Senior Engineer", "Acme Corp", "2019-2024"],
               ["Engineer", "Beta Ltd", "2016-2019"]]),
        ("p", "SKILLS"),
        ("t", [["Category", "Tools"],
               ["Languages", "python, go"],
               ["Infrastructure", "kubernetes, terraform"]]),
        ("p", "EDUCATION"),
        ("p", "BSc Computer Science, 2016"),
    ])
    return out


@pytest.fixture(scope="session")
def fixtures() -> dict[str, Path]:
    return {
        "clean": FIXTURES / "clean_single_column.txt",
        "two_column": FIXTURES / "two_column_tabs.txt",
        "table_source": FIXTURES / "table_heavy.txt",
        "malformed": FIXTURES / "malformed.docx",
        "image_pdf": FIXTURES / "image_only.pdf",
    }
