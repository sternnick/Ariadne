

## Summary
Both sub literatures exist and are now dense on arXiv. The "career vault" longitudinal multi-source RAG idea is a real, findable paper: **arXiv:2605.05257** (May 2026), which reports ATS-style fit-score deltas. Fairness work has moved from name-based audits (2024) to causal/path-specific and adverse-impact-style gap measurement (2026).

## Findings — (a) tailoring / RAG
- **Career vault paper found.** "Resume Tailor": 12-node LangGraph agent keeping a longitudinal career vault in a vector DB, multi-source RAG over historical resumes + structured career records, hybrid semantic-lexical confidence scoring, provenance tracking, anti-hallucination guardrails. Pilot, 9 JDs, one candidate's career history: **enabling the vault improved ATS-style fit scores +7.8 pts avg** on 6 same-occupational-category JDs, **−8.0 pts** on 2 out-of-domain JDs, +2 on a partial overlap (source: https://arxiv.org/abs/2605.05257, 2026-05-06; also on SSRN, 6 pages).
- ResumeFlow — LLM pipeline for personalized resume generation/tailoring; SIGIR 2024 demo, no headline metric in abstract (source: https://arxiv.org/abs/2402.06221, 2024-02-09).
- ConFit v2 — LLM-generated hypothetical reference resumes + runner-up hard-negative mining for resume–job matching: **+13.8% recall, +17.5% nDCG** avg vs BM25/OpenAI text-embedding-003 (source: https://arxiv.org/abs/2502.12361, 2025-02-17).
- Multi-agent RAG resume screening (extractor/evaluator/summarizer/formatter, RAG inside evaluator), CVPR 2025 Workshop (source: https://arxiv.org/abs/2504.02870, 2025-04-01).
- JobResQA — multilingual résumé/JD MRC benchmark: 581 QA pairs, 105 synthetic résumé-JD pairs, 5 languages, placeholders for bias studies (source: https://arxiv.org/abs/2601.23183, 2026-01-30).

## Findings — (b) screening fairness / adverse impact
- **Paired-resume adverse-impact estimate**: 14 LLMs, 24,024 paired postings/model, Kline–Rose–Walters method; the 2023-vintage model reproduces the **+2.12 pp pro-White gap (p<0.01)**; every 2024+ model shows a null gap or pro-Black reversal up to **−3.01 pp** (source: https://arxiv.org/abs/2606.28978, 2026-06-27).
- PopResume — population-representative dataset, **60.8K résumés**, 5 occupations, 4 LLMs + 4 VLMs; path-specific-effect decomposition into business-necessity vs redlining paths; 5 discrimination patterns invisible to aggregate metrics. EMNLP 2026 Main (source: https://arxiv.org/abs/2603.22714, 2026-03-24).
- Anonymized résumés still leak: 100 neutral résumés → 4,100 variants, 4 ethnicities × 2 genders, **18 LLMs**; models recover demographics at high F1, favour Chinese/Caucasian male markers; rationale prompting can amplify bias. EMNLP 2026 (source: https://arxiv.org/abs/2603.05189, 2026-03-05).
- Validity audit: systematically built comparable tailored-résumé corpus with known ground-truth superiority; many LLMs fail to pick the more qualified candidate and don't abstain on ties (source: https://arxiv.org/abs/2602.18550, 2026-02-20).
- ATS-mechanism bias: screening-as-classification, friction = excess false negatives; keyword ATS logic shows high friction, vector-semantic matching cuts FN rejections without losing precision (source: https://arxiv.org/abs/2602.04087, 2026-02-03).
- AI self-preferencing: candidates using the same LLM as evaluator are **23–60% more likely** to be shortlisted; >50% reducible via intervention. EAAMO/AIES 2025 (source: https://arxiv.org/abs/2509.00462, 2025-08-30).
- Presentation sensitivity: 6 open instruction-tuned LLMs; **Llama-3.1-8B best validity 0.781 but 29.6% matched-pair reversals** (source: https://arxiv.org/abs/2609.16517, 2026-09-15).
- Generation-side leakage: German LLM résumés (GPT-4o-mini, Gemini 2.5 Flash-Lite, Qwen3 4B/8B/14B) leak gender/ethnicity under name variation; EU AI Act high-risk framing. ECML PKDD 2026 BIAS ws (source: https://arxiv.org/abs/2609.22188, 2026-08-28). Also: Silicon Ceiling, GPT-3.5, 32 names × 10 occupations (https://arxiv.org/abs/2405.04412, 2024-05-07); FAccT 2026 human-AI: +3–4% selection chance with longer viewing, up to 55.6% longer viewing without AI recs (https://arxiv.org/abs/2606.22213, 2026-06-20).

## GAPS
- **TOOL FAILED (partial)**: first 3 `http://export.arxiv.org` curls returned 0 bytes; switching to `https://` fixed it (http=200).
- **Not found**: a tailoring paper naming **LLaMA-3 / Mixtral / Gemma** as the RAG backbone. `searxng_search` returned 5 rows, all `quality.usable: 0` (Reddit/HN/tooling listicles) — no scholarly hit. Closest model-named work is 2609.16517 (Llama-3.1-8B, screening) and 2609.22188 (Qwen3/Gemini/GPT-4o-mini, generation). Suggest Semantic Scholar / SSRN / IEEE Xplore API query for the journal-only tailoring paper.
- No paper stating a formal **4/5ths-rule adverse-impact ratio**; 2606.28978's callback-gap pp estimates are the closest proxy.
- ResumeFlow and 2602.18550 report no quantitative metric in the abstract (bodies not fetched — paywalled browsing disallowed).
- Venue/peer-review status mixed: several 2026 items are "Under review"/6-page case studies — treat 2605.05257's ±8-point numbers as pilot, n=1 candidate.