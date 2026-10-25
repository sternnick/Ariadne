# SOURCES.md — the source register

```
Last verified: 2026-10-25
Reviewed by:   Ariadne (principal)
Rule:          every [Xn] cited in docs/ must appear here; every entry here must be cited at
               least once in docs/. Enforced by scripts/provenance.py (AGENT_CONTRACT C4).
```

**Grade legend** (AGENT_CONTRACT C5.2): **A** primary text read · **B** official secondary
guidance read, or a structural inference from primary text · **C** snippet only · **U** attempted,
unreachable.

**Access convention.** `accessed` is the date *this repository* retrieved or read the item.
`status` is the last recorded result from `scripts/check-sources.py` (`ok`, `walled`, `dead`,
`unprobed`). A `walled`/`dead` source keeps its grade only for the claims it supported **at the time
it was read**; it may not support a new claim until re-probed (C6.3).

**Retrieval note that applies to every EU instrument below.** `eur-lex.europa.eu/legal-content/…`
returns **HTTP 202 with a zero-byte body** to this machine (edge bot-handling). The instruments were
therefore read from the Publications Office repository (`publications.europa.eu/resource/celex/…`),
which serves the same Official Journal XML/PDF, or from the EUR-Lex **PDF datastream** of that same
CELEX id. Both are official. Where a datastream did not exist, the record says so.

---

## EU legal instruments

| id | Source | What it supports | Grade | accessed | status |
|---|---|---|---|---|---|
| EU-01 | Regulation (EU) 2024/1689 (AI Act), OJ L 165/3, 13.7.2024 — Cellar `celex/32024R1689` (XHTML + 144-page PDF) | Annex III(4)(a) verbatim; Art. 3(3)(4)(12)(52); Art. 5(1)(g); Art. 6(2)–(4); Art. 26; Art. 43(1)–(2); Art. 49; Art. 50; Art. 113; Section 3 vs Section 4 headings | A | 2026-10-25 | ok |
| EU-02 | **Regulation (EU) 2026/1744** ("Digital Omnibus on AI"), done at Brussels 12.10.2026 — Cellar `celex/32026R1744` | amends Art. 113(3): Annex III route → 2 Dec 2027, Annex I → 2 Aug 2028; new Art. 5(1)(ba),(bb) from 2 Dec 2026; Art. 111(4) → 2 Dec 2026 | A | 2026-10-25 | ok |
| EU-03 | Regulation (EU) 2016/679 (GDPR) — Cellar `celex/32016R0679` | Arts. 4(7)(8), 5, 6, 9, 13–17, 20, 22, 25, 32, 35 | A | 2026-10-25 | ok |
| EU-04 | Directive (EU) 2024/2831 (platform work) — Cellar `celex/32024L2831` | Art. 1(1) purpose; Art. 2(1) 'digital labour platform' definition → scope exclusion | A | 2026-10-25 | ok |
| EU-05 | Directive 2006/54/EC — Cellar `celex/32006L0054` | Art. 14(1)(a): access to employment incl. selection criteria and recruitment conditions | A | 2026-10-25 | ok |
| EU-06 | Directive 2000/43/EC — Cellar `celex/32000L0043` **PDF datastream** (no XHTML datastream exists) | Art. 3(1)(a) verbatim, racial/ethnic origin, selection criteria and recruitment conditions | A | 2026-10-25 | ok |
| EU-07 | Directive 2004/113/EC — Cellar `celex/32004L0113` | recital: employment/occupation is covered by other instruments → out of scope for hiring | A | 2026-10-25 | ok |
| EU-08 | Directive (EU) 2024/1500 — Cellar `celex/32024L1500` | equality bodies' competences (Member-State duties); AI appears only in a recital | A | 2026-10-25 | ok |
| EU-09 | Commission Implementing Decision (EU) 2026/2274, done 12.10.2026 — Cellar `celex/32026D2274` | cites **EN 18286:2026** (AI quality management system) as the first Art. 40 harmonised standard | A | 2026-10-25 | ok |
| EU-10 | **WP251rev.01** — *Guidelines on Automated individual decision-making and Profiling for the purposes of Regulation 2016/679*, Art. 29 WP, adopted 3.10.2017, last revised and adopted 10.10.2017 (EDPB-endorsed), 37 pp | "solely" = no human involvement; "cannot avoid … by fabricating human involvement"; "meaningful, not a token gesture"; "authority and competence to change the decision"; human involvement does not remove profiling | B | 2026-10-25 | ok |
| EU-11 | Directive 2000/78/EC — archived EUR-Lex copy (Wayback) | Art. 3(1)(a): conditions for access to employment incl. selection criteria | B (archive) | 2026-10-25 | ok |

