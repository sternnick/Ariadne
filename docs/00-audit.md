```
Last verified: 2026-10-25
Reviewed by:   Ariadne (principal engineer / repo steward)
Purpose:       Rule-1 audit. The one-page precondition to any implementation.
Method:        full tree read, git status, all 9 lane reports read, all 3 src modules read
               in full, and 12 executable probes run against the code (not opinions).
```

# 00 — Audit

---

## A. Inventory

### A.1 Tracked after this turn (18 files, 2 commits)

| Path | Purpose | State | Current? |
|---|---|---|---|
| `AGENT_CONTRACT.md` | Binding clauses C1–C7 + compliance ledger | **committed** `63a0216` | yes |
| `DECISIONS.md` | Decision log D-001…D-008 | committed `c45ed02` | yes |
| `LICENSE` | MIT + CC BY for docs | committed `c45ed02` | **holder + SPDX now [OPEN G1/G2]**; 2 dead references removed this turn |
| `.gitignore` | keeps scratch/raw out; now un-ignores `.work/lanes/` | committed `c45ed02` | yes |
| `data/sources/2026-10-25-jobSuit-ai-demo-transcript.md` | 351-line primary source: Jobsuit demo, verbatim + provenance header | committed | yes — its own header states `verified against audio: NO`, names/numbers non-citable |
| `data/harvest/arxiv-hiring.csv` | 46 rows of hiring-AI papers harvested from the arXiv API | committed | yes after this turn — `date_conflict` column added (6/46 rows conflict; cause unresolved, D-006) |
| `src/ats_research/__init__.py` | package surface | committed, **corrected this turn** | now honest (`0.0.1`, 15 exports, all real) |
| `src/ats_research/textutil.py` | normalisation, tokenising, section/bullet detection (151→~190 lines w/ limitation notes) | committed | **behaviour stale** — 4 measured defects, deferred to A1 by the no-code rule |
| `src/ats_research/lexical.py` | TF-IDF + cosine, pure Python (100 lines) | committed, docstring corrected | behaviour fine for English; **no background corpus exists** → IDF is meaningless in the 2-document case |
| `.work/lanes/*.md` (9) | the distilled research reports — this repo's only evidence corpus: 393 lines, **98 unique URLs, 18 arXiv ids** | **now tracked** (were untracked; D-003) | yes, as of 15:2x today |

### A.2 Present but intentionally untracked

| Path | What | Why untracked |
|---|---|---|
| `.work/rescue/*.txt` (9 files, **244 KB**) | raw transcripts of research runs: tool calls + fetched bodies | contains full prompts and vendor page bodies; disposable once distilled. This is where every fact in the lane reports came from |
| `.work/mine.py` | the transcript-miner that recovered evidence from *timed-out* children | scratch, but reproducible; worth promoting into `scripts/` if we ever re-run research |

### A.3 Missing entirely (a public repo must have these)

`README.md` — **none exists**. `pyproject.toml` — none. `tests/` — none. `docs/` — empty
before this file. `docs/SOURCES.md` — none, so **no claim in this repo is currently
resolvable by id**. `scripts/` — none, so C3/C4 are unenforced. CI — none. `Makefile`,
`CONTRIBUTING.md`, `SECURITY.md` — none.

### A.4 What I changed this turn (Rule 2, commit `c45ed02`)

1. **Deleted** 5 files / 41 KB: `.work/rescue/{18ea5316,1a28a27e,4acf9ebf,d792319c,d7c8d8de}.md`
   — each a timeout stub whose content was a `git diff --no-index` usage dump, not findings.
2. **`src/ats_research/__init__.py:10`** read `from .resume import parse_resume, Resume, Role`.
   Five of its seven imports named files that do not exist; `import ats_research` raised
   `ModuleNotFoundError: No module named 'ats_research.resume'`. Surface trimmed to the 15
   real names, version `0.1.0 → 0.0.1` (0.1.0 advertised an API that did not exist).
3. **`lexical.py`** docstring promised *"the helper `idf_from_background` exists to supply a
   corpus"* — `hasattr(module,'idf_from_background') == False`. Claim deleted. Its pointer to
   `docs/04-matching-and-scoring.md` was dead (docs/ empty) → retargeted to `.work/lanes/scoring.md`.
   Dead import `tokenize` removed (0 uses).
