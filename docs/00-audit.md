```
Last verified: 2026-10-27
Reviewed by:   Ariadne (principal engineer / repo steward)
Purpose:       Rule-1 audit. The one-page precondition to any implementation.
Method:        full tree read, git status, all 9 lane reports read, all 3 src modules read
               in full, and 12 executable probes run against the code (not opinions).
Snapshot:      sections A.2-A.5, B, C, D and E describe the tree at commit `8f31ba9` (2026-10-25).
               They are history and are left in place because retracting an audit is how an audit
               stops being evidence.
Current state: section A.0, checked against `git rev-parse HEAD` on 2026-10-27. Anything in this
               file that speaks in the present tense belongs to A.0 or says which commit it means.
```

# 00 — Audit

---

## A.0 Current state, checked against the tree on 2026-10-27

> Why this section exists: an external review on 2026-10-27 correctly found that this document stated
> "`README.md` — none exists … CI — none" under a `Last verified: 2026-10-25` header while the
> repository had had a README, packaging, nine docs, four scripts and an eight-job pipeline since
> commits made that same day. The audit was not wrong when it was written; it stopped being true and
> kept its date. That is a documentation-reliability defect of the first order, and a renewed date
> would not have fixed it. So the history stays, and current state moves here, checked against a
> tree rather than remembered. The rule is now C3.5 in `AGENT_CONTRACT.md`.

Machine-checked, from `git ls-files`, `pytest --collect-only` and `.github/workflows/`:

| What the audit said was missing | State now | Where to see it |
|---|---|---|
| `README.md` | exists, 84+ lines, with a measured-results section | `README.md` |
| `pyproject.toml` | exists; zero runtime dependencies; `ariadne` console script | `pyproject.toml`, D-016 |
| `tests/` | 8 files, 98 collected: **97 pass, 1 skips** when the optional PyMuPDF backend is absent, which is how CI runs it (`tests/test_parser.py::test_pdf_with_text_layer_extracts` uses `importorskip`, because the runtime dependency list is empty by policy). Verified on a clean clone under Python 3.11 with `pip install -e .[dev]` | `tests/`, `pyproject.toml` |
| `docs/` | 9 research docs + `SOURCES.md` + this file | `docs/` |
| `docs/SOURCES.md` | exists; `provenance.py` reports 0 dangling / 0 uncited | `scripts/provenance.py` |
| `scripts/` | `fresh.py`, `provenance.py`, `check-sources.py`, `check-links.py`, **`bench.py`** | `scripts/` |
| CI | 8 workflow files; the `ci.yml` pipeline runs 7 jobs (fresh, provenance, sources, links, compile, pytest, benchmark) | `.github/workflows/ci.yml` |
| `CONTRIBUTING.md`, `SECURITY.md`, `LICENSE` | all present | repo root |
| Accuracy measurement of any kind | **now exists**: 24 synthetic CVs + 6 job descriptions, hand-labelled; per-field precision/recall, forbidden-emission count, and a perturbation-stability run, gated by a ratchet | `data/gold/`, `docs/02` §2.7, `docs/05` §5.1, D-035 |

What is still true from the snapshot below, and matters: the evidence discipline is real (98 URLs,
18 arXiv ids, five retractions in B.2), the parser is deterministic and dependency-free, and the two
load-bearing commercial unknowns in B.3 — vendor acceptance rules and vendor parser attribution —
remain unanswered. What changed since: the five measured defects P1-P5 are fixed and tested,
and "no accuracy measurement of any kind" is no longer a fair description.

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
| `src/ariadne_ats/__init__.py` | package surface | committed, **corrected this turn** | now honest (`0.0.1`, 15 exports, all real) |
| `src/ariadne_ats/textutil.py` | normalisation, tokenising, section/bullet detection (151→~190 lines w/ limitation notes) | committed | **behaviour stale** — 4 measured defects, deferred to A1 by the no-code rule |
| `src/ariadne_ats/lexical.py` | TF-IDF + cosine, pure Python (100 lines) | committed, docstring corrected | behaviour fine for English; **no background corpus exists** → IDF is meaningless in the 2-document case |
| `.work/lanes/*.md` (9) | the distilled research reports — this repo's only evidence corpus: 393 lines, **98 unique URLs, 18 arXiv ids** | **now tracked** (were untracked; D-003) | yes, as of 15:2x today |

### A.2 Present but intentionally untracked