## ISO / IEC standards (jurisdiction-neutral)

| id | Source | What it supports | Grade | accessed | status |
|---|---|---|---|---|---|
| ISO-01 | ISO/IEC 42001:2023 — iso.org/standard/81230.html | published [60.60], 51 pp, 2023-12, JTC 1/SC 42; **catalogue page read only** — clause text and Annex A are paywalled | A (catalogue) / U (content) | 2026-10-25 | ok |
| ISO-02 | ISO/IEC 27001:2022 — iso.org/standard/27001 | published [60.60], 19 pp, 2022-10, JTC 1/SC 27 | A (catalogue) / U (content) | 2026-10-25 | ok |
| ISO-03 | ISO/IEC TS 27701:2025 — iso.org/standard/27701 | published [60.60], Ed. 2, 64 pp, privacy information management extension to 27001/27002 | A (catalogue) / U (content) | 2026-10-25 | ok |
| ISO-04 | ISO 30405:2023 — iso.org/standard/79488.html | **guidance only** ("provides guidance on how to attract, source, assess and employ people"), Ed. 2, 2023-06, 16 pp, ISO/TC 260 — not a certification target | A (catalogue page read via browser) | 2026-10-25 | ok |

## Research evidence cited by docs/

| id | Source | What it supports | Grade | accessed | status |
|---|---|---|---|---|---|
| EV-01 | arXiv 2605.05257 — career-vault / multi-source RAG tailoring, case study | vault retrieval: +7.8 pts same-domain, **−8.0 pts out-of-domain** (n=1, 9 JDs, pilot) → retrieval gating | A | 2026-10-25 | unprobed |
| EV-02 | arXiv 2609.16517 — competence-preserving resume perturbations | best validity 0.781 with **29.6 % matched-pair reversals** → score must ship as a band | A | 2026-10-25 | unprobed |
| EV-03 | arXiv 2602.18550 — measuring validity in LLM resume screening | LLMs fail to pick the objectively better CV; no abstention on ties | A | 2026-10-25 | unprobed |
| EV-04 | arXiv 2602.04087 — algorithmic friction in automated screening | friction = excess false negatives; semantic matching cuts FN without losing precision | A | 2026-10-25 | unprobed |
| EV-05 | arXiv 2509.06200 — MSLEF segment-specialised ensemble | +7 % Recruitment Similarity; layout/segmentation is the failure axis | A | 2026-10-25 | unprobed |
| EV-06 | arXiv 1910.03089 — parser + BERT suitability classifier | 100 % parse accuracy on LinkedIn-format input only; 73 % suitability | A | 2026-10-25 | unprobed |
| EV-07 | arXiv 2503.17438 — resume-screening survey | TF-IDF + cosine is the implemented baseline; hybrid layer stack | A | 2026-10-25 | unprobed |
| EV-08 | arXiv 2603.05189 — demographic leakage in anonymised screening | anonymisation leaks; 4,100 variants × 18 LLMs | A | 2026-10-25 | unprobed |
| EV-09 | arXiv 2609.20188 — ResumeShield, indirect prompt injection | channel separation is a required design control | A | 2026-10-25 | unprobed |
| EV-10 | arXiv 2509.00462 — AI self-preferencing in hiring | +23–60 % shortlisting for same-LLM candidates | A | 2026-10-25 | unprobed |
| EV-11 | arXiv 2606.28978 — paired-resume adverse impact | +2.12 pp gap reproduced (2023 model); 2024+ null-to-−3.01 pp | A | 2026-10-25 | unprobed |
| EV-12 | arXiv 2609.22188 — German LLM-generated CVs | generation-side demographic leakage | A | 2026-10-25 | unprobed |
| EV-13 | arXiv 2601.23183 — JobResQA benchmark | multilingual résumé/JD benchmark, 5 languages | A | 2026-10-25 | unprobed |
| EV-14 | arXiv 2603.22714 — PopResume | 60.8 K résumés; path-specific discrimination effects | A | 2026-10-25 | unprobed |
| EV-15 | sbert.net semantic-search docs | cosine is the default score function; ANN + retrieve→re-rank needed at scale | A | 2026-10-25 | unprobed |
| EV-16 | jsonresume.org/schema — JSON Resume v1.7.0 | Draft-07, ISO 8601, 14 optional sections, `custom` extension point preserved by tools | A | 2026-10-25 | unprobed |
| EV-17 | en.wikipedia.org/wiki/Applicant_tracking_system (rev. 2026-10-16) | ATS definition and the nine canonical modules | A (for the definition) | 2026-10-25 | unprobed |
| EV-18 | pin.com/blog/ats-market-share-report + matchr.io | 97.4 % of Fortune 500 have a detectable ATS; Workday >40 %; **vendor telemetry — self-interested** | B⁻ | 2026-10-25 | unprobed |
| EV-19 | github.com/latenightsbeats1208-pixel/jobscout (README body) | deterministic local scoring, no AI call; ±10/−6 contract; deletion-based anti-hallucination; pdf-parse/mammoth/tesseract cascade | A | 2026-10-25 | unprobed |
| EV-20 | sinaatalay/avicv (README body) | MCP endpoint at avicv.com/mcp; RenderCV PDF; "factual checks" | A | 2026-10-25 | unprobed |
| EV-21 | rezi.ai/pricing (page body) | Free $0 / Pro $29/mo / Lifetime $149 / Enterprise $99 per 200 users; "62 % of users land an interview" = marketing | A (page) / C (claim) | 2026-10-25 | unprobed |
| EV-22 | `data/sources/2026-10-25-jobSuit-ai-demo-transcript.md` (this repo) | Jobsuit workflow: autofix → score → keyword proposal with accept/reject → categories modification/contextual match/not applicable. **Unverified transcript; workflow only, no names or numbers** | B | 2026-10-25 | ok |
| EV-23 | `.work/lanes/parsing.md` (this repo, distilled research) | parser pipeline stages; the "~95 % accuracy" claim is marketing; no public leaderboard found | B | 2026-10-25 | ok |
| EV-25 | `.work/lanes/fundamentals.md` (this repo) | ATS definition, nine modules, F500 adoption, the unsupported "75 % auto-reject" claim | B | 2026-10-25 | ok |
| EV-29 | `.work/lanes/commercial.md` (this repo) | Rezi/Enhancv pricing read from page bodies; Teal/Kickresume snippet-only; Jobscan walled | B | 2026-10-25 | ok |
| EV-28 | `.work/lanes/opensource.md` (this repo) | JobScout/AviCV/Resume-Scanner/career-ops mechanisms with PROVEN/SNIPPET-ONLY labels | B | 2026-10-25 | ok |
| EV-31 | `.work/lanes/data.md` (this repo) | JSON Resume v1.7.0 field list; ESCO/O*NET/Lightcast state of knowledge | B | 2026-10-25 | ok |
| EV-27 | `.work/lanes/scoring.md` (this repo) | TF-IDF/cosine as the implemented baseline; SBERT defaults; ANN + re-rank | B | 2026-10-25 | ok |
| EV-30 | `.work/lanes/papers.md` (this repo) | the 2024-2026 tailoring + fairness literature index | B | 2026-10-25 | ok |
| EV-26 | `.work/lanes/engines.md` (this repo) | what vendor documentation actually says about formats/limits — and the six documented fetch failures | C | 2026-10-25 | ok |
| EV-24 | `.work/lanes/legal.md` (this repo, distilled research) | the record of what *failed* — LL144 page, ilga.gov timeout, snippet-only case law. Retained as a **negative** result, not authority | C/U | 2026-10-25 | ok |

