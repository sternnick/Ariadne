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
| `scripts/check-sources.py` *(or `.py`)* | Re-probes every URL in `SOURCES.md`. Reports HTTP status, content-length delta and a body hash delta since the recorded check. A 404/timeout is recorded against the source id and forces its grade to `U` until re-resourced. Budget: never hammer a host — one request per URL per run, and a `403/401` is reported as *walled*, not as *absent*. |
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

## C8 — USER-FACING STRINGS ARE LEGAL INSTRUMENTS

**8.1** Every user-facing string — README, UI copy, docs that read as marketing, sales material,
error messages, the package `description`, commit messages that ship in a changelog — is checked
against `docs/09-eu-legal-compliance.md` §8 (Explicit non-claims) **before it is committed**.

**8.2** Why this is a clause and not style advice: Reg. (EU) 2024/1689 Art. 3(12) defines intended
purpose by reference to "the information supplied by the provider in the instructions for use,
**promotional or sales materials and statements**, as well as in the technical documentation".
A tagline can therefore move us into Annex III(4)(a) and, with it, into the high-risk regime. Copy is
classification.

**8.3** Banned unless a named artifact satisfies the claim: "AI Act compliant/ready", any ISO
certification or control count, "ISO 30405 certified", blanket "GDPR compliant", "ATS-proof",
"guarantees passing", "beats the ATS", "bias-free", "fairness-audited", and any restatement of the
"2027 delay" narrative that does not cite Reg. (EU) 2026/1744.

**8.4** A new user-facing string that makes a comparative or outcome claim requires: the evidence id
from `docs/SOURCES.md`, the §8 line it satisfies or the reason it is not covered, and the sentence
shown to the user that qualifies it. Recorded in `DECISIONS.md` (template: D-010).

**8.5** Enforcement: `scripts/provenance.py` covers citations, not prose. String review is manual
and is a checklist item in the commit that introduces the string; a later automated scanner is a
nice-to-have, not a substitute (a scanner cannot tell a metaphor from a promise).

## C9 — NO-PROFILING IS A PERMANENT CONSTRAINT

**9.1** `tests/test_no_profiling.py` is an **architectural gate**, not an incidental test. It asserts
that the package contains no person-attribute inference, no person-level scoring callable, and no
surface that evaluates a human rather than a document.

**9.2** Any requirement that needs person-attribute inference, person-level scoring, or a profile of a
natural person is **out of scope by construction**. It is **rejected**, not negotiated. The test is
**not weakened** to accommodate it, and it is not skipped, marked xfail, or narrowed to a subset of
files.

**9.3** The rationale is legal *and* technical, and both are load-bearing: Reg. (EU) 2024/1689
Art. 6(3) makes an Annex III system "**always** … high-risk where the AI system performs profiling of
natural persons", and WP251rev.01 establishes that human review does not cure it — "human involvement
does not necessarily take the activity out of the definition". A procedural defence therefore cannot
be the answer; the only durable defence is that the system measures documents and never builds a
profile. See `DECISIONS.md` D-019 and `docs/09-eu-legal-compliance.md` §1.2.

**9.4** A pull request that deletes, disables or loosens this gate requires an owner decision recorded
in `DECISIONS.md` with a new Art. 6(4) classification assessment attached. Reviewers must treat its
absence as a blocking defect, in the same class as a deleted failing test.

---

## Compliance ledger (must be updated in the same change that changes status)

| Clause | Status | Evidence / debt |
|---|---|---|
| C1 Read-before-write | **ENFORCED** | This turn: full tree, `git status`, all 9 lane reports, all 3 `src/` modules read; defects quoted by line in `docs/00-audit.md` §A/§D |
| C2 Update-before-create | **ENFORCED** | Corrections applied in place this turn (see `DECISIONS.md` 2026-10-25 entries); 41 KB of boilerplate deleted, not filed |
| C3 `Last verified:` + 90-day rule | **ENFORCED** | Header pair on every doc; `scripts/fresh.py` computes age, applies the 90-day general clock and the 30-day `Live surfaces:` clock, and exits 1 on a missing header or a stale doc |
| C4 `check-sources.py`, `fresh.py`, `provenance.py` | **CLOSED 2026-10-25** | All three exist and run: `provenance.py` passes bidirectionally (39 sources, 0 dangling, 0 uncited); `fresh.py` reports every doc dated/attributed/within clock; `check-sources.py` has a 39-line probe manifest, fails on a registered-but-unprobeable source, records `ok/walled/dead/unreachable`, and writes `docs/source-status.json`. `--probe` is manual, never a hook (a push may not depend on third parties) |
| C5 Labels + grades | **ENFORCED** | Grades used in `docs/00-audit.md` §B, including 5 retractions and 8 `U` items |
| C6 Known-unknowns + probe | **PARTIAL — improving** | Three of six legal unknowns **closed at A/B** this turn (OJ-1/2/3, `docs/09` §7.1) with the primary evidence named; OJ-4/5/6 remain with probes. `docs/08-known-unknowns.md` is still an A0 artifact; the open three migrate into it verbatim |
| C7 Product posture | **ENFORCED** | No dependency added (package still has zero runtime deps); `__init__.py` no longer advertises an API that does not exist. Test dependency: `pytest` (dev-only; declared when `pyproject.toml` lands in A0) |
| C9 No-profiling gate | **ENFORCED** | `tests/test_no_profiling.py` (7 tests) runs in CI; clause added 2026-10-25 with the WP251 rationale in D-019 |
| C8 User-facing strings | **ENFORCED (manual)** | Clause added 2026-10-25 with the Art. 3(12) rationale; first application recorded in `DECISIONS.md` D-010 (tagline verdict) |

**Escalation rule:** if an agent cannot satisfy a clause it must stop and report the clause
number, the missing input, and the cheapest action that would close it. It may not
substitute judgement for a clause.

*End of contract. From the commit that introduced this file, it binds.*
