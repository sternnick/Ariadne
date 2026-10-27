```
Last verified: 2026-10-27
Reviewed by:   Ariadne (principal)
Live surfaces: none
```

# 05 — Reliability, fairness, security

Three properties that are usually written as adjectives and must instead be written as **tests,
numbers, or they do not exist**.

## 5.1 Reliability: what "the score is stable" would have to mean

| Finding | Number | Grade | Source |
|---|---|---|---|
| Matched-pair reversal rate under competence-preserving perturbation (best of 6 open instruction-tuned models) | validity **0.781**, **29.6 % reversals** | **A** | [EV-02] |
| LLMs fail to identify the more qualified résumé; no abstention on ties | — | **A** | [EV-03] |
| 2023-vintage model reproduces a pro-White callback gap; 2024+ models null-to-reversed | **+2.12 pp** (p<0.01) vs up to **−3.01 pp** | **A** | [EV-11] |
| Semantic matching reduces false-negative rejections **without** losing precision relative to keyword logic | — | **A** | [EV-04] |

**29.6 %** is the reliability number that governs our product decisions. A tool that reports a point
estimate is claiming a precision the class of systems demonstrably lacks under *presentation-only*
changes — same candidate, same content, reordered. Two consequences, both already binding:

1. **Scores ship as bands** (doc 03 §3.4).
2. **Perturbation is a test, not an audit ritual.** A release test must take a fixture, apply
   competence-preserving perturbations (reorder sections, rephrase bullets, change template), and
   assert the ranking does not invert beyond a declared tolerance. **Written 2026-10-27**: the
   substrate below; the acceptance criterion for an A2 score is the same test run against that score,
   which does not exist yet and is the honest half of what remains.

### Our own number, measured 2026-10-27

The test the paragraph above asked for now exists (`src/ariadne_ats/bench.py::stability`, gated by
`scripts/bench.py --check`, artefact `data/gold/results.json`). Each of the 26 gold documents is
rebuilt through four competence-preserving transforms and compared against itself, and three separate
things are reported instead of one blended score:

| Transform | fixtures changed | facts preserved | fact retention | max cosine move | ranking inversions |
|---|---|---|---|---|---|
| reorder sections | 21 | yes | 1.000 | 0.0000 | 0.0 % |
| rename headings | 16 | yes | 1.000 | 0.0983 | 6.7 % |
| change bullet markers | 22 | yes | 1.000 | 0.0000 | 0.0 % |
| inject ligature / soft hyphen | 11 | yes | 1.000 | 0.0000 | 0.0 % |

The middle column is the honest one and the one a reader will otherwise ignore: it is how many of the
26 documents the transform actually **changed**, and a transform that finds nothing to do measures
nothing. `add_typographic_damage` needs five bullets or three commas to have a target, so it fired on
11; `rename_headings` knows two English headings, so it fired on 16 (which is the same vocabulary limit
as M-9, on the fixture side). Where a transform applied, retention was 1.000; the claim is "every
change we actually made preserved every fact", not "every document was perturbed four ways".)

Read the columns before comparing them to 29.6 %, because the easy reading is wrong:

* **The ledger is presentation-proof on this corpus.** Every fact survived every transform, and every
  transform that claimed to preserve competence did (`competence_hash` identical). That is the design
  claim of the two-hash model, and it held.
* **Cosine over a bag of terms is permutation-invariant by construction.** Reordering sections cannot
  move it, so the 0.0 % on row 1 is a property of the arithmetic, not evidence of robustness. Anyone
  quoting that row as "stable under reordering" is quoting the wrong thing: it says our comparison
  layer cannot *see* order.
* **What does move the number is vocabulary.** Renaming `EXPERIENCE` to `WORK HISTORY` moves the
  cosine against a fixed advertisement by up to 0.098 and inverts the order of 6.7 % of fixture pairs,
  with zero change in content. That is the same disease as [EV-02]'s 29.6 %, in our own tool, at about
  a quarter of the published rate - and the mechanism is now identified: heading words are themselves
  terms in the vector.
* The ranking figure is the only one comparable to 29.6 %, and it is not the same experiment: [EV-02]
  reverses *candidate pairs on competence-preserving edits*; we invert *fixture order against one
  advertisement*. Say which one is meant.

**Decision (D-038), not a fact:** the declared tolerance is 0.02 for cosine-preserving transforms and
0.09 for heading-rename inversions, recorded as a ratchet in `data/gold/thresholds.json`. The first
number is arithmetic; the second is a ceiling we accepted because we can name its mechanism and have
not yet paid to remove it. `[OPEN]` whether stripping heading terms from the comparison removes the
vocabulary sensitivity without losing term evidence - that is an A2 experiment, and the measurement
above is what makes it worth running.

## 5.2 Fairness: the claims we are allowed to make

| Claim | Status |
|---|---|
| "Bias-free" / "non-discriminatory" / "fairness-audited" | **banned** (`AGENT_CONTRACT` C8, `docs/09` §8) — we have run no validity or fairness test |
| Anonymisation removes demographic signal | **false**: 4,100 variants, 18 LLMs recover demographics at high F1 ([EV-08], **A**) |
| Generated CVs are demographically neutral | **false**: German LLM CVs leak gender/ethnicity under name variation ([EV-12], **A**) |
| Aggregate metrics detect discrimination | **insufficient**: path-specific decomposition exposes 5 patterns invisible to aggregates ([EV-14], **A**) |
| Using the same model as the screener is neutral | **false**: **23–60 %** shortlisting advantage ([EV-10], **A**) |

