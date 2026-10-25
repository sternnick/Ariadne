# Ariadne

**The thread through the ATS labyrinth.**

> Ariadne approximates how a parser may read your CV. It does not predict or guarantee any
> employer's decision, and it is not affiliated with any applicant tracking system.

Status: **0.0.1 — research + parser spine.** No scoring, no generation, no hosted service yet. What
exists is documented below and tested by CI; what does not exist is listed as `[OPEN]` in
`docs/08-known-unknowns.md` rather than implied.

## What this is

A research repository and a dependency-free Python package about one narrow question: **what happens
to a CV between "upload" and "a human reads it", and what can be measured honestly about that?**

Two outputs:

1. **`docs/`** — the evidence, with a source id and a grade (`A`/`B`/`C`/`U`) on every claim, a
   freshness date on every page, and a register (`docs/SOURCES.md`) that CI checks in both
   directions: no dangling citation, no uncited source.
2. **`src/ariadne_ats/`** — a deterministic implementation of the parts that can be implemented
   without a model: text normalisation, layout-damage detection, section segmentation, a fact ledger,
   and TF-IDF comparison that shows the terms behind the number.

## What this is not

* Not an ATS, and not a way to "beat" one. We do not know any vendor's acceptance rules — 7 of 8
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
ariadne inspect path/to/cv.txt        # tokens, sections, layout heuristic
ariadne compare cv.txt job.txt        # cosine + the terms that produced it
```

Python ≥ 3.10. `pytest` is the only dev dependency. The baseline performs **no network call**.

## Repository map

| Path | What it is |
|---|---|
| `AGENT_CONTRACT.md` | binding rules for every agent working here (read-before-write, freshness, labels) |
| `DECISIONS.md` | decision log, newest first — every non-obvious choice with its evidence |
| `docs/00-audit.md` | the audit: inventory, evidence map, measured defects, plan |
| `docs/01`…`docs/07` | the research, one topic each, every claim graded |
| `docs/08-known-unknowns.md` | everything we do not know, with the probe that would close it |
| `docs/09-eu-legal-compliance.md` | EU-only legal and standards analysis, primary sources |
| `docs/SOURCES.md` | the source register CI enforces |
| `scripts/` | the gates: freshness, provenance, source probing, dead links |
| `src/ariadne_ats/` | the package |
| `tests/` | including the no-profiling gate |

## The gates

Every push runs, and `main` requires: freshness (90-day and 30-day clocks), provenance (bidirectional
citation check), source registry (offline), dead relative links, `compileall`, and `pytest`. A green
build means **claims are dated and linked** — never that they are true.

## Licence

MIT for code; documentation additionally CC BY 4.0. See `LICENSE`.

## Contributing

Read `AGENT_CONTRACT.md` first. It is not advisory: a change that adds an unsourced claim, an
undated doc, or a person-level inference fails the gates or the review, by design.
