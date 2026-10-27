"""Competence-preserving perturbations — the fixtures M-2 needs.

A perturbation here is defined by its *effect on the evidence model*, not by its name:

    same `competence_hash`  +  different `surface_hash`

Every transform below changes presentation only. It never adds, removes or edits a fact: bullets keep
their wording, skills keep their spelling, dates keep their values. What changes is order, heading
vocabulary, bullet markers, and (for the ligature case) prose that produces no facts.

That constraint is what makes A2's stability test meaningful. If a transform accidentally changed a
fact, `competence_changed` would be True and the test would be measuring a different document — a
silent corruption that would look like a stability failure. `tests/test_evidence_model.py` asserts the
constraint for every transform, so a fixture bug fails loudly instead of producing a wrong number.
"""
from __future__ import annotations

import re

# Heading synonyms drawn from the same vocabulary the segmenter already accepts, so a rename changes
# the heading text without changing the canonical section kind.
HEADING_SYNONYMS = {
    "EXPERIENCE": "WORK HISTORY",
    "experience": "work history",
    "SKILLS": "CORE COMPETENCIES",
    "skills": "core competencies",
    "SUMMARY": "PROFILE",
    "summary": "profile",
    "EDUCATION": "QUALIFICATIONS",
    "education": "qualifications",
}

LIGATURES = {"fi": "\ufb01", "fl": "\ufb02", "ff": "\ufb00"}


def reorder_sections(text: str) -> str:
    """Move the SKILLS block after EDUCATION. Facts are untouched; order and spans are not.

    Fixed 2026-10-27, and the fix belongs to the fixture, not the parser: the split consumes the
    newline that precedes each heading, and the old reassembly joined the chunks with "". That glued
    one heading onto the end of the previous block ("...fewer late departuresEDUCATION"), which both
    destroyed a heading and added a fact. `data/gold/cv-20` (a document with no blank lines) is what
    exposed it: the measurement was reporting a stability failure that was a broken perturbation.
    """
    blocks = [b.strip("\n") for b in re.split(r"\n+(?=[A-Z][A-Z &/]{2,}$)", text, flags=re.M)]
    if len(blocks) < 3:
        return text
    head, *sections = blocks
    skills = [s for s in sections if re.match(r"(?i)^skills\b", s.strip())]
    rest = [s for s in sections if s not in skills]
    return "\n".join([head] + rest + skills)


def rename_headings(text: str) -> str:
    """Swap heading vocabulary for its synonym. Section kinds are preserved by design."""
    out = text
    for old, new in HEADING_SYNONYMS.items():
        out = re.sub(rf"(?m)^{re.escape(old)}\s*$", new, out)
    return out


def change_markers(text: str) -> str:
    """`* ` bullets become `- `. Bullet text — and therefore every bullet fact — is identical."""
    return re.sub(r"(?m)^\*\s+", "- ", text)


def add_typographic_damage(text: str, target_line: str = "SUMMARY") -> str:
    """Inject glyph-level damage into non-fact prose only.

    Tries a real ligature (`fi`/`fl`/`ff` → U+FB0x) and, if the prose has no such pair, inserts a soft
    hyphen (U+00AD) inside a long word instead. Both are artefacts a PDF extraction produces; both are
    folded by `normalize()`; neither touches a bullet, a skill or a date, so competence is preserved.

    Restricted to the SUMMARY block for exactly that reason: bullets and skills produce facts, so
    damaging them would change competence and invalidate the comparison.
    """
    lines = text.split("\n")
    in_summary = False
    for i, line in enumerate(lines):
        if line.strip().upper().startswith(target_line):
            in_summary = True
            continue
        if in_summary and line.strip() and line.strip().isupper():
            break
        if in_summary and line.strip():
            for plain, glyph in LIGATURES.items():
                if plain in line:
                    lines[i] = line.replace(plain, glyph, 1)
                    return "\n".join(lines)
            for word in sorted(line.split(), key=len, reverse=True):
                if len(word) >= 5 and word.isalpha():
                    lines[i] = line.replace(word, word[:3] + "\u00ad" + word[3:], 1)
                    return "\n".join(lines)
    return text


TRANSFORMS = {
    "reorder_sections": reorder_sections,
    "rename_headings": rename_headings,
    "change_markers": change_markers,
    "add_typographic_damage": add_typographic_damage,
}