---

## Recorded failures (these are results, not gaps — C6.1)

| Target | Error | Consequence |
|---|---|---|
| `eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:*` | HTTP **202**, `size_download: 0` (every CELEX, cookie-jar and referer retries both) | route via Cellar/PDF, documented above |
| `publications.europa.eu/resource/celex/32000L0043` with `Accept: application/xhtml+xml` | HTTP **400**: "does not hold a content datastream of the requested type" | used the **PDF** datastream instead (EU-06) |
| `nyc.gov/site/ccp/services-projects/local-law-144/` | boilerplate "outdated or non-existing page" | out of scope for this EU-only document; the earlier LL144 claim stays retracted (`docs/00-audit.md` B.2) |
| EDPB `guidelines-012025-*`, `guidelines-automated-individual-*`, `/our-documents/guidelines_en` | HTTP **404** ×3 | guidance reached via the official Commission newsroom copy of WP251rev.01 (EU-10) |
| iso.org `standard/79488.html` via curl | HTTP **403** Cloudflare | retrieved via `browser_navigate` (browser rung) — same catalogue page |
| `digital-strategy.ec.europa.eu/en/policies/ai-act-practice/harmonised-protocols-and-standards-ai-act` | "Page not found" | EN 18286 citation confirmed instead from the OJ instrument (EU-09) |