| Path | What | Why untracked |
|---|---|---|
| `.work/rescue/*.txt` (9 files, **244 KB**) | raw transcripts of research runs: tool calls + fetched bodies | contains full prompts and vendor page bodies; disposable once distilled. This is where every fact in the lane reports came from |
| `.work/mine.py` | the transcript-miner that recovered evidence from *timed-out* children | scratch, but reproducible; worth promoting into `scripts/` if we ever re-run research |

### A.3 Missing entirely (a public repo must have these) — **historical, superseded by A.0**

Written against `8f31ba9` on 2026-10-25, when it was accurate:

`README.md` — **none exists**. `pyproject.toml` — none. `tests/` — none. `docs/` — empty
before this file. `docs/SOURCES.md` — none, so **no claim in this repo is currently
resolvable by id**. `scripts/` — none, so C3/C4 are unenforced. CI — none. `Makefile`,
`CONTRIBUTING.md`, `SECURITY.md` — none.

**Every line above is now false** (see A.0). It is kept because the audit trail is the point of an
audit; the sentence that made it a defect was using it as a statement about the present.

### A.4 What I changed this turn (Rule 2, commit `c45ed02`)

1. **Deleted** 5 files / 41 KB: `.work/rescue/{18ea5316,1a28a27e,4acf9ebf,d792319c,d7c8d8de}.md`
   — each a timeout stub whose content was a `git diff --no-index` usage dump, not findings.
2. **`src/ariadne_ats/__init__.py:10`** read `from .resume import parse_resume, Resume, Role`.
   Five of its seven imports named files that do not exist; `import ats_research` raised
   `ModuleNotFoundError: No module named 'ats_research.resume'`. Surface trimmed to the 15
   real names, version `0.1.0 → 0.0.1` (0.1.0 advertised an API that did not exist).
