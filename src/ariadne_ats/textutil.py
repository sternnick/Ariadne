"""Text handling that imitates what a parser sees, not what a human sees.

A resume rendered to PDF is re-extracted as a flat stream of glyphs. Reading order can be
wrong, column boundaries disappear, and soft hyphens or ligatures survive. Everything in
this module assumes the text is already that damaged stream.
"""
from __future__ import annotations

import re
import unicodedata
from collections import Counter

# Ligatures and substitutions that survive PDF text extraction and break token equality.
_LIGATURES = {
    "\ufb00": "ff", "\ufb01": "fi", "\ufb02": "fl", "\ufb03": "ffi",
    "\ufb04": "ffl", "\ufb05": "st", "\ufb06": "st",
    "\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"',
    "\u2013": "-", "\u2014": "-", "\u2012": "-", "\u2212": "-",
    "\u00a0": " ", "\u202f": " ", "\u200b": "", "\ufeff": "", "\u00ad": "",
    "\u2022": "* ", "\u25cf": "* ", "\u25aa": "* ", "\u25e6": "* ", "\u00b7": "* ",
}
_TRANS = {ord(k): v for k, v in _LIGATURES.items()}

# Unicode-aware. The earlier pattern used re.ASCII, so "Développeur" tokenised as ['d','veloppeur']
# and any non-English CV was shredded (audit P1). A token may contain dots, plus signs, hashes and
# slashes (c++, c#, .net, ci/cd) and may END in + or # for exactly those cases.
TOKEN_RE = re.compile(r"[^\W_](?:[\w.+#/-]*[^\W_+#])?", re.UNICODE)
_WS_RE = re.compile(r"[ \t\u00a0]+")
_NL_RE = re.compile(r"\n{3,}")
_SENT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9])")

SECTION_HEADINGS = {
    # Job-description sections (A1). A JD is a list of asks; these heading names let the segmenter
    # find them. They are vocabulary, not a model of the employer.
    # Deliberately NOT "qualifications": on a CV that heading means education, and the segmenter
    # resolves a line to exactly one kind. Version 1 of this vocabulary mapped QUALIFICATIONS to
    # requirements and silently swallowed the EDUCATION block (caught by the perturbation test:
    # facts 15 -> 14, the graduation year vanished).
    "requirements": ["requirements", "must have", "required", "about you", "who you are",
                     "what you bring"],
    "responsibilities": ["responsibilities", "what you will do", "the role", "your role", "duties",
                         "day to day"],
    "contact": ["contact", "contact information", "personal details", "personal information"],
    "summary": ["summary", "professional summary", "profile", "about me", "objective",
                "career objective", "career summary", "highlight of qualifications"],
    "skills": ["skills", "technical skills", "core competencies", "core skills",
               "areas of expertise", "technologies", "tools", "expertise", "skill set"],
    "experience": ["experience", "work experience", "professional experience",
                   "employment", "employment history", "work history", "career history",
                   "relevant experience"],
    "projects": ["projects", "selected projects", "personal projects", "side projects",
                 "open source", "publications", "patents"],
    "education": ["education", "education & qualifications", "academic background",
                  "qualifications", "certifications", "certificates", "courses"],
    "languages": ["languages", "language skills"],
    "awards": ["awards", "honors", "achievements", "volunteer", "volunteering",
               "activities", "interests"],
}


def normalize(text: str) -> str:
    """NFKC + ligature/bullet folding + whitespace collapse. Idempotent."""
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)
    text = text.translate(_TRANS)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = "\n".join(_WS_RE.sub(" ", ln).rstrip() for ln in text.split("\n"))
    return _NL_RE.sub("\n\n", text).strip()


def tokenize(text: str) -> list[str]:
    """Lowercase word tokens, Unicode-aware.

    Fixed in A1 (2026-10-25): the previous pattern was compiled with `re.ASCII`, which made every
    non-ASCII letter a separator ("Développeur" -> ['d', 'veloppeur']). Multilingual input is a stated
    requirement (docs/02 §2.6), so this is a correctness fix, not a nicety.
    """
    return [t.lower() for t in TOKEN_RE.findall(text)]


def content_words(text: str, stop: set[str] | None = None) -> list[str]:
    """Tokens minus stopwords, minus punctuation, and minus non-letter single characters.

    Fixed in A1 (2026-10-25): the previous rule dropped every `len == 1` token, which made the skill
    "C" invisible to the whole lexical layer (audit P2). The rule is now about *kind*, not length: a
    single **letter** survives, a single digit or symbol does not.
    """
    stop = stop or set()
    out: list[str] = []
    for t in tokenize(text):
        if t in stop:
            continue
        if len(t) == 1 and not t.isalpha():
            continue
        out.append(t)
    return out


def sentences(text: str) -> list[str]:
    out = []
    for para in text.split("\n"):
        para = para.strip()
        if not para:
            continue
        out.extend(s.strip() for s in _SENT_RE.split(para) if s.strip())
    return out


def ngrams(tokens: list[str], n: int) -> list[str]:
    if n == 1:
        return tokens
    if len(tokens) < n:
        return [" ".join(tokens)] if tokens else []
    return [" ".join(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]


def term_frequencies(tokens: list[str]) -> Counter:
    return Counter(tokens)
