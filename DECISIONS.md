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

## D-032 · 2026-10-25 · Zero-touch automation: three workflows, and why each shape was chosen
The owner must not have to watch the repository. Three workflows, all SHA-pinned, all with explicit
least-privilege `permissions:`, none referencing a secret a fork could reach.

**A — `.github/workflows/health-check.yml`** (daily 00:00 UTC + manual).
Runs the three gates that decay without a push: `fresh.py`, `provenance.py`, and
`check-sources.py --probe` (**the only place live probing happens**; push CI stays offline so a
third party's bad afternoon cannot block a commit). On failure it opens **one** issue labelled
`health-check` and *comments on it* on subsequent failures rather than opening a new one per day —
alert volume is the thing that kills alerting. When green it comments "recovered" and closes it. The
run still exits non-zero after the issue exists: a red repo must not produce a green run.

**B — `.github/workflows/ci-failure-alert.yml`** (`workflow_run` on `ci`, completed).
Fires only when `conclusion == 'failure'` **and** `head_branch == 'main'` — a red PR branch is normal
work in progress, not an alarm. Opens `CI Failed on main: <sha>` with the run link, assigns the repo
owner, and de-duplicates by title so repeated failures on one commit become comments.

**C — `.github/workflows/dependabot-auto-merge.yml`** (`pull_request`, actor Dependabot).
`semver-patch`/`semver-minor` → approve + `gh pr merge --auto --squash`; **major stays manual**.
Auto-merge only *queues*: the six required checks still gate the merge, which is what makes this safe.

**Honest limits, recorded rather than discovered later:**
* The `dependency-review` job cannot run on this account (D-031). It is retained, non-blocking, and
  emits a `::warning::` on every PR that it did not actually review. A skipped check that pretends to
  be green would be worse than no check.
* Workflow B's true test needs a failing `main` run, which I will not manufacture. It is verified
  syntactically (YAML parses, event/condition correct) and by the same `github-script` code path that
  Workflow A exercises live.
* Workflow A's `schedule` cannot be triggered on demand to prove the cron; `workflow_dispatch` proves
  the *job*, and the cron expression is validated only by GitHub accepting the file.

## D-031 · 2026-10-25 · GATE 5 executed: repository public, protected, and monitored
**Flip:** `gh repo edit sternnick/Ariadne --visibility public --accept-visibility-change-consequences`
→ `gh repo view --json visibility` returns **`PUBLIC`**. Performed only after D-028/D-029/D-030 were green.

**Branch protection — API proof** (`gh api repos/sternnick/Ariadne/branches/main/protection`):
```json
{
  "allow_deletions": false,
  "allow_force_pushes": false,
  "enforce_admins": true,
  "required_conversation_resolution": true,
  "required_pull_request_reviews": {
    "count": 0,
    "dismiss_stale": true
  },
  "required_status_checks": {
    "contexts": [
      "fresh",
      "provenance",
      "sources",
      "links",
      "compile",
      "pytest"
    ],
    "strict": true
  }
}
```
Six required contexts, `strict: true`, admins enforced, force-push and deletion refused.
**Deliberate deviation, recorded:** `required_approving_review_count` is **0**, not 1. This is a
single-maintainer repository; requiring one approval would mean the owner can never merge their own
PR and would have to self-approve through a second account. A PR *is* still required, which is the
part that makes "the first public commit unguarded" impossible.

**Security features, each verified by API, not by clicking:**
| Feature | State | Evidence |
|---|---|---|
| Secret scanning | **enabled** | `security_and_analysis.secret_scanning.status` |
| Secret scanning push protection | **enabled** | same block, `…push_protection.status` |
| Dependabot alerts | **enabled** | `PUT /vulnerability-alerts` → **204**, re-read 204 |
| Dependabot security updates | **enabled** | `security_and_analysis.dependabot_security_updates.status` |
| CodeQL default setup | **configured** | `PATCH /code-scanning/default-setup` → run `40219758977`; `state: configured` |
| Auto-merge (needed by Workflow C) | **enabled** | `allow_auto_merge: true` |
| Delete branch on merge | **enabled** | `delete_branch_on_merge: true` |

**Two features the platform refused, recorded as refusals rather than silently missing:**
* `secret_scanning_validity_checks` and `secret_scanning_non_provider_patterns` remain **disabled**
  after an explicit PATCH — they are gated behind GitHub Advanced Security on this account.
* `dependency-review-action` fails with *"Dependency review is not supported on this repository.
  Please ensure that Dependency graph is enabled along with GitHub Advanced Security"* even though
  `/dependency-graph/sbom` answers **200**. Consequence: the job is retained but made
  **non-blocking** (`continue-on-error: true`) with the reason in the workflow; the real dependency
  policy (C7.2: a new runtime dependency needs a DECISIONS entry) is enforced by review and
  Dependabot, not by that action.

**DR-13 closed** in `docs/08-known-unknowns.md`.

## D-030 · 2026-10-25 · GATE 4 hardening: pinned actions, read-only permissions, no secrets
Before a public flip, the workflow surface is the attack surface a stranger can reach. Recorded item by
item, with the file that proves it:

| Item | Status | Proof |
|---|---|---|
| Third-party actions pinned to a full commit SHA | **done** | `.github/workflows/ci.yml` — `actions/checkout@11d5960a…` (v4), `actions/setup-python@a26af69b…` (v5); `.github/workflows/dependency-review.yml` — `actions/dependency-review-action@a1d282b3…` (v5.0.0). Verified by scanning for `@v[0-9]`/`@main`: **none remain** |
| Explicit `permissions:`, default `contents: read` | **done** | top-level `permissions: contents: read` in both workflows, plus a per-job block in `ci.yml`; the dependency-review job adds only `pull-requests: write` (to post its own summary) |
| No `pull_request_target` with untrusted checkout | **done** | `grep -rn pull_request_target .github/` → only the comment stating the rule |
| No secrets reachable by a fork PR | **done** | `grep -rn 'secrets\.' .github/` → **none**. No workflow references a secret at all |
| No self-hosted runner | **done** | every job is `runs-on: ubuntu-latest` (GitHub-hosted, ephemeral) |
| `dependency-review` job on `pull_request` | **done** | `.github/workflows/dependency-review.yml` (`fail-on-severity: moderate`) |
| Dependabot for pip + github-actions | **done** | `.github/dependabot.yml`, weekly, grouped, `deps(...)` prefixes |
| `persist-credentials: false` on checkout | **done** | every `actions/checkout` step; a fork PR's token cannot be pushed with |

**One honest limit:** SHA pinning freezes the action *supply chain* but also freezes security fixes.
The mitigation is Dependabot's `github-actions` ecosystem, which will open a PR with the new SHA —
i.e. pinning plus automated bumping, not pinning alone.

## D-029 · 2026-10-25 · GATE 3: local paths removed from the published tree
The GATE 3 sweep for absolute paths found `/Users|/home/<user>|C:\Users` **clean**, but a broader scan
(whose absence the literal command would have hidden) found six files carrying non-identifying
absolute paths and one harness env var:
`/tmp/ats-research` → `<working copy>` (in `DECISIONS.md`, `docs/00-audit.md`, `.work/lanes/data.md`),
`ls /tmp/ats-research` → `ls <repo>` and `$PI_CODING_AGENT_DIR/trusted-sources.md` →
`<agent-dir>/trusted-sources.md` (`.work/lanes/commercial.md`), and one `~/.pi/sessions/...` reference.
**Judgement recorded:** `/tmp/a.txt` in the CI smoke test and `/tmp/ariadne-gate.log` in the pre-push
hook are *runner/process* temp paths, not machine state, and are kept — rewriting them to a fictional
path would make working code worse to satisfy a pattern.
**What this does not do:** earlier commits still contain the old strings. They are non-sensitive, so a
history rewrite (`git filter-repo`) would trade real risk (rewriting published history) for no gain.
The distinction the gate asks about — personal data and credentials — was clean in every revision.

## D-028 · 2026-10-25 · GATE 1 result: history is clean, with two findings that are not secrets
Every command was run over **all refs** (`--all`, `git rev-list --all`), not just `main`:
* secret-shaped files: **none** (`\.env|\.pem|\.key|\.p12|\.pfx|secrets?/|credentials?/|\.token|\.sqlite|\.db`);
* secret-shaped content: the loose `sk-` pattern matched 12 lines in `docs/09` and `check-links.py` —
  all of them the substring inside **"ri*sk-*assessment"**. The strict pattern
  (`gh[pousr]_…|github_pat_…|sk-ant-…|\bsk-[A-Za-z0-9]{32,}|AKIA…|AIza…|xox[baprs]-…`) returned
  **nothing** in any revision;
* identity: author and committer are `ariadne@local` in every commit — no personal email;
* personal files: the only `*.docx` ever committed is `tests/fixtures/malformed.docx`, whose 46 bytes
  are literally `PK\x03\x04this is not a zip central directory at all` — a deliberate corrupt-input
  fixture, not a CV;
* blobs >1 MB: **none** (largest blob in history: 35,965 bytes, a markdown doc);
* dangling/unreachable objects: **none** (`git fsck --full --unreachable --no-reflogs` empty).
**Two commit messages matched the credential grep** and are false positives of the word "key"/"token":
"P1 … key" and "tokeniser"/"tokenize". No message contains a credential.

## D-025 · 2026-10-25 · A1 also fixed audit P1–P5 and deleted the superseded helpers
A1 could have added `layout.py`/`segment.py` beside the defective `textutil` helpers. That would have
left two contradictory implementations of the same idea — the "ghost" C2.4 bans. So:
* **P1 fixed**: `TOKEN_RE` is Unicode (`re.ASCII` removed). `Développeur` no longer becomes
  `['d','veloppeur']`; `c++`, `c#`, `.net`, `ci/cd` survive as tokens.
* **P2 fixed**: the single-character rule is now *kind-based* (a single **letter** survives), so the
  skill **C** is visible to the lexical layer.
* **P3 fixed by replacement, not repair**: `looks_multicolumn` is **deleted**; `layout.analyze()` reads
  the raw extraction, where tabs still exist.
* **P4/P5 fixed**: `bullets_of`/`detect_sections`/`heading_of` are **deleted**; `segment.bullets()`
  accepts an achievement shape, and `segment.segment()` keeps every heading occurrence.
**A defect found by the new test, not by inspection:** adding `qualifications` to the JD requirement
vocabulary made `QUALIFICATIONS` resolve to *requirements* instead of *education*, and the education
year silently disappeared — `facts 15 → 14`. The perturbation test caught it because a "competence-
preserving" transform changed competence. That is exactly the class of silent loss A1 exists to make
impossible, and it validates the Guard-2 design.

## D-024 · 2026-10-25 · Schemas: JSON Resume 1.7.0 extended under `custom`; JD schema is ours
`schemas/resume.schema.json` extends the JSON Resume 1.7.0 document shape and puts every citation-
relevant artefact (fact id, span, confidence, both hashes, layout report, issues) under
`custom["ariadne.provenance"]`. `custom` is the spec's designated, preserved extension point
([EV-16], [EV-31]), so the document stays valid for other tools while carrying our provenance.
`schemas/jd.schema.json` is **ours**, not a standard: the research found no public JD document schema
at grade B ([EV-31] covers ESCO/O*NET *taxonomy* APIs, which enumerate skills and occupations, not a
job advert). Saying so in the schema's `$comment` is cheaper than implying an authority we do not have.
**Validation without a dependency:** `tests/test_schemas.py` implements the small draft-07 subset the
schemas use, and includes a test that a deliberately broken document is rejected — a validator that
cannot fail is decoration.

## D-023 · 2026-10-25 · A1 design: how the evidence model makes M-2 measurable (Guard 2)
**The problem.** A2 must answer "does the score move when only the presentation moves?" ([EV-02]:
29.6 % matched-pair reversals). To measure that, the model must be able to state *mechanically* that
two documents carry the same competence and different surfaces. An assertion in a test would not
survive a refactor; a property of the model does.
**The design.** Every `Ledger` carries two digests:
* `surface_hash` = sha256 of the **raw** text as it arrived (order, headings, markers, whitespace, and
  glyph damage all count);
* `competence_hash` = sha256 over the **sorted set of (kind, normalised value)** facts — order- and
  span-insensitive.
`Ledger.delta(other)` then reports `surface_changed` / `competence_changed` plus the fact ids added,
removed or changed. A competence-preserving perturbation is therefore *defined* as
`surface_changed and not competence_changed`, not asserted in prose.
**Why raw text for the surface hash:** the first implementation hashed the *normalised* text, and the
typographic-damage transform was invisible to it (ligatures are folded by `normalize()`). "What
arrived" and "what it means" are different questions; hashing the repaired text cannot tell a clean
document from a damaged one that repaired cleanly. Caught by the test, not by review.
**What this buys A2.** The stability test becomes: for each fixture and each transform, `delta` says
competence preserved → any score movement is attributable to presentation. If a transform changes
competence, the *fixture* is broken and says so loudly, instead of producing a wrong number that looks
like a stability result.
**Recorded limit.** `competence_hash` is only as good as the fact extractor. A fact the parser never
extracted cannot make competence "change", so M-2 is a test of the *scorer given this model*, never a
test of whether the model captured everything. That residual is `docs/08` M-1.

## D-022 · 2026-10-25 · Gate-bug class: configuration-as-signal, not logic
The `fresh.py` bug (`Live surfaces: none` being read as an opt-in to the 30-day clock) is a specific
recurring class worth naming: **presence-of-configuration treated as intent**. The code was logically
correct; the *interpretation* of an empty-but-present field was wrong.
Why the class matters here — the same shape appears in three other places, and they must be audited
before trusting any gate:
1. `provenance.py` — a source row that exists but is never cited ≠ a source that is fine (it fails, correctly).
2. `check-sources.py` — a manifest line with no row ≠ nothing to check (it fails, correctly, after the fix).
3. `fresh.py` — `Live surfaces:` with no value ≠ a live surface (fixed).
4. **Not yet audited**: `check-links.py` treats `Missing artifact:` on the same line as an exemption —
   meaning a genuine broken link on a line that mentions a missing artifact would be skipped. That is
   the same class, one level deeper (a *marker* is configuration-as-signal).
**Rule for future gates:** every field that can be present-but-empty needs an explicit "absent" value
and a test for it. a gate self-test belongs in `tests/` (not written yet; D-022 lists it) and is tracked in
`docs/08` §8.8.

## D-021 · 2026-10-25 · Branch protection is BLOCKED by plan; substitute installed, decision escalated
**What happened.** Both APIs refuse on this repository:
```
PUT /repos/sternnick/Ariadne/branches/main/protection
POST /repos/sternnick/Ariadne/rulesets
→ 403 "Upgrade to GitHub Pro or make this repository public to enable this feature."
```
`gh api user` reports no `plan` object at all. So the requirement "branch protection active with six
required checks" **cannot be satisfied today**, and the honest status is **not active**.
**What was done instead** (not a substitute in kind — a guard rail):
* CI runs six separate jobs, so each gate is its own status check (`fresh`, `provenance`, `sources`,
  `links`, `compile`, `pytest`) — proven green on `main` at `c85c86d`.
* `.githooks/pre-push` runs the same six locally and **refuses** the push; wired with
  `git config core.hooksPath .githooks`. Tested both ways: exit 1 on a red tree, exit 0 when clean.
* Its limits are written into the hook itself: it runs on the pushing machine, `--no-verify` bypasses
  it, and a fresh clone has no hook until it runs the config command. It is **advisory**.
**Options, with cost:**
| Option | Cost | Consequence |
|---|---|---|
| A. Make the repository public | free; reverses G8 (private until A2) | protection works immediately; the research becomes public before A2 validation |
| B. GitHub Pro | paid subscription | protection works, repo stays private |
| C. Accept hook + CI (current) | free | a direct push to `main` that bypasses the hook is possible; the CI run would still go red, but after the fact |
**Recommendation: A, only when the owner is ready to publish** — because `docs/09` §8 and the README's
C8 pass make public exposure defensible now, while A2 is the increment that adds a score (and with it
the claims that need validation). Otherwise **B**. Until either, this is recorded as debt **DR-13** in
`docs/08` §8.8 and must not be reported as "protected".

## D-020 · 2026-10-25 · A0 documents written; two sources registered late by design
All eight A0 docs exist (`docs/01`…`docs/08`) plus `docs/09` and `docs/SOURCES.md`.
**One process note worth keeping:** `EV-27`…`EV-31` (the lane reports) were registered in
`SOURCES.md` **only when the doc that cites them was written**, not up front. Registering them early
made `scripts/provenance.py` fail on "registered but never cited" for every intermediate step — a true
finding, but about our bookkeeping rather than the evidence. Deferring registration keeps the gate
strict at every commit instead of loosening it to accommodate a plan.
**Bug found and fixed by the gate itself:** `fresh.py` treated any `Live surfaces:` line as opting into
the 30-day clock, including `Live surfaces: none` — so every methods doc would have gone stale in a
month for no reason. A noisy gate is an ignored gate; the rule is now "non-`none` value ⇒ live clock".
**Not claimed:** the docs do not assert parser accuracy, ATS compatibility, or fairness. Those are
`[OPEN]` in `docs/08` §8.3 (M-1…M-5) because the measurements do not exist.

## D-019 · 2026-10-25 · C9 rationale: why no-profiling is policy *and* architecture
WP251rev.01 (Art. 29 WP, EDPB-endorsed) settles the tempting argument. Two findings decide it:

1. **"Profiling has to involve some form of automated processing – although human involvement does
   not necessarily take the activity out of the definition."** (§II.) A human reviewer does not
   convert a profile into "not a profile".
2. For Art. 22, involvement must be real: *"The controller cannot avoid the Article 22 provisions by
   fabricating human involvement … any oversight of the decision is meaningful, rather than just a
   token gesture … carried out by someone who has the authority and competence to change the
   decision."* (§III.A.)

Combined with Reg. (EU) 2024/1689 Art. 6(3) — an Annex III system "shall **always** be considered to
be high-risk where the AI system performs profiling" — a procedural defence (review screens, approval
steps, an "AI-assisted" label) is **not** a defence at all. The only durable one is structural: the
system never derives an attribute of the person. That is what `tests/test_no_profiling.py` enforces,
and why C9 says a conflicting requirement is rejected rather than negotiated.