4. **`textutil.py`** — four false docstring claims replaced with measured limitations (below).
5. **`LICENSE`** — dropped `See docs/10-legal-and-compliance.md` (never existed) and replaced
   it with an explicit "there is no legal analysis here yet" notice; holder line fixed (D-002).
6. **`.gitignore`** — `.work/` blanket-ignored meant all 9 evidence reports were untracked and
   unresolvable from a clone; now `/.work/*` + `!/.work/lanes/`.
7. **`data/harvest/arxiv-hiring.csv`** — added `date_conflict` (6 rows) rather than pick a date.

### A.5 Measured defects in the existing code (12 probes, behaviour unchanged this turn)

| # | Probe result | Where | Consequence |
|---|---|---|---|
| P1 | `tokenize("Développeur … mit C++ und C")` → `['d','veloppeur','full-stack','mit','c','und','c']` | `textutil.py:24` `re.ASCII` | **any non-English résumé is shredded.** Directly contradicts evidence in our own corpus (German resumes arXiv 2609.22188; French pipeline JobScout; 5-language JobResQA 2601.23183) |
| P2 | `content_words("C, Python, Go")` has **no `'c'`** | `content_words` `len(t)>1` | the skill **C** is invisible to every lexical feature. A toy test `compare('a b','b c')` returns cosine **0.0** for exactly this reason |
| P3 | `looks_multicolumn(tab-separated 2-column text)` → `False`, both before and after `normalize()` | `looks_multicolumn` | its only two signals are `\t` and ≥4 spaces, and `normalize()` collapses both → **a dead feature that always says "single column"** |
| P4 | `bullets_of("Led a team of nine engineers to ship the platform")` → `[]` | `bullets_of` | CSS-list or table-layout resumes lose markers on extraction → the whole achievement-quantification feature family silently scores 0 |
| P5 | `detect_sections("SUMMARY/experience/SUMMARY")` → `['summary','experience']` | first-heading-wins | second block of a repeated heading dropped **silently** |
| P6 | `normalize` idempotent → `True` | — | this one claim was true |
| P7 | `Tfidf(['a b c','b c']).idf('kubernetes')=2.099` vs `idf('fox')=1.405` with n_docs=2 | — | unseen terms outrank seen ones; with a 2-doc "corpus" IDF carries no market signal. Needs a real corpus (we have none) |
| P8 | `import ats_research` → ok now, `0.0.1`, 15 exports | — | the only green probe that mattered 20 minutes ago |

---

## B. Evidence map after corrections

Grades: **A** primary read · **B** ≥2 independent secondaries · **C** snippet/single secondary ·
**U** attempted, unanswered.

### B.1 Standing claims