The distinction that matters legally and ethically: the evidence above is about **screening systems
that decide about people**. Ariadne does not decide; it edits a document for its author (doc 09 §1.2).
That is a *scope* argument, not an absolution — which is why C9 forbids person-attribute inference
outright rather than promising fair inference.

**What we will do instead of claiming fairness:** publish, per release, (a) the perturbation stability
number from 5.1, (b) the abstention rate from doc 04 §4.7, and (c) a statement that no demographic
attribute is an input to any computation, enforced by `tests/test_no_profiling.py`. Those are
falsifiable; "fair" is not.

## 5.3 Security: the attack surface of a document tool

| Threat | Evidence | Mitigation (design) |
|---|---|---|
| **Indirect prompt injection** via document text | [EV-09] ResumeShield, channel separation; benchmarked class | document text is data; instructions never come from it (doc 04 §4.3) |
| Real-world injection prevalence | [EV-30] → arXiv 2605.28999 (benchmark) | log instruction-like patterns as findings |
| Exfiltration through generated output | [HYPOTHESIS] — no source; plausible: a model asked to "improve" a CV could echo unrelated context | provenance checker: every span must map to a fact in the user's document |
| Supply chain | `D-016`: zero runtime dependencies | nothing to compromise at install time |
| Personal data in logs/prompts | [EV-03]/GDPR Art. 5(1)(c) | minimise; no CV content in logs (`docs/09` §3) |
| Model-side retention | not covered by any source we hold | **U** — see `docs/08` |

**A note on what "secure" cannot mean here.** A tool that sends a CV to a third-party model inherits
that provider's retention and training terms, which we have not read for any provider. Until we do,
the only defensible statement is the local-first one: the baseline computes without any network call
(`D-016`), and any remote call is an explicit, documented opt-in.

## 5.4 Operational reliability we can actually test today

| Test | Status |
|---|---|
| `normalize()` is idempotent | **passes** (audit P6) |
| Import of the package is clean; no phantom API | **passes** (audit P8, D-004) |
| No person-level inference in the package | **passes**, two ways: the static scan and the behavioural verbatim/kind check over every gold fixture (`tests/test_no_profiling.py`; see its "what this file cannot prove" section for the limits) |
| Field extraction is verbatim, never inferred | **passes** - every emitted fact value is a substring of its own document, over all 26 fixtures |
| Every doc citation resolves; no uncited source | **passes** (`scripts/provenance.py`) |
| No stale doc | **passes** (`scripts/fresh.py`) |
| No dead relative link | **passes** on docs 01–05; `docs/08` still a forward reference |
| Score stability under perturbation | **measured 2026-10-27**: facts preserved 1.000, ranking inverted 0-6.7 % depending on transform (5.1); the *score* half still waits on A2, because there is no score |
| Field-level parse quality | **measured 2026-10-27**: `data/gold/results.json`, published in 02 2.7, gated by `scripts/bench.py --check` |
| Forbidden emissions (a value present that should never be) | **0**, over 26 labelled documents, and the build stops on the first one |

## 5.5 The honest summary

Reliability is *measurable and now measured at the extraction layer* (02 2.7, and 5.1 for what a
presentation change does to a fact set and to a similarity number); it is still unmeasured wherever
there is no number yet, which is anywhere a score would sit. Fairness is *evidenced against us and therefore
must not be claimed*; security is *architecturally addressed at the one boundary we control* (channel
separation) and *unaddressed at the one we do not* (model provider retention).

**[HYPOTHESIS]** The perturbation-stability test will fail for any pipeline whose proposals depend on
document ordering, because our section detector currently drops the second occurrence of a repeated
heading (audit P5) — i.e. the reliability defect may be a *parser* defect, not a scoring defect.
Probe: run the perturbation test against the A1 parser before wiring any scorer to it, so the
attribution is unambiguous.

## What would make this strong

| Gap | Probe that closes it (exact) |
|---|---|
| No stability number of our own (§5.1, M-2) | the stability test (not yet written): five fixtures × three competence-preserving perturbations (reorder sections, rephrase bullets without changing claims, swap template); assert ranking/score delta within a declared tolerance. **This is A2's acceptance criterion**, not A1's — A1 builds the substrate. |
| Fairness is an absence of claims, not a measurement (§5.2) | A perturbation audit of *our own* output: take 40 synthetic CVs differing only in name signal (a published name list is enough for the *test*, not for a product claim), run the pipeline, and publish the delta. If we cannot run it without ingesting demographic signal, that itself is the finding — and C9 says we do not build that capability. |
| No field-level parse quality (§5.4) | 20 synthetic résumés hand-annotated for employer/title/dates/skills; score exact-match and F1 per field. Publish the confusion per field, not one aggregate. |
| Provider retention/training terms are unread (X-1) | Read the data-processing terms of the one provider we would use, quote the retention sentence, and record the date. Until then the baseline stays local-only (`D-016`). |
| Prompt-injection prevalence unknown (§5.3) | Run the public ResumeShield / LongPIBench prompt sets through the A1 parser, count how many survive normalisation unchanged, and store them as a regression corpus. |

