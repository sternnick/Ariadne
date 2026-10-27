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
    # facts 15 -> 14, the graduation year vanished). The same trap exists in French: adding bare
    # "compétences" here hid cv-07's whole skills block, because on a CV it means skills. It lives
    # under `skills` now, and only the qualified French form stays here.
    #
    # The non-English entries are the headings of the languages the gold set has fixtures for
    # (data/gold/manifest.json: en, de, fr, es, el, ga), added on 2026-10-27 after that benchmark
    # measured an English-only vocabulary at 0.0 recall on every non-English fixture: the section was
    # never found, so nothing downstream could run. This is a heading list, not a language model, and
    # it is exactly as complete as its fixtures prove it. A language with no fixture has no vocabulary
    # here and is recorded as unknown in docs/08, not silently assumed.
    # All entries are the LOWER-CASED form, because `_classify` folds case first.
    "requirements": ["requirements", "must have", "required", "about you", "who you are",
                     "what you bring",
                     # jd-06 measured the English-only version of this list at "no requirements at
                     # all": the heading was never found, so no bullet was ever considered. Same
                     # shape and same limit as the other non-English entries - a list, no model.
                     "anforderungen", "voraussetzungen", "was sie mitbringen", "was du mitbringst",
                     "competences requises", "profil requis", "profil recherche",
                     "requisitos", "requisitos del puesto", "perfil buscado"],
    "responsibilities": ["responsibilities", "what you will do", "the role", "your role", "duties",
                         "day to day", "ihre aufgaben", "hre aufgaben", "vos taches",
                         "tus responsabilidades", "funktionen"],
    "contact": ["contact", "contact information", "personal details", "personal information"],
    "summary": ["summary", "professional summary", "profile", "about me", "objective",
                "career objective", "career summary", "highlight of qualifications",
                "profil", "próifíl", "perfil", "προσοντικα"],
    "skills": ["skills", "technical skills", "core competencies", "core skills",
               "areas of expertise", "technologies", "tools", "expertise", "skill set",
               "kenntnisse", "fähigkeiten", "kompetenzen", "compétences", "habilidades",
               "δεξιότητες", "teicneolóiste"],
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


# ------------------------------------------------------------------ skills, read as the table it is
# Skills blocks arrive in three shapes: a comma list, a bullet list, and - the one that used to fail -
# a two-column table read back as text ("Languages\tpython, go"). Splitting only on punctuation made
# the table produce one value per cell ("Languages", "python, go"), which the gold set scored on cv-23.
_SKILL_SEP_RE = re.compile(r"[,;/|]")
_SKILL_LIST_SEPARATORS = ",;/|"
# Words that name a *class* of skills. In a flattened table they are the row label, not a skill; a
# label this list has never seen survives as a skill, i.e. as a visible false positive rather than a
# silent loss. Same shape of rule as the heading vocabulary: a list, its limit stated.
_SKILL_ROW_LABELS = {"languages", "infrastructure", "data", "tools", "tooling", "frameworks",
                     "libraries", "databases", "platforms", "stack", "tech", "technologies",
                     "methods", "practices", "testing", "monitoring", "cloud", "other", "misc",
                     "miscellaneous", "certifications", "spoken", "programming", "development"}
_AND_PAIR_RE = re.compile(r"^([A-Za-z][\w.+#-]{1,20}) and ([A-Za-z][\w.+#-]{1,20})$")


def _split_skills(text: str) -> list[str]:
    """Split on `, ; / |`, but never inside brackets.

    "spreadsheets (excel, google sheets)" names one skill; splitting that comma is what made
    data/gold/cv-06 carry two parser-shaped labels instead of the single value a reader would write.
    Depth counting rather than a regex, because the nesting a CV produces is arbitrary and a regex for
    it would be a claim about parentheses this corpus does not need.
    """
    out: list[str] = []
    buf: list[str] = []
    depth = 0
    for ch in text:
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth = max(0, depth - 1)
        if depth == 0 and ch in _SKILL_LIST_SEPARATORS:
            out.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    out.append("".join(buf).strip())
    return [x for x in out if x]


def skill_items(text: str) -> list[str]:
    """The individual skills a skills block names, in document order.

    Three rules, each traceable to a fixture, and one refusal:

    * a row with a tab and a comma-separated second cell is **label + list**, so the label is dropped
      and the list is split (cv-23);
    * an item of the form `X and Y`, where both sides are single tokens, names two skills (cv-13:
      `* git and docker`). The single-token constraint is the whole point: "Design and implementation
      of distributed systems" is one skill-shaped phrase, not two, and splitting prose to raise recall
      would be tuning the corpus instead of reading it;
    * an item is kept when it has at least one letter and is at most 60 characters. The length floor is
      about kind, not size - the skill "C" is one character and must survive (cv-10, audit P2).

    What this does not solve: a table whose second column is a level rather than a list
    ("Python\tAdvanced") yields both cells, because nothing in the row says which column is the skill.
    That gap is stated in docs/02 2.7 rather than hidden in a vocabulary of level words.
    """
    cells: list[str] = []
    for line in text.split("\n"):
        raw = line.strip().strip("*\u00b7\u2022- \t")
        if not raw:
            continue
        if "\t" in raw:
            row = [c.strip() for c in raw.split("\t") if c.strip()]
            row = [_split_skills(c) for c in row]
            if (len(row) == 2 and len(row[1]) > 1
                    and row[0][0].lower().strip() in _SKILL_ROW_LABELS):
                cells += row[1]                              # row 0 named the class of the row
            else:
                for cell in row:
                    cells += cell
        else:
            cells += _split_skills(raw)
    items: list[str] = []
    for cell in cells:
        cell = cell.strip(" \t*\u00b7\u2022-")
        if not cell:
            continue
        pair = _AND_PAIR_RE.match(cell)
        if pair:
            items += [pair.group(1), pair.group(2)]
        else:
            items.append(cell)
    return [i for i in items if 1 <= len(i) <= 60 and any(ch.isalpha() for ch in i)]


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
    # A *fuzzy* heading candidate must carry no column or list separator. The line
    # "Languages\tpython, go" begins with an capitalised vocabulary word and is three tokens long, so
    # the loose path used to claim it as a `languages` **heading** - and everything after the tab
    # disappeared into a heading line. That, not the splitter, is why cv-23 lost its skills: a heading
    # is a boundary, and a line with columns in it is data. Exact matches are unaffected: "SKILLS" has
    # no separators to begin with.
    if len(plain.split()) <= 3 and raw[:1].isupper() and not any(c in raw for c in "\t,;|"):
        fplain = fold(plain)
        for word, kind in _FOLDED_LONG:
            if word in fplain:
                return kind, FUZZY_CONFIDENCE
    return None, 0.0
