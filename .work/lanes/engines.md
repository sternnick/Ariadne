

# Research: ATS resume parsers — formats, limits, parser vendor

## Summary
Tool budget exhausted (6 calls) with **only one hard, official-grade data point**: Lever's developer docs listing accepted upload extensions. All 5 direct help-center fetches I attempted failed (404/401/Cloudflare challenge/DNS fail), and two of four searxng queries returned **NO RESULTS**. Everything else below is SEO-blog grade and explicitly unverified. Do not treat the vendor-attribution column as established.

## Findings (claim → source, date)
- **Lever accepts these upload file types: `docx; doc; js; jpg; png; pdf; txt`** — verbatim from search snippet of the Lever API overview ("supported file formats: docx; doc; js; jpg; png; pdf; txt. Note: In cases where the desired outcome is that an uploaded file be parsed for information…"). (source: https://hire.sandbox.lever.co/developer/documentation, date unknown; *sandbox* subdomain, so may be a mirror — NEEDS VERIFICATION)
- **Lever has a ~30 MB documented upload limit, formats DOCX/DOC/PDF/TXT/JPG** — third-party guide, not Lever itself. (source: https://slimfiles.net/guides/reduce-file-size-for-job-application-portal, undated) NEEDS VERIFICATION
- **Greenhouse accepts doc, docx, pdf, rtf, txt; candidate uploads up to 100 MB** — SEO blog, flagged `entity_mismatch`/weak by the search quality scorer. (source: https://www.resumeadapter.com/ats/greenhouse, 2026-09-03) NEEDS VERIFICATION
- **Greenhouse candidate help center lists PDF, DOC, DOCX, TXT, RTF** — same claim independently, different SEO blog. (source: https://resumeoptimizerpro.com/blog/greenhouse-ats-resume-guide, 2026-04-08) Two independent secondary sources agree on the extension set; neither is Greenhouse. NEEDS VERIFICATION on the 100 MB figure (only 1 source).
- **Breezy HR parses best on text-based DOCX/TXT/RTF/PDF, not scanned images** (adjacent datapoint, not a target). (source: https://parseur.com/blog/best-ats, 2026-10-13) LOW
- **Workday: recommended workaround is single-column DOCX or text-based PDF with no tables/text boxes/header-only contact info** — implies table/text-box/headless parsing fragility, but is a career-blog, not Workday docs. (source: https://hireflow.net/blog/workday-resume-upload-formatting-issues-the-real-fixes-that-work, 2026-02-06) LOW

**Tool failures (exact errors, not fabricated):**
- `support.greenhouse.io/hc/en-us/articles/360020744252` → **HTTP 404**
- `help.lever.co/hc/en-us/articles/360001122232` → **HTTP 401**
- `help.smartrecruiters.com/Resume_parsing` → HTTP 200 but Cloudflare JS challenge only (`__CF$cv$params`), no content
- `help.ashbyhq.com` → **HTTP:000** (connection failed)
- `help.teamtailor.com/hc/en-us/articles/360008374878` → **HTTP 404**
- searxng `…site:support.greenhouse.job OR site:help.lever.co OR site:myworkday.com` → **count: 0, NO RESULTS** (site: operators unsupported)
- searxng vendor query (`Textkernel Daxtra Sovren …`) → **count: 0, NO RESULTS**

## GAPS
1. **Parser vendor attribution: 0/8 targets answered.** The vendor query returned zero results and no vendor page was fetched. Textkernel/Daxtra/Sovren/Radancy mapping for Workday, Greenhouse, Lever, Taleo, iCIMS, SmartRecruiters, Ashby, Teamtailor is **UNKNOWN — do not infer**.
2. **Re-typed-into-form vs. true parsing: 0/8 answered.** No official source confirms whether any target falls back to manual form entry on parse failure. (The Workday blog finding is circumstantial only.)
3. **Size limits: only 2 secondary claims** (Greenhouse 100 MB, Lever 30 MB). Workday, Taleo, iCIMS, SmartRecruiters, Ashby, Teamtailor: UNKNOWN.
4. **Extensions for Oracle Taleo/Oracle Recruiting Cloud, iCIMS, SmartRecruiters, Ashby, Teamtailor: UNKNOWN** — never successfully fetched.
5. **Workday**: no official myworkday.com content retrieved.

Suggested next steps: (a) searxng without `site:` operators, one query per vendor using their own product nouns; (b) `browser_navigate`→`browser_content` on `help.smartrecruiters.com/Resume_parsing`, `developers.smartrecruiters.com`, `teamtailor.com/help`, `developers.ashbyhq.com`, `workday.com/community` (browser bypasses the Cloudflare challenge that blocked curl); (c) Textkernel/Daxtra partner-page listings for reverse vendor mapping; (d) Oracle docs.oracle.com Fusion HCM "Resume Parsing" chapter for Taleo/RC formats.

## Verification
- Cross-referenced (2 sources, both LOW quality): Greenhouse extension set `doc/docx/pdf/rtf/txt` — resumeadapter.com + resumeoptimizerpro.com.
- Single-source: Lever formats (sandbox doc page); Lever 30 MB; Greenhouse 100 MB; Workday layout fragility.
- Conflicting: none observed, but absence of conflict ≠ confirmation.
- Source quality: HIGH = none retrieved. MEDIUM = none. LOW = 5 SEO/career blogs. Official = 1 (Lever sandbox mirror, unconfirmed).