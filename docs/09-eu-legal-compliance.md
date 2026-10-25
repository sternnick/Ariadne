```
Last verified: 2026-10-25
Reviewed by:   Ariadne (principal) — primary text read, not summarised from secondary sources
Jurisdiction:  EUROPEAN UNION ONLY. Non-EU instruments are neither analysed nor cited here.
Retrieval note: eur-lex.europa.eu/legal-content/EN/TXT/HTML returned HTTP 202 with a zero-byte
body for every CELEX request (edge bot-handling). All instrument text below was therefore read
from the Publications Office repository (publications.europa.eu/resource/celex/…) at HTTP 200,
which serves the same Official Journal XML. That is an official source; it is not a blog.
```

# 09 — EU legal & standards compliance

**Scope statement.** This document is an **EU plan that is extensible by construction**, not a
global legal plan. Section 2 uses a fixed column schema; §9 lists the triggers that would bring a
new jurisdiction into scope; §10 records only cross-regime conflicts we can actually evidence.
Adding a jurisdiction later means **filling rows**, never rewriting this file.

Grade legend (this document): **A** = primary instrument text read · **B** = official secondary
guidance read, or structural inference from primary text · **C** = snippet only · **U** = attempted,
unreachable (a recorded result, not a conclusion).

---

## 1. Scope and role determination

### 1.1 Ariadne is a **provider**, not a deployer

> **Art. 3(3)**: "'*provider*' means a natural or legal person, public authority, agency or other
> body that develops an AI system or a general-purpose AI model or that has an AI system or a
> general-purpose AI model developed and places it on the market or puts the AI system into service
> under its own name or trademark, whether for payment or free of charge" — **A**
> (Reg. (EU) 2024/1689, Art. 3(3), Cellar `celex/32024R1689`)

> **Art. 3(4)**: "'*deployer*' means a natural or legal person … using an AI system **under its
> authority except where the AI system is used in the course of a personal non-professional
> activity**" — **A**, Art. 3(4)

Consequences, stated as the text gives them:
* We place a system on the market under our own name → **provider duties attach to us**, whoever
  buys it. (Art. 3(3), Art. 16.)
* A job seeker using Ariadne for their own application is plausibly **outside the deployer
  definition entirely** ("personal non-professional activity", Art. 3(4)). That is a *scope*
  observation, not a licence: it moves duties onto us as provider, it does not create a duty-free
  zone. **Grade B** (the phrase is read; its application to a self-serving candidate is inference).
* The employer who screens with an ATS **is** a deployer, and Arts. 26/49/50(4) obligations are
  **theirs**. Do not conflate them with ours — see §8.

### 1.2 Is Ariadne high-risk under Annex III(4)? — both branches

> **Annex III, point 4(a)**: "AI systems **intended to be used for the recruitment or selection of
> natural persons**, in particular to place targeted job advertisements, **to analyse and filter
> job applications, and to evaluate candidates**" — **A** (Annex III(4)(a))
> **Art. 6(2)**: "In addition to the high-risk AI systems referred to in paragraph 1, AI systems
> referred to in Annex III shall be considered to be high-risk." — **A**

Classification attaches to the **system and its intended purpose**, and intended purpose is defined
by *our own words*:

> **Art. 3(12)**: "'*intended purpose*' means the use for which an AI system is intended by the
> provider, including the specific context and conditions of use, **as specified in the information
> supplied by the provider in the instructions for use, promotional or sales materials and
> statements**, as well as in the technical documentation" — **A**

**Therefore our marketing copy is a classification instrument.** "Analyse and filter applications"
in a landing page is an act of legal self-classification.

**Branch A — not high-risk (the position we hold today, and must keep true).** Ariadne's stated
purpose is to help a candidate draft and tailor *their own* document. It does not place targeted
job advertisements, does not filter applications for a selecting party, and does not evaluate
candidates *for selection*. Recital 58's own example of the Art. 6(3) derogation is close to our
mechanics: an AI system "intended to **improve the language used in previously drafted documents**"
— **A** for the recital text (recitals interpret, they do not oblige).

