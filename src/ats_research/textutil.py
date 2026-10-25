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

TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9.+#/-]*[a-z0-9]|[a-z0-9]", re.ASCII)
_WS_RE = re.compile(r"[ \t\u00a0]+")
_NL_RE = re.compile(r"\n{3,}")
_SENT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9])")

SECTION_HEADINGS = {
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
    """Lowercase word tokens.

    LIMITATION (measured 2026-10-25): TOKEN_RE is compiled with re.ASCII, so non-ASCII
    letters are separators, not letters. "Développeur" tokenises as ['d', 'veloppeur'].
    Any non-English resume is shredded by this. Fixing it is increment A1; until then
    this module is English-only, which contradicts the multilingual evidence in the
    research corpus (German resumes arXiv 2609.22188, French pipeline in JobScout,
    5-language JobResQA arXiv 2601.23183).
    """
    return TOKEN_RE.findall(text.lower())


def content_words(text: str, stop: set[str] | None = None) -> list[str]:
    """Tokens minus stopwords and minus single characters.

    LIMITATION (measured): dropping len==1 tokens makes the skill "C" invisible to the
    whole lexical layer -- content_words("C, Python, Go") has no 'c'. A skill list is
    exactly where single-character tokens are meaningful, so this must become a
    stopword-list decision, not a length rule. Increment A1.
    """
    stop = stop or set()
    return [t for t in tokenize(text) if t not in stop and len(t) > 1]


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


def bullets_of(text: str) -> list[str]:
    """Marker-prefixed lines only (*, -, bullet glyphs) longer than 12 characters.

    LIMITATION (measured): a real achievement written as a plain line --
    "Led a team of nine engineers to ship the platform" -- returns []. Resumes rendered
    from CSS list-styling or a table layout lose their markers during PDF extraction,
    which is precisely the damage this module is supposed to survive. Increment A1.
    """
    out = []
    for line in text.split("\n"):
        s = line.strip()
        if not s:
            continue
        if s.startswith(("*", "-", "\u2022", "\u25cf", "\u00b7")):
            body = s.lstrip("*-\u2022\u25cf\u00b7 ").strip()
            if len(body) > 12:
                out.append(body)
    return out


def detect_sections(text: str) -> dict[str, str]:
    """Split a flat resume stream into named sections using heading vocabulary.

    LIMITATION (measured): the first heading of each kind wins and later ones are
    discarded -- "SUMMARY / EXPERIENCE / SUMMARY" yields only ['summary', 'experience'],
    silently dropping the second summary block. Section bodies are also sliced by line
    order, so a two-column resume whose headings interleave with content will be cut at
    the wrong place. Increment A1.
    """
    lines = [ln for ln in text.split("\n")]
    idx: list[tuple[str, int]] = []
    for i, ln in enumerate(lines):
        key = heading_of(ln)
        if key and not any(key == k for k, _ in idx):
            idx.append((key, i))
    if not idx:
        return {"unstructured": text}
    out: dict[str, str] = {}
    for n, (key, i) in enumerate(idx):
        end = idx[n + 1][1] if n + 1 < len(idx) else len(lines)
        body = "\n".join(lines[i + 1:end]).strip()
        out[key] = body if body else out.get(key, "")
    return out


def heading_of(line: str) -> str | None:
    """Exact heading match, else a fuzzy match on any short ALL-CAPS/Title line that
    contains a heading word longer than 5 characters. The fuzzy branch is why
    'Selected Publications' maps to `projects` and why an over-eager match is possible;
    no source measures heading-recognition accuracy, so this is [HYPOTHESIS]-grade
    engineering, not a validated parser."""
    s = line.strip()
    if not s or len(s) > 46 or s.endswith((".", ";", ",", ":")) and len(s.split()) > 4:
        return None
    plain = s.strip(" :#*_-\t").lower()
    if not plain or len(plain.split()) > 4:
        return None
    for key, names in SECTION_HEADINGS.items():
        if plain in names:
            return key
    # ALL CAPS / Title-ish short line containing a heading word
    if len(plain.split()) <= 3 and s[:1].isupper():
        for key, names in SECTION_HEADINGS.items():
            if any(w in plain for w in names if len(w) > 5):
                return key
    return None


def looks_multicolumn(text: str) -> bool:
    """Heuristic: many lines carry two aligned text runs.

    PRECONDITION AND DEFECT (measured 2026-10-25): both detectors need a tab or a run of
    >=4 spaces, and normalize() collapses tabs and multi-space runs to one space. On a
    genuinely tab-separated two-column resume this returns False after normalize() and
    even before it on the sample tested -- i.e. as wired it is a dead feature that will
    always report "single column". The fix (A1) is to run this on the raw extraction and
    keep the raw text available, not to tune the 0.30 threshold, which is unsourced.
    """
    lines = [ln for ln in text.split("\n") if ln.strip()]
    if len(lines) < 8:
        return False
    hits = 0
    for ln in lines:
        runs = re.findall(r"\S[^\t]{0,40}\t[^\t]+", ln)
        wide = re.findall(r"\S{2,}\s{4,}\S{2,}", ln)
        if runs or (len(wide) >= 1 and len(ln) > 45 and len(ln.split()) >= 5):
            hits += 1
    return hits / max(1, len(lines)) > 0.30


def term_frequencies(tokens: list[str]) -> Counter:
    return Counter(tokens)
