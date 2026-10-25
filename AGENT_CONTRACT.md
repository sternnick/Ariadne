# AGENT_CONTRACT.md — Binding rules for every agent working in this repository

```
status:        BINDING since 2026-10-25 (first commit of this file)
applies_to:    principal agent, every subagent, every future session
scope:         every file in this repository, including this one
Last verified: 2026-10-25
Reviewed by:   Ariadne (principal) / owner (rules issued 2026-10-25)
```

This project is intended to become a professional, possibly commercial system. An
unverified claim in `docs/` is a legal and reputational liability. A stale `Last
verified:` date is a liability. A source that silently died is a fact that is silently
false. These clauses exist to make that class of failure structurally impossible.

Where a clause cannot yet be honoured, the **Compliance ledger** at the bottom must say
so. A clause marked `DECLARED` is a debt, not an excuse. Silence about a clause is a
violation.

---

## C1 — READ BEFORE WRITE

**1.1** Before any create, edit, or delete, the agent must have read in that session:
  (a) the full file tree (files, not directories);
  (b) `git log --oneline` and `git status --porcelain`;
  (c) every file in `docs/`;
  (d) `docs/SOURCES.md`, `docs/08-known-unknowns.md`, `DECISIONS.md`;
  (e) the primary evidence for the claim it is about to write (a lane report under
      `.work/lanes/`, a raw source under `data/sources/`, a harvest under `data/harvest/`,
      or a fetched URL);
  (f) every `src/` module it will touch, in full.

**1.2** Implementation may not begin until the agent can state, in writing, what exists,
in what state, and what is missing. If that statement is not producible, the correct
output is a question, not a change.

**1.3** A claim may be written only from an artifact the agent has actually read in this
session. Memory of a previous session, a subagent summary, or a model's prior knowledge
is not evidence. Prior knowledge may raise a hypothesis; it may not raise a claim.

## C2 — UPDATE BEFORE CREATE

**2.1** Existing files are corrected in place. A grade change, an upgrade, a downgrade,
or a retraction is applied to the file that carries the claim. Creating
`corrections.md`, `notes-v2.md`, `*-addendum.md`, or a parallel doc that "clarifies" an
older one is a violation.

**2.2** A retracted claim is either deleted or restated as the uncertainty it now is,
with its retraction reason. No ghosts: a retracted number must not remain readable as
fact.

**2.3** A new file requires an entry in `DECISIONS.md`, written before or with the file,
stating which existing file's responsibility was considered and why it could not absorb
the content. A new file whose DECISIONS entry only says "new feature" is rejected.

**2.4** Garbage found is garbage removed, in the same turn: stale facts, dead links,
contradictory statements, unreferenced claims, dead imports, docstrings that describe
behaviour the code does not have. The finder fixes it; the finder does not file it for
someone else.

## C3 — FRESHNESS

**3.1** Every file in `docs/` that carries any claim begins with:
```
Last verified: YYYY-MM-DD
Reviewed by: <agent|person>
```

**3.2** `docs/SOURCES.md` records for every source: id, URL, what it proves, access date,
and grade. An entry without an access date is not a source, it is a rumour.

**3.3 The 90-day rule.** If `Last verified` is older than 90 days, the document is
**stale**: it may describe history, it may not be cited as current fact. `scripts/fresh.py`
prints the table; a stale doc cited as current is a defect in the citing artifact.

**3.4** Any claim about a live third-party surface (a vendor page, a price, a schema
version, an endpoint, a statute page) carries a shorter clock: **30 days**. Prices, plan
tiers, star counts and "current" product behaviour decay fastest and are the classic
source of a confident, wrong statement.

**3.5** Refreshing a fact re-dates it in the same change. Re-dating without re-checking
is forgery, not maintenance.

## C4 — UPDATE TOOLING (part of the contract, not optional)

All three live in `scripts/`, run from a clean checkout, exit non-zero on failure:

| Script | Contract |
|---|---|
| `scripts/check-sources.mjs` *(or `.py`)* | Re-probes every URL in `SOURCES.md`. Reports HTTP status, content-length delta and a body hash delta since the recorded check. A 404/timeout is recorded against the source id and forces its grade to `U` until re-resourced. Budget: never hammer a host — one request per URL per run, and a `403/401` is reported as *walled*, not as *absent*. |
| `scripts/fresh.py` | Walks `docs/`, prints `file, Last verified, age days, stale (90d), stale (30d claims)`. Non-zero exit if any doc lacks the header pair. |
| `scripts/provenance.py` | Bidirectional: every `[Xn]` id cited in `docs/**` resolves to a `SOURCES.md` entry, and every `SOURCES.md` entry is cited by at least one doc. Uncited source = delete it or use it. Dangling id = hard fail. |

**4.1** These scripts are the enforcement of C2/C3/C5, not documentation of intent. While
one of them does not exist, the compliance ledger says `DECLARED` and the repo is
**not** releasable.

**4.2** CI runs: `py_compile`, tests, `fresh.py`, `provenance.py`. Dead links in docs fail
the build. A green build therefore means "claims are linked and dated", never "claims are
true".

## C5 — NO THEORY WITHOUT A LABEL

