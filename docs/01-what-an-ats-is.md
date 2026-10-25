```
Last verified: 2026-10-25
Reviewed by:   Ariadne (principal)
Live surfaces: vendor market-share figures, adoption statistics
```

# 01 — What an ATS is, and what it is not

Scope: what the software *is*, at the level of entities and modules. Parsing is `02`, scoring is
`03`. Every claim carries a source id from `docs/SOURCES.md` and a grade.

## 1.1 Definition

> "An applicant tracking system (ATS) is a software application that enables the electronic handling
> of recruitment and hiring processes." — **A**, [EV-17] (Wikipedia, rev. 2026-10-16)

That definition is thin, and the useful one is structural: an ATS is the **system of record for a
requisition-and-candidate pipeline** — a domain-specific CRM whose entities are requisition, job,
candidate, application, pipeline stage and activity, and whose workflow is hiring rather than
selling. **A**, [EV-25].

Design consequence for us: everything Ariadne produces is an *input to someone else's system of
record*. We are not a system of record, and a document that has to be re-keyed into one is a worse
product than a document that arrives parseable.

## 1.2 The module set is near-canonical

Nine modules appear in the standard description: sourcing, job posting/distribution, résumé parsing,
database search and filtering, candidate ranking/rating, applicant management and tracking, interview
scheduling, automated communication, and reporting/analytics. **A**, [EV-25] → [EV-17].

Two of those nine matter to a candidate-side tool: **parsing** (what survives ingestion) and **search
and filtering** (how a recruiter's query reaches the record). Ranking matters only where a vendor
ships it, and we have no verified knowledge of any vendor's ranking implementation — see §1.5.

## 1.3 Who is actually in the path

| Claim | Grade | Source |
|---|---|---|
| Software touches nearly every application before a human: parse → dedupe → structured-field/keyword filter → optional rank | **B** (two secondaries) | [EV-25] |
| ~98 % of Fortune 500 run every résumé through an ATS before a human sees it | **C** (single secondary, marketing-adjacent) | [EV-25] |
| 97.4 % of Fortune 500 have a *detectable* ATS; Workday on >40 % of them | **B⁻** — vendor telemetry from a company selling a competing product | [EV-18] |
| Outside the F500: 23 distinct systems across 600+ teams, none >16.5 % of connections, HHI ≈1,000 | **C** (same single vendor dataset) | [EV-18] |
| Retained search firms largely do not use an ATS; SME adoption cited at 17 % | **C** | [EV-25] |

The contradiction between "Workday >40 % of the F500" and "no platform above 16.5 %" is **not** a
contradiction: different populations (F500 vs an agency-heavy connected-ATS sample). Both are recorded
because a reader will meet both.

## 1.4 Claims that are widely repeated and are *not* supported

* **"ATSs auto-reject 75 % of résumés."** No empirical backing found; the ATS filters and surfaces,
  and a human makes the reject decision in most configurations. **B**, [EV-25].
* **"~95 % parse accuracy."** Universal vendor marketing; no public leaderboard or benchmark was
  found. That is a **negative** result from our own search, graded **U** for "is there a benchmark?"
  and **C** for the vendor claims. [EV-23], [EV-06].
* **A market size.** Two sources disagree 6.9× ($17.22 B vs $2.5 B) depending on whether bundled HCM
  recruiting modules are counted. **B as a conflict.** We do not quote a market size at all. [EV-18].

**Why this section exists**: every one of these three is a sentence a product would like to put on a
landing page. Under `AGENT_CONTRACT` C8 they are banned, and this is the evidence for the ban.

## 1.5 What we do *not* know about any ATS

| Unknown | Status | Why it matters |
|---|---|---|
| Which parser vendor each ATS uses (Textkernel / Daxtra / Sovren / Radancy …) | **U** — 0 of 8 targets answered; the vendor query returned zero results | decides whether a failure is the *engine* or the *integration* |
| Accepted file formats and size limits per vendor | **U** for 7 of 8; only a *sandbox* Lever mirror lists `docx; doc; js; jpg; png; pdf; txt` | decides our export formats and lint rules |
| Whether a parse failure falls back to manual re-entry | **U** — no official source | decides whether a bad parse is *fatal* or merely *annoying* |
| Boolean/keyword search implementation | **U** | decides whether keyword placement matters at all |
| Any published match-rate threshold with a named owner | **U** | every "match score" we ship is our own construct, not a reproduction |

The fetch failures are recorded, not glossed: `support.greenhouse.io` **404**,
`help.lever.co` **401**, `help.smartrecruiters.com` Cloudflare JS shell, `help.ashbyhq.com`
connection failure, `help.teamtailor.com` **404**. **A** (as a record of failure), [EV-26].

**[OPEN]** The one official-grade artefact we hold is a *sandbox* subdomain
(`hire.sandbox.lever.co/developer/documentation`), which may be a mirror rather than Lever's
production documentation. Probe: read `developers.lever.co` and Lever's production help centre through
the browser rung, then re-grade the row.

## 1.6 The interaction model a competitor actually ships

From the Jobsuit demo transcript (workflow evidence only — **not** its numbers, names or claims):

1. per-section review with "best practice" fixes;
2. a numeric score that moves as sections are fixed;
3. a keyword-match step against a specific job description;
4. **per-keyword bullet proposals, each accepted or rejected individually**;
5. three dispositions per requirement — *modification*, *contextual match*, *not applicable*;
6. questions asked of the user instead of invented content.

**B**, [EV-22] (transcript; provenance header records that it was never checked against audio).

This is the most useful single artefact in the whole corpus for product design, and its authority is
narrow on purpose: it tells us what a shipped product *does*, never what an ATS *is*.

## 1.7 Consequences for Ariadne

| Consequence | Evidence |
|---|---|
| We cannot claim to "pass", "beat" or "optimise for" any ATS: we do not know any vendor's rules (1.5) | [EV-26] |
| Parsing robustness is the primary product surface, because parsing is the one module that touches every application (1.3) | [EV-25] |
| Our output must be *re-parseable*, not merely pretty — the document re-enters a system we do not control (1.1) | [EV-17] |
| Per-item accept/reject with reasons is the interaction to copy, because a shipped product converged on it and it is also the human-oversight story in `docs/09` §4 | [EV-22] |
| Any "match score" is ours, must be defined, and must carry uncertainty | [EV-02] |

**[HYPOTHESIS]** A candidate-side tool that produces a *parseable* document and an honest explanation
will outperform one that produces a high score against an imaginary ATS, because the score cannot be
verified by the user while the parse can. Probe (A2): render the same CV two ways, parse both with our
own parser, and measure field-recovery difference; then test whether users prefer the higher-scoring
or the better-parsing artefact.

**[OPEN]** No measurement exists of *time-to-first-human-view* or of how often a recruiter reads the
parsed record rather than the PDF. Every adoption figure in 1.3 is a proxy. Probe: vendor
documentation on "candidate profile view" (not attempted — the same walls as 1.5).
