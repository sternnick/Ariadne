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

Runtime dependencies: **none**. `pytest` is the only dev dependency, and the baseline performs **no
network call**. Interpreters, stated as they are tested and not as they are hoped for:

| Python | How it is exercised |
|---|---|
| 3.11 | the required `pytest` job in CI, and every local run recorded in these docs |
| 3.10 | the `pytest-3.10` job in CI, which prints the interpreter it used so the claim is checkable in the log. Not a required status check: a required *matrix* leg would rename the `pytest` context, and a renamed required context silently stops gating |
| 3.12+ | not claimed. `requires-python >=3.10` means "we run 3.10 and up and test two of them", not "tested on each" |

To see the one skipped test actually run, install the optional backend the extractor uses when the host
already has one (it is not a runtime dependency):

```bash
pip install -e ".[dev,pdf]" && ARIADNE_REQUIRE_PDF_BACKEND=1 python -m pytest -q tests/test_parser.py
```

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

## What we have measured (2026-10-27, re-measured after the parser fixes)

Field extraction is not a claim without a number. **26 synthetic CVs and 7 job advertisements**,
hand-labelled before any parser output was read, are scored by `src/ariadne_ats/bench.py`, gated by
`scripts/bench.py --check` on every push, and published in `data/gold/results.json`. Micro-averaged:

| Field | precision | recall | f1 | fixtures exactly right | what the misses are |
|---|---|---|---|---|---|
| employer | 0.977 | 0.977 | 0.977 | 25/26 | one employer-first line with no naming evidence keeps the default order (cv-26) |
| title | 0.977 | 1.000 | 0.988 | 25/26 | the same document, the same line |
| date | 1.000 | 1.000 | 1.000 | 26/26 | a year in prose is not an employment date, and is not emitted |
| skill | 0.981 | 1.000 | 0.990 | 25/26 | a level column in a skills table becomes a skill (cv-25) |
| contact | 1.000 | 1.000 | 1.000 | 26/26 | channels only, from the contact block only |
| name | 1.000 | 1.000 | 1.000 | 26/26 | abstains when the headline sits above the name |

Requirement weighting over the 7 advertisements: expected `{must 10, nice 6, unknown 8}`, measured
`{must 7, nice 6, unknown 11}`; cue accuracy 0.750, 5 of 7 exactly right. **Forbidden emissions: 0**
across 12 labelled "must never appear" values, and the build stops on the first one.

Under four competence-preserving perturbations of the same documents (re-order, rename headings, change
bullet markers, add typographic damage) **every fact that existed before still exists**: mean fact
retention 1.000 in every direction, and no ranking change above |Δcos| = 0.098 on one anchor
advertisement. The transforms do not fire on every fixture (12 to 24 of 26), so read the coverage
column with the number.

**What is in the corpus.** 26 CVs: 20 English, one each in German, Greek, Spanish, French, Irish and
Dutch; single-column, tab-separated two-column, table, all-caps, marker-free, headingless, contact-heavy,
repeated-section, ligature-damaged, and six written to be hard (cv-21 employer-first, cv-22 date on its
own line, cv-23 a skills table, cv-24 a headline above the name, cv-25 a skill-level table, cv-26 an
employer-first line with no naming evidence). 7 advertisements: obligations, negations, contradictory
cues, no cues at all, duplicates, German, French. 310 labelled field values, 12 forbidden values, 24
labelled requirement weights, in `data/gold/manifest.json`.

Three limits, stated here rather than buried:

1. The corpus was **written by the same session that wrote the rules**. Seven documents were added to
   fail or to be labelled partially, and cv-25/cv-26 are left failing rather than answered with another
   word list. These figures describe this corpus and no other.
2. 310 values across 26 documents is a floor, not a distribution: no statistical claim, no confidence
   interval, and every non-English CV is **n = 1**.
3. Nothing here measures real-world parsing. No real CV, no personal data, and no third-party corpus
   has been used; `docs/04` G-5/G-8 are the routes to a measurement anyone outside this repository
   could reuse.

Reproduce it yourself:

```bash
python scripts/bench.py            # the report, including what was missed and where
python scripts/bench.py --check    # the CI gate (exit 1 on a regression)
python scripts/bench.py --write    # refreshes data/gold/results.json; commit it in the same PR
```

### An end-to-end example, with synthetic data

Input (`data/gold/cv-01-single-column.txt`, a file in this repository, not a person):

```text
MARIA GONZALEZ
maria.gonzalez@example.org | Madrid | linkedin.com/in/mariagonzalez

SUMMARY
Data engineer with 7 years building batch and streaming pipelines.

EXPERIENCE
Data Engineer, Norddata 2020-2024
* Rebuilt the nightly ETL in Airflow, cutting runtime from 6 hours to 40 minutes
```

`ariadne parse data/gold/cv-01-single-column.txt` prints the ledger (`21 facts`, `surface_hash`
`475d826e603df1dc`, `competence_hash` `09d51d048deda0f6`); `--json` gives the JSON Resume document:

```json
{
  "basics": { "name": "MARIA GONZALEZ", "email": "maria.gonzalez@example.org",
              "url": "linkedin.com/in/mariagonzalez" },
  "work": [{ "name": "Norddata", "position": "Data Engineer", "startDate": "2020", "endDate": "2024",
             "highlights": ["Rebuilt the nightly ETL in Airflow, cutting runtime from 6 hours to 40 minutes",
                            "Owned the migration of 300 tables to Snowflake"] }]
}
```

Every value above is a byte-exact substring of the input, which is what the no-profiling tests enforce.
Nothing in the output is a score, a ranking, or a judgement about Maria Gonzalez.

## The gates

`pytest` reports one skip on a machine without PyMuPDF: the text-PDF test needs an optional backend,
and the runtime dependency list is empty by policy, so the skip is the honest outcome rather than a
silent pass. Nothing else skips, and the `pytest-pdf` job exists to prove that one would pass: it
installs `.[dev,pdf]` and sets `ARIADNE_REQUIRE_PDF_BACKEND=1`, which turns the skip into a failure.

Seven of those checks are required on `main`: `fresh`, `provenance`, `sources`, `links`, `compile`,
`pytest`, `benchmark`. The two informational legs above are not, deliberately: adding a *matrix* leg to
the required set renames the `pytest` context, and a renamed required context silently stops gating.

Every push runs, and `main` requires: freshness (90-day and 30-day clocks), provenance (bidirectional
citation check), source registry (offline), dead relative links, `compileall`, `pytest`, and the
benchmark ratchet (`data/gold/thresholds.json`). A green build means **claims are dated, linked, and
not worse than last time** - never that they are true.

## Licence

MIT for code; documentation additionally CC BY 4.0. See `LICENSE`.

## Contributing

Read `AGENT_CONTRACT.md` first. It is not advisory: a change that adds an unsourced claim, an
undated doc, or a person-level inference fails the gates or the review, by design.