## D-018 · 2026-10-25 · Tagline must be re-reviewed before any public launch
D-010's "PASS with qualifier" is accepted **for a private repository only**. Before any public
launch, the tagline and every user-facing string are re-reviewed against C8 and `docs/09` §8 — the
qualifier sentence is **mandatory wherever the tagline appears**, and the review is recorded as a new
DECISIONS entry, not assumed to have carried over. Reason: Art. 3(12) makes promotional statements
part of the intended purpose, so copy that is harmless in private becomes a classification input at
launch.
**Trigger:** any change of repository visibility, any landing page, any app-store listing.

## D-017 · 2026-10-25 · CI is the enforcement mechanism for C4's intent
`.github/workflows/ci.yml` runs six gates: `fresh.py`, `provenance.py`, `check-sources.py` (offline),
`check-links.py`, `compileall`, and `pytest` (including the C9 no-profiling gate), plus a CLI smoke
test of the declared entry point.
**Branch protection is part of the decision, not an optional extra**: `main` must require the `gates`
check to pass. The rule that makes it real:
```
gh api -X PUT repos/sternnick/Ariadne/branches/main/protection \
  -F required_status_checks.strict=true \
  -F required_status_checks.contexts[]='contract gates' \
  -F enforce_admins=true \
  -F required_pull_request_reviews.required_approving_review_count=0 \
  -F restrictions=
```
**Status, honestly:** the workflow file exists and every gate runs locally; protection **cannot be
applied until the first branch exists on the remote** (the GitHub repo is empty and this tree has no
remote configured). Recorded as a debt to execute immediately after the first push — a CI file with
no protection is advisory, which is exactly the "prose not enforcement" failure C4 exists to end.
**Rejected:** putting `check-sources.py --probe` in CI (third-party dependency on the push path);
running only the tests named in the last commit (a gate that can be dodged by not naming a file).

