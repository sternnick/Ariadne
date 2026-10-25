

**Role adopted: code-analyst/repo-analyst** — distilling one recovered transcript file, read-only.

## Open-source repos proven in `.work/rescue/opensource.txt`

- JobScout scans 6 job sites, scores locally, never invents a skill; MIT licence, "gratuit, sans compte ni abonnement" [PROVEN] (https://github.com/latenightsbeats1208-pixel/jobscout.git, file:86,129,148)
- JobScout anti-hallucination = Zod validation + confidence score + "garde-fou anti-hallucination" deleting companies/skills not anchored in the profile [PROVEN] (file:108)
- JobScout CV-parsing cascade: `pdf-parse`/`pdfjs-dist` multi-column, `mammoth` DOCX, `tesseract.js` FR+EN OCR, TXT; OCR models fetched from cdn.jsdelivr.net [PROVEN] (file:108)
- JobScout models: two per provider (rédaction + relecture); Anthropic reference "Opus 4.8 pour la rédaction, Sonnet 5 pour la relecture"; local `gemma4:12b`, `qwen3.5:9b`, `ministral-3:14b` [PROVEN] (https://platform.claude.com, https://aistudio.google.com/apikey, file:14,51)
- JobScout scoring is deterministic/local, "Aucun appel IA : instantané et illimité", `lib/scoring/local.ts`, contract ±10/−6; re-score `POST /api/offres/rescore` [PROVEN] (file:86,91,95)
- JobScout licence = MIT code + ODbL 1.0 `geo-fr.json.gz`, CC BY 4.0 GeoNames, Licence Ouverte 2.0 INSEE, SIL OFL 1.1 fonts [PROVEN] (https://opendatacommons.org/licenses/odbl/1-0/, file:150-153)
- JobScout cost claim "environ 0,12 à 0,20 $ par dossier" with Claude [PROVEN text, vendor estimate] (file:114)
- JobScout activity: 81 stars, TypeScript, push 2026-10-21T18:42:56Z, commit `3786397` "JobScout v3.4.17 — offres par distance" 2026-10-21T13:29:25Z [SNIPPET-ONLY] (file:20,189)
- Resume-Scanner: Sentence-BERT `all-MiniLM-L6-v2` embeddings + TF-IDF cosine + Gradient Boosting `HybridMatcher`, Streamlit, "25 automated tests", MIT badge; API row says lic MIT, 3 stars, push 2026-09-01T05:31:17Z [PROVEN body / SNIPPET-ONLY metadata] (https://img.shields.io/badge/license-MIT-green, file:22,79,168,10,188)
- Resume-Scanner disclaimer: ATS score is "an analytical estimate", not guaranteed outcomes [PROVEN] (file:105)
- agentic-resume-tailor: MIT shield + CI badge, "Auto-Verification & Token Management" (Issue #24), experience-log-as-source-of-truth docs [PROVEN] (https://github.com/BPMSoftwareSolutions/agentic-resume-tailor/actions/workflows/ci.yml, https://github.com/BPMSoftwareSolutions/agentic-resume-tailor/issues/24, file:127-131)
- agentic-resume-tailor contradiction: README says MIT but API row `lic None`; dormant since push 2025-12-11T01:33:34Z [SNIPPET-ONLY] (file:128,7,190)
- AviCV: browser + coding-agent job matcher; MCP endpoint `https://avicv.com/mcp`; "factual checks" on tailored PDFs [PROVEN] (https://avicv.com, file:193,203,199)
- AviCV stack: SvelteKit/Svelte/Bun frontend, FastAPI/Python/SQLite backend, TypeSafe's Jev matching, Gemini via OpenRouter, RenderCV, CopilotKit + Darwin from speedrun-amber [PROVEN] (https://github.com/rendercv/rendercv, https://github.com/ziadgit/speedrun-amber, https://bun.com, https://docs.astral.sh/uv/, file:207-213)
- AviCV requires `OPENROUTER_API_KEY` + `TYPESAFE_API_KEY`; data in `backend/data/`; no account recovery; Anthropic optional [PROVEN] (http://localhost:5173, http://127.0.0.1:8000/docs, file:229-233)
- AviCV metadata: 1 star, Python, lic None, push 2026-10-12T02:54:24Z, commit "Lower CV drafting reasoning effort while retaining factual r…" [SNIPPET-ONLY] (file:8,191)
- gr8monk3ys/resume-AI: GPL-3.0, 8 stars, "deterministic ATS scoring, tailoring and cover letters"; only recent commit is a dependabot certifi bump — pipeline NOT-IN-FILE [SNIPPET-ONLY] (file:21,192)
- vmlgtm/imprintcv: MIT, 2 stars, "deterministic zero-token fact verifi…" — README body NOT-IN-FILE [SNIPPET-ONLY] (file:41,193)
- Sathvik-Rao/StackResume: GPL-3.0, 16 stars, "self-hosted open-source AI resume builder", last commit 2026-06-09 — internals NOT-IN-FILE [SNIPPET-ONLY] (file:38,194)
- career-ops-hq/career-ops: MIT, JavaScript, 77167 stars, push 2026-10-25T15:14:16Z; commit `fix(fact-gate): read French counts in generated CVs` proves an anti-hallucination "fact-gate" exists [SNIPPET-ONLY] (file:57,195)
- ai-job-search-dev/ai-job-search 65453 stars MIT; AienTech/dossier AGPL-3.0 self-hosted tailored resumes; olyaiy/resume-lm AGPL-3.0 Next.js 15/React 19; jerry-ai-dev/MODULAR-RAG-MCP-SERVER 1188 stars "modular RAG with MCP" (no vector DB named) [SNIPPET-ONLY] (file:73-75,66)
- EceDalpolat/job-hunt-agent MIT "LangChain deepagents"; nirajmind/CareerPilot MIT "powered by Gemini"; wallentx/jobscout Apache-2.0 Go TUI [SNIPPET-ONLY] (file:48,63,23)
- Sungchunn/AI-Resume-Tailor does NOT exist in the file — 20 repos listed, closest are `Resume-Reader` (0★ JS) and `PDF-RAG-Backend` [SNIPPET-ONLY]; "sira" repos are unrelated CV one-offs (Tiqni/sira 0★ Arabic multi-agent) (file:146-166,174)
- Vector DB: **no vector database is named for any repo anywhere in the file** (only "Semantic Embeddings"/"RAG" wording) — NOT-IN-FILE (file:22,66)
- "avicv.com" and jobscout.github.io pages were never fetched — only README text via raw curl [PROVEN of method] (file:78-79,142)

**GAPS:** No vector DB, embedding store, or reranker for any repo. No README bodies for imprintcv, StackResume, career-ops, resume-AI, MODULAR-RAG-MCP-SERVER. `Sungchunn/AI-Resume-Tailor` absent. career-ops' 77167★ is implausible vs peers — unverified. No licence for avicv/agentic-resume-tailor per API despite shields.

**NUMBERS** (all GitHub-API/measured unless noted):
- HTTP `200` — api.github.com reachable [measured]
- Stars: 77167 (career-ops), 65453 (ai-job-search), 1188 (MODULAR-RAG), 797, 506, 492, 434, 332, 131, 114×2, 88, 81 (jobscout), 75, 74, 65, 52, 47, 39, 35, 26, 19, 16×3, 14, 13×3, 8×4, 7, 5×3, 4×3, 3×3, 2, 1×5, 0 — API counts, not measured quality
- `0,12–0,20 $` per dossier JobScout [vendor marketing/estimate]
- `±10 / +10 / −6` contract scoring weights [product spec]
- `25` Resume-Scanner tests [repo self-reported]
- `6` job sites scanned [vendor claim]
- Versions: Opus 4.8 / Sonnet 5 / Opus 5.5 / Sonnet 5.5, gemma4:12b, qwen3.5:9b, ministral-3:14b, all-MiniLM-L6-v2, certifi 2026.1.4→2026.10.19, Bun 1.4+, Python 3.14, Next.js 15, React 19, v3.4.17, v0.2.0 [identifiers; certifi bump measured]
- Licences: MIT, GPL-3.0, AGPL-3.0, Apache-2.0, ODbL 1.0, CC BY 4.0, Licence Ouverte 2.0, SIL OFL 1.1, NOASSERTION
- Ports 5173 / 8000; Issue #24; PR #2, #20; `per_page=100`; 51M (Linkedin-user-DB name); timestamps 2015-01-29 → 2026-10-25T15:14:16Z [measured API fields]