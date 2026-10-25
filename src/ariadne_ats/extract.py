"""Deterministic text extraction. No ML, no NER, no model.

Backends, in order of preference, all optional except stdlib:

| input | backend | dependency |
|---|---|---|
| `.txt` `.md` `.text` | built-in | none |
| `.docx` | **stdlib** (`zipfile` + `xml.etree`) — a DOCX is a zip of XML | none |
| `.pdf` | `pymupdf`, else `pypdf` | optional extra |
| `.pdf` with no text layer | OCR backend (`pytesseract`), else a typed failure | optional extra |

The point of doing DOCX with the standard library is not purity: it means the parser's *default* path
has no dependency that can be missing, unpinned, or compromised, which is the same product property
`D-016` states for the package as a whole.

When a backend is absent we raise `PDF_BACKEND_MISSING` / `OCR_BACKEND_MISSING` rather than returning
empty text. Empty text is indistinguishable from an empty document, and that ambiguity is how a parse
failure silently becomes a "bad CV".
"""
from __future__ import annotations

import zipfile
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET

from .errors import Code, ParseFailure, ParseIssue, ParseReport, Severity

TEXT_SUFFIXES = {".txt", ".text", ".md", ".markdown"}
DOCX_SUFFIXES = {".docx"}
PDF_SUFFIXES = {".pdf"}

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

# Below this many non-space characters per page, the extraction is treated as suspicious rather than
# successful. Chosen as a floor, not a measurement: 200 chars is roughly two lines.
MIN_CHARS_PER_PAGE = 200


@dataclass
class Extraction:
    text: str
    method: str
    pages: int
    tables: int
    report: ParseReport

    @property
    def chars_per_page(self) -> float:
        return round(len(self.text) / self.pages, 1) if self.pages else 0.0


def _read_text(path: Path, report: ParseReport) -> Extraction:
    text = path.read_text(encoding="utf-8", errors="replace")
    return Extraction(text=text, method="stdlib-text", pages=max(1, text.count("\f") + 1), tables=0, report=report)


def _read_docx(path: Path, report: ParseReport) -> Extraction:
    try:
        with zipfile.ZipFile(path) as zf:
            xml = zf.read("word/document.xml")
    except (zipfile.BadZipFile, KeyError) as e:
        raise ParseFailure(ParseIssue(Code.CORRUPT_DOCUMENT, Severity.BLOCKING, f"not a readable DOCX: {e}")) from e

    try:
        root = ET.fromstring(xml)
    except ET.ParseError as e:
        raise ParseFailure(ParseIssue(Code.CORRUPT_DOCUMENT, Severity.BLOCKING, f"document.xml unparseable: {e}")) from e

    lines: list[str] = []
    tables = 0
    for para in root.iter(f"{W}p"):
        # A paragraph's text is the concatenation of its runs; tabs and breaks are preserved as text
        # so that the layout detector can see what the renderer actually produced.
        parts: list[str] = []
        for node in para.iter():
            if node.tag == f"{W}t" and node.text:
                parts.append(node.text)
            elif node.tag == f"{W}tab":
                parts.append("\t")
            elif node.tag in (f"{W}br", f"{W}cr"):
                parts.append("\n")
        line = "".join(parts)
        if line.strip():
            lines.append(line)

    for _ in root.iter(f"{W}tbl"):
        tables += 1
    if tables:
        report.add(Code.TABLE_STRUCTURE, Severity.DEGRADED,
                   f"{tables} table(s) present; cell order is document order, not visual layout")
    report.add(Code.LIGATURE_FOLDED, Severity.NOTE, "DOCX text extracted structurally (no glyph layer)")

    text = "\n".join(lines)
    return Extraction(text=text, method="stdlib-docx", pages=1, tables=tables, report=report)


def _pdf_backend():
    try:
        import pymupdf  # type: ignore

        return "pymupdf", pymupdf
    except Exception:  # noqa: BLE001 - a missing optional backend is a normal state
        pass
    try:
        import pypdf  # type: ignore

        return "pypdf", pypdf
    except Exception:  # noqa: BLE001
        return None, None


def _read_pdf(path: Path, report: ParseReport) -> Extraction:
    name, mod = _pdf_backend()
    if name is None:
        raise ParseFailure(ParseIssue(
            Code.PDF_BACKEND_MISSING, Severity.BLOCKING,
            "no PDF backend installed; install the 'pdf' extra (pymupdf or pypdf)"))

    pages_text: list[str] = []
    if name == "pymupdf":
        with mod.open(str(path)) as doc:
            pages = doc.page_count
            for page in doc:
                pages_text.append(page.get_text("text"))
    else:
        reader = mod.PdfReader(str(path))
        pages = len(reader.pages)
        for page in reader.pages:
            pages_text.append(page.extract_text() or "")

    text = "\f".join(pages_text)
    extraction = Extraction(text=text, method=f"pdf-{name}", pages=max(1, pages), tables=0, report=report)

    if not text.strip():
        report.add(Code.NO_TEXT_LAYER, Severity.BLOCKING,
                   "PDF has no extractable text layer (scanned/image-only); OCR rung required")
        raise ParseFailure(ParseIssue(
            Code.NO_TEXT_LAYER, Severity.BLOCKING,
            "no text layer; this document is an image. OCR is required and is not enabled."))

    if extraction.chars_per_page < MIN_CHARS_PER_PAGE:
        report.add(Code.LOW_TEXT_YIELD, Severity.DEGRADED,
                   f"{extraction.chars_per_page} chars/page; extraction may be partial")
    return extraction


def extract(path: str | Path) -> Extraction:
    """Extract text from a document, or raise a typed failure explaining why it cannot be."""
    p = Path(path)
    report = ParseReport()
    if not p.exists():
        raise ParseFailure(ParseIssue(Code.EMPTY_INPUT, Severity.BLOCKING, f"no such file: {p}"))
    if not p.is_file():
        raise ParseFailure(ParseIssue(Code.EMPTY_INPUT, Severity.BLOCKING, f"not a file: {p}"))
    if p.stat().st_size == 0:
        raise ParseFailure(ParseIssue(Code.EMPTY_INPUT, Severity.BLOCKING, "file is empty"))

    suffix = p.suffix.lower()
    if suffix in TEXT_SUFFIXES:
        out = _read_text(p, report)
    elif suffix in DOCX_SUFFIXES:
        out = _read_docx(p, report)
    elif suffix in PDF_SUFFIXES:
        out = _read_pdf(p, report)
    elif suffix in {".doc", ".rtf", ".pages", ".odt"}:
        raise ParseFailure(ParseIssue(
            Code.UNSUPPORTED_FORMAT, Severity.BLOCKING,
            f"{suffix} is not supported: convert to .docx, .pdf or .txt (legacy binary formats are "
            "not parsed, and guessing at them is how a parser invents structure)"))
    else:
        raise ParseFailure(ParseIssue(Code.UNSUPPORTED_FORMAT, Severity.BLOCKING, f"unknown extension: {suffix or '(none)'}"))

    if not out.text.strip():
        raise ParseFailure(ParseIssue(Code.NO_TEXT_LAYER, Severity.BLOCKING, "extraction produced no text"))
    return out