**5.1** Every paragraph in `docs/` is exactly one of:
  (a) **fact** — with source id + grade;
  (b) `[HYPOTHESIS]` — reasoned, unproven, with the probe that would settle it;
  (c) `[OPEN]` — a question we are asking the owner or the world.
"Plausible but unsourced" is banned as a fourth state.

**5.2 Grades:**
| Grade | Meaning |
|---|---|
| **A** | Primary / peer-reviewed / official spec, body text read |
| **B** | Secondary, corroborated by ≥2 independent sources |
| **C** | Single secondary source, or a search snippet only |
| **U** | **Attempted and unanswered** — the fetch failed or proved nothing. `U` is a real, useful result; it is not "false", it is "we do not know" |
| `[PROVEN]` / `[SNIPPET-ONLY]` / `[NOT-IN-FILE]` | When the evidence is our own captured transcript of a research run: body text / search-result row / absent |

**5.3** A number without a unit, a population, and a date is banned. "97.4 %" is not a
fact until you know 97.4 % of *what*, measured *when*, by *whom*. Vendor-authored numbers
are labelled as vendor telemetry at the point of use, not in a footnote.

**5.4** Transcripts (spoken demos, ASR) may establish **workflow and wording**, never a
person, a proper noun, or a number as a benchmark. See `data/sources/*-transcript.md`.

## C6 — REAL RESOLUTION ONLY

**6.1** "Source unreachable" is a valid recorded outcome (`U`) with the exact error.
"Probably true" is not an outcome.

**6.2** Every unresolved item lives in `docs/08-known-unknowns.md` with the **specific
next probe** that would resolve it (browser rung, primary-source filing, vendor doc with a
named URL, dataset request, an experiment we can run here). An unknown without a probe is
an excuse.

**6.3** Retry order for a walled source: direct → feed/API → anti-detect browser →
archive → human. A `403` is a rung, never an answer. If a rung is skipped, the log says it
was skipped.

**6.4** A failed probe is recorded with its error text so a later agent does not mistake a
`Cloudflare "Just a moment…"` for empty content, or a `404` for a non-existent fact.

## C7 — PROFESSIONAL-PRODUCT POSTURE

**7.1** Every design choice names, in the same paragraph or ADR: the user problem, the
evidence (source id), and the cost/complexity trade-off — including what we gave up.

**7.2** No dependency without a stated reason in `pyproject.toml` comments **and** a
`DECISIONS.md` entry. Optional extras live in `[project.optional-dependencies]` and the
package must import and pass tests without them.

**7.3** No feature "because it sounds good". A feature not traceable to a documented user
problem or a documented finding is cut, not built.

**7.4** Reproducibility is a product requirement: same inputs + same documented decisions ⇒
same outputs. Any nondeterminism is named in the output, never hidden.

**7.5** Honesty toward the user is a feature. A score ships with its uncertainty and its
failure modes. The word "score" never appears without a definition of what it measures and
what it does not — and never as "an ATS score".

**7.6** Licences are inputs: MIT-family sources may inform design; copyleft sources
(AGPL/GPL) are design-only reading, never code import, unless the repo's own licence is
changed deliberately and recorded.

**7.7** Failures are visible: no bare `except`, no silent skip, no `pass` on an error path.
A degraded result says it is degraded, in the artifact a downstream consumer reads.

---

## Compliance ledger (must be updated in the same change that changes status)

| Clause | Status | Evidence / debt |
|---|---|---|
| C1 Read-before-write | **ENFORCED** | This turn: full tree, `git status`, all 9 lane reports, all 3 `src/` modules read; defects quoted by line in `docs/00-audit.md` §A/§D |
| C2 Update-before-create | **ENFORCED** | Corrections applied in place this turn (see `DECISIONS.md` 2026-10-25 entries); 41 KB of boilerplate deleted, not filed |
| C3 `Last verified:` + 90-day rule | **PARTIAL** | Header pair present on every doc written since this file was committed (`docs/00-audit.md`, `docs/09-eu-legal-compliance.md`); the clock is still **manual** because `scripts/fresh.py` does not exist |
| C4 `check-sources.mjs`, `fresh.py`, `provenance.py` | **DECLARED — DEBT** | Scripts promised as A0 exit criteria; until they exist this repo is not releasable. Owner forbade code in the audit turn, so they are not written yet |
| C5 Labels + grades | **ENFORCED** | Grades used in `docs/00-audit.md` §B, including 5 retractions and 8 `U` items |
| C6 Known-unknowns + probe | **PARTIAL — improving** | `docs/00-audit.md` §C plus **six legal unknowns with named probes** at `docs/09-eu-legal-compliance.md` §7 (OJ-1…OJ-6). `docs/08-known-unknowns.md` itself is still an A0 artifact; those six migrate into it verbatim |
| C7 Product posture | **ENFORCED** | No dependency added (package still has zero runtime deps); `__init__.py` no longer advertises an API that does not exist |

**Escalation rule:** if an agent cannot satisfy a clause it must stop and report the clause
number, the missing input, and the cheapest action that would close it. It may not
substitute judgement for a clause.

*End of contract. From the commit that introduced this file, it binds.*