## Probe manifest

Machine-readable `ID  URL` lines consumed by `scripts/check-sources.py`. A plain line block,
not a table row, so `scripts/provenance.py` counts each source exactly once. A registered source
with no line here is reported as `no-manifest` — a defect, not a skip.

**EV-22/23/24** are in-repo artifacts, declared as `local:<path>`: the checker verifies the file
exists in the tree instead of attempting a network fetch (a deleted evidence artifact is a real
defect, and this catches it).

```
EU-01 https://publications.europa.eu/resource/celex/32024R1689
EU-02 https://publications.europa.eu/resource/celex/32026R1744
EU-03 https://publications.europa.eu/resource/celex/32016R0679
EU-04 https://publications.europa.eu/resource/celex/32024L2831
EU-05 https://publications.europa.eu/resource/celex/32006L0054
EU-06 https://publications.europa.eu/resource/celex/32000L0043
EU-07 https://publications.europa.eu/resource/celex/32004L0113
EU-08 https://publications.europa.eu/resource/celex/32024L1500
EU-09 https://publications.europa.eu/resource/celex/32026D2274
EU-10 https://ec.europa.eu/newsroom/article29/redirection/document/49826
EU-11 https://web.archive.org/web/2025/https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32000L0078
ISO-01 https://www.iso.org/standard/81230.html
ISO-02 https://www.iso.org/standard/27001
ISO-03 https://www.iso.org/standard/27701
ISO-04 https://www.iso.org/standard/79488.html
EV-01 https://arxiv.org/abs/2605.05257
EV-02 https://arxiv.org/abs/2609.16517
EV-03 https://arxiv.org/abs/2602.18550
EV-04 https://arxiv.org/abs/2602.04087
EV-05 https://arxiv.org/abs/2509.06200
EV-06 https://arxiv.org/abs/1910.03089
EV-07 https://arxiv.org/abs/2503.17438
EV-08 https://arxiv.org/abs/2603.05189
EV-09 https://arxiv.org/abs/2609.20188
EV-10 https://arxiv.org/abs/2509.00462
EV-11 https://arxiv.org/abs/2606.28978
EV-12 https://arxiv.org/abs/2609.22188
EV-13 https://arxiv.org/abs/2601.23183
EV-14 https://arxiv.org/abs/2603.22714
EV-15 https://sbert.net/examples/applications/semantic-search/README.html
EV-16 https://jsonresume.org/schema/
EV-17 https://en.wikipedia.org/wiki/Applicant_tracking_system
EV-18 https://www.pin.com/blog/ats-market-share-report/
EV-19 https://github.com/latenightsbeats1208-pixel/jobscout
EV-20 https://github.com/sinaatalay/avicv
EV-21 https://www.rezi.ai/pricing
EV-22 local:data/sources/2026-10-25-jobSuit-ai-demo-transcript.md
EV-23 local:.work/lanes/parsing.md
EV-24 local:.work/lanes/legal.md
EV-25 local:.work/lanes/fundamentals.md
EV-26 local:.work/lanes/engines.md
EV-27 local:.work/lanes/scoring.md
EV-30 local:.work/lanes/papers.md
EV-28 local:.work/lanes/opensource.md
EV-29 local:.work/lanes/commercial.md
EV-31 local:.work/lanes/data.md
```
