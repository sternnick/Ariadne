```
Last verified: 2026-10-25
Reviewed by:   Ariadne (principal)
Live surfaces: vendor pricing and plan tiers (30-day clock — these change without notice)
```

# 07 — Product workflow teardown

Two sources only: one spoken demo transcript (workflow evidence, **no** numbers or names) and the
pricing pages of four commercial products (page bodies where we got them). Everything commercial is
graded as such; nothing here is a claim about ATS internals.

## 7.1 The demo: a workflow, not a benchmark

From the Jobsuit demonstration ([EV-22], **B**; provenance header records that it was never checked
against audio, has no video URL, and that its score numbers are not citable):

1. Open a target job description; **per-section** review of the CV with "best practice" fixes.
2. A **numeric score** that moves as sections are edited (the transcript shows 66 → 69).
3. A **keyword-match** step against that specific JD.
4. **Per-keyword bullet proposals**, each accepted or rejected individually.
5. Three dispositions per requirement: **modification**, **contextual match**, **not applicable**.
6. **Questions to the user** where evidence is missing, instead of invented content.

Why this is the most valuable artefact in the corpus: it is a *shipped interaction model* that
independently converged on the constraints our evidence demands — per-item human control (doc 09 §4),
abstention over invention (doc 04 §4.7), and explicit disposition classes (doc 04 §4.4).

What it does **not** establish: that the score is valid, that the keyword logic matches any ATS, that
66→69 means anything, or that any vendor behaves as described. The transcript is a description of a
UI, and that is the only use permitted by its provenance record.

## 7.2 The commercial field, from page bodies

| Product | What the page **proves** | Grade |
|---|---|---|
| **Rezi** | Free $0 (1 résumé, 3 PDF downloads, Score/Keyword marked *Limited*), Pro **$29/mo**, Lifetime **$149**, Enterprise **$99/mo per 200 users**; products named "Rezi Score", "AI Keyword Targeting", "Real Time Content Analysis" | **A** for the page ([EV-29]) |
| **Rezi** (claims) | "62 % of Rezi users land an interview", "4,510,834 job seekers helped", Trustpilot 4.7/5 (250 reviews) — **self-reported marketing** | **C** |
| **Enhancv** | free tier "€0 Valid for 7 days", **max 12 section items**, Pro includes "ATS check (Applicant Tracking System)", no branding | **A** ([EV-29]) |
| **Enhancv** (trap) | the Pro price is JS-injected: raw HTML literally renders `€ NaN - SAVE NaN%` | **A** — and a warning: scraping it yields a confident `NaN` |
| **Teal** | products proven ("Resume Job Description Match", "ATS Resume Checker", "Resume Keyword Scanner"); prices **snippet-only** ($13/week, $29/30d, $79/90d) | **A** products / **C** prices |
| **Kickresume** | privacy statement "we'll never share your resumes and cover letters with recruiters or job sites"; prices snippet-only (€8/€18/€24 per month variants) | **A** statement / **C** prices |
| **Jobscan** | **nothing** — curl returned 6,653 bytes of "Jobscan", `app.jobscan.co/plan` returned `content_chars: 0`, Camoufox hit "Just a moment…" | **U** |

The Jobscan row matters: a widely cited product in this category published **no** price we could
retrieve at any rung. Any competitor analysis that quotes its price is quoting something we could not
verify.

## 7.3 The disclaimers actually present

Only two disclaimers were captured verbatim, and both matter more than any marketing number:

* **Resume-Scanner** (open source): the ATS score is *"an analytical estimate"*, not a guarantee
  ([EV-28], **A**).
* **Kickresume**: resumes are *"never share[d] … with recruiters or job sites"* ([EV-29], **A**).

Not captured, and therefore not quotable: Rezi's or Teal's language about whether their score reflects
an official ATS. The audit's earlier claim that Rezi says "this is not an official ATS score" is
**retracted** — the pricing page does not contain it (audit B.2).

## 7.4 What the market converges on

| Pattern | Evidence | Adopt? |
|---|---|---|
| Free tier limited by **artefact count** (1 résumé / 3 downloads) | Rezi (**A**) | No — our baseline is local and unlimited; a count limit would be artificial |
| Paid unlock = **unlimited + score/keyword features** | Rezi, Enhancv (**A**) | Not now; pricing is a `D-008`-class business decision |
| **ATS check** as a named feature, with no definition | Enhancv, Teal (**A**) | **No** — we must define any check we ship (C7.5) |
| Privacy as a headline claim ("never shared") | Kickresume (**A**) | Yes, but only as a verifiable property (local-first, `D-016`), not a promise |
| Per-item accept/reject + three dispositions | Jobsuit (**B**) | Yes — the core interaction |

## 7.5 What none of them do (in the evidence we hold)

* None publishes **what its score means** (formula, inputs, error) — Enhancv and Teal name a check,
  not a definition. **A** (by absence across page bodies we read).
* None publishes a **reversal/stability** number. Given [EV-02]'s 29.6 %, an unstated stability claim
  is the category's biggest unexamined assumption.
* None states which **ATS vendor** its advice is tuned for.

That trio is our differentiation *if we can execute it honestly*: a defined score, a published
stability number, and no vendor-compatibility claim we cannot support (`docs/01` §1.5).

## 7.6 Consequences for Ariadne

1. **Ship the interaction, not the score.** The per-item proposal with three dispositions is proven
   behaviour and legally coherent (real human oversight, doc 09 §4).
2. **Define any metric, or do not show it.** "ATS check" without a definition is the pattern to
   refuse (C7.5, C8).
3. **Price is not a product decision yet.** The evidence gives competitor price points and nothing
   about willingness to pay. **`[OPEN]`**.
4. **Never quote Jobscan.** We could not retrieve its pricing at any rung; `U` is the record.

**[OPEN]** No source establishes **willingness to pay** in this category, nor churn, nor whether users
prefer a subscription to a one-off purchase. The pricing evidence is a menu of competitors' numbers,
not a demand signal. Probe: none available without primary research; do not infer from competitor
pricing in the meantime.

**[HYPOTHESIS]** A product that shows *what changed and why* (the provenance view) will retain users
better than one that shows only a rising score, because the score is unverifiable by the user while a
diff is inspectable. Probe (A3): instrument whether users open the evidence view, and whether opening
it correlates with completing a revision.
