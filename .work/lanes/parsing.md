

# Research: How resume parsing works internally

## Summary
Two verified academic anchors (arXiv 1910.03089, 2019; arXiv 2509.06200, 2025) plus a ScienceDirect field-level-eval paper confirm the shape of the pipeline: text-layer extraction with OCR fallback → layout/reading-order recovery → section segmentation → per-section NER/field extraction → normalisation to a controlled vocabulary, with evaluation moving from raw accuracy to EM/F1/RS at field level. Published hard numbers are scarce: the only benchmark-named figure I received verbatim is 100% parse accuracy on LinkedIn-format resumes (2019) and +7% Recruitment-Similarity for a segment-aware LLM ensemble (2025). The "~95–98%" figures circulating are vendor-blog claims, not benchmarks.

## Findings
- Pipeline stages named in literature: OCR + layout-aware parsing as preprocessing, with accuracy scored at field level (source: https://www.sciencedirect.com/science/article/pii/S2590005626004418, n.d./2026)
- Two-stage architecture is standard: a parser that extracts complete structured resume info, then a separate BERT sentence-pair classifier for job-candidate suitability (source: https://arxiv.org/abs/1910.03089, 2019-09-30)
- Benchmark-named number: "We parse the LinkedIn resumes with 100% accuracy and establish a strong baseline of 73% accuracy for candidate suitability" — same source; the 100% is on *LinkedIn-format* resumes only, i.e. the easy, structured-input regime.
- Section segmentation is explicit and segment-aware: MSLEF gives "each model specializing in a specific resume segment," with "field-specific weighting tailored to each resume part," explicitly to overcome "diverse formats and structures" and "varied resume layouts" (source: https://arxiv.org/abs/2509.06200, 2025-09-07, AICCSA 2025)
- Second published number: MSLEF reports gains in Exact Match, F1, BLEU, ROUGE, and "Recruitment Similarity (RS)," beating the best single model "by up to +7% in RS"; stack = Gemma 9B + LLaMA 3.1 8B + Phi-4 14B under weighted voting with Gemini-2.5-Flash as high-level aggregator (source: https://arxiv.org/abs/2509.06200, 2025-09-07)
- MSLEF builds on MLAR, a multi-layer LLM + RPA pipeline over ATS workflows (source: https://arxiv.org/abs/2507.10472, 2025-07-14, title/abstract metadata only)
- Field extraction is described as section-scoped: "Within each section, the parser extracts structured fields. Job title, employer, dates, location for experience…" (source: https://www.thehirehub.ai/blog/ai-resume-parsing-in-2026-how-it-works-how-accurate-it-actually-is-and-what-breaks-it, 2026-05-07, vendor blog)
- Error-compounding claim: "OCR accuracy on a clean scan is around 98% at the character level, which compounds to roughly 85% at the field level" (source: https://resumeoptimizerpro.com/blog/how-resume-parsers-actually-work, 2026-04-22, vendor blog, low quality)
- "~95% accuracy" is marketing-universal: "Every resume parser and AI extraction tool claims ~95% accuracy" (source: https://imagetotable.ai/blog/resume-parsing-software-vs-ai-extraction, 2026-08-10, vendor blog)

## Verification
- **Cross-referenced**: (a) field-level/section-scoped evaluation — ScienceDirect + MSLEF + HireHub; (b) OCR-then-NER pipeline — ScienceDirect + Medium OCR+NER-vs-LLMs article; (c) layout as a first-class failure axis — MSLEF wording + HireHub.
- **Needs verification (single source)**: the 98%→85% character-vs-field compounding figure; the generic ~95% claim; MLAR's role (abstract not fetched).
- **Conflicting**: 100% parse accuracy (2019, LinkedIn-format) vs ~85–95% field accuracy (2026 vendor blogs). Not truly conflicting — different input distributions — but the 2019 number is frequently mis-cited as general-purpose accuracy.
- **Source quality**: HIGH — two arXiv records + arXiv API feed; MEDIUM — ScienceDirect (abstract snippet only); LOW — three vendor blogs.
- **Unverified engineering detail**: byte-level `ToUnicode`/`ActualText` text-layer extraction, x-y projection reading-order recovery, ligature (`fi`/`fl`) decomposition, header/footer band rejection, OCR'd icon/logo handling, and mapping to ESCO/ONET/SOAT skill taxonomies — this is standard-engineering synthesis from my own knowledge, NOT from any tool output in this run. Mark UNVERIFIED.

## GAPS
- No page bodies were fetched for the three vendor blogs (fast-path budget), so their "what breaks parsers" lists (multi-column, tables, text boxes, headers/footers, images, icons, hyperlinks, ligatures, custom/embedded fonts) are **not** confirmed verbatim — only MSLEF's "diverse formats and structures / varied resume layouts" is attested.
- No named public resume benchmark or leaderboard found. The 2019 paper uses an internal LinkedIn-format corpus; MSLEF does not name its dataset in the abstract. Candidate: RESUME (Kuznetsov & Lagun, WeLM 2016) — **NOT retrieved, DO NOT CITE without fetching**.
- No skill-taxonomy-normalisation paper surfaced (ESCO/ONET mapping, schema linking).
- First arXiv API call returned zero bytes over plain HTTP; retried over HTTPS successfully.

**TOOL FAILED: `curl http://export.arxiv.org/...` returned empty output; HTTPS retry worked.**