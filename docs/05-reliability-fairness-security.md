```
Last verified: 2026-10-25
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
   assert the ranking does not invert beyond a declared tolerance. That test does not exist yet — it is
   A2's acceptance criterion, and it is the single most important test we will write.

**[OPEN]** A tolerance threshold is a product decision with no source: we cannot cite a number for
"acceptable reversal rate". Probe: publish our measured rate against the 29.6 % baseline and state our
own threshold explicitly as a decision (`DECISIONS.md`), not as a fact.

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
| No person-level inference in the package | **passes** (`tests/test_no_profiling.py`, 7 tests) |
| Every doc citation resolves; no uncited source | **passes** (`scripts/provenance.py`) |
| No stale doc | **passes** (`scripts/fresh.py`) |
| No dead relative link | **passes** on docs 01–05; `docs/08` still a forward reference |
| Score stability under perturbation | **does not exist** — A2 |
| Field-level parse quality | **does not exist** — A1/A2 |

## 5.5 The honest summary

Reliability is *measurable and currently unmeasured*; fairness is *evidenced against us and therefore
must not be claimed*; security is *architecturally addressed at the one boundary we control* (channel
separation) and *unaddressed at the one we do not* (model provider retention).

**[HYPOTHESIS]** The perturbation-stability test will fail for any pipeline whose proposals depend on
document ordering, because our section detector currently drops the second occurrence of a repeated
heading (audit P5) — i.e. the reliability defect may be a *parser* defect, not a scoring defect.
Probe: run the perturbation test against the A1 parser before wiring any scorer to it, so the
attribution is unambiguous.