3. **`lexical.py`** docstring promised *"the helper `idf_from_background` exists to supply a
   corpus"* — `hasattr(module,'idf_from_background') == False`. Claim deleted. Its pointer to
   `docs/03-matching-and-scoring.md` was dead (docs/ empty) → retargeted to `.work/lanes/scoring.md`.
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
| P1 | `tokenize("Développeur … mit C++ und C")` → `['d','veloppeur','full-stack','mit','c','und','c']` | `textutil.py:24` `re.ASCII` | **any non-English résumé is shredded.** Directly contradicts evidence in our own corpus (German resumes arXiv 2609.22188 [EV-12]; French pipeline JobScout; 5-language JobResQA 2601.23183 [EV-13]) |
| P2 | `content_words("C, Python, Go")` had **no `'c'`** | `content_words` `len(t)>1` | **FIXED in A1**: the rule is now kind-based (a single *letter* survives; a single digit/symbol does not), so the skill **C** is visible. |
| P3 | `looks_multicolumn(...)` → `False` on tab-separated input | old `looks_multicolumn` | **FIXED in A1 by replacement, not repair**: the helper is deleted; `layout.analyze()` runs on the **raw** extraction (where tabs still exist) and reports `MULTICOLUMN_FLATTENED` with a ratio. Proven by `tests/test_parser.py::test_two_column_fixture_is_flagged…` |
| P4 | `bullets_of("Led a team of nine engineers…")` → `[]` | old `bullets_of` | **FIXED in A1**: `segment.bullets()` accepts a marker **or** an achievement shape; the marker-only helper is deleted. |
| P5 | `detect_sections("SUMMARY/experience/SUMMARY")` → 2 keys | first-heading-wins | **FIXED in A1**: `segment.segment()` emits one segment per heading occurrence, flags `SECTION_REPEATED`, and keeps both bodies. |
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
| ATS = requisition/candidate CRM; 9 canonical modules | **A** | `.work/lanes/fundamentals.md` → Wikipedia rev. 2026-10-16 [EV-17] |
| Software touches nearly every application first (parse → dedupe → field/keyword filter → optional rank) | B | fundamentals (2 sources) |
| 97.4 % of Fortune 500 have a detectable ATS; Workday >40 % | **B⁻** *(vendor telemetry, 2 secondaries, self-interested)* | `pin.com/blog/ats-market-share-report`, `matchr.io` [EV-18] |
| Outside F500: 23 systems, none >16.5 %, HHI ≈1,000 | C *(single vendor's telemetry)* | pin.com |
| Market size: $17.22 B vs $2.5 B — 6.9× disagreement | **B (recorded as a conflict, not a number)** | pin.com |
| "ATS auto-rejects 75 %" is unsupported | B | davron.net, duperrin.com |
| Parser pipeline = extraction → OCR fallback → layout/reading-order → **section segmentation** → per-section NER → normalisation; evaluated as field-level EM/F1 | **A** | arXiv 1910.03089 [EV-06], 2509.06200 [EV-05] |
| Segment-specialised ensemble beats single model: **+7 % Recruitment-Similarity**, field-specific weighting | **A** | arXiv 2509.06200 (MSLEF) [EV-05] |
| "100 % parse accuracy" is LinkedIn-format-only; 73 % on suitability | **A** | arXiv 1910.03089 [EV-06] |
| "~95 % accuracy" claims are vendor marketing; **no public leaderboard found** | C + **U** | 3 vendor blogs; absence is our measurement |
| TF-IDF + cosine is the real baseline; hybrid = NER → skill normalisation → TF-IDF → sentence embeddings → weighted ranking | **A** | arXiv 2503.17438 [EV-07]; sbert.net docs [EV-15] |
| Embeddings at scale need ANN + **retrieve→cross-encoder re-rank** | **A** | sbert.net [EV-15] |
| Career vault exists: 12-node LangGraph agent; **+7.8 pts same-domain, −8.0 pts out-of-domain** (n=1, 9 JDs, pilot) | **A, pilot** | **arXiv 2605.05257** [EV-01] |
| ConFit v2 +13.8 % recall / +17.5 % nDCG | **A** | arXiv 2502.12361 [EV-07] |
| Score instability: validity 0.781 with **29.6 % matched-pair reversals** | **A** | arXiv 2609.16517 [EV-02] |
| LLMs fail to pick the objectively better résumé; no abstention on ties | **A** | arXiv 2602.18550 [EV-03] |
| Screening friction = excess false negatives; semantic matching cuts FN without losing precision | **A** | arXiv 2602.04087 [EV-04] |
| Adverse-impact: +2.12 pp pro-White gap reproduced by a 2023 model, null-to-−3.01 pp for 2024+ | **A** | arXiv 2606.28978 [EV-11] |
| Anonymisation **leaks** demographics (4,100 variants, 18 LLMs) | **A** | arXiv 2603.05189 [EV-08] |
| Self-preferencing: +23–60 % shortlisting for same-LLM candidates | **A** | arXiv 2509.00462 [EV-10] |
| Prompt-injection benchmarks exist for résumé screening (channel separation) | **A** | arXiv 2609.20188 [EV-09] |
| **JSON Resume v1.7.0**: Draft-07, ISO 8601, 14 optional sections, `custom` = sanctioned, preserved extension point | **A** | jsonresume.org/schema/ (`[PROVEN]`) [EV-16] |
| Rezi: Free $0 / Pro **$29/mo** / Lifetime **$149** / Enterprise **$99/mo per 200 users**; "62 % of users land an interview" = marketing | **A** for the page, **C** for the claim | rezi.ai/pricing `[PROVEN]` [EV-21] |
| Enhancv free = 7 days, 12 section items; Pro price is JS-injected (`€ NaN` in raw HTML) | **A** | enhancv.com/pricing `[PROVEN]` |
| JobScout: **deterministic local scoring, no AI call**, ±10/−6 contract, re-score endpoint, deletion-based anti-hallucination, pdf-parse/pdfjs/mammoth/tesseract FR+EN | **A** (`[PROVEN]` README body) | github.com/latenightsbeats1208-pixel/jobscout [EV-19] |
| AviCV exposes **MCP** at `avicv.com/mcp`, RenderCV PDF, FastAPI+SQLite, Gemini via OpenRouter | **A** | sinaatalay/avicv `[PROVEN]` [EV-20] |
| Resume-Scanner = all-MiniLM-L6-v2 + TF-IDF + Gradient Boosting; calls its score *"an analytical estimate"* | **A** | Soham-Barate/Resume-Scanner `[PROVEN]` |
| career-ops has a **fact-gate** (commit-level) | **C** | `fix(fact-gate): read French counts in generated CVs` |
| Jobsuit workflow: per-section autofix → score 66→69 → keyword-match → per-keyword bullet proposal w/ accept/reject → categories **modification / contextual match / not applicable** | **B** (transcript; workflow only, **not** its numbers) | `data/sources/…jobSuit-ai-demo-transcript.md` [EV-22] |
| This box: pypdf/pymupdf/python-docx/numpy **present**; sklearn/sentence-transformers/chromadb/rendercv/typst **absent** | **A** (executed 15:38Z) | local probe |

### B.2 Retracted this turn — corrected in place, no `corrections.md`

| Retracted claim | What it became | Where the wrong statement came from |
|---|---|---|
| *"NYC LL144 effective 1 Jan 2023"* | **U** — deleted from evidence; the date was **in my own search query string**, never in retrieved text; the NYC.gov page returned *"outdated or non-existing page"* | `.work/lanes/legal.md:13,37` [EV-24] |
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
notes as its knowledge, not as retrieved text** (`.work/lanes/parsing.md` [EV-23], "Unverified engineering
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
| G-5 | ~~EU AI Act high-risk status for a candidate-side tool~~ **RESOLVED 2026-10-25 at grade A** — Annex III(4)(a) read verbatim, Art. 6(3) derogation + profiling override read, and the amending instrument **Reg. (EU) 2026/1744** read in the OJ (Annex III route now 2 Dec 2027; Art. 50 live since 2 Aug 2026). Two branches answered in `docs/09` §1.2 | settled, with residual items at `docs/09` §7 | Publications Office Cellar `celex/32024R1689` + `celex/32026R1744` after EUR-Lex HTML returned **202 with a zero-byte body** | 0 |
| G-6 | Rezi's "not an official ATS score" wording | our own disclaimer benchmark | `help.rezi.ai` search for "ATS score" | 2 fetches |
| G-7 | A background corpus for IDF (P7) | without it, IDF is decorative | ESCO skills API + 500 public JDs, or `data/` seed we compile; declare licence in DECISIONS | 1 day |
| G-8 | Ground-truth superiority pairs | no accuracy claim is possible without them | build synthetically per arXiv 2602.18550 [EV-03] / 2609.16517 method; PopResume (2603.22714 [EV-14]) availability request | 2-3 days |
| G-9 | arXiv `date_conflict` cause (6 rows) | tiny, but it is an unlabelled data defect in a shipped file | one arXiv API call per conflicting id, compare `published` vs `updated` | 6 calls |

### C.2 Promised in A0 and not written

`docs/SOURCES.md` · `01-what-an-ats-is.md` · `02-parsing-and-what-breaks-it.md` ·
`03-matching-and-scoring.md` · `04-generation-rag-and-provenance.md` ·
`05-reliability-fairness-security.md` · `06-open-source-landscape.md` ·
`07-product-workflow-teardown.md` · `08-known-unknowns.md` · `DECISIONS.md` *(placed at
repo root as `DECISIONS.md` instead — D-001 reasoning; if you want it under `docs/`, say so and
I move it with history)*.
**Status updated 2026-10-25: 2 of 10 written** — `docs/09-eu-legal-compliance.md` (owner-mandated EU
deliverable, D-009) and **`docs/SOURCES.md`** (the source register, C4, D-013), plus this file. The other 8 are unwritten; `.work/lanes/*.md` still hold their content as raw reports (no `Last verified:` header, no source ids, mixed voice). `docs/08-known-unknowns.md` is now partly **forced** by `docs/09` §7, whose six legal unknowns each carry a named probe and migrate into it verbatim when it is written.
they are raw reports, not docs — no `Last verified:` header, no source ids, mixed voice.

### C.3 Infrastructure

1. ~~`scripts/check-sources.py`~~ **DONE 2026-10-25** — `scripts/check-sources.py`: 39-source probe
   manifest, `ok/walled/dead/unreachable` classification, content-length + hash delta, `--probe`
   manual only, fails on a registered-but-unprobeable source.
2. ~~`scripts/fresh.py`~~ **DONE** — 90-day general clock + 30-day `Live surfaces:` clock, exits 1 on
   a missing header or a stale doc.
3. ~~`scripts/provenance.py`~~ **DONE** — bidirectional `[Xn]` ↔ `SOURCES.md`, currently
   **39 sources / 0 dangling / 0 uncited**.
4. CI — **historical**: at the snapshot nothing ran. Since then: `.github/workflows/ci.yml` with the
   six original gates plus a seventh (`benchmark`, added 2026-10-27, D-035), and three further
   workflows for dependency review, failure alerting and health checks.
5. Packaging — **historical**: `pyproject.toml` now exists, declares zero runtime dependencies and
   puts `pytest` in the `dev` extra, so `pytest` is no longer undeclared.
6. `README.md` — **historical**: present, and it now leads with measured numbers rather than intent.

---

## D. Health assessment

> **Snapshot verdict (2026-10-25, tree at `8f31ba9`).** Read A.0 first: the paragraph below describes
> that tree. Two of its five numbered blockers (no tests/CI, no accuracy measurement) have since been
> closed; the other three have not.

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
**(3)** a legal surface assessed for the EU only (`docs/09-eu-legal-compliance.md`, grade A on the
instruments that bind a candidate-side tool, six items still open at its §7) and for **nothing**
directly outside the EU by explicit scope decision, **(4)** a codebase that
fails on non-English input while the literature we cite is explicitly multilingual, and
**(5)** an undecided licence and copyright holder. Drifting? No — but the gap is now *measured*
rather than assumed, which is the difference between a project with debts and one with surprises.

### D.1 The same five blockers, re-checked on 2026-10-27

| # | Blocker as written at the snapshot | State now | Evidence |
|---|---|---|---|
| 1 | no verified knowledge of any real ATS's acceptance rules (7 of 8 UNKNOWN) | **unchanged**. V-1 is still the item that limits what the product may say | `docs/08` §8.2, DR-1 |
| 2 | no validity harness, so every accuracy sentence would be invented | **closed for extraction**: 24 hand-labelled documents, per-field precision/recall, a forbidden-emission count and a stability run, all gated | `data/gold/`, `docs/02` §2.7, D-035 |
| 3 | legal surface assessed for the EU only | **unchanged by decision** (`docs/09` §9); six items still open at §7 | `docs/09` |
| 4 | codebase fails on non-English input while the literature is multilingual | **partly closed and measured**: the tokenizer is Unicode-aware, the heading vocabulary now covers de/fr/es/el/ga, and the gold set scores those fixtures at the same recall as English ones — with n=1 per language, which is a coverage floor, not language support | `docs/02` §2.7, D-040 |
| 5 | undecided licence and copyright holder | **unchanged**; `LICENSE` still records holder as [OPEN G2] | `LICENSE`, G2 |

The strategic risk named in the external review — investing in more process before proving the base
parser — is the reason increment 2 of this round was a benchmark and not a gate. One gate was added
(`benchmark`, which measures) and no gate that only checks paperwork was added.

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
   multilingual evidence 2609.22188 / 2601.23183 [EV-13].

---

## G. Your decisions — as choices

| # | Choice | Recommendation | Reasoning |
|---|---|---|---|
| **G1** | Name: **A** `ariadne` everywhere (rename `src/ats_research`, one commit with history) / **B** keep `ats_research` package, `Ariadne` repo / **C** other | **A, now** | Cheapest before the first tag, first PyPI name, or first citation. Two names in a repo is how a project loses its import path |
| **G2** | Licence: **A** MIT + CC BY docs / **B** AGPL-3.0 / **C** Apache-2.0 | **A** | Matches the ecosystem we cite; keeps AGPL sources design-only (C7.6). B is a business model choice we have not made |
| **G3** | Positioning: **A** candidate-side only / **B** both sides / **C** recruiter-side | **A for v1** | Mobley treats a vendor that *screens/ranks/rejects* as a potential direct defendant (C-grade but consistent across 5 law-firm sources); candidate-side tooling does not carry that surface |
| **G4** | Repo mechanics: **A** commit `main` from `<working copy>` into empty `Ariadne` / **B** push, then branch+PR for everything after / **C** keep local, mirror | **B** | A one-shot push to seed history, then PRs; `Ariadne` is private and empty, so there is no second writer to race |
| **G5** | Corpus: **A** synthetic fixtures only / **B** synthetic + your own CV behind a local flag (gitignored) / **C** public datasets | **B** | No public corpus has ground-truth superiority (G-8) and HF `datasetmaster/resumes` is flagged weak; your own CV is the single best reality check, kept out of the public tree by `.gitignore` |
| **G6** | Models: **A** OpenAI-compatible adapter + offline hashing baseline / **B** require sentence-transformers / **C** remote-only | **A** | `sentence-transformers`/`sklearn` absent here; a scoring lane with no network call is also the reproducible one (JobScout's "no AI call" precedent, ±10/−6 contract) |
| **G7** | Legal depth: **A** primary-source verification pass (done for the EU, 2026-10-25) / **B** publish with a "no legal analysis" notice | **A for the EU is complete**; next is `docs/09` §7 OJ-1/OJ-2/OJ-3 (registration section, EDPB Art. 22 guidance, Dir. 2000/43) before any public release | The EU deliverable is now grade A on the binding instruments and records 6 unresolved items with probes instead of filling them; `LICENSE` still carries the no-legal-advice notice. Non-EU stays deferred per `docs/09` §9 |
| **G8** | Visibility: **A** keep private until A2 exit / **B** publish now / **C** publish at A0 | **A** | A2 is where we can say what the score means and how often it is wrong; publishing an unvalidated score invites the criticism we would deserve |

**Stop here.** No further file will be written until you approve this report (C1.2, and your
instruction). Two clauses remain `DECLARED` debt on the ledger — **C3** (doc headers) and **C4**
(the three scripts) — and closing them is exactly action F.1.