| Claim | Grade | Source |
|---|---|---|
| ATS = requisition/candidate CRM; 9 canonical modules | **A** | `.work/lanes/fundamentals.md` → Wikipedia rev. 2026-10-16 |
| Software touches nearly every application first (parse → dedupe → field/keyword filter → optional rank) | B | fundamentals (2 sources) |
| 97.4 % of Fortune 500 have a detectable ATS; Workday >40 % | **B⁻** *(vendor telemetry, 2 secondaries, self-interested)* | `pin.com/blog/ats-market-share-report`, `matchr.io` |
| Outside F500: 23 systems, none >16.5 %, HHI ≈1,000 | C *(single vendor's telemetry)* | pin.com |
| Market size: $17.22 B vs $2.5 B — 6.9× disagreement | **B (recorded as a conflict, not a number)** | pin.com |
| "ATS auto-rejects 75 %" is unsupported | B | davron.net, duperrin.com |
| Parser pipeline = extraction → OCR fallback → layout/reading-order → **section segmentation** → per-section NER → normalisation; evaluated as field-level EM/F1 | **A** | arXiv 1910.03089, 2509.06200, ScienceDirect S2590005626004418 |
| Segment-specialised ensemble beats single model: **+7 % Recruitment-Similarity**, field-specific weighting | **A** | arXiv 2509.06200 (MSLEF) |
| "100 % parse accuracy" is LinkedIn-format-only; 73 % on suitability | **A** | arXiv 1910.03089 |
| "~95 % accuracy" claims are vendor marketing; **no public leaderboard found** | C + **U** | 3 vendor blogs; absence is our measurement |
| TF-IDF + cosine is the real baseline; hybrid = NER → skill normalisation → TF-IDF → sentence embeddings → weighted ranking | **A** | arXiv 2503.17438; sbert.net docs |
| Embeddings at scale need ANN + **retrieve→cross-encoder re-rank** | **A** | sbert.net |
| Career vault exists: 12-node LangGraph agent; **+7.8 pts same-domain, −8.0 pts out-of-domain** (n=1, 9 JDs, pilot) | **A, pilot** | **arXiv 2605.05257** |
| ConFit v2 +13.8 % recall / +17.5 % nDCG | **A** | arXiv 2502.12361 |
| Score instability: validity 0.781 with **29.6 % matched-pair reversals** | **A** | arXiv 2609.16517 |
| LLMs fail to pick the objectively better résumé; no abstention on ties | **A** | arXiv 2602.18550 |
| Screening friction = excess false negatives; semantic matching cuts FN without losing precision | **A** | arXiv 2602.04087 |
| Adverse-impact: +2.12 pp pro-White gap reproduced by a 2023 model, null-to-−3.01 pp for 2024+ | **A** | arXiv 2606.28978 |
| Anonymisation **leaks** demographics (4,100 variants, 18 LLMs) | **A** | arXiv 2603.05189 |
| Self-preferencing: +23–60 % shortlisting for same-LLM candidates | **A** | arXiv 2509.00462 |
| Prompt-injection benchmarks exist for résumé screening (channel separation) | **A** | arXiv 2609.20188, 2605.28999 |
| **JSON Resume v1.7.0**: Draft-07, ISO 8601, 14 optional sections, `custom` = sanctioned, preserved extension point | **A** | jsonresume.org/schema/ (`[PROVEN]`) |
| Rezi: Free $0 / Pro **$29/mo** / Lifetime **$149** / Enterprise **$99/mo per 200 users**; "62 % of users land an interview" = marketing | **A** for the page, **C** for the claim | rezi.ai/pricing `[PROVEN]` |
| Enhancv free = 7 days, 12 section items; Pro price is JS-injected (`€ NaN` in raw HTML) | **A** | enhancv.com/pricing `[PROVEN]` |
| JobScout: **deterministic local scoring, no AI call**, ±10/−6 contract, re-score endpoint, deletion-based anti-hallucination, pdf-parse/pdfjs/mammoth/tesseract FR+EN | **A** (`[PROVEN]` README body) | github.com/latenightsbeats1208-pixel/jobscout |
| AviCV exposes **MCP** at `avicv.com/mcp`, RenderCV PDF, FastAPI+SQLite, Gemini via OpenRouter | **A** | sinaatalay/avicv `[PROVEN]` |
| Resume-Scanner = all-MiniLM-L6-v2 + TF-IDF + Gradient Boosting; calls its score *"an analytical estimate"* | **A** | Soham-Barate/Resume-Scanner `[PROVEN]` |
| career-ops has a **fact-gate** (commit-level) | **C** | `fix(fact-gate): read French counts in generated CVs` |
| Jobsuit workflow: per-section autofix → score 66→69 → keyword-match → per-keyword bullet proposal w/ accept/reject → categories **modification / contextual match / not applicable** | **B** (transcript; workflow only, **not** its numbers) | `data/sources/…jobSuit-ai-demo-transcript.md` |
| This box: pypdf/pymupdf/python-docx/numpy **present**; sklearn/sentence-transformers/chromadb/rendercv/typst **absent** | **A** (executed 15:38Z) | local probe |

### B.2 Retracted this turn — corrected in place, no `corrections.md`

| Retracted claim | What it became | Where the wrong statement came from |
|---|---|---|
| *"NYC LL144 effective 1 Jan 2023"* | **U** — deleted from evidence; the date was **in my own search query string**, never in retrieved text; the NYC.gov page returned *"outdated or non-existing page"* | `.work/lanes/legal.md:13,37` |
| *"Illinois AEDTA/AIVA dates"* | **C with an unresolved conflict** — 820 ILCS 42, "effective January 2020" ×3 blogs; `ilga.gov` ActID=4088 **timed out at 45 s** | `legal.md:8,9` |
| *career-ops 77,167 ★ as landscape evidence* | **C, not a design input** — implausible vs peers, flagged by the lane itself; popularity is metadata | `opensource.md:33` |
| *"Jobscan $49.95/mo"* (from the owner's brief) | **U** — curl → 6,653 bytes of "Jobscan"; `app.jobscan.co/plan` → `content_chars: 0`; Camoufox → *"Just a moment…"* | `commercial.md` |
| *"Rezi states its score is not an official ATS score"* / *"94 % Workday, 96 % Greenhouse parse rates"* (owner's brief) | **U** — not found on any page we captured. Unverified ≠ false | `commercial.md`, no lane |

### B.3 U — attempted and unanswered, with the error that proved it

`support.greenhouse.io/hc/…/360020744252` **404** · `help.lever.co/hc/…/360001122232` **401** ·
`help.smartrecruiters.com/Resume_parsing` **200 + Cloudflare JS shell** · `help.ashbyhq.com`
**connect fail** · `help.teamtailor.com/hc/…` **404** · `docs.oracle.com` Taleo chapter **never
attempted** · `nyc.gov/…/local-law-144/` **404 boilerplate** · `ilga.gov` **timeout** ·
`jobscan.co/pricing` **walled** · `aws.amazon.com/buildercenter` article **not found** ·
searxng `site:` operators → **count 0, unsupported** · any ATS **boolean-search implementation
doc** · any **engineered-feature + gradient-boosting feature list** · any published
**match-rate threshold with a named owner** · **latency in ms** · **vector DB / reranker used by
any OSS repo** · **O\*NET endpoint shape** · **ESCO licence/terms**.

**[REFUSED TO INVENT]** The single most load-bearing unknown in the whole map — *which parser
vendor each ATS uses, and what formats each accepts* — has an empty answer column for 7 of 8
targets. The obvious filler is the pair of SEO blogs that "agree" on Greenhouse's extension
set, and the standard-engineering story (ToUnicode/ActualText extraction, x-y projection reading
order, header-band rejection, ESCO/O\*NET linking). I have left both out of the standing table:
the first is two low-quality secondaries for one fact, the second appeared **in a subagent's own
notes as its knowledge, not as retrieved text** (`.work/lanes/parsing.md`, "Unverified engineering
detail… Mark UNVERIFIED"). The map says UNKNOWN instead.

---

## C. Gaps

### C.1 Facts needed, with the probe that resolves each

| # | Missing | Why it is load-bearing | Probe (specific) | Cost |
|---|---|---|---|---|
| G-1 | Accepted formats + size limits per ATS (Workday, Greenhouse, Lever ✓partial, Taleo, iCIMS, SmartRecruiters, Ashby, Teamtailor) | decides our output formats and our lint rules | `browser_navigate`→`browser_content` on each help center (bypasses the Cloudflare shell that killed curl); `docs.oracle.com` Fusion HCM "Resume Parsing" chapter | 1 lane, ~8 fetches |
| G-2 | Parser vendor attribution (Textkernel / Daxtra / Sovren / Radancy) | tells us which failure modes are *engine* vs *vendor*; also our competitive claim | partner/partner-listing pages of Textkernel + Daxtra (their own "works with X" pages) | 1 lane |
| G-3 | NYC LL144 requirement + enforcement date + penalty | C6 + product posture: we ship a score | `camo_navigate` `nyc.gov/site/ccp/services-projects/local-law-144/`, then `rules.cityof.newyorkcity.gov` and the NYC CCP FAQ PDF | 3 fetches |
| G-4 | Illinois 820 ILCS 42 effective date | B.2 conflict | `ilga.gov` with a 120 s budget, or IL Public Act 101-0657 text via `ilga.gov/legislation/publicacts/` | 2 fetches |
| G-5 | EU AI Act: is employment screening high-risk as of 2026, and does a candidate-side tool inherit anything | decides whether our scoring code needs an audit trail as a product requirement | `eur-lex.europa.eu` Annex III (3) + Art. 6(3), official text, not a blog | 2 fetches |
| G-6 | Rezi's "not an official ATS score" wording | our own disclaimer benchmark | `help.rezi.ai` search for "ATS score" | 2 fetches |
| G-7 | A background corpus for IDF (P7) | without it, IDF is decorative | ESCO skills API + 500 public JDs, or `data/` seed we compile; declare licence in DECISIONS | 1 day |
| G-8 | Ground-truth superiority pairs | no accuracy claim is possible without them | build synthetically per arXiv 2602.18550 / 2609.16517 method; PopResume (2603.22714) availability request | 2-3 days |
| G-9 | arXiv `date_conflict` cause (6 rows) | tiny, but it is an unlabelled data defect in a shipped file | one arXiv API call per conflicting id, compare `published` vs `updated` | 6 calls |

### C.2 Promised in A0 and not written

`docs/SOURCES.md` · `01-what-an-ats-is.md` · `02-parsing-and-what-breaks-it.md` ·
`03-matching-and-scoring.md` · `04-generation-rag-and-provenance.md` ·
`05-reliability-fairness-security.md` · `06-open-source-landscape.md` ·
`07-product-workflow-teardown.md` · `08-known-unknowns.md` · `docs/DECISIONS.md` *(placed at
repo root as `DECISIONS.md` instead — D-001 reasoning; if you want it under `docs/`, say so and
I move it with history)*. **Status: 0 of 9 written.** `.work/lanes/*.md` hold the content;
they are raw reports, not docs — no `Last verified:` header, no source ids, mixed voice.

### C.3 Infrastructure

1. `scripts/check-sources.mjs` — 98 URLs currently have **no reachability record at all**.
2. `scripts/fresh.py` — the 90-day/30-day clocks; nothing enforces the header yet.
3. `scripts/provenance.py` — bidirectional `[Xn]` ↔ SOURCES check; **cannot pass today because
   SOURCES.md does not exist** (that is the honest C4 `DECLARED` entry).
4. CI — nothing runs. `py_compile` passes by hand; there are **zero tests**; the package was
   broken-on-import until this turn and **no existing check would have caught it**.
5. Packaging — `pyproject.toml` absent, so "installable" is false, and C7.2 (declared
   dependencies) has nothing to declare into.
6. `README.md` absent → an outside engineer cannot learn what this is in 30 seconds.

---

## D. Health assessment

**Verdict: the research track is professional; the engineering track does not exist yet; the
product is unsellable tomorrow and the reason is honest, not cosmetic.** The evidence discipline
is real — 98 unique URLs, 18 arXiv ids, every vendor claim labelled PROVEN vs SNIPPET-ONLY, five
confident claims retracted rather than softened, and a 244 KB raw trail that lets any statement be
re-checked. Against that: the code is ~350 lines of text utilities that are **English-only**
(P1), **blind to the skill "C"** (P2), **incapable of detecting the very two-column layout the
docs name as the top parse failure** (P3), and **blind to unmarked bullets** (P4); it had **no
tests**, and its package surface lied so badly that importing it raised an exception — a state a
single CI job would have refused. There is no README, no packaging, no CI, no source registry,
and no accuracy measurement of any kind, so we cannot state what our score means, how often it is
wrong, or on which populations. The commercial blockers are therefore not missing features: they
are **(1)** no verified knowledge of any real ATS's acceptance rules or internals (B.3 — 7 of 8
targets UNKNOWN), **(2)** no validity harness, so every accuracy sentence would be invented,
**(3)** an unassessed legal surface (we could not even source LL144), **(4)** a codebase that
fails on non-English input while the literature we cite is explicitly multilingual, and
**(5)** an undecided licence and copyright holder. Drifting? No — but the gap is now *measured*
rather than assumed, which is the difference between a project with debts and one with surprises.

---

## E. Plan, restated after the audit

| Inc | Was | Now | Change and why |
|---|---|---|---|
| **A0** | "distil research into docs/" | **A0 = docs + enforcement, one increment** | **Merged** the three C4 scripts + CI *into* A0. C4 is contract law; shipping docs the tooling cannot police re-creates today's state. Exit = `provenance.py` exits 0, `fresh.py` clean, CI green |
| **A1** | parser spine | **A1 = spine + fix the 5 measured defects + JSON Resume 1.7.0 model** | **Expanded.** A parser that cannot see a tab-separated column or the token "C" is not a spine. JSON Resume chosen over a bespoke schema (`[PROVEN]` spec, `custom` extension point) |
| **A2** | hybrid scorer | unchanged + **corpus decision (G-7)** | P7 proved IDF is inert without a background corpus; that decision now gates A2 rather than hiding inside it |
| **A3** | proposals + classifier + deletion path | unchanged | JobScout's deletion garde-fou + career-ops fact-gate + Jobsuit's three categories are three independent attestations of the same design |
| **A4** | vault-gated retrieval + audit trail | unchanged, **explicitly allowed to abstain** | arXiv 2605.05257: −8.0 pts out-of-domain is the reason retrieval needs a domain gate, not a flag |
| ~~A5~~ | MCP surface (AviCV parity) | **CUT from v1** | [HYPOTHESIS] that coding-agent users matter; zero evidence in our corpus. Recorded, not built (C7.3) |

---

## F. Next three actions, on your approval

1. **A0 — SOURCES.md + 9 docs + the three scripts + CI.**
   *Acceptance:* every `[Xn]` in docs resolves; every SOURCES entry is cited ≥1×; `fresh.py`
   prints a table with no missing headers; CI runs `py_compile` + tests + both checkers; all
   98 URLs carry a status (`ok <code>`, `walled`, `dead`), and every `walled/dead` entry has its
   grade set to `U` *and* appears in `08-known-unknowns.md` with a probe.
   *Evidence:* `.work/lanes/*.md` (98 URLs, 18 arXiv ids), B.3 error list, C4 ledger debt.
2. **The browser-rung resolution pass on the 6 walled primary targets (G-1…G-6).**
   *Acceptance:* each of the 8 ATS format/limit rows is A/B/C or a recorded failure; LL144 and
   820 ILCS 42 either carry quoted primary text with an access date or are listed as unknowns
   with the exact failing URL; `docs/02` updated **in place**, grades moved, no new "corrections"
   file.
   *Evidence:* our own ladder rule (a 403/401 is a rung) + the measured Cloudflare-shell results
   in `.work/lanes/engines.md`.
3. **A1 — spine, defect fixes, tests.**
   *Acceptance:* a test fails if accented text is split (`P1`), if `C` is absent from a skill
   vector (`P2`), if a tab-separated résumé reports single-column (`P3`), if an unmarked
   achievement yields no bullet (`P4`), and if a repeated heading loses content (`P5`); résumé
   round-trips to JSON Resume 1.7.0; package installs from `pyproject.toml`; import + CI green
   with **zero runtime dependencies**.
   *Evidence:* the 12 probes above; arXiv 2509.06200 (layout/segmentation is the failure axis);
   multilingual evidence 2609.22188 / 2601.23183.

---

## G. Your decisions — as choices

| # | Choice | Recommendation | Reasoning |
|---|---|---|---|
| **G1** | Name: **A** `ariadne` everywhere (rename `src/ats_research`, one commit with history) / **B** keep `ats_research` package, `Ariadne` repo / **C** other | **A, now** | Cheapest before the first tag, first PyPI name, or first citation. Two names in a repo is how a project loses its import path |
| **G2** | Licence: **A** MIT + CC BY docs / **B** AGPL-3.0 / **C** Apache-2.0 | **A** | Matches the ecosystem we cite; keeps AGPL sources design-only (C7.6). B is a business model choice we have not made |
| **G3** | Positioning: **A** candidate-side only / **B** both sides / **C** recruiter-side | **A for v1** | Mobley treats a vendor that *screens/ranks/rejects* as a potential direct defendant (C-grade but consistent across 5 law-firm sources); candidate-side tooling does not carry that surface |
| **G4** | Repo mechanics: **A** commit `main` from `/tmp/ats-research` into empty `Ariadne` / **B** push, then branch+PR for everything after / **C** keep local, mirror | **B** | A one-shot push to seed history, then PRs; `Ariadne` is private and empty, so there is no second writer to race |
| **G5** | Corpus: **A** synthetic fixtures only / **B** synthetic + your own CV behind a local flag (gitignored) / **C** public datasets | **B** | No public corpus has ground-truth superiority (G-8) and HF `datasetmaster/resumes` is flagged weak; your own CV is the single best reality check, kept out of the public tree by `.gitignore` |
| **G6** | Models: **A** OpenAI-compatible adapter + offline hashing baseline / **B** require sentence-transformers / **C** remote-only | **A** | `sentence-transformers`/`sklearn` absent here; a scoring lane with no network call is also the reproducible one (JobScout's "no AI call" precedent, ±10/−6 contract) |
| **G7** | Legal depth: **A** primary-source verification pass now (G-3/4/5) / **B** publish with an explicit "no legal analysis" notice | **A before any public release**, **B is acceptable only while private** | The notice is already in `LICENSE`; publishing a commercial tool on a snippet-grade legal surface is the exact liability you named |
| **G8** | Visibility: **A** keep private until A2 exit / **B** publish now / **C** publish at A0 | **A** | A2 is where we can say what the score means and how often it is wrong; publishing an unvalidated score invites the criticism we would deserve |

**Stop here.** No further file will be written until you approve this report (C1.2, and your
instruction). Two clauses remain `DECLARED` debt on the ledger — **C3** (doc headers) and **C4**
(the three scripts) — and closing them is exactly action F.1.