## D-016 · 2026-10-25 · `pyproject.toml`: zero runtime dependencies, pytest dev-only
`dependencies = []` is a **product property**, not laziness: the package must compute its claims with
the standard library so that (a) a CV never has to leave the machine to be measured, (b) results are
reproducible for a reader who installs nothing, and (c) there is no supply-chain surface behind a
document containing personal data. `pytest>=8` sits in `[project.optional-dependencies].dev` so
`pip install ariadne-ats` installs no test stack.
**Consequence accepted:** no `sentence-transformers`, no `scikit-learn`, no `chromadb` in the
baseline. A semantic embedder, when A2 needs one, arrives as an *optional* extra with its own
DECISIONS entry — and the baseline keeps working without it (measured 2026-10-25: `sklearn`,
`sentence-transformers`, `chromadb` are all absent from this machine anyway).

## D-015 · 2026-10-25 · G1 executed: package renamed `ats_research` -> `ariadne_ats`, CLI added
The rename was forced by the approved `[project.scripts] ariadne = "ariadne_ats.cli:main"`, and it
was the right time: before the first tag, the first PyPI name, or the first citation.
**What moved:** `src/ats_research/` -> `src/ariadne_ats/` (via `git mv`, so blame survives), imports
updated in `tests/test_no_profiling.py`, and every stale `src/ats_research/...` reference in
`docs/00-audit.md` corrected in place (the dead-link gate found all of them — see D-017).
**`cli.py` is real, not a stub** (C7.7): `ariadne inspect` reports tokens, sections and the
multicolumn heuristic; `ariadne compare` prints cosine plus the terms that produced it. There is no
"score my CV" command, because no score exists yet, and a flag that pretended otherwise would be a
user-facing claim under C8. The CLI carries a stop list *of its own* (a display choice, not a model
of ATS filtering) so output is not "the / is / and".
**Behaviour of existing modules: unchanged** (`textutil`, `lexical` untouched in this step).

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
was recovered separately from `<agent-dir>/sessions/.../session.jsonl` into the `.txt` files.
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
`<working copy>`, Python package is `ats_research`, and LICENSE now says "Ariadne project
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
