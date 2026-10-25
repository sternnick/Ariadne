# DECISIONS.md — decision log (AGENT_CONTRACT C2.3, C7.1, C7.2)

Newest first. Every new file needs an entry here saying which existing file's
responsibility was considered and why it could not absorb the content.

---

## D-013 · 2026-10-25 · C4 closed: the three enforcement scripts now exist
`scripts/fresh.py`, `scripts/provenance.py`, `scripts/check-sources.py` (+ `docs/SOURCES.md`,
`docs/source-status.json`). Before this, C3/C4 were prose: the 90-day rule had no clock, and no
claim had an address a reader could resolve.
**Two design choices worth recording, because the obvious version of each is wrong:**
1. `check-sources.py` is **offline by default** and fetches only under `--probe`. Reason: a push must
   not depend on third parties (the parent project lost every push for a day to one expired
   credential). Recording status ≠ probing it.
2. A source with **no manifest line fails the run** (`no-manifest`). The naive checker iterates over
   the URLs it finds; a source registered without one is then silently "clean" — the "skipped
   sources never print READY" trap. In-repo artifacts (EV-22/23/24) are declared `local:<path>` and
   checked for existence instead of being exempted.
**Verified:** `provenance.py` → 39 sources, 0 dangling, 0 uncited. `fresh.py` → 3 docs, all fresh,
0 missing headers. `check-sources.py --probe` → 5 sources live-checked (`ok`), status file written.

## D-012 · 2026-10-25 · Art. 6(4) + 49(2): comply now, do not wait for a clarification
**Decision.** We treat the Art. 6(4) documented non-high-risk assessment and the Art. 49(2) EU-database
registration as **applicable today**, and will prepare both before any first sale, rather than waiting
for a reading that would defer them to 2 December 2027.
**Evidence (A).** OJ **L 165/3**, p.62 places Art. 49 inside Chapter III **Section 3**; Section 4
(p.70) is "Notifying authorities and notified bodies". Amended Art. 113(3)(c) (by Reg. (EU) 2026/1744)
defers Sections 1–3 "as regards AI systems **classified as high-risk** pursuant to Article 6(2) and
Annex III". A system declared non-high-risk under Art. 6(3) is not so classified, so the residual date
is the general **2 August 2026** — already passed.
**Cost, stated plainly:** one assessment document plus one registration, with the usual
precision problem (we must describe intended purpose, which is the same text that decides
classification). **Cost of being wrong the other way:** placing on the market without a mandatory
registration — a compliance failure on the record at the moment we most want a clean one.
**Rejected:** waiving the duty by not claiming Art. 6(3) at all (that leaves us either high-risk by
default or undocumented — strictly worse); deferring until a Commission FAQ appears (an FAQ is not
an instrument).
**Revisit if:** an official Commission/Board text states the deferral covers 6(3)-declared systems.