**Branch B — high-risk.** Triggers, each reachable by a product decision we could make by accident:
(i) we ship candidate *ranking/scoring* for a selecting party; (ii) we market the tool as doing the
analysing/filtering; (iii) **the system performs profiling.** On (iii) the text is unforgiving:

> **Art. 6(3)**: derogation available where the Annex III system does not pose significant risk and
> meets one of: (a) narrow procedural task; (b) **improves the result of a previously completed
> human activity**; (c) detects decision-making patterns without replacing the human assessment;
> (d) preparatory task. "**Notwithstanding the first subparagraph, an AI system referred to in
> Annex III shall always be considered to be high-risk where the AI system performs profiling of
> natural persons.**" — **A** (Art. 6(3)), with 'profiling' by reference to GDPR Art. 4(4) (Art. 3(52)).

**Design consequence, and it is the single most load-bearing one in this document:** a pipeline that
infers candidate *characteristics* (traits, potential, "read between the lines of this career") is
profiling, and profiling forecloses the Art. 6(3) route. Our evidence-constrained architecture
(generate only from user-stated facts, abstain otherwise) is therefore not only an anti-hallucination
measure — it is the thing that keeps us out of the high-risk regime. This must stay true in code,
be asserted in the instructions for use, and be testable.

**Obligation that follows even in Branch A**: **Art. 6(4)** — a provider concluding "not high-risk"
must **document that assessment before placing on the market** and, per **Art. 49(2)**, register the
system in the EU database. — **A**

### 1.3 Dates — read from the amending instrument, not from the "2027 delay" narrative

The amending instrument exists and is in the Official Journal: **Regulation (EU) 2026/1744**
("Digital Omnibus on AI"), Cellar `celex/32026R1744`, done at Brussels **12 October 2026**. Its
point (40) replaces Art. 113(3)(a) and (c) and adds (d) — **A**:

| Provision | As amended by Reg. 2026/1744 |
|---|---|
| Chapters I–II (definitions, prohibited practices) | from **2 Feb 2025**, except Art. 5(1) points (ba),(bb) and Art. 5(1a),(1b) from **2 Dec 2026** |
| Chapter III Sections 1, 2, 3 — for systems high-risk under **Art. 6(2)/Annex III** | from **2 December 2027** |
| Chapter III Sections 1, 2, 3 — for systems high-risk under **Art. 6(1)/Annex I** | from **2 August 2028** |
| Chapter III **Section 4**, Chapters V, VII, XII, Art. 78 | from **2 Aug 2025** (Art. 113(b), **unamended**) |
| Arts. 102–110 | from **27 July 2026** |
| Rest of the Act (incl. **Chapter IV, Art. 50**) | from **2 August 2026** (Art. 113 second paragraph, unamended) |
| Generative systems already on the market before 2 Aug 2026 | must meet **Art. 50(2) by 2 Dec 2026** (amended Art. 111(4)) |

What the omnibus did **not** do: Annex III point 4 is **not amended**; its new Art. 6(1a)–(1c) insert
concerns product safety components (Art. 6(1)/Annex I route); its new prohibitions (Art. 5(1)(ba),
(bb)) concern intimate-imagery/CSAM generation, not employment. **A**. Practical reading:
**for a candidate-side tool, the substantive high-risk obligations are a 2 Dec 2027 event, but the
transparency obligations of Art. 50 are already live for anything we place on the market today.**

---

## 2. Obligation matrix (EU rows only)

