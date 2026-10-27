```
Last verified: 2026-10-27
Reviewed by:   Ariadne (principal)
Live surfaces: vendor documentation reachability (the walls below can open or close)
```

# 08 — Known unknowns

Everything this repository **does not know**, with the probe that would close it. A `U` is a recorded
result, not a gap in effort (`AGENT_CONTRACT` C6). An item leaves this file only when the probe
succeeds and the claim is written into the doc that owns it.

Ordering: legal first (highest exposure), then vendor internals, then measurement, then commercial.

## 8.1 Legal (EU) — carried from `docs/09` §7

| id | Unknown | Attempted (all failed) | Next probe |
|---|---|---|---|
| OJ-4 | ISO/IEC 42001 clause structure and the "Annex A = 38 controls" figure | iso.org catalogue page (A for pages/stage); annex text paywalled | obtain the standard, or an ISO-issued public explanatory source. **No control count is stated in this repo until then.** |
| OJ-5 | whether Art. 50(2) machine-readable marking has an adopted code of practice | Commission AI-practice page → "Page not found" | search the AI Office transparency-code pages and the OJ C series |
| OJ-6 | whether a national law in a target market adds provider-side registration beyond Art. 49 | not attempted — out of scope by `docs/09` §9 | only once that jurisdiction's trigger fires |

Resolved and no longer open (kept for the trail in `docs/09` §7.1): OJ-1 Art. 49's section, OJ-2 the
"solely automated" test (WP251rev.01), OJ-3 Dir. 2000/43/EC Art. 3(1)(a).

## 8.2 Vendor internals — the largest hole in the map

| id | Unknown | Attempted | Next probe |
|---|---|---|---|
| V-1 | accepted file formats + size limits, 7 of 8 engines (Workday, Taleo, iCIMS, SmartRecruiters, Ashby, Teamtailor; Greenhouse only via two SEO blogs) | `support.greenhouse.io` **404**; `help.lever.co` **401**; `help.smartrecruiters.com` Cloudflare shell; `help.ashbyhq.com` connect fail; `help.teamtailor.com` **404** | `browser_navigate` on each help centre; `docs.oracle.com` Fusion HCM "Resume Parsing" chapter for Taleo |
| V-2 | parser vendor attribution (Textkernel / Daxtra / Sovren / Radancy) | vendor query returned **0 results** | Textkernel/Daxtra partner-listing pages (their own "works with" pages) |
| V-3 | whether a parse failure silently falls back to manual re-entry | no official source; one career blog is circumstantial | vendor help-centre article search, or a tester account |
| V-4 | boolean/keyword search implementation in any ATS | zero vendor engineering docs surfaced | vendor developer docs (Lever/Greenhouse have public APIs — read their search endpoints) |
| V-5 | any published match-rate threshold owned by a named party | not found; Jobscan's page is walled | none identified; revisit if documentation appears |
| V-6 | parse latency in ms, and corpus size where IDF stabilises | not found | measure IDF variance on 50/500/5,000 synthetic JDs (**we can do this ourselves**) |

V-1 is the item that most limits the product: without it we cannot say which format to emit, and any
"ATS-friendly" claim stays banned (`docs/01` §1.7).

## 8.3 Measurement we have not performed

| id | Unknown | Why it blocks | Probe |
|---|---|---|---|
| M-2 | whether a **score** is stable under competence-preserving perturbation | there is no score to stabilize. The extraction layer's half is measured and published (doc 05 5.1): facts preserved 1.000, ranking inverted 0-6.7 % by transform | A2: the same `bench.stability()` run against `score()` once a score exists, with the declared tolerance from `data/gold/thresholds.json` |
| M-3 | false-negative rate for skill matching | friction is the harm ([EV-04]) | 40 hand-labelled requirement/evidence pairs; compare TF-IDF vs lexicon vs both |
| M-4 | abstention rate, and whether users experience it as failure | doc 04 §4.7 ships abstention as a success value | instrument abstentions and follow-up completion in A3 |
| M-5 | whether better-parsing artefacts are preferred over higher-scoring ones | the core product bet ([HYPOTHESIS] in doc 01 §1.7) | A/B two rendered CVs; measure which users keep |

## 8.3b Opened by the benchmark itself (2026-10-27)

A measurement that closes one unknown always names two more. These are the ones M-1 produced; each is
a question, not a to-do, and each says what would answer it.

