"""Field extraction: the lines of a CV that a parser is actually judged on.

WHY THIS MODULE EXISTS
----------------------
Before 2026-10-27 the ledger emitted `bullet`, `skill` and `date` facts and nothing else, while
`KINDS`, the resume schema and `to_resume_json()` all named `role`, `employer`, `contact` and
`summary` fields. The consequence was invisible in the code and total in the output: `work[0].position`
was always `""`, `basics.name`/`basics.email` were always `""`, and the gold-standard benchmark added in
the same round (`data/gold/`) measured employer and title extraction at 0.0 recall. A field that the
interface names and the implementation never fills is worse than a missing field, because the reader
of the JSON cannot tell "absent" from "empty".

RULES, AND THE LIMIT OF THEM
----------------------------
Every rule here is lexical and every one of them *abstains* rather than guesses:

* **contact**: email / URL / phone-shaped fragments, read from the **contact block only** (the lines
  before the first heading, or a section whose heading says `contact`). Reading emails from the whole
  document would turn a reference's address into the candidate's address; `data/gold/cv-19` is that
  test and `cv-14` proves a postal address is a location, not a channel.
* **name**: the first contact-block line that is not a channel and has the shape of a personal name.
* **role / employer**: from a role line in an `experience` section: a line with a date span and at
  least two segments separated by `,`, `|`, tab, a spaced dash, or an `X at Y` form. Title-first is the
  convention assumed; `cv-11` is the labelled key-value form (`Role: … Company: …`). One segment plus a
  date is *ambiguous* and yields no fact plus a `ROLE_LINE_AMBIGUOUS` issue: the alternative is a
  guess that reads as data.
* **dates**: years, and only years inside an `experience` or `education` section. A year in a sentence
  ("joined the field in 2003") is not an employment date; `cv-15` forbids it.

Nothing here is a *model*. Vocabulary and separators are engineering defaults, calibrated against the
gold set and measured by `scripts/bench.py`; the numbers, not this docstring, are the claim.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .errors import Code, ParseReport, Severity
from .segment import Section

EMAIL_RE = re.compile(r"\b[\w.+-]+@(?:[\w-]+\.)+[A-Za-z]{2,}\b")
URL_RE = re.compile(
    r"\b(?:(?:https?://|www\.)[\w.-]+(?:/[\w./~%+-]*)?"
    r"|(?:github|gitlab|bitbucket|linkedin|x|twitter|medium|stackoverflow)\.com/[\w./-]+)",
    re.I,
)
PHONE_RE = re.compile(r"^\+?[\d][\d().\s-]{6,}[\d]$")

# Fragments of a contact block are separated by these, never by a plain space: "+358 40 1234567" and
# "Via Roma 12" both contain spaces that belong inside a value.
_FRAGMENT_RE = re.compile(r"[|\t,;\u00b7\u2022*]| {2,}")

_YEAR = r"(?:19|20)\d{2}"
_PRESENT = (r"present|current|today|now|heute|heden|inniu|actualidad|actuel|"
            r"s[ií]mera|σήμερα|ongoing")
# A date span, as it survives extraction: "2019-2024", "2018 - Present", "03/2019 - heute",
# "2013/2019", "2016 - present". The separators are read literally, not semantically.
_DATE_SPAN_RE = re.compile(
    rf"(?:\b\d{{1,2}}/)?\b{_YEAR}\b[\s.\-/]{{0,5}}(?:\b\d{{1,2}}/)?\b(?:{_YEAR}|{_PRESENT})\b",
    re.I,
)
_DATE_SINGLE_RE = re.compile(rf"(?:\b\d{{1,2}}/)?\b{_YEAR}\b")
_DATE_TAIL_RE = re.compile(rf"\b(?:{_YEAR}|{_PRESENT})\b", re.I)

# `X at Y` is the one English prose form where the employer follows the title.
_AT_FORM_RE = re.compile(r"^(?P<title>.+?)\s+at\s+(?P<employer>.+?)\.?$", re.I)
# `period|dates` are in the alternation for one reason: a label the parser does not know survives in
# the *value* of the label before it ("Saxen AB          Period:" on data/gold/cv-11), which the gold
# set scored as a wrong employer. Unknown labels have to be consumed, not ignored.
_LABEL_RE = re.compile(
    r"(?P<label>role|title|position|job title|company|employer|organisation|organization|firm|"
    r"location|period|dates?|duration)\s*:",
    re.I,
)
_LABEL_ORDER = [
    ("title", ("role", "title", "position", "job title")),
    ("employer", ("company", "employer", "organisation", "organization", "firm")),
]
# Field separators, written as escapes so no gate can "helpfully" fold the dash glyphs
# into one another: a tab, a pipe, a spaced dash of any width, or a comma.
_SEGMENT_SPLIT_RE = re.compile(r"[\t|]|\s*[-\u2013\u2014]\s+|,\s+|\s+,")

# Words that appear in a CV headline. A line made of these is a job title, not a name, and reading
# one as a name puts the wrong string in `basics.name`: which is worse than abstaining. Same shape
# of rule as the heading vocabulary: a list, measured against data/gold/cv-24, no claims beyond it.
TITLE_WORDS = {"engineer", "engineering", "manager", "analyst", "developer", "architect",
               "administrator", "consultant", "specialist", "director", "scientist", "technician",
               "designer", "programmer", "officer", "associate", "assistant", "intern", "graduate",
               "devops", "security", "software", "senior", "junior", "staff", "principal",
               "platform", "backend", "frontend", "full-stack"}


NAME_PARTICLES = {"de", "den", "der", "van", "von", "di", "da", "del", "della", "la", "le", "ten",
                  "ter", "bin", "ibn", "al", "dos", "das", "y", "e", "af", "av", "of"}


# A personal-name line: letters, spaces, hyphens, apostrophes and full stops only, 2 to 4 tokens,
# each token capitalised or fully upper-cased (an all-caps CV is a formatting choice, not a fact).
_NAME_JUNK_RE = re.compile(r"\d|@|https?|www\.|\.(com|net|org|de|fr|es|it|nl|ie|gr|hu|pl|pt|dk|se|no|fi|tr)\b", re.I)


@dataclass
class FieldHit:
    kind: str            # contact | name | role | employer | summary
    value: str
    span: tuple[int, int]
    confidence: float
    derived_from: str
    channel: str = ""    # email | url | phone | "" for non-contact kinds


@dataclass
class RoleHit:
    title: str
    employer: str
    start: str
    end: str
    span: tuple[int, int]
    bullets: list[str] = field(default_factory=list)
    ambiguous: bool = False


def _spans_of(text: str, needles: list[str]) -> dict[str, tuple[int, int]]:
    out: dict[str, tuple[int, int]] = {}
    low = text.lower()
    for n in needles:
        if not n or n in out:
            continue
        i = low.find(n.lower())
        out[n] = (max(0, i), max(0, i) + len(n))
    return out


# --------------------------------------------------------------------------- contact block


def contact_block(sections: list[Section]) -> str:
    """The lines a CV puts its own channels in: the preamble, or a `contact` section.

    Deliberately *not* the whole document. An email inside a REFERENCES block belongs to the
    reference, and `data/gold/cv-19` is the labelled case that keeps this rule honest.
    """
    parts: list[str] = []
    for sec in sections:
        if sec.kind == "preamble":
            parts.append(sec.body)
        elif sec.kind == "contact":
            parts.append(sec.body)
        elif sec.kind in ("summary", "experience", "skills", "education", "projects",
                          "unstructured", "requirements", "responsibilities", "languages", "awards"):
            if sec.kind == "unstructured":
                parts.append(sec.body)      # no headings at all: the whole thing is the preamble
            break
    for sec in sections:
        if sec.kind == "contact":
            parts.append(sec.body)
    return "\n".join(p for p in parts if p)


def contacts(text: str, confidence: float = 0.9) -> list[FieldHit]:
    """Email, URL and phone fragments from a contact block, each with its span in `text`."""
    hits: list[FieldHit] = []
    seen: set[str] = set()

    def add(kind_channel: str, value: str) -> None:
        value = value.strip(" \t.,;()")
        key = value.lower()
        if not value or key in seen:
            return
        seen.add(key)
        idx = text.lower().find(key)
        hits.append(FieldHit("contact", value, (max(0, idx), max(0, idx) + len(value)),
                             confidence, "contact-block", kind_channel))

    for line in text.split("\n"):
        if not line.strip():
            continue
        for channel, rx in (("email", EMAIL_RE), ("url", URL_RE)):
            for m in rx.finditer(line):
                add(channel, m.group(0))
        # What is left after the channels are removed may be a phone number.
        residue = EMAIL_RE.sub(" ", URL_RE.sub(" ", line))
        for frag in _FRAGMENT_RE.split(residue):
            frag = frag.strip(" \t()-")
            if PHONE_RE.match(frag):
                add("phone", re.sub(r"\s+", " ", frag))
    return hits


_NAME_TOKEN_RE = re.compile(r"[^\W\d_]+(?:['.\u2019\u2019-][^\W\d_]+)*", re.UNICODE)


def person_name(text: str, confidence: float = 0.75) -> FieldHit | None:
    """The candidate's name, from the first contact-block line that is not a channel.

    The rule stops at the first non-channel line: if that line is not name-shaped, the answer is
    *no name*, not "keep looking". Two consequences, both measured rather than assumed.

    * Single-letter and lower-case particles are names, not noise: "Ó Briain" (Irish, cv-18) and
      "de Vries" (Dutch, cv-20) both failed the first version of this rule and both are real names.
    * A city line is not a name. Stopping at the first line is what keeps "Berlin" or "New York" out
      of `basics.name`; a CV that puts its name anywhere other than ahead of its channels is outside
      this rule, which `docs/08` records as unmeasured rather than as supported.
    """
    for line in text.split("\n"):
        raw = line.strip()
        if not raw:
            continue
        if EMAIL_RE.search(raw) or URL_RE.search(raw):
            continue
        residue = EMAIL_RE.sub(" ", URL_RE.sub(" ", raw))
        if all(PHONE_RE.match(f.strip(" \t()-")) for f in _FRAGMENT_RE.split(residue)
               if f.strip(" \t()-")) and _FRAGMENT_RE.split(residue):
            continue                      # a line of phone numbers is not a name line
        if _FRAGMENT_RE.search(raw):
            return None                   # separators on the first line: a data row, not a name
        tokens = raw.split()
        if not (2 <= len(tokens) <= 5):
            return None
        if any(t.lower() in TITLE_WORDS for t in tokens):
            return None                   # "SENIOR SECURITY ENGINEER" is a headline (cv-24)
        if any(not _NAME_TOKEN_RE.fullmatch(t) for t in tokens):
            return None
        if not any(len(t) >= 2 and (t[0].isupper() or t.isupper()) for t in tokens):
            return None
        if not all(t[0].isupper() or t.isupper() or t.lower() in NAME_PARTICLES or len(t) == 1
                   for t in tokens):
            return None
        idx = text.find(raw)
        return FieldHit("name", raw, (max(0, idx), max(0, idx) + len(raw)), confidence, "contact-block")
    return None


# --------------------------------------------------------------------------- role lines


# --- role-line ordering: which segment is the employer -------------------------------------------
# Two vocabularies do this job, and they are deliberately separate from TITLE_WORDS (which guards the
# *name* rule, where a false positive puts the wrong string in `basics.name`). Here a wrong answer puts
# the wrong employer in `work[].name`, and the alternative to deciding is abstaining.
#   evidence that a segment is a job title
# Words a *role* contains that a company name does not. That filter is the whole list, and it is
# measured rather than intuited: "data", "security", "analytics", "software" and "platform" were in
# the first version and each one broke a fixture, because they are what employers are called -
# "Meridian Data", "Danubia Data", "Norrsen Security" all read as titles and the fields came out
# transposed by the rule that was meant to stop transposing them.
ROLE_TITLE_EVIDENCE = {"engineer", "engineering", "manager", "management", "analyst", "developer",
                       "architect", "administrator", "consultant", "specialist", "director",
                       "scientist", "technician", "designer", "programmer", "officer", "associate",
                       "assistant", "intern", "graduate", "lead", "head", "team", "devops", "sre",
                       "qa", "senior", "junior", "staff", "principal", "backend", "frontend",
                       "full-stack", "scrum", "agile", "product", "project", "program"}
#   evidence that a segment is a company: a legal form or a corporate noun. A company name is the only
#   thing in a CV that says "AB", "GmbH", "Oyj" or "& Co".
COMPANY_SUFFIX_RE = re.compile(
    r"(?i)\b(ab|gmbh|kg| AG|sas|s.a.s.|sl|sl\.?|ltd|limited|inc|llc|plc|ag|oy|oyj|bv|nv|as|asa|"
    r"co|corp|corporation|company|partners|holdings|group|bank|capital| Ventures|"
    r"systems|technologies|digital|analytics|solutions|consulting|labs|works|media|finance|"
    r"logistics|industries|electronic|electronics|energy|telecom|insurance)\b")


def _title_score(segment: str) -> int:
    """+1 if the segment looks like a job title, -1 if it looks like a company, 0 if it says neither."""
    words = re.findall(r"[^\W\d_]+", segment.lower(), re.UNICODE)
    score = 0
    if any(w in ROLE_TITLE_EVIDENCE for w in words):
        score += 1
    if COMPANY_SUFFIX_RE.search(segment):
        score -= 1
    return score


def _order_segments(segs: list[str]) -> tuple[str, str] | None:
    """(title, employer), or None when the segments carry no evidence about their order.

    cv-21 ("Norra Bank - Senior Engineer") made the old assumption - first segment is the title - cost
    two false positives and two false negatives on one document, and the same class of document is the
    most common reason a role line could be transposed. Rather than guess a second convention, the
    segments are scored: the one that reads as a job title is the title, the one that reads as a
    company is the employer. When the scores **conflict** - two company-looking names, or two
    title-looking names - the answer is no facts, with a `ROLE_LINE_AMBIGUOUS` issue saying why. When
    they are merely **silent** (no evidence on either side) the documented title-first default stands:
    silence is not evidence of an unfamiliar convention, and abstaining there would be a new failure
    invented in the name of caution.
    """
    a, b = _title_score(segs[0]), _title_score(segs[1])
    if a == b == 0:
        # Neither segment says anything either way, which is the common case for a non-English title
        # beside a company name the vocabulary has never seen ("PrÃ­omhinnealtÃ³ir, Coho Networks").
        # The documented default stands: title-first is the convention this corpus measures. Abstaining
        # here would turn a convention into a new failure, and docs/08 M-6 records the gap.
        return segs[0], segs[1]
    if a == b:
        return None                 # both read as titles, or both as companies: no answer
    return (segs[0], segs[1]) if a > b else (segs[1], segs[0])


def _strip_date(line: str) -> tuple[str, str, str]:
    """Return (line without its date span, start marker, end marker). End may be `present`-shaped."""
    m = _DATE_SPAN_RE.search(line)
    if m:
        span = m.group(0)
        start = _DATE_SINGLE_RE.search(span)
        tail = span[start.end():] if start else span
        end_hit = _DATE_TAIL_RE.search(tail)
        return (line[:m.start()] + " " + line[m.end():],
                start.group(0) if start else "", end_hit.group(0) if end_hit else "")
    m = _DATE_SINGLE_RE.search(line)
    if m:
        return line[:m.start()] + " " + line[m.end():], m.group(0), ""
    return line, "", ""


def _labelled(residual: str) -> tuple[str, str] | None:
    """Parse `Role: X   Company: Y` (the table-read-as-text form)."""
    if not _LABEL_RE.search(residual):
        return None
    found = {m.group("label").lower(): (m.start(), m.end()) for m in _LABEL_RE.finditer(residual)}
    out = {"title": "", "employer": ""}
    ordered = sorted(found.items(), key=lambda kv: kv[1][0])
    for i, (label, (_s, end)) in enumerate(ordered):
        stop = ordered[i + 1][1][0] if i + 1 < len(ordered) else len(residual)
        value = residual[end:stop].strip(" \t-,.")
        for kind, labels in _LABEL_ORDER:
            if label in labels and not out[kind]:
                out[kind] = value
    return out["title"], out["employer"]


_DATE_ONLY_LINE_RE = re.compile(
    rf"^\s*(?:\b\d{{1,2}}/)?\b{_YEAR}\b[\s.\-/]{{0,5}}(?:(?:\b\d{{1,2}}/)?\b(?:{_YEAR}|{_PRESENT}))?\b[\s.,-]*$",
    re.I,
)


def _dates_below(lines: list[str]) -> dict[int, tuple[str, str]]:
    """Indices of role lines whose date sits on the *following* line, paired with that date.

    cv-22 is the labelled case: the two-column and table-derived layouts that put the role on one line
    and "2019 - 2024" alone underneath produced no role fact at all, because the rule required the date
    and the fields to share a line - while the years themselves were still extracted as dates elsewhere,
    which is the combination that makes the loss silent.

    The pairing is deliberately unforgiving: the date line must contain a date and nothing else, and the
    line above it must be a real line that is not a bullet and not an all-caps heading. A blank line or
    a bullet above stops the search rather than reaching further back, because reaching further back is
    how a date gets attached to the wrong employer.
    """
    out: dict[int, tuple[str, str]] = {}
    for j, raw in enumerate(lines):
        if not _DATE_ONLY_LINE_RE.match(raw):
            continue
        _, start, end = _strip_date(raw.strip())
        if not start or not end:
            continue
        for i in range(j - 1, max(-1, j - 3), -1):
            above = lines[i].strip()
            if not above or above.startswith(("*", "-", "\u2022", "\u00b7")):
                break                      # blank or bullet: do not reach past it
            if above.isupper() and len(above.split()) <= 4:
                break                      # a heading, not a role line
            out[i] = (start, end)
            break
    return out


def role_lines(body: str, report: ParseReport | None = None,
               confidence: float = 0.7) -> list[RoleHit]:
    """Every role line of one experience section, in document order.

    A line qualifies when it carries a date span and either a labelled form or two or more segments.
    A date plus a single segment is reported as ambiguous and produces no fact: that is the difference
    between an abstention and a wrong employer, and `data/gold/cv-08` is the labelled example.
    """
    report = report or ParseReport()
    hits: list[RoleHit] = []
    lines = body.split("\n")
    below = _dates_below(lines)
    for i, raw in enumerate(lines):
        line = raw.strip()
        if len(line) < 10 or line.startswith(("*", "-", "\u2022", "\u00b7")):
            continue
        residual, start, end = _strip_date(line)
        if not (start or end):
            paired = below.get(i)
            if not paired:
                continue
            residual, start, end = line, paired[0], paired[1]
        at = _AT_FORM_RE.match(residual.strip())
        if at:
            title, employer = at.group("title").strip(), at.group("employer").strip()
        else:
            labelled = _labelled(residual)
            if labelled:
                title, employer = labelled
            else:
                segs = [s.strip(" \t") for s in _SEGMENT_SPLIT_RE.split(residual) if s.strip(" \t")]
                if len(segs) < 2:
                    report.add(Code.ROLE_LINE_AMBIGUOUS, Severity.DEGRADED,
                               f"'{line[:60]}' has a date but one field-shaped segment; no employer or "
                               "title extracted rather than a guess")
                    continue
                ordered = _order_segments(segs[:2])
                if ordered is None:
                    report.add(Code.ROLE_LINE_AMBIGUOUS, Severity.DEGRADED,
                               f"'{line[:60]}' names two segments but neither reads as a job title; "
                               "employer and title left unextracted rather than ordered by guesswork")
                    continue
                title, employer = ordered
        if not title or not employer:
            report.add(Code.ROLE_LINE_AMBIGUOUS, Severity.DEGRADED,
                       f"'{line[:60]}' resolved to a partial role line; left unextracted")
            continue
        hits.append(RoleHit(title, employer, start, end, (0, 0), [], False))

    # Attach the bullets that follow each role line to that role, in document order.
    if hits:
        assigned: list[list[str]] = [[] for _ in hits]
        current = -1
        for raw in lines:
            stripped = raw.strip()
            for n, h in enumerate(hits):
                if h.title in stripped and h.employer in stripped:
                    current = n
                    break
            else:
                if stripped.startswith(("*", "-", "\u2022", "\u00b7")) and current >= 0:
                    assigned[current].append(stripped.lstrip("".join(("*", "-", "\u2022", "\u00b7")) + " ").strip())
                elif current >= 0 and len(stripped) > 20 and not stripped.isupper():
                    assigned[current].append(stripped)
        for h, bullets in zip(hits, assigned):
            h.bullets = [b for b in bullets if b]
    return hits


# --------------------------------------------------------------------------- summary


def summary_statement(sections: list[Section], confidence: float = 0.6) -> FieldHit | None:
    """The first non-heading paragraph of a `summary` section, verbatim."""
    for sec in sections:
        if sec.kind != "summary":
            continue
        for line in sec.body.split("\n"):
            s = line.strip()
            if len(s) > 12 and not s.isupper():
                idx = sec.body.find(s)
                return FieldHit("summary", s, (sec.start + idx, sec.start + idx + len(s)),
                                confidence * sec.confidence, "text")
    return None


__all__ = ["FieldHit", "RoleHit", "contact_block", "contacts", "person_name", "role_lines",
           "summary_statement", "EMAIL_RE", "URL_RE", "PHONE_RE"]