| jurisdiction | instrument | role | classification | obligation | applies_from | grade | status | evidence |
|---|---|---|---|---|---|---|---|---|
| EU | Reg. 2024/1689 Art. 3(3), 16 | provider | n/a | provider duties attach to whoever places the system on the market under its name | 2 Aug 2026 (Sec. 2 → 2 Dec 2027 for Annex III) | A | applies now (role determination) | Cellar 32024R1689, Art. 3(3), 16 |
| EU | Art. 50(1) | provider | non-high-risk | inform natural persons they are interacting with an AI system, unless obvious to a reasonably well-informed person | 2 Aug 2026 | A | **applies now** | Art. 50(1); 113 2nd para |
| EU | Art. 50(2) | provider | non-high-risk | mark synthetic **text** output machine-readable / detectable as AI-generated, "as far as technically feasible" given state of the art | 2 Aug 2026 (or 2 Dec 2026 if already on market pre-2 Aug 2026) | A | **applies now** | Art. 50(2); omnibus Art. 111(4) |
| EU | Art. 50(4) 2nd sub-para | deployer | n/a | disclose AI-generated text **published to inform the public on matters of public interest** | 2 Aug 2026 | A | does not apply to our users' CVs (a CV is not public-interest journalism) — and is not our duty in any case | Art. 50(4) |
| EU | Art. 6(4) | provider | claimed non-high-risk | document the non-high-risk assessment **before** placing on market | 2 Aug 2025 (if Sec. 4) / 2 Dec 2027 (if Sec. 2) — **see §7 OJ-1** | A (duty) / B (date) | applies; date unresolved → treat as in force | Art. 6(4), 49(2), 113(b) |
| EU | Art. 49(2) | provider | claimed non-high-risk | register the system in the EU database | same ambiguity as above | A / B | applies if we rely on Art. 6(3) | Art. 49(2) |
| EU | Art. 6(3) final sub-para | provider | classification rule | if the system performs **profiling**, it is *always* high-risk | 2 Dec 2027 (Annex III route) | A | does not apply **only if** we keep the no-inference design constraint | Art. 6(3), 3(52) |
| EU | Chapter III Sections 1–3 (Arts. 9–15, 16–27: risk mgmt, data governance, technical documentation, logging, instructions, human oversight, accuracy/robustness) | provider | high-risk (Branch B) | full conformity stack + CE marking (Art. 48) + declaration of conformity | **2 Dec 2027** | A | **does not apply in Branch A**; conditional on Branch B | Art. 113(c)(i) as amended by 2026/1744 |
| EU | Art. 43(2) | provider | high-risk (Annex III pts 2–8) | conformity assessment by **internal control, Annex VI — no notified body** (Annex VII only where no harmonised standard/common specification is applied, Art. 43(1)) | 2 Dec 2027 | A | route for Branch B if it ever triggers | Art. 43(1)–(2) |
| EU | Art. 26 | deployer (employer, recruiter, or a professional user) | high-risk | use per instructions, assign competent human oversight, ensure input-data relevance, monitor, keep logs, **inform workers' representatives before workplace use** (26(7)), inform affected persons (26(11)) | 2 Dec 2027 | A | does not apply to Ariadne as provider; **applies to a professional user** — do not absorb it as ours | Art. 26(1)–(11) |
| EU | Art. 5(1)(g) | anyone | prohibited | inferring emotions of a natural person **in the workplace/education** (except medical/safety) | 2 Feb 2025 | A | does not apply — and is a hard "never build" | Art. 5(1) |
| EU | Reg. 2016/679 Art. 5, 6, 13, 14, 15, 17, 25, 32 | controller | n/a | see §3 | applies now | A | applies now | Cellar 32016R0679 |
| Reg. 2016/679 | Art. 22 | controller (usually the employer/ATS; ours only for our own decisions) | n/a | no decision based **solely** on automated processing producing legal/significant effects | applies now | A | applies now; our own flows are editing assistance, not decisions → see §3/§4 | Art. 22(1)–(4) |
| EU | Dir. (EU) 2024/2831 (PWD) | not a digital labour platform | out of scope | algorithmic-management duties attach to **platform work** and to providers meeting the cumulative Art. 2(1) service definition | — | A | **does not apply**: Ariadne is not a digital labour platform and our users do not perform platform work *through* Ariadne; PWD's purpose is expressly "improve working conditions … **in platform work**" (Art. 1(1)) | Cellar 32024L2831, Art. 1(1), 2(1) |
| EU | Dir. 2000/78/EC Art. 3(1)(a) | employer's law, reaches our output indirectly | n/a | no direct/indirect discrimination on religion/belief, disability, age, sexual orientation in "conditions for access to employment … **including selection criteria and recruitment conditions**" | in force | B (archived copy) | applies to the selecting employer; our exposure is contributory, not primary | Wayback copy of EUR-Lex CELEX 32000L0078 |
| EU | Dir. 2006/54/EC Art. 14(1)(a) | employer | n/a | no sex discrimination in "conditions for access to employment, to self-employment or to occupation, **including selection criteria and recruitment conditions**" | in force | A | as above | Cellar 32006L0054 |
| EU | Dir. 2000/43/EC | — | — | intended citation: race/ethnicity origin, access to employment | — | **U** | **not resolved** — see §7 OJ-3 | all four retrieval rungs failed |
| EU | Dir. 2004/113/EC | — | out of scope (employment) | applies to access to and supply of **goods and services**, not employment | in force | A (recital) | does not apply to hiring: "There are already a number of existing legal instruments … in matters of employment and occupation. Therefore, this Directive should not apply in that area." | Cellar 32004L0113 |
| EU | Dir. (EU) 2024/1500 | — | not addressed to us | Member States must ensure equality bodies can prevent discrimination, assist victims and **conduct inquiries** into breaches (Arts. cited in Cellar text); automated systems incl. AI appear in a **recital** only | transposition | A (recital + operative) | creates **no direct obligation on Ariadne**; it creates a body that may investigate the employer's system and ask us for information | Cellar 32024L1500 |
| EU | Impl. Decision (EU) 2026/2274 | provider | conformity route | **EN 18286:2026** (AI — quality management system) is the **first harmonised standard** cited under Art. 40; citation confers presumption of conformity for the requirements it covers | 14 Oct 2026 (OJ citation) | A | available to us; it covers QMS, **not** the Annex III technical requirements | Cellar 32026D2274 |

