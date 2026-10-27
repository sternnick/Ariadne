# Ariadne

**The thread through the ATS labyrinth.**

> Ariadne approximates how a parser may read your CV. It does not predict or guarantee any
> employer's decision, and it is not affiliated with any applicant tracking system.

Status: **0.0.1: research, parser spine, and a measurement.** No scoring, no generation, no hosted
service yet. What exists is documented below, tested by CI, and **scored against a labelled corpus**;
what does not exist is listed as `[OPEN]` in `docs/08-known-unknowns.md` rather than implied.

## What this is

A research repository and a dependency-free Python package about one narrow question: **what happens
to a CV between "upload" and "a human reads it", and what can be measured honestly about that?**

Two outputs:

1. **`docs/`**: the evidence, with a source id and a grade (`A`/`B`/`C`/`U`) on every claim, a
   freshness date on every page, and a register (`docs/SOURCES.md`) that CI checks in both
   directions: no dangling citation, no uncited source.
2. **`src/ariadne_ats/`**: a deterministic implementation of the parts that can be implemented
   without a model: text normalisation, layout-damage detection with named failure codes, section
   segmentation with per-section confidence, a fact ledger (id, span, confidence, two hashes), a JD
   requirement extractor, and TF-IDF comparison that shows the terms behind the number.

`ariadne parse` reports what the extraction **lost**, not just what it found. A document that cannot be
read produces a typed failure (`PDF_BACKEND_MISSING`, `NO_TEXT_LAYER`, `CORRUPT_DOCUMENT`,
`UNSUPPORTED_FORMAT`) rather than a plausible-looking empty result.

## What this is not

* Not an ATS, and not a way to "beat" one. We do not know any vendor's acceptance rules: 7 of 8
  targets are recorded as `U` (attempted, unanswered) in `docs/01` §1.5.
* Not a score. There is no "ATS score" here, because the evidence says scores of this class reverse
  on **29.6 %** of competence-preserving pairs (`docs/03` §3.4).
* Not "AI Act compliant", not certified against any ISO standard, and not "GDPR compliant" as a
  blanket claim. `docs/09` §8 lists the sentences this project may never use, and why.
* Not a profile of a person. Person-attribute inference is rejected by construction and enforced by
  `tests/test_no_profiling.py` (`AGENT_CONTRACT` C9).

## Install and run

```bash
python -m pip install -e ".[dev]"     # runtime dependencies: none
ariadne --version
ariadne parse  path/to/cv.docx        # evidence ledger: facts, spans, confidence, both hashes
ariadne parse  path/to/cv.txt --json  # full JSON Resume 1.7.0 document with provenance
ariadne jd     path/to/job.txt        # requirement list with weights and spans
ariadne inspect path/to/cv.txt        # tokens, sections, layout heuristic
ariadne compare cv.txt job.txt        # cosine + the terms that produced it
ariadne bench                         # score the parser against data/gold/ (the software, not a CV)
```

Python ≥ 3.10. `pytest` is the only dev dependency. The baseline performs **no network call**.

## Repository map

| Path | What it is |
|---|---|
| `AGENT_CONTRACT.md` | binding rules for every agent working here (read-before-write, freshness, labels) |
| `DECISIONS.md` | decision log, newest first: every non-obvious choice with its evidence |
| `docs/00-audit.md` | the audit: inventory, evidence map, measured defects, plan |
| `docs/01`…`docs/07` | the research, one topic each, every claim graded |
| `docs/08-known-unknowns.md` | everything we do not know, with the probe that would close it |
| `docs/09-eu-legal-compliance.md` | EU-only legal and standards analysis, primary sources |
| `docs/SOURCES.md` | the source register CI enforces |
| `data/gold/` | the labelled corpus, the matching rule, the ratchet floors, the results |
| `scripts/` | the gates: freshness, provenance, source probing, dead links, benchmark |
| `src/ariadne_ats/` | the package |
| `tests/` | including the no-profiling gate |

## What we have measured (2026-10-27)

Field extraction is no longer a claim without a number. 24 synthetic CVs and 6 job descriptions were
hand-labelled first, then the parser was run against them (`data/gold/`, scorer `ariadne_ats.bench`,
gate `scripts/bench.py --check`, artefact `data/gold/results.json`):

| field | precision | recall | what the misses are |
|---|---|---|---|
| employer | 0.947 | 0.900 | employer-first role lines; a date on its own line |
| title | 0.947 | 0.900 | the same two documents, values swapped rather than missing |
| dates | 1.000 | 1.000 | years only inside experience/education, so a year in prose stays out |
| skills | 0.989 | 0.919 | `* git and docker` names two tools in one item; a skills table yields compound rows |
| contact | 1.000 | 1.000 | read from the contact block only, so a reference's email is not the candidate's |
| name | 1.000 | 1.000 | abstains when a headline sits above the name instead of guessing one |

Forbidden emissions (a value present that must never be): **0**, and the build stops on the first one.

Requirement extraction from job advertisements is measured the same way: 5 of 6 labelled fixtures
exactly right, and the sixth is German, where it yields **no requirements at all** - the heading
vocabulary is as English as the cue vocabulary (`tests/test_jd.py` pins that limitation so a future
change has to change the claim with it).
Under competence-preserving perturbation every fact survived every transform; renaming a heading moves
the cosine against a fixed advertisement by up to 0.098 and reorders 6.7 % of fixture pairs, which is
our own version of the reversal rate in the literature, at roughly a quarter of the published figure.

Three limits, stated here rather than buried: the corpus was written by the same session that wrote the
rules (five documents were added specifically to fail, which is why the numbers are not all 1.000); 24
documents is a floor, not a distribution, and carries no statistical claim; and every non-English
language in it has exactly one document, so those rows are a coverage floor, not language support.
The full table, the failure cases named per fixture, and what the corpus cannot tell you: `docs/02`
§2.7.

## The gates

`pytest` reports one skip on a machine without PyMuPDF: the text-PDF test needs an optional backend,
and the runtime dependency list is empty by policy, so the skip is the honest outcome rather than a
silent pass. Nothing else skips.

Every push runs, and `main` requires: freshness (90-day and 30-day clocks), provenance (bidirectional
citation check), source registry (offline), dead relative links, `compileall`, `pytest`, and the
benchmark ratchet (`data/gold/thresholds.json`). A green build means **claims are dated, linked, and
not worse than last time** - never that they are true.

## Licence

MIT for code; documentation additionally CC BY 4.0. See `LICENSE`.

## Contributing

Read `AGENT_CONTRACT.md` first. It is not advisory: a change that adds an unsourced claim, an
undated doc, or a person-level inference fails the gates or the review, by design.