| id | Unknown | Why it is a question and not a task | Probe |
|---|---|---|---|
| M-6 | how common the employer-first role line is in real CVs ("Acme Corp - Senior Engineer") | our rule assumes title-first; on the one adversarial fixture we have, both fields come out **swapped**, which is worse than missing. Whether this is 2 % or 30 % of documents is unknown and decides whether the rule needs a tie-breaker at all | label 100 real CVs by convention once a corpus exists (D-4); until then the failure is published, not averaged away |
| M-7 | whether the name rule's "first non-channel line" holds on documents whose name sits elsewhere | cv-24 proves the abstention; it does not say how often the abstention fires in the wild | same corpus as M-6; measure name recall per layout class |
| M-8 | whether stripping heading vocabulary from the comparison removes the 0.098 cosine move that a heading rename causes | we can name the mechanism (heading words are terms) but not the side-effect on term evidence | A2 experiment: cosine with and without heading terms over the gold corpus |
| M-9 | per-language extraction quality beyond one document per language | the 1.000 recall rows for de/el/es/fr/ga/nl are n=1 and must not be read as language support | 5+ documents per language, then report the spread, not the mean |
| M-10 | what the numbers look like on documents nobody here wrote | the gold corpus is author-written by the session that wrote the rules; the 0.947 is a property of this pairing | D-4 / G-8 again: it is the cheapest way to turn our numbers into someone else's numbers |

## 8.4 Data and taxonomy

| id | Unknown | Attempted | Next probe |
|---|---|---|---|
| D-1 | ESCO licence and terms | API existence proven ([EV-31]); terms **NOT-IN-FILE** | read `esco.ec.europa.eu` terms-of-use page and record the licence |
| D-2 | O*NET endpoint shape, size, licence, fields | only mentioned inside search snippets | fetch `services.onetcenter.org` documentation |
| D-3 | JSON Resume schema licence | page body states none ([EV-31]) | GitHub repo `LICENSE` file for the schema |
| D-4 | a corpus with **ground-truth superiority** labels | none found; HF `datasetmaster/resumes` is `weak/entity_mismatch`, Kaggle ones licence-less ([EV-31]) | build synthetic pairs (M-2 method); request PopResume access ([EV-14]) |
| D-5 | ESCO/O*NET → our skill lexicon mapping | not attempted | map 50 skills by hand, measure coverage |

## 8.5 Commercial

| id | Unknown | Evidence status | Next probe |
|---|---|---|---|
| C-1 | willingness to pay in this category | competitor prices only ([EV-29]); **no demand signal** | primary research; do not infer from competitor menus (doc 07 §7.6) |
| C-2 | Jobscan's pricing and claims | **U** at all rungs: 6,653-byte page, `content_chars: 0`, "Just a moment…" | Camoufox with a warm profile; otherwise leave as `U` |
| C-3 | Rezi's / Teal's exact disclaimer wording on score vs ATS | not captured; the earlier "not an official ATS score" claim is **retracted** (audit B.2) | search `help.rezi.ai` for "ATS score" |
| C-4 | whether open-source star counts reflect adoption | `career-ops` 77,167 vs peers flagged implausible ([EV-28]) | contributor graphs, issue quality, release cadence |

## 8.6 Cross-cutting

| id | Unknown | Note |
|---|---|---|
| X-1 | model-provider retention and training terms for any LLM we would call | **U** — no provider terms read. This is why the baseline is local-only (`D-016`) and remote calls are opt-in |
| X-2 | whether our `[HYPOTHESIS]` about layout → field-recovery holds | **partly answered 2026-10-27, and it split.** Where the layout damage leaves field boundaries on the same line (tab-separated role lines, cv-03; glyph damage, cv-20) the fields come back intact. Where the damage moves a boundary to another line (the date on its own line, cv-22) recovery fails completely while the years survive. So "layout damages fields" is too coarse: the recoverable axis is *within-line* structure, and the unrecoverable one is *line merging*. What remains open is the frequency of each in real documents (M-6, M-10) | label real CVs by damage class once a corpus exists (D-4) |
| X-3 | the reversal-rate tolerance we should declare | a **decision**, not a fact: publish the measurement, then set the threshold in `DECISIONS.md` |


## 8.8 Debt register — what would make the thin documents strong

The review accepted four documents as thin (`01`, `05`, `06`, and this one by design). Thinness is a
debt only if it is unnamed. Each row here is the *specific* probe that closes it, the document that
owns the gap, and the artefact that would prove closure. This table is the single place to look for
"what is the cheapest thing that would make us materially stronger".

