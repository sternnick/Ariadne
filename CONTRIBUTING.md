# Contributing

```
Last verified: 2026-10-25
Reviewed by:   Ariadne (principal)
```

Read `AGENT_CONTRACT.md` first. It is the law in this repository, and it is unusual: it makes
**evidence** a reviewable artefact, not just code.

## The three things that will get a PR rejected

1. **A claim without a source id and a grade.** `docs/` is not prose; every paragraph is a fact with
   `[EV-nn]`/`[EU-nn]`/`[ISO-nn]` and a grade, or it is labelled `[HYPOTHESIS]`/`[OPEN]`. There is no
   third state. `scripts/provenance.py` enforces the ids in both directions.
2. **A document without its freshness header.** `Last verified:` and `Reviewed by:` on line 1–3.
   `scripts/fresh.py` fails the build otherwise, and a doc older than its clock (90 days general,
   30 days if it declares `Live surfaces:`) is stale.
3. **Person-level inference.** Any feature that infers attributes of a human — traits, potential,
   demographics, emotion — is out of scope **by construction** (`AGENT_CONTRACT` C9). It is not a
   trade-off to discuss; it is rejected, and `tests/test_no_profiling.py` is the gate. Do not weaken,
   skip or narrow that test.

## Workflow

```bash
python -m pip install -e ".[dev]"
pytest -q                       # 33 tests
python scripts/fresh.py         # freshness clocks
python scripts/provenance.py    # citation integrity, both directions
python scripts/check-sources.py # registry integrity (offline)
python scripts/check-links.py   # dead relative links
```

All six run in CI. Locally, `.githooks/pre-push` runs the same set — enable it once per clone:

```bash
git config core.hooksPath .githooks
```

`--no-verify` bypasses the hook. That is a review offence, not a technique.

## What to send

* **Bug reports**: the command, the input shape (synthetic), the typed failure code if there is one.
* **Evidence corrections**: the source id, what it actually says, and the URL. If you find a claim we
  graded too highly, that is the most valuable contribution this project can receive — five claims
  have already been retracted (`docs/00-audit.md` §B.2).
* **New sources**: a row in `docs/SOURCES.md` (id, URL, what it proves, access date, grade) and the
  doc that cites it. A source with no citation fails the build, deliberately.

## What not to send

* A real CV, or any real person's data. The corpus is synthetic (`D-011`); a real CV in a PR is a
  security report, not a contribution.
* A scraper for a vendor's help centre that ignores `robots.txt` or hammers a host.
* "Improvements" to the score that cannot be measured against `docs/08` M-2.

## Licence

Contributions are accepted under MIT (code) and CC BY 4.0 (documentation), matching `LICENSE`.