## D-011 · 2026-10-25 · G5 corpus: **synthetic-only**. The personal-CV option is dropped.
Owner condition: default-off **and** never in git history, "if that cannot be guaranteed
mechanically, use synthetic-only and drop G5". It cannot be guaranteed: `.gitignore` plus a check
script stops `git add personal/cv.pdf` but not `git add -f`, and nothing un-writes history once
pushed. So G5 is **dropped**, not softened: fixtures are synthetic, and the "real CV" reality check
lives outside the repository (an operator's own machine) and is never referenced by a test, a doc,
or a commit. `/personal/` stays in `.gitignore` as defence in depth, not as the control.
**Cost:** our fixtures may encode our own assumptions about CV shape. **Mitigation:** the layout
fixtures are derived from the documented failure modes (multi-column, tables, unmarked bullets,
ligatures) rather than from one person's document.

## D-010 · 2026-10-25 · Tagline audit under the new C8: "The thread through the ATS labyrinth"
**Verdict: PASS with a binding qualifier.** Checked line by line against `docs/09` §8:
- It does **not** claim compliance, certification, or an outcome ("ATS-proof", "guarantees passing",
  "beats the ATS" are all absent). ✔
- It **does** name the ATS and frames it as a maze to be navigated, which leans toward "gaming the
  filter" without asserting it. ⚠
- It asserts nothing about ATS behaviour, so it does not contradict audit §B.3 (7 of 8 engines
  UNKNOWN). ✔
**Conditions (all three required wherever the tagline appears):** (1) it is never paired with an
outcome word — "pass", "beat", "optimise for", "get past"; (2) the same surface carries one plain
sentence: *"Ariadne approximates how a parser may read your CV. It does not predict or guarantee any
employer's decision."*; (3) it is not used on the same page as a numeric score without the score's
definition and uncertainty (C7.5).
**Why record it at all:** Art. 3(12) makes promotional statements part of the intended purpose, so a
tagline is a classification input. This is the first string audited under C8 and the template for
D-014-style future audits.
**Rejected:** deleting it (it is accurate as a metaphor and carries no legal claim); keeping it
unqualified (a metaphor next to a score is read as a promise).

## D-014 · 2026-10-25 · OJ-1/2/3 closed — and what each closure changed
Recorded because in all three cases **the answer was not the one we had been working from**:
* **OJ-1** — I had framed the question as "Section 4 (2 Aug 2025) or Section 2 (2 Dec 2027)". The
  text puts Art. 49 in **Section 3**; Section 4 is the notified-body machinery. The question was
  wrong, not just unanswered. → D-012.
* **OJ-2** — WP251 supplies the test we needed ("no human involvement"; no fabricated involvement;
  meaningful, with authority to change the decision) and also the warning that **human involvement
  does not remove profiling** — which is why `tests/test_no_profiling.py` is structural rather than
  procedural.
* **OJ-3** — the Cellar record has **no XHTML datastream**; the directive is only available as PDF.
  A checker that treats "no XHTML" as "no document" would have recorded a false `U` forever.

## D-009 · 2026-10-25 · New file: `docs/09-eu-legal-compliance.md` (EU-only, owner-mandated)
**Considered:** `docs/08-known-unknowns.md` (its responsibility is unresolved items, not obligations —
and the owner specified §7 of the deliverable *feeds* it rather than replaces it); `docs/00-audit.md`
§C.1 (a gap list is not an obligation matrix); a `legal/` subdirectory (one jurisdiction does not need
a tree).
**Why it could not be absorbed:** no existing file carried an instrument-by-instrument obligation
matrix, and the mandated column schema (jurisdiction | instrument | role | classification |
obligation | applies_from | grade | status | evidence) is the extensibility mechanism for future
jurisdictions — that schema belongs in one file that is *about* jurisdictional extension.
**Sources, all read at primary level on 2026-10-25:** Reg. (EU) 2024/1689; **Reg. (EU) 2026/1744**
(the amending instrument — read rather than believed from press coverage); Reg. (EU) 2016/679;
Dir. (EU) 2024/2831; Dir. 2006/54/EC; Dir. 2004/113/EC; Dir. (EU) 2024/1500; Impl. Decision (EU)
2026/2274; ISO catalogue pages 81230 / 27001 / 27701 / 79488.
**Rejected:** citing any law-firm or vendor page for a date or obligation (owner's rule + C5);
analysing non-EU regimes (scope restriction).
**Downgrade recorded here:** Dir. 2000/43/EC is left **U** with all four failed rungs listed — the
employment-access article is *not* cited in the document, and it was tempting to cite it from memory.
ISO/IEC 42001's "Annex A = 38 controls" figure is likewise **not asserted**: no official source found.

## D-008 · 2026-10-25 · Licence posture MIT (code) + CC BY 4.0 (docs) — [OPEN G2]
**Decision used for now:** MIT with a CC BY 4.0 grant over documentation, and an explicit
non-affiliation / non-compliance-advice notice.
**Evidence:** the two most-referenced open systems are MIT (`career-ops`, `ai-job-search`)
and the next tier is permissive; copyleft ones (`AienTech/dossier` AGPL-3.0,
`gr8monk3ys/resume-AI` GPL-3.0, `StackResume` GPL-3.0) are therefore **design-only reading**,
never code import (C7.6). Sources recorded in `.work/lanes/opensource.md`, `.work/lanes/commercial.md`.
**Rejected:** AGPL-3.0 (forces the same licence on any hosted derivative — a real cost if this
becomes a service, and unforced); Apache-2.0 (patent grant is nice-to-have, adds ceremony,
no evidence we need it yet).
**Needs from owner:** confirm. This is a commercial decision, not an engineering one.

## D-007 · 2026-10-25 · Deleted 5 files of timeout boilerplate
`rm .work/rescue/{18ea5316,1a28a27e,4acf9ebf,d792319c,d7c8d8de}.md` — 41 KB, each file a
`Subagent timed out after 300000ms` stub whose bulk is a `git diff --no-index` usage dump
(the run's cwd was not a git repository). No findings inside; the real content of those runs
was recovered separately from `~/.pi/sessions/.../session.jsonl` into the `.txt` files.
**Rule:** C2.4 (garbage found is garbage removed, same turn).

## D-006 · 2026-10-25 · Added `date_conflict` column instead of choosing a date
`data/harvest/arxiv-hiring.csv`: 6 of 46 rows have `listed_date` in a different month than
the arXiv id encodes (e.g. `2609.20188` listed `2026-07-24`). Cause is unresolved — arXiv
exposes both *published* and *updated*, and our recovered listing mixed them.
**Decision:** keep both columns, flag the conflict, do not silently pick one.
**Rejected:** overwriting `listed_date` with the id-derived month (would destroy the only
signal that our harvest mixed two fields); deleting the 6 rows (they are real papers).
**Rule:** C5.3 / C6.1.

## D-005 · 2026-10-25 · Docstring corrections only in `textutil.py` / `lexical.py`
Behaviour left untouched: the audit turn forbids implementation, and four of the five defects
are behavioural (tokenizer ASCII-only, `looks_multicolumn` dead signal, `bullets_of` marker
dependence, `detect_sections` first-heading-wins). What was **changed** is every claim that
was false: phantom helper `idf_from_background`, dead `docs/04-…` reference, unused `tokenize`
import, and the `bullets_of` docstring that promised detection of unmarked bullets.
**Rejected:** writing 7 stub modules to satisfy the old `__init__.py` — that is stub code
created to appease a false claim, the exact pattern C2.4 bans.

## D-004 · 2026-10-25 · Package surface reduced to what exists; version 0.0.1
`import ats_research` raised `ModuleNotFoundError: ats_research.resume` because `__init__.py`
lines 10-16 imported seven modules of which two exist. Surface trimmed to `textutil` +
`lexical`; the unimplemented names are listed in the docstring as A1/A2/A3 work, not exported.
Version dropped 0.1.0 → 0.0.1: 0.1.0 claimed an API that did not exist. **Rule:** C7.7, C2.2.

## D-003 · 2026-10-25 · `.work/*` ignored, `.work/lanes/` tracked
`docs/` will cite the 9 distilled lane reports as primary evidence; a citation that resolves
only in my working directory is not a citation (C1.1(e)). Raw transcripts under
`.work/rescue/` stay ignored: they embed full prompts and vendor HTML, and they are
disposable once distilled.
**Rejected:** committing all of `.work/` (240 KB of raw transcripts, prompt text, vendor page
bodies in a public repo); moving reports straight to `docs/evidence/` (that is A0's job and
would create doc content in an audit-only turn).

## D-002 · 2026-10-25 · Naming — [OPEN G1]
Repo/agent is `Ariadne` (owner's words, 2026-10-25). Working directory is
`/tmp/ats-research`, Python package is `ats_research`, and LICENSE now says "Ariadne project
contributors" instead of "ats-research contributors" — a holder claim I could not leave
naming a project the owner does not use. Renaming the package/directory is deferred until G1
so a single commit does the move with history.

## D-001 · 2026-10-25 · New file: `AGENT_CONTRACT.md` (first commit, 63a0216)
**Considered:** `README.md` (does not exist yet; would bury binding rules under onboarding
prose and get rewritten at A0), `docs/` (forbidden this turn, and the contract must be
discoverable at root by an agent that has not read the tree), `CONTRIBUTING.md` (a contribution
how-to is weaker than a precondition clause list).
**Why it could not be absorbed:** no existing file had a "rules that bind every future turn"
responsibility — the repository had no committed file at all before this one.
**Contents note:** the compliance ledger inside it is the enforcement mechanism; two clauses
(C3 freshness headers, C4 the three scripts) are recorded as **DECLARED debt**, because the
owner forbade code in this turn. Until C4 closes, the repo is not releasable.
