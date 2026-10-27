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
# A tab survives normalisation as exactly one tab. It is a column boundary, not whitespace
# ambiguity: collapsing it is what made the two-column role line in data/gold/cv-03 read as one
# undifferentiated segment (audit P3 again, in a different function). Spaces collapse; tabs persist.
_WS_RE = re.compile(r"[ \u00a0]+")
_TAB_RUN_RE = re.compile(r"[ \t\u00a0]*\t[ \t\u00a0]*")
_NL_RE = re.compile(r"\n{3,}")
_SENT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9])")

SECTION_HEADINGS = {
    # Job-description sections (A1). A JD is a list of asks; these heading names let the segmenter
    # find them. They are vocabulary, not a model of the employer.
    # Deliberately NOT "qualifications": on a CV that heading means education, and the segmenter
    # resolves a line to exactly one kind. Version 1 of this vocabulary mapped QUALIFICATIONS to
    # requirements and silently swallowed the EDUCATION block (caught by the perturbation test:
    # facts 15 -> 14, the graduation year vanished).
    #
    # The non-English entries are the headings of the languages the gold set has fixtures for
    # (data/gold/manifest.json: en, de, fr, es, el, ga), added on 2026-10-27 after that benchmark
    # measured an English-only vocabulary at 0.0 recall on every non-English fixture: the section was
    # never found, so nothing downstream could run. This is a heading list, not a language model, and
    # it is exactly as complete as its fixtures prove it. A language with no fixture has no vocabulary
    # here and is recorded as unknown in docs/08, not silently assumed.
    # All entries are the LOWER-CASED form, because `_classify` folds case first.
    "requirements": ["requirements", "must have", "required", "about you", "who you are",
                     "what you bring"],
    "responsibilities": ["responsibilities", "what you will do", "the role", "your role", "duties",
                         "day to day"],
    "contact": ["contact", "contact information", "personal details", "personal information"],
    "summary": ["summary", "professional summary", "profile", "about me", "objective",
                "career objective", "career summary", "highlight of qualifications",
                "profil", "próifíl", "perfil", "προσοντικα"],
    "skills": ["skills", "technical skills", "core competencies", "core skills",
               "areas of expertise", "technologies", "tools", "expertise", "skill set",
               "kenntnisse", "fähigkeiten", "compétences", "habilidades", "δεξιότητες",
               "teicneolóiste"],
    "experience": ["experience", "work experience", "professional experience",
                   "employment", "employment history", "work history", "career history",
                   "relevant experience",
                   "berufserfahrung", "expérience professionnelle", "experiencia",
                   "εμπειρικη εργοσειρα", "taithí oibre"],
    "projects": ["projects", "selected projects", "personal projects", "side projects",
                 "open source", "publications", "patents"],
    "education": ["education", "education & qualifications", "academic background",
                  "qualifications", "certifications", "certificates", "courses",
                  "ausbildung", "formation", "formación", "σπουδες", "oideachas"],
    "languages": ["languages", "language skills"],
    "awards": ["awards", "honors", "achievements", "volunteer", "volunteering",
               "activities", "interests"],
}


def fold(text: str) -> str:
    """Casefold and strip diacritics, for *heading matching only*.

    Two facts make this necessary. Accented headings are the norm in French, German, Spanish, Irish
    and Greek, so an ASCII-only fold loses them (audit P1, same class). And Greek is harsher still:
    capitalising "δεξιότητες" yields "ΔΕΞΙΟΤΗΤΕΣ" - the accents are simply gone - so a vocabulary
    keyed on the accented dictionary form misses every all-caps Greek heading. Both were measured by
    data/gold/ on 2026-10-27, not theorised.

    Nothing in the output is folded: a fact value keeps its accents, so matching a heading accent-
    insensitively never rewrites a person's text.
    """
    decomposed = unicodedata.normalize("NFD", text.casefold())
    return unicodedata.normalize("NFC", "".join(c for c in decomposed
                                                if not unicodedata.combining(c)))


def normalize(text: str) -> str:
    """NFKC + ligature/bullet folding + whitespace collapse. Idempotent; tabs survive as tabs."""
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)
    text = text.translate(_TRANS)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = "\n".join(_WS_RE.sub(" ", _TAB_RUN_RE.sub("\t", ln)).rstrip() for ln in text.split("\n"))
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


_FOLDED_HEADINGS: dict[str, tuple[str, float]] = {}
for _kind, _names in SECTION_HEADINGS.items():
    for _name in _names:
        _FOLDED_HEADINGS.setdefault(fold(_name), (_kind, 0.0))
_FOLDED_LONG: list[tuple[str, str]] = [(fold(w), _k) for _k, _ws in SECTION_HEADINGS.items()
                                       for _w in _ws for w in _w.split() if len(w) > 5]


def heading_kind(line: str) -> tuple[str | None, float]:
    """Classify a heading line against the vocabulary: (kind, base confidence).

    Exact (after `fold`) is 0.9; a long vocabulary word appearing inside the line is 0.6. The rules
    and the numbers are `segment`'s; this function exists so the fold lives in one place.
    """
    from .segment import EXACT_CONFIDENCE, FUZZY_CONFIDENCE

    raw = line.strip()
    if not raw or len(raw) > 46:
        return None, 0.0
    plain = raw.strip(" :#*_-").strip("\t").lower()
    if not plain or len(plain.split()) > 4:
        return None, 0.0
    hit = _FOLDED_HEADINGS.get(fold(plain))
    if hit:
        return hit[0], EXACT_CONFIDENCE
    if len(plain.split()) <= 3 and raw[:1].isupper():
        fplain = fold(plain)
        for word, kind in _FOLDED_LONG:
            if word in fplain:
                return kind, FUZZY_CONFIDENCE
    return None, 0.0
