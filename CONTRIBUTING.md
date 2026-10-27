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

All four run in CI, alongside `compile`, `pytest` and `benchmark`: those seven context names are the required status checks on `main`. Locally, `.githooks/pre-push` runs the same set - enable it once per clone:

```bash
git config core.hooksPath .githooks
```

`--no-verify` bypasses the hook. That is a review offence, not a technique.

## Running what CI runs

```bash
python -m pip install -e ".[dev]"          # runtime dependencies: none
python scripts/fresh.py                    # every dated claim inside its clock
python scripts/provenance.py               # citations both ways
python scripts/check-sources.py            # recorded source state (add --probe for the live read)
python scripts/check-links.py              # no dead relative link
                                              # and the pytest-pdf job proves it would pass
python -m compileall -q src scripts tests  # what the `compile` job is
python -m pytest                           # 112 tests; one skips without the optional PDF backend,
python scripts/bench.py --check            # the parser-quality gate (exits 1 on a regression)
```

Two jobs exist to close a gap the list above cannot, and both are informational rather than required:

```bash
python -m pytest                                       # under 3.10 as well (CI: pytest-3.10)
pip install -e ".[dev,pdf]" && ARIADNE_REQUIRE_PDF_BACKEND=1 python -m pytest -q   # CI: pytest-pdf
```

The second one matters more than it looks. `ariadne_ats.extract` uses PyMuPDF when the host has one and
the dependency policy keeps the runtime list empty, so the default run skips one test. A skip that
nobody ever runs is how a broken optional import survives forever: in the `pytest-pdf` job the same
test *fails* if the backend is missing, so "it would have passed" is checked, not asserted.

## Changing the benchmark

* A fixture is a `.txt` file under `data/gold/` plus a labelled row in `manifest.json`. The scorer
  refuses to run a manifest whose expected or forbidden value does not occur in its fixture, so a
  transcription error fails the build instead of scoring quietly.
* **Never widen a label or a vocabulary list to make a red run green.** If a change makes a fixture
  pass that used to fail, say so in the PR; if it makes one pass that should not, the fixture is wrong.
* Floors move **with** the measurement and in the same commit that explains the move
  (`AGENT_CONTRACT` C2.4). Adding a fixture that fails and raising the floors in the same commit is the
  expected shape of a good round: a ratchet that only ever rises has stopped measuring.
* `tests/test_bench.py` mutates the parser twice on purpose (one rule stops firing, one invents a value)
  and asserts the gate goes red. If you weaken a floor, that test is where you will be caught.

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