---

## 3. GDPR data-flow obligations (candidate-side, we are the controller of the user's CV)

Role determination: **Art. 4(7)** "*controller* means the natural or legal person … which, alone or
jointly with others, **determines the purposes and means** of the processing of personal data" —
**A**. We choose what is ingested, how long it is kept, what is derived → controller for the user's
own CV; our model vendors are processors (**Art. 4(8)**, A), which requires Art. 28 terms.

| Stage | What Ariadne must do | Article |
|---|---|---|
| **Ingest** | Lawful basis for the user's own CV: **Art. 6(1)(b)** (necessary for performance of a contract with the data subject) for the core service; **Art. 6(1)(a)** consent only where processing goes beyond what the service requires, because consent must be freely given and withdrawable. Provide the Art. 13 notice **at collection**. **Data minimisation at the door** (Art. 5(1)(c)) — do not ingest what the task does not need. **Art. 25(1)** by-design: technical/organisational measures "intended to implement the data protection principles". | 5(1)(a)–(f), 6(1), 13(1), 25(1) |
| | **Special categories**: a CV can carry disability/health/ethnicity signals. Art. 9 has no basis in plain contract; do not build features that **infer** protected characteristics (and do not ingest a photo by default). | 9(1), 9(2)(a),(e) |
| **Processing** | Purpose limitation (Art. 5(1)(b)); accuracy of the derived output (Art. 5(1)(d)); integrity/confidentiality (Art. 5(1)(f)); **Art. 22** — our accept/reject flow is the *user* amending their own document, which is not a decision producing legal effects taken by us; the legal-effects decision belongs to the selecting party. Where an employer ever runs our scoring on candidates, Art. 22(1) engages and human-in-the-loop must be **meaningful** — the interpretive authority (EDPB guidance) was **not retrieved**, so this last clause is **C** and §7 OJ-2 closes it. | 5, 22(1)–(4) |
| **Storage** | Art. 32 measures appropriate to risk: confidentiality/integrity/availability, resilience, restore capability, testing regime. **Storage in the EU or with Art. 46 safeguards**; no CV content in logs, prompts sent to third-party models must be minimised (Art. 5(1)(c) applies to *transfers too*). Retention limit + deletion schedule (Art. 5(1)(e)). | 32(1), 5(1)(e), 44–46 |
| **Deletion** | Right to erasure on request without undue delay (Art. 17(1)), including derived artefacts and vectors/embeddings — a vector store with no delete path is an Art. 17 defect, not a backlog. Access: Art. 15 includes providing the personal data **in a structured, commonly used, machine-readable format** (Art. 20 by extension). **Design the store so a person's data is addressable**: this is why we hold CVs in a document model, not only in an embedding index. | 15, 17(1), 20 |

**Local-first posture is a legal control, not a feature preference**: the smaller the set of personal
data that leaves the user's machine, the smaller Art. 32 and Chapter V exposure. That is the GDPR-side
argument for `G6` (offline baseline).

---

## 4. Transparency and human oversight

**What the user must be told (Art. 50(1))** — that they are interacting with an AI system, unless it
is obvious to a reasonably well-informed, observant and circumspect person. **We will not rely on the
"obvious" carve-out**: a product whose own landing page has to explain what it does has not met
"obvious". Disclosure at the latest at first interaction, in a clear and distinguishable manner,
conforming to accessibility requirements (Art. 50(5)). — **A**

**Machine-readable marking (Art. 50(2))** — text output must be marked as AI-generated and
detectable, "as far as technically feasible" given the state of the art and costs. We must record
which marking technique we adopted and why it is state of the art; the feasibility qualifier is a
documentation duty in practice. — **A**

**Human oversight.** Two different things, deliberately not merged:
* *Ours (product)*: every generated change is a **proposal the user accepts or rejects**, with the
  source fact shown; a proposal we cannot ground is asked about or dropped. This exists because the
  research shows LLM tailoring invents content, not because a regulator asked (see
  `docs/00-audit.md` §B and `.work/lanes/papers.md`).
* *Theirs (Art. 26(2), Art. 14)*: the **deployer** must assign oversight to competent, trained,
  authorised persons — an employer-side duty. Ariadne does not discharge it and must not claim to.
* **What a human must be able to override**: in our flow, the user overrides *us* on every proposal
  and every section; we keep an audit trail of accepted/rejected proposals so a later dispute can
  reconstruct who changed what. That is the artifact an Art. 22 or Art. 80 discussion turns on.

---

## 5. ISO / standards readiness (jurisdiction-neutral)

Not a certification claim. A statement of where we would stand if pursued, from each organisation's
own catalogue entry.

| Standard | Publisher / status | Certifiable? | Clauses that would apply to a small candidate-side tool | What we'd need in place | Gap + **named missing artifact** |
|---|---|---|---|---|---|
| **ISO/IEC 42001:2023** — *AI management systems* | ISO (JTC 1/SC 42); catalogue: "International Standard published [60.60]", **51 pages**, publ. 2023-12 (**A**) | Management-system standard → **auditable/certifiable in principle**; the catalogue page does **not** state "certifiable", and we found **no official source for the widely repeated "Annex A = 38 controls"** figure → **C/U, do not assert it** | Clauses 4–10 structure is asserted from the standard's type, **B (inference — §7 OJ-4)**; the AI-specific parts that matter to us are AI risk assessment, AI-system impact assessment and lifecycle operational control — the *substance* is behind a paywall and **has not been read (U)** | AI policy; AI-relevant interest identification; AI risk assessment incl. impact on individuals; AI impact assessment; data governance for training/RAG data; lifecycle controls (dev → deploy → monitor); incidents & complaints; internal audit + management review; **responsible AI code of conduct** | **RED.** Missing artifact: `docs/aims/ai-risk-assessment.md` + `docs/aims/ai-impact-assessment.md` (a document set, not a PDF). **Scoped answer:** a tool that makes no decisions about others arguably needs a **scoped** AIMS (declared scope = "development and operation of a candidate-side document-assistance tool"), not a full one — but scope must be written down and defended, or the certificate will not say what we think it says |
| **ISO/IEC 27001:2022** — *Information security management systems* | ISO (JTC 1/SC 27); "published [60.60]", **19 pages** (the ISMS standard) (**A**) | Yes — certifiable ISMS | Cl. 4–10; Annex A controls relevant to CV ingestion/storage/deletion: A.5.34 privacy & PII protection, A.5.33 protection of records, A.8.1 user endpoint devices, A.8.11 masking, A.8.12 data leakage prevention, A.8.10 information deletion, A.8.13 backup, A.8.8/A.8.9 access management & privileged rights, A.8.25 secure development, A.5.19–5.22 supplier security (model API vendors), A.5.24 incident management, A.5.7 threat intelligence | Statement of Applicability; SoA-justified exclusions; **asset inventory naming the résumé corpus and the vector store**; key management; deletion path with evidence; DPA + security review per model vendor; log retention | **AMBER.** Missing artifact: `docs/isms/statement-of-applicability.md`. Realistic first certification for a small team — the controls are process+evidence, not research |
| **ISO/IEC TS 27701:2025** — *privacy information management, extension to 27001/27002* | ISO (SC 27); catalogue: **64 pages**, published [60.60], Ed. 2 (**A**) | Extension to a 27001 ISMS — audited as part of/alongside it, not as a standalone management-system certificate in the way 42001/27001 are; **do not present it as its own cert** | PII-controller obligations mapped to the GDPR surface in §3: purpose specification, minimisation, retention, deletion, disclosure management, PII incident response | Same inventory, plus a PII processing register per data category, and a deletion path that reaches derived vectors | **AMBER**, contingent on 27001. Missing artifact: `docs/isms/piir-register.csv` (one row per data category × purpose × retention) |
| **ISO 30405:2023** — *HR management — Guidelines on recruitment* | ISO/TC 260, Ed. 2, **2023-06, 16 pages**, abstract: "provides **guidance** on how to attract, source, assess and employ people …" (**A**) | **Guidance-only. Not a certification target** — say so plainly and do not list it as a milestone | Its recruitment-process framing is useful for how we describe our own boundary (candidate experience, "managing the different phases and stakeholders") | Nothing for a certificate | **GREEN, but not a milestone.** If someone writes "ISO 30401/30405 certified" in marketing, that is a false claim by construction |
| **Harmonised standards under Art. 40** | Commission standardisation request **C(2025) 3871**; first cited standard: **EN 18286:2026** (AI quality management system) by Impl. Decision **(EU) 2026/2274**, OJ citation 14 Oct 2026 (**A**) | Conformity route, not a commercial cert | For Annex III systems, presumption of conformity for the requirements the cited standard covers. **EN 18286 covers QMS, not the Annex III(4) technical requirements** — so it does not by itself discharge Branch B | If Branch B ever triggers: apply the QMS standard **and** follow Annex VI internal control (Art. 43(2)); note Annex VII (notified body) becomes the route where no harmonised standard/common specification is applied (Art. 43(1)) | **AMBER by design.** Missing artifact: none today; a decision memo if Branch B triggers |
| **SC 42 AI standards generally** (e.g. 23894 risk-management guidance, 42005 impact assessment) | Cited in the catalogue/committee space; **only EN 18286:2026 is cited in the OJ as a harmonised standard** as of 2026-10-25 (**A** for that one; others **U** — their catalogue pages returned Cloudflare 403) | Guidance / support standards, not OJ-cited | Would be the method behind our AI risk + impact assessment | Adopt the method or write our own and defend it | **AMBER.** Missing artifact: `docs/aims/method-bibliography.md` |

---

## 6. Certification sequence — recommendation for a small team

1. **Nothing as a claim; everything as an artifact.** Publish the artifacts of §5 that are cheap and
   legally forced: Art. 6(4) non-high-risk assessment, §3 register, §4 disclosure, deletion path.
   *Reason:* these are obligations, not marketing. **Cost:** days. **Given up:** the certification
   story we cannot honestly tell yet.
2. **ISO/IEC 27001 first** (2026-2027 window). *Reason:* it is the only one whose requirements are
   auditable without AI-specific research, it is what enterprise buyers ask for, and its Annex A
   already covers the CV corpus (A.5.34, A.8.10, A.8.11, A.5.21). Adding **TS 27701** in the same
   audit is marginal effort and buys us the privacy register we need anyway. **Cost:** the real cost
   is 6–12 months of evidence discipline, not the audit fee.
3. **ISO/IEC 42001 scoped, second** — scope it to what we actually do (§5 row 1). Do this *after*
   27001 so the ISMS machinery (documents, internal audit, management review, incident process) is
   reused rather than invented twice. **Trade-off:** a scoped AIMS is defensible but must state its
   scope out loud; an unscoped one implies a coverage we do not have.
4. **Harmonised standard EN 18286 only if Branch B triggers** — before 2 Dec 2027, or we re-plan.
5. **ISO 30405 is never a milestone.** Read it, cite it as guidance, do not put it on a roadmap.

---

## 7. Open legal questions (genuinely unresolved, with the next probe)

| # | Unresolved | Rungs already tried (all failed) | **Exact next probe** |
|---|---|---|---|
| **OJ-1** | Whether **Art. 49 registration** (incl. the 49(2) duty for providers relying on Art. 6(3)) sits in **Chapter III Section 4** → in force since **2 Aug 2025**, or in Section 2 → **2 Dec 2027**. The Cellar XML omits Chapter/Section headings, so the mapping is inference (**B**), not reading | Cellar XML (headings absent); EUR-Lex HTML 202/0 bytes | Open the printed OJ **L 165/3, 13.7.2024** table of contents (EUR-Lex PDF `OJ_L_2024165_EN.pdf`, p. 186 ff.) and confirm which Articles Section 4 contains. **Engineering posture meanwhile: treat registration as already in force.** |
| **OJ-2** | EDPB interpretation of "**solely** automated" for a human-in-the-loop product (what makes involvement *meaningful*) | 4 EDPB URLs → 404 (`guidelines-012025-…`, `guidelines-automated-individual-…`, `/our-documents/guidelines_en`) | EDPB register search at `edpb.europa.eu/our-work-tools/our-documents` for the Art. 22 guidance (WP251rev.1 and successors); read and re-grade §3's Art. 22 row. Until then that row is **C**. |
| **OJ-3** | **Dir. 2000/43/EC** — its access-to-employment article is uncited here, not paraphrased | EUR-Lex HTML 202/0; Cellar `celex/32000L0043` 404; Cellar OJ page-id 404; Wayback 429 ×2, raw copy returned corrupt | Cellar `oj/JOL_2000_180_R_000022_01` with `Accept: application/xhtml+xml`, `Accept-language: eng`, retried at a different hour; else Wayback after cooldown. **Do not fill from memory.** |
| **OJ-4** | ISO/IEC 42001's clause/Annex-A structure (the "38 controls" figure) | iso.org catalogue (A for pages/stage); annex text behind paywall | Buy or borrow the standard; or cite an ISO-issued public explanatory source **from ISO itself**. Until then no control count is stated anywhere in this repo. |
| **OJ-5** | Whether Art. 50(2)'s machine-readable marking has an adopted code of practice / technical standard we should implement, as opposed to our own feasibility judgement | Commission "ai-act-practice/harmonised-protocols-and-standards-ai-act" page → "Page not found"; transparency-code pages not located | Locate the AI Office code of practice on transparent marking (AI Office / digital-strategy pages, or search the OJ C series) and re-grade §4. |
| **OJ-6** | Whether a national implementation law in a market we intend to sell into adds a provider-side registration beyond Art. 49 (member-state discretion) | not attempted (out of scope for this deliverable) | Only in scope once the jurisdiction's trigger in §9 fires. |

**Note on discipline:** this section exists because it must. A legal document with zero open
questions has not looked.

---

## 8. Explicit non-claims (banned in marketing, README, UI and sales decks)

Banned because no legal basis is established here — **not** because they happen to be untrue today:

* "**AI Act compliant**" / "**AI Act ready**" / "high-risk compliant" — until an obligation row in §2
  is closed by a named artifact, there is nothing to point at.
* "**ISO 42001 certified**", "aligned with ISO 42001" as a badge, or any control count for it (§5, OJ-4).
* "**ISO 30405 certified**" — impossible; the document is guidance (**A**: it is titled *Guidelines on recruitment*).
* "**GDPR compliant**" as a blanket claim. Admissible instead: "we act as controller for the data you
  give us; here is the basis, the retention period and the deletion path" — pointing at §3 artifacts.
* "**ATS-proof**", "guarantees passing the filter", "beats the ATS" — we have no verified knowledge of
  any ATS's acceptance rules (audit §B.3: 7 of 8 engines UNKNOWN), and this sentence would be a claim
  about a third party's system we have not read.
* "**Bias-free**" / "non-discriminatory" / "fairness-audited" — the literature in `docs/` shows
  anonymisation leaks and 29.6 % matched-pair reversals; we have run **no** validity or fairness test.
* "**Not an ATS**" said in a way that implies "therefore unregulated": Art. 3(3) does not care what we
  call it; the trigger is *placing on the market under our name*.
* Any statement that **we** discharge the employer's Art. 26(7) worker-notification duty, or that our
  human-in-the-loop satisfies **their** Art. 26(2)/Art. 14 duty. Different role, different duty.
* Any date claim quoted from the "2027 delay" press narrative. Cite **Reg. (EU) 2026/1744** or say
  nothing.

---

## 9. Jurisdictional triggers

A jurisdiction enters scope when **either** trigger fires, and only then:

| Trigger | Definition | Evidence required to fire it |
|---|---|---|
| **T1 — market presence** | ≥ 1 active user or customer in that jurisdiction, or a support/contract commitment to one | billing country, account metadata, or a signed contract |
| **T2 — committed launch** | a launch decision for that market within two quarters, recorded in `DECISIONS.md` | the DECISIONS entry (date + decision owner) |

Until a trigger fires, the jurisdiction is recorded as **`deferred`** with the reason **in this file's own §2 and
§9 rows** — a per-jurisdiction registry file is created only when that jurisdiction's first trigger
fires, so no dead pointer sits here (AGENT_CONTRACT C2.4). Deferred ≠ irrelevant: it is
"out of scope **by decision**, with the reason on the record", which is the only defensible posture
for a small team that cannot research 27+ regimes at grade A. **Default: every non-EU jurisdiction is
`deferred` — no analysis performed, no speculation stored.**

## 10. Known conflicts (EU baseline)

Conflicts we can actually evidence between EU obligations and those of markets already deferred.
Anything we have not read at A/B is marked **[LEAD]** and is a work item, not a conclusion.

* **[LEAD]** Divergent provider/deployer duty allocation — the EU places classification, conformity
  and registration duties on the **provider** (Art. 3(3), 16, 43); some deferred markets instead
  regulate the **user/employer** and impose audit duties there. Our §2 rows are EU-shaped and will not
  transplant. *Probe: read one deferred regime's primary text at grade A before writing its rows.*
* **[LEAD]** Transparency timing — EU Art. 50(1) requires disclosure at first interaction; deferred
  markets may permit after-the-fact notice. If so, the disclosure component must be
  per-jurisdiction configurable rather than a single global banner. *Probe: same as above.*
* **Not a conflict on current evidence:** nothing in the EU baseline requires us to withhold anything
  that a deferred market would require us to publish. Recorded so that a later agent does not invent
  the tension.

*End of document. Every row above carries an instrument identifier and a grade; unresolved items are
in §7 with a named probe.*
