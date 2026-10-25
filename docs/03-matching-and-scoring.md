```
Last verified: 2026-10-25
Reviewed by:   Ariadne (principal)
Live surfaces: none (methods and papers)
```

# 03 — Matching and scoring

What is actually computed when a product says "match", what the literature validates, and where our
own score stops being defensible.

## 3.1 The implemented baseline is lexical, not semantic

| Claim | Grade | Source |
|---|---|---|
| TF-IDF for feature extraction + **cosine similarity** for candidate↔posting matching is what academic systems implement ("Roy et al. used …"; "cosine similarity … is prevalent across multiple approaches") | **A** | [EV-07] (arXiv 2503.17438, ITADATA 2024) |
| An implementation paper names the same stack: TF-IDF vectors, Word2Vec, BERT encodings, cosine between résumé and JD vectors | **A** | [EV-27] |
| IDF is used over raw counts specifically *because job descriptions are verbose* — it suppresses boilerplate so rare skill terms dominate | **C** (snippet only; full text returned `Access Denied`) | [EV-27] |
| Cosine is the default `score_function` in the Sentence-BERT stack | **A** | [EV-15] |
| Production pipelines stack layers: NER → skill normalisation → TF-IDF/cosine → sentence embeddings → weighted ranking | **A** | [EV-07] |

So the honest description of "AI matching" in most systems is: **term statistics, plus optionally an
embedding layer, plus weights**. Not a judgement about a person.

## 3.2 What embeddings add, and what they cost

* Exact search over "millions of embeddings" is "time-consuming", so ANN indexes (Annoy, FAISS,
  hnswlib) are required; manual implementation is advised only "up to about 1 million entries"; for
  complex search a **two-stage retrieve → cross-encoder re-rank** pipeline is advisable. **A**, [EV-15].
* Sentence-BERT is benchmarked *against* TF-IDF/Word2Vec as the baseline it must beat. **C** (snippet),
  [EV-27].

Consequence: a small tool does not need an ANN index, and adding one is a cost with no benefit until
the corpus is large. **We do not ship one** (`D-016`).

## 3.3 The one published threshold we found is not a match threshold

`sim ∈ [0, 1−θ]` with `λ = 2`, `θ = 0.2`, producing 9,900,941 edges — a **graph-edge pruning**
parameter, not a candidate cut-off. **A**, [EV-07].

Recording this matters because it is exactly the kind of number that gets quoted as "the industry
threshold". It is not.

## 3.4 Numbers that changed how we think about the score

| Finding | Number | Grade | Source |
|---|---|---|---|
| Matched-pair **reversals** under competence-preserving perturbation (best model) | validity 0.781, **29.6 % reversals** | **A** | [EV-02] |
| LLMs fail to pick the objectively better résumé, and do not abstain on ties | — | **A** | [EV-03] |
| Screening-as-classification: **friction = excess false negatives**; keyword logic has high friction, semantic matching cuts FN **without losing precision** | — | **A** | [EV-04] |
| Vault-based tailoring helps in-domain, hurts out-of-domain | **+7.8 pts** (6 same-category JDs) vs **−8.0 pts** (2 out-of-domain) | **A (pilot, n=1)** | [EV-01] |
| Retrieval / matching gain over BM25 | **+13.8 % recall, +17.5 % nDCG** | **A** | [EV-27] → arXiv 2502.12361 |

**The 29.6 % reversal number is the most important figure in this document.** It means a single point
estimate of "your match is 72" is making a claim of precision the underlying systems demonstrably do
not have. Therefore:

* a score ships as a **band** (interval), never a bare number;
* the band is derived from measurement (perturbation stability), not from a vibe;
* the explanation (which terms contributed) is the primary output, the number secondary.

**C9 interaction:** fit-to-JD scoring is a *document* measurement under our construction, not a
profile of a person — see `tests/test_no_profiling.py` for the reasoning and `docs/09` §1.2. If a
future feature scores the *candidate* rather than the document, C9 rejects it.

## 3.5 What we compute today, exactly

`ariadne_ats.lexical.Tfidf`:

1. tokenise → drop stopwords (caller-supplied) and single characters;
2. sublinear TF: `w = 1 + ln(tf)`;
3. IDF over a supplied background corpus: `ln((1+N)/(1+df)) + 1`;
4. L2-normalise; cosine = dot product;
5. `compare()` returns the cosine **plus** `shared_terms`, per-term `contributions`,
   `missing_from_a` (terms in the JD absent from the CV, ranked by IDF×weight).

Limitations, measured:
* **No background corpus is shipped** → in the two-document case IDF is close to meaningless
  (audit P7: unseen `kubernetes` at 2.099 vs seen `fox` at 1.405 on a 2-doc corpus).
* **Single-character tokens are dropped** → the skill "C" is invisible (audit P2).
* **ASCII-only tokenisation** → accented text is shredded (audit P1).
* No stemming, no synonyms, no skill normalisation, no embeddings.

So today's output is a *lexical overlap explanation*, and calling it a "match score" would overstate
it by at least two layers.

## 3.6 Design rules that follow

| Rule | Why |
|---|---|
| The number is a band; the explanation is the product | [EV-02] 29.6 % reversals |
| Report **false negatives** (requirements present but unmatched), not only a similarity | [EV-04] friction is the harm |
| Retrieval must be able to say "no" — out-of-domain retrieval *hurts* (−8.0 pts) | [EV-01] |
| Never compare scores across job descriptions | IDF depends on the corpus; the scale is not absolute |
| A corpus is a **licensing** decision, not just a data one | [EV-31] later; no asset licence proven |

**[HYPOTHESIS]** For a single CV and a single JD, a *curated skill lexicon* (exact term + alias
matching) will beat TF-IDF cosine on false negatives, because the failure that matters is a synonym
("k8s" vs "Kubernetes"), which term statistics cannot bridge and a lexicon can. Probe (A2): hand-label
40 requirement/evidence pairs; compare FN rate of TF-IDF vs lexicon vs both.

**[OPEN]** No source we retrieved states the **latency budget** a recruiter-facing ATS applies, nor
the corpus size at which IDF weights stabilise for this domain. Probe: measure IDF variance across
corpora of 50/500/5,000 synthetic JDs.
