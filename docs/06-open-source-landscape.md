```
Last verified: 2026-10-25
Reviewed by:   Ariadne (principal)
Live surfaces: repository star counts, licences and last-push dates (30-day clock)
```

# 06 — Open-source landscape

What other people's code actually does — separated from what their README says, and from what their
star count implies. Star counts are metadata, not quality, and several claims below are deliberately
graded down.

## 6.1 The systems worth studying, and why

| Project | Licence | What is **proven** about the mechanism | Grade |
|---|---|---|---|
| **JobScout** (`latenightsbeats1208-pixel/jobscout`) | MIT (+ ODbL 1.0 / CC BY 4.0 for geo data, SIL OFL fonts) | scoring is **deterministic and local** — "Aucun appel IA : instantané et illimité", `lib/scoring/local.ts`, with a stated score contract **±10 / −6** and a `POST /api/offres/rescore` path; anti-hallucination is a **deletion** garde-fou (removes companies/skills not anchored in the profile) plus Zod validation and a confidence value; parse cascade `pdf-parse`/`pdfjs-dist` (multi-column) → `mammoth` (DOCX) → `tesseract.js` FR+EN OCR → TXT | **A** (`[PROVEN]` README body, [EV-28]) |
| **AviCV** (`sinaatalay/avicv`) | none declared | exposes an **MCP endpoint** at `avicv.com/mcp`; runs "factual checks" on the tailored PDF; RenderCV for PDF; FastAPI + SQLite + SvelteKit/Bun; Gemini via OpenRouter | **A** (`[PROVEN]`, [EV-28]) |
| **Resume-Scanner** | MIT | `all-MiniLM-L6-v2` embeddings + TF-IDF cosine + Gradient Boosting in a `HybridMatcher`; its own README calls the ATS score "an analytical estimate" | **A** (`[PROVEN]`, [EV-28]) |
| **career-ops** (`career-ops-hq/career-ops`) | MIT | a **fact-gate** exists (commit `fix(fact-gate): read French counts in generated CVs`) | **C** (`[SNIPPET-ONLY]` commit message, [EV-28]) |
| agentic-resume-tailor | MIT badge, API `lic: None` | "experience-log-as-source-of-truth", CI badge | **C** |
| resume-AI / StackResume | GPL-3.0 | "deterministic ATS scoring" / "self-hosted builder" — internals **NOT-IN-FILE** | **C** |
| imprintcv | MIT | "deterministic zero-token fact verifi…" — README body absent | **C** |

## 6.2 What is *not* in the file (and therefore not a fact)

* **No vector database is named for any repository** across the ~20 examined. "RAG" and "semantic
  embeddings" appear; the store is never identified. **`[NOT-IN-FILE]`**, [EV-28].
* No README body for career-ops, resume-AI, StackResume, imprintcv, MODULAR-RAG-MCP-SERVER.
* `Sungchunn/AI-Resume-Tailor` — reported earlier in this session as a relevant repo — **does not
  appear in the evidence at all**. It is recorded as absent ([EV-28]); treat the earlier mention as
  unverified.
* Licence for AviCV and agentic-resume-tailor: shields say MIT, the GitHub API says none. **A
  contradiction, unresolved** — we treat both as "no licence granted" until the file `LICENSE` is read.

## 6.3 Star counts: recorded, not trusted

API-observed: `career-ops` **77,167**, `ai-job-search` **65,453**, `MODULAR-RAG-MCP-SERVER` 1,188,
then a long tail (506, 492, 434, 332, 131, 114, 88, 81 for JobScout, 75, 74, 65, 52, 47, 39, 35, 26,
19, 16, 14, 13, 8, 7, 5, 4, 3, 2, 1, 0). **C** — [EV-28].

The research lane itself flagged `career-ops`' figure as **implausible against its peers**. Two numbers
in the same table cannot both be taken at face value, so the table is reported as metadata and **no
adoption claim is built on it**. This is `docs/01` §1.4 applied to ourselves.

## 6.4 What we take, and what we refuse

**Taken as design evidence (not code):**

| Pattern | Source | Why |
|---|---|---|
| Deterministic local scoring with a **declared tolerance**, and a re-score path | JobScout ([EV-28], **A**) | reproducibility; matches [EV-02]'s instability finding |
| **Deletion** of unanchored entities as the anti-hallucination control | JobScout (**A**), career-ops fact-gate (**C**) | a filter that can only remove is auditable; a prompt is not |
| Parse cascade with explicit fallbacks (PDF → DOCX → OCR) | JobScout (**A**) | matches doc 02's rung structure |
| Per-item accept/reject with three dispositions | Jobsuit ([EV-22], **B**) | human oversight that is real, not a token gesture (doc 09 §4) |
| Owning the whole local stack (SQLite, no cloud dependency) | AviCV (**A**) | consistent with `D-016` |

**Refused:**

* **Copying AGPL/GPL code** — `AienTech/dossier` (AGPL-3.0), `resume-AI` and `StackResume` (GPL-3.0).
  Design-only reading under `D-008`/C7.6.
* **Any "ATS score" parity claim.** Resume-Scanner's own disclaimer is the model to follow: an
  analytical estimate, not an outcome.
* **Building an MCP surface in v1.** One project ships one ([EV-28]); that is *evidence it is
  possible*, not evidence anyone wants it. Cut in the audit's plan revision (C7.3).

## 6.5 The gap that matters

The ecosystem has converged on three things — deterministic scoring, deletion-based fact gating, and
local-first data — and on **nothing** about parser compatibility with real ATS products. That is the
same gap `docs/01` §1.5 records: nobody in this sample has published which formats or layouts a named
vendor accepts.

**[OPEN]** We have no evidence on **maintenance health beyond last-push dates**: no issue-close rates,
no release cadence, no bus factor. Probe: GitHub API `closed_issues`, `releases`, contributor counts for
the five projects we cite, if we ever depend on one.

**[OPEN]** `career-ops`' 77k stars and `ai-job-search`' 65k are either real (and the category is far
larger than the ATS vendor market implies) or artefacts (coordinated starring, or a very different
audience). Probe: read the repositories' contributor graphs and issue quality; do not repeat the
numbers as adoption evidence meanwhile.

## What would make this strong

| Gap | Probe that closes it (exact) |
|---|---|
| Only READMEs + API metadata; no maintenance signal | For the five cited projects: `GET /repos/{o}/{r}` (`open_issues_count`, `pushed_at`), `/releases`, `/contributors?per_page=100`, and a 90-day commit histogram. Publish median time-to-close for issues. |
| Star counts untrusted (§6.3) | Same probe as above plus `stargazers` growth over time (`/stargazers?per_page=100` timestamps): organic growth is smooth, coordinated starring is a step. Report a verdict per project, or report that the data cannot distinguish them. |
| No licence file read for two projects (§6.2) | `GET /repos/sinaatalay/avicv/contents/LICENSE` and the same for `BPMSoftwareSolutions/agentic-resume-tailor`; quote the first line. Until then both stay "no licence granted". |
| No vector-DB evidence anywhere (`[NOT-IN-FILE]`) | Grep each repository tree via the API for `chromadb|qdrant|pgvector|faiss|pinecone` (code search) and record hits. That turns an absence-of-mention into an absence-of-use. |
| `career-ops` 77k stars implausible | Contributor graph + issue quality, as above. If it is real, the category is far larger than the vendor market implies — a finding worth having. |

