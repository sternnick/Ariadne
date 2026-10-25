

# Research: The math an ATS uses to match resume ↔ job description

**TOOL USE: 8 calls** (2 searxng searches, 1 failed `research_fetch`, 4 curl fetches — 2 blocked). No files created, per instructions.

## Findings

- **TF-IDF + cosine similarity is the baseline "vector-space" matcher and is what academic resume-screening systems actually implement**: "Roy et al. used Term Frequency–Inverse Document Frequency (TF-IDF) for feature extraction and cosine similarity for matching candidates with job postings"; "The use of similarity measures, particularly cosine similarity, is prevalent across multiple approaches." (source: https://arxiv.org/html/2503.17438v1 , submitted 21 Mar 2025, ITADATA 2024)
- **Same pipeline stated in an implementation paper**: features are "TF-IDF Vectors | Word2Vec Embeddings | BERT Encoding" and "Cosine similarity is computed between the resume feature vector and the job description vector." (source: https://ijcope.org/wp-content/uploads/2026/05/Automated-Resume-Screening-System-Using-Natural-Language-Processing-and-Machine-Learning.pdf , undated/2026)
- **Why IDF matters (documented rationale)**: TF-IDF is used over raw term counts in content-based job matching "because job descriptions are often verbose" — IDF is what suppresses boilerplate JD terms so rare skill terms dominate the score. (source: https://www.mdpi.com/2078-2489/16/4/333 , 21 Apr 2025 — **snippet only, full-text fetch returned `Access Denied … Reference #18.95b01302`**)
- **Cosine similarity is also the default scoring function in the Sentence-BERT stack**: `score_function` "By default, cosine similarity"; normalised embeddings let you substitute dot-product. (source: https://sbert.net/examples/applications/semantic-search/README.html , accessed 2026-10-25)
- **Documented SBERT limits / latency mitigation**: exact search over "millions of embeddings" is "time-consuming," so ANN indexes (Annoy, FAISS, hnswlib) are required; manual implementation is only advised "up to about 1 million entries"; and for "complex semantic search scenarios, a two-stage retrieve & re-rank pipeline is advisable" (bi-encoder recall → Cross-Encoder rescoring). (source: https://sbert.net/examples/applications/semantic-search/README.html )
- **Sentence-BERT is benchmarked against TF-IDF/Word2Vec as the baseline it must beat for resume ranking.** (source: https://www.researchgate.net/publication/383953314_RESUME_RANKING_FOR_A_JOB_DESCRIPTION_DERIVING_SIMILARITY_OF_REPRESENTATIONAL_EMBEDDING_USING_SENTENCE_BERT , 12 Sep 2024 — snippet only)
- **Hybrid production pipelines stack layers**: "named-entity extraction, skill normalization, TF–IDF/cosine similarity, sentence embeddings, and weighted ranking"; and academic systems combine Sentence-BERT skill vectorisation with K-means grouping (Skill Scanner, Bothmer et al.), or LSA+BERT+SVM, or TF-IDF + competence knowledge-graph (Wang et al.). (source: https://arxiv.org/html/2503.17438v1 ; https://answerthis.io/shared/what-does-recent-research-say-about-job-search-usi )
- **One published numeric threshold found** — but it is a *graph-edge pruning* threshold, not a candidate match rate: sim ∈ [0, 1−θ] with "λ = 2 and θ = 0.2," yielding 9,900,941 edges. (source: https://arxiv.org/html/2503.17438v1 , 21 Mar 2025)

## GAPS

- **AWS Builder Center article: NOT FOUND.** The scoped search returned no aws.amazon.com/buildercenter result — only IJSREM, MDPI, IJERT, a GitHub repo, and answerthis.io. **TOOL FAILED:** `aiproject_research_fetch` rejected `max_chars` (`unexpected_keyword_argument`) — one wasted call.
- **Boolean/keyword search as implemented in ATS products (Taleo/Workday/Greenhouse/Ashby): NO EVIDENCE** — zero vendor/engineering docs surfaced in either search. Needs a vendor-docs lane.
- **Hybrid engineered-feature + gradient-boosting classifier feature list: NO EVIDENCE.** No source in these results enumerated features (e.g. skill-overlap ratio, boolean hits, years-of-experience delta, job-title edit distance) fed to an LGBM/XGBoost head.
- **Published match-rate threshold with a named owner (e.g. a vendor "75% match rate"): NOT FOUND.** https://www.jobscan.co/blog/how-do-ats-systems-work/ returned Cloudflare "Just a moment…" (5 KB). Record as unverified.
- **Typical latency in ms: NOT FOUND** in any fetched source.

## Verification
- Cross-referenced (2+): cosine similarity as the comparison metric (arXiv survey + IJCOPE + sbert.net docs + ACM DL 10.1145/3787330.3787359 snippet).
- NEEDS VERIFICATION (1 source, snippet only): MDPI verbosity/IDF rationale; ResearchGate SBERT-beats-TF-IDF result.
- Source quality: HIGH — arXiv:2503.17438, sbert.net official docs. MEDIUM — IJCOPE/IJESAT/ACM DL. LOW — answerthis.io.