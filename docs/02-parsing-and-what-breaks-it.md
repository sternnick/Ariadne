```
Last verified: 2026-10-27
Reviewed by:   Ariadne (principal)
Live surfaces: none (specs and papers; no vendor pricing or star counts depend on this page)
```

# 02 — Parsing, and what breaks it

The claim this document has to support is narrow and load-bearing for the whole product: **the
failure mode that matters is layout, and the damage happens before any model sees the text.**

## 2.1 The pipeline, as the literature describes it

Extraction → OCR fallback → layout/reading-order recovery → **section segmentation** → per-section
field extraction → normalisation to a controlled vocabulary. Evaluation is at **field level**
(exact-match / F1 / recruitment-similarity), not "accuracy" as one number. **A**, [EV-05], [EV-06],
[EV-23].

Two-stage architecture is the norm: a parser that extracts structured résumé data, then a separate
classifier for job–candidate suitability. **A**, [EV-06] (arXiv 1910.03089).

**Section segmentation is explicit and segment-aware**, and the paper that says so gives the reason:
"each model specializing in a specific resume segment", "field-specific weighting tailored to each
resume part", to overcome "diverse formats and structures" and "varied resume layouts". **A**,
[EV-05] (MSLEF, AICCSA 2025).

That is the single most useful sentence in the corpus for us: the literature treats *layout variation*
as the reason segmentation needs special handling, not as a presentation detail.

## 2.2 What the published numbers actually measure

| Number | What it really covers | Grade |
|---|---|---|
| "100 % parse accuracy" | **LinkedIn-format résumés only** (structured input), with 73 % on suitability in the same paper | **A**, [EV-06] |
| "+7 % Recruitment Similarity" | a segment-specialised ensemble vs the best single model | **A**, [EV-05] |
| "98 % character → ~85 % field" compounding | one vendor blog; no method published | **C**, [EV-23] |
| "~95 % accuracy" | universal marketing; the same source notes *every* tool claims it | **C**, [EV-23] |
| Any public parser leaderboard | **none found** | **U**, [EV-23] |

The 2019 "100 %" figure is routinely mis-cited as general accuracy. It is not; it is the easy regime.
This is why no accuracy target appears anywhere in our own docs.

## 2.3 The damage list, and which items we can actually evidence

| Failure mode | Evidence grade | Note |
|---|---|---|
| Multi-column reading order | **A** (implied by "varied resume layouts" + segment specialisation) | the mechanism (x-y projection, band detection) is standard engineering, **not** in our retrieved sources — do not cite it as fact |
| Tables / text boxes | **C** ([EV-26]: a career blog recommends avoiding them for Workday) | plausible, unverified officially |
| Headers/footers absorbing contact details | **C** ([EV-26], same blog) | same |
| Ligatures (`fi`/`fl`) and soft hyphens | **[HYPOTHESIS]** | standard PDF-extraction behaviour; we can test it here rather than cite it |
| Unmarked bullets (CSS list styling) | **[HYPOTHESIS]** | testable; our own `bullets_of` currently fails it (0×00 audit P4) |
| Scanned image PDFs → OCR | **B** ([EV-19]: JobScout runs tesseract FR+EN as a fallback) | OCR is a real rung, and it costs field accuracy |
| Non-Latin / accented text | **A** (by our own measurement, 0×00 audit P1) | our tokenizer currently destroys it |

**Rule derived from this table:** a font/ligature/encoding claim may be written as fact only after we
have produced the artefact ourselves. The repository therefore prefers "we measured X on this input"
over "PDFs usually do Y". `docs/00-audit.md` P1–P5 is the template.

## 2.4 What our own code does today (measured, not claimed)

From the audit's twelve probes, all reproducible:

| Probe | Result | Consequence |
|---|---|---|
| `tokenize("Développeur Full-Stack mit C++ und C")` | was `['d','veloppeur',…]`; **now** `['développeur','full-stack','mit','c','und','c']` | `re.ASCII` was shredding non-English text — **fixed in A1**, asserted by the multilingual token test |
| `content_words("C, Python, Go")` | was no `'c'`; **now** `['c','python','go']` | the skill **C** was invisible — **fixed in A1** (kind-based rule, not length) |
| multi-column detection | was dead (signals destroyed by `normalize()`); **now** `layout.analyze()` runs on raw text and returns `MULTICOLUMN_FLATTENED` + a ratio | the detector must run before normalisation — **fixed in A1** |
| unmarked achievement → bullet | was `[]`; **now** recognised by achievement shape | markers vanish when a layout flattens — **fixed in A1** |
| repeated heading | was dropped; **now** two segments + `SECTION_REPEATED` | **fixed in A1** |
| `normalize(normalize(x)) == normalize(x)` | `True` | idempotence holds — this one is fine |

These are **A** by construction (we ran them). They are also the reason A1 is not "add a parser" but
"fix the substrate first".

## 2.5 Layout as a product surface

**A**, [EV-05]: if segmentation quality depends on layout, then a tool that emits a document should
choose a layout that is *cheap to segment*. That is a different objective from "looks good", and it is
measurable: render the same content in N layouts, run our own parser, compare field recovery.

**[HYPOTHESIS]** A single-column, marker-bearing, Unicode-normalised layout with standard section
headings recovers more fields than a two-column design with the same content. Probe (A2): build five
fixtures of identical content in different layouts; measure field recovery with our parser; publish
the table. **This is falsifiable and cheap, which is why it is a hypothesis and not a belief.**

**[OPEN]** Which layout real ATS vendors tolerate best is unknown for 7 of 8 engines ([EV-26], 0×00
audit B.3). Until that closes, we optimise for *our own* parser and say so; we must not imply vendor
compatibility.

## 2.6 Design rules for Ariadne that follow

1. **Parse before you advise.** No recommendation may be made about text we have not round-tripped
   through our own extractor; otherwise the advice is about the source file, not the artefact
   (2.1, 2.5).
2. **Never normalise away a signal you later test for.** P3 is the cautionary case: the detector and
   the normaliser disagreed about what text is (2.4).
3. **Report what the parse lost, not just what it found.** A field-level diff is honest; an "ATS
   score" is not (2.2, [EV-02]).
4. **Multilingual is a requirement, not a stretch goal.** Our own corpus contains German (EV-08/EV-12),
   French (EV-19) and a 5-language benchmark (EV-13). The tokenizer used to fail P1 on exactly that
   input; it now passes, and 2.7 is the measurement that says so rather than the prose.

## 2.7 Field-level accuracy, measured (M-1 closed 2026-10-27, re-measured the same day after four fixes)

The probe named above was run: 26 synthetic CVs and 7 job advertisements, hand-labelled before any
parser output was read (`data/gold/manifest.json` records the matching rule and every expected value:
310 labelled field values, 12 forbidden values, 24 labelled requirement weights). The scorer is
`src/ariadne_ats/bench.py`, the gate is `scripts/bench.py --check`, and the artefact these numbers were
read from is `data/gold/results.json`. Micro-averaged over the corpus:

| Field | precision | recall | f1 | fixtures exactly right | What the misses are |
|---|---|---|---|---|---|
| employer | 0.977 | 0.977 | 0.977 | 25/26 | one employer-first line whose words carry no naming evidence keeps the title-first default and comes out transposed (cv-26) |
| title | 0.977 | 1.000 | 0.988 | 25/26 | the same document, the same line |
| date | 1.000 | 1.000 | 1.000 | 26/26 | a year is emitted only inside experience/education, so a year in a sentence stays out (cv-15 forbids it) |
| skill | 0.981 | 1.000 | 0.990 | 25/26 | a table whose second column is a level ("Python\tAdvanced") yields two extra skill facts (cv-25) |
| contact | 1.000 | 1.000 | 1.000 | 26/26 | read from the contact block only, so a reference's email never becomes the candidate's (cv-19) |
| name | 1.000 | 1.000 | 1.000 | 26/26 | abstains on a headline above the name (cv-24) instead of guessing |

**What moved the numbers since the first measurement**, each item traced to a fixture that was failing:

* **cv-21, the transposition.** A role line was read as `title, employer` because title-first is the
  convention. The two segments are now scored for evidence - a role word, or a legal/corporate suffix -
  and the order follows the evidence. Where the evidence **conflicts** (two names that both read as
  companies) the parser abstains with `ROLE_LINE_AMBIGUOUS`; where it is merely **silent** (a foreign
  job title beside a company name the vocabulary has never seen) the documented default stands, because
  silence is not evidence of an unfamiliar convention. The first version of that evidence list contained
  "data", "security", "analytics" and "software", and it *broke three fixtures*, because those are what
  employers are called (`Meridian Data`, `Norrsen Security`). The filter that produced the final list is
  in the code comment, and it is a limit, not a role ontology.
* **cv-22, the date on the next line.** A role line whose date sat alone underneath produced no role
  fact at all while its years were still extracted as dates elsewhere - the combination that makes a
  loss invisible from the JSON. The pairing refuses to reach past a bullet or a blank line, because
  reaching is how a date gets attached to the wrong employer.
* **cv-13 and cv-23, skills.** One fix and **one correction to this document**. The mechanism recorded
  yesterday for cv-23 was wrong: the row was not being merged by the splitter, the line
  `Languages\tpython, go` was being classified as a **`languages` heading** by the fuzzy heading rule,
  so the row disappeared into a heading line. A fuzzy heading candidate may now contain no tab and no
  list separator. Splitting itself moved into `textutil.skill_items`: bracket-aware (`spreadsheets
  (excel, google sheets)` is one skill - and until today cv-06 carried two parser-shaped labels because
  of it), label+list rows, and `X and Y` split only when both sides are single tokens.
* **jd-06 and jd-07, non-English advertisements.** The heading vocabulary was English, so a German
  advertisement produced **no requirements at all**. Headings and cues now cover de/fr/es, cues are
  matched in the accent-insensitive form the headings already used (`souhaitée` does not contain the
  bytes of "souhaite"), and `jd.py` trusts the segmenter's classification instead of keeping a second
  heading list that had silently disagreed with it.

Requirement weighting over the 7 advertisements: expected `{must 10, nice 6, unknown 8}`, measured
`{must 7, nice 6, unknown 11}`; cue accuracy 0.750, 5 of 7 fixtures exactly right (0.857 before the
non-English headings were recognised - the number went **down** because two documents that previously
contributed nothing now contribute three labelled requirements each, two of which we cannot weight).

**Two of the fixtures exist to fail.** cv-25 (a skill-level table) and cv-26 (an employer-first line
with no naming evidence) were added *after* the fixes, are labelled as failures, and are left failing:
passing them would need a level vocabulary and more role words, and adding vocabulary until the corpus
stops complaining is tuning the measurement rather than improving the parser. The floors in
`data/gold/thresholds.json` were raised in the same commit that grew the corpus, so the ratchet is not
monotone by construction - and `tests/test_bench.py` mutates the parser twice to prove the gate still
fails when it should.

One annotation error of the same kind, named because it was measured rather than noticed: the two new
fixtures omitted their education years, so the parser scored two false-positive dates that were the
labels' fault, not the code's. Corrected against the convention cv-01 and cv-03 already follow.

**Forbidden emissions: 0** (12 labelled "must never be emitted" values; the build stops on the first
one, because emitting a reference's email address is a different class of failure from missing a field).

Three things this corpus cannot tell anyone, stated because the table above invites the wrong
inference:

1. It is **author-written by the same session that wrote the extraction rules**. Seven of the 33
   documents (cv-21 to cv-26, jd-06 and jd-07) were added specifically to fail or to be labelled
   partially, which is the only reason several headline numbers are not 1.000. These figures describe
   this corpus and no other. `[OPEN]` a real or
   licensed corpus is G-8/D-4, still unresolved.
2. 24 documents is a floor, not a distribution. A 0.947 with 38 true positives has a confidence
   interval roughly as wide as the gap between 0.947 and 1.000; no statistical claim is being made.
3. Nothing here says what any *vendor's* parser does with the same file. It says what ours does, and
   2.6 rule 1 is the reason we may not imply the former.

**[OPEN]** M-3 (skill-matching false negatives) still needs its 40 labelled requirement/evidence
pairs: this benchmark measures *extraction*, not matching. `[OPEN]` a corpus of real documents, and
the label noise that comes with it (D-4).
