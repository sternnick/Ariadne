```
Last verified: 2026-10-25
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
4. **Multilingual is a requirement, not a stretch goal** — our own corpus contains German
   (EV-08/EV-12), French (EV-19) and a 5-language benchmark (EV-13), and our tokenizer fails P1.

**[OPEN]** Field-level evaluation needs annotated pairs we do not have. Probe: hand-annotate 20
synthetic résumés (fields: employer, title, dates, skills) and score our parser against them; that is
the minimum honest basis for saying anything about parse quality.