| # | Owned by | Gap | Probe (exact) | Artefact that proves closure |
|---|---|---|---|---|
| DR-1 | `01` §1.5 | formats / size limits / parser vendor, 7 of 8 engines | browser rung on `support.greenhouse.io`, `help.lever.co`, `help.smartrecruiters.com`, `developers.ashbyhq.com`, `help.teamtailor.com`, `docs.oracle.com` (Fusion HCM → Resume Parsing); then Textkernel + Daxtra partner pages | `docs/01` §1.5 table with quoted sentences + access dates, grades moved off `U` |
| DR-2 | `01` §1.3 | adoption measured only by vendor telemetry | DNS/HTTP census of `careers.<company>` across a fixed 100-company sample | a method paragraph + the sample + the number, in `docs/01` |
| DR-3 | `01` §1.4 | "75 % auto-rejected" rests on one sceptical blog | trace the statistic to its earliest citation, or record that none exists | a paragraph saying "no origin found", with the searches listed |
| DR-4 | `05` §5.1 | no stability number of our own (**M-2**) - **half closed 2026-10-27**: fact-set preservation and a ranking-inversion rate against one fixed advertisement are measured and gated; the number that waits is the one a score would produce | `bench.stability()` over the gold corpus, D-038 | the published rates, in `docs/05` 5.1 |
| DR-5 | `05` §5.2 | fairness is an absence of claims | 40 synthetic CVs differing only in name signal; publish the output delta, or record that measuring it would require a capability C9 forbids | a paragraph either way — both outcomes are publishable |
| ~~DR-6~~ | `05` §5.4 | ~~no field-level parse quality (**M-1**)~~ **CLOSED 2026-10-27**: 24 documents hand-labelled before the parser ran, per-field precision/recall, forbidden-emission count, ratchet floors | `data/gold/manifest.json`, `scripts/bench.py --check`, D-035 | published table in `docs/02` §2.7, artefact `data/gold/results.json` |
| DR-7 | `05` §5.3 | provider retention terms unread (**X-1**) | read the DPA/terms of the single provider we would call; quote the retention sentence | `docs/09` §3 row + a `DECISIONS` entry |
| DR-8 | `06` §6.3 | no maintenance signal; star counts untrusted | per project: `/repos`, `/releases`, `/contributors?per_page=100`, 90-day commit histogram, stargazer timestamps | maintenance table in `docs/06`, star counts either vindicated or annotated |
| DR-9 | `06` §6.2 | two licences unread | `GET /repos/{o}/{r}/contents/LICENSE` for `sinaatalay/avicv`, `BPMSoftwareSolutions/agentic-resume-tailor` | quoted first line per project |
| DR-10 | `06` §6.2 | "no vector DB anywhere" is an absence of mention | code search per repo for `chromadb|qdrant|pgvector|faiss|pinecone` | hits, or "absence-of-use confirmed" |
| DR-11 | `08` §8.2 | every vendor `U` | as DR-1 | as DR-1 |
| DR-12 | `08` §8.4 | no corpus with ground-truth superiority (**D-4**) | synthetic pairs per the M-2 method; request PopResume access ([EV-14]) | a corpus path + a licence note, or a recorded refusal |
| ~~DR-13~~ | `05`/`09` | ~~branch protection absent (plan-gated)~~ **CLOSED 2026-10-25** — repository flipped public, protection active with six required contexts (`D-031` carries the API response) | — | — |

**Priority.** DR-1 is first now that DR-4's extraction half is closed: it is the only remaining gap
that limits what the product may *say*. Next is the corpus gap (D-4/G-8): our own numbers are measured
on 24 documents written by the session that wrote the rules, which is a floor and not a distribution.
DR-13 is third because it is a purchase/visibility decision, not an engineering one.: it is the only gap that limits what the product may *say* about
compatibility. DR-13 is third because it is a purchase/visibility decision, not an engineering one.

## 8.7 How this file is maintained

* An item is added when a doc records `[OPEN]` or a probe returns `U`.
* An item is **closed** by writing the resolved claim into the owning doc and deleting the row here —
  not by adding a "resolved" note (that is how this file would rot into a changelog).
* `scripts/fresh.py` puts this file on the **30-day** clock, because most of its rows are about live
  external surfaces: a stale unknown is an unknown that may already have been answered.

## What would make this strong

This file is thin **by design** — it is a schedule, not an argument. It becomes strong when rows
leave it: each closure must delete its row here *and* land the resolved claim in the owning doc (8.7).
Its weakness is that it can quietly become a museum of stale unknowns, which is why it sits on the
**30-day** clock: an unfreshened unknown is an unknown that may already have been answered.
