# DECISIONS.md — decision log (AGENT_CONTRACT C2.3, C7.1, C7.2)

Newest first. Every new file needs an entry here saying which existing file's
responsibility was considered and why it could not absorb the content.

---

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
