

# Research: What an ATS is (technical definition)

**Definition (Wikipedia, en, rev. 2026-10-16):** "An applicant tracking system (ATS) is a software application that enables the electronic handling of recruitment and hiring processes." Framed as a recruitment-shaped CRM.

## Findings

- **Working definition** — An ATS is the system-of-record for a requisition-and-candidate pipeline: a domain-specific CRM whose entities are job/requisition, candidate/applicant, pipeline stage, and activity, with hiring as the workflow instead of selling. (source: https://en.wikipedia.org/wiki/Applicant_tracking_system, 2026-10-16)
- **The module set is near-canonical** — sourcing qualified candidates, job posting/distribution, resume parsing, database search and filtering, candidate ranking/rating, applicant management and tracking, interview scheduling, automated communication (emails, reminders to candidates and hiring managers), reporting and analytics. Nine modules, all standard. (source: https://en.wikipedia.org/wiki/Applicant_tracking_system, 2026-10-16)
- **Compliance is a module, not an add-on** — Wikipedia's extract does not name compliance/EEO retention explicitly; the audit-trail requirement is implied by "reporting and analytics" only. Treat "compliance" as inferred-from-practice, not sourced. (GAP, see below)
- **Adoption is near-total at the top of the market** — 97.4% of Fortune 500 companies have a detectable ATS; Workday alone appears on more than 40% of them (Jobscan 2026 usage report, as cited by two independent secondary write-ups). (source: https://www.pin.com/blog/ats-market-share-report/, 2026-07-20; https://matchr.io/blog/top-15-ats-for-recruiters, 2026-10-07)
- **No dominant vendor outside the Fortune 500** — across 600+ recruiting teams with a connected ATS, 23 distinct systems appear; no single platform exceeds 16.5% of connections; top four = 58.7%; Ashby 15.6%, Crelate 13.6%, Bullhorn 6.0%, Greenhouse 5.2%; HHI ≈1,000 = unconcentrated. Every team ran exactly one ATS. (source: https://www.pin.com/blog/ats-market-share-report/, 2026-07-20 — vendor's own telemetry, self-interested)
- **Market size is unresolvable** — $17.22B (Fortune Business Insights, 2025) vs $2.5B (Apps Run The World, 2024) for the same market: a 6.9x disagreement driven by whether bundled HCM-suite recruiting modules are counted. (source: https://www.pin.com/blog/ats-market-share-report/, 2026-07-20)
- **Greenhouse footprint** — 7,500+ self-reported customers; topped G2 Winter 2026 ATS rankings; center of gravity mid-market/enterprise in-house. (source: https://www.pin.com/blog/ats-market-share-report/, 2026-07-20)
- **Human vs software** — software touches essentially every application first (parse → dedupe → structured-field/keyword filter → optional rank) before a recruiter's eyes; ~98% of Fortune 500 run every resume through an ATS before a human sees it. (source: https://mypersonalrecruiter.com/ats-resume-what-applicant-tracking-systems-actually-look-for-in-2026/, 2026-06-09)
- **But the "ATS auto-rejects 75%" claim is unsupported** — the widely-circulated 75%-rejected-by-ATS statistic has no strong empirical backing; ATSs filter and surface, human reviewers make the reject decision in most setups. (source: https://www.davron.net/ats-systems-explained-75-percent-resumes-rejected/, 2025-10-09)
- **Executive search and SMEs are the exception** — retained search firms largely do not use ATSs; SME adoption cited at 17%. So "ATS = gatekeeper" is a mid-market/large-employer statement only. (source: https://www.duperrin.com/english/2026-06-22/ats-recruitment-myths/, 2026-06-22)
- **Behavioral side-effect** — application filtering has produced "resume SEO" formatting behavior among candidates. (source: https://en.wikipedia.org/wiki/Applicant_tracking_system, 2026-10-16)

## Verification
- **Cross-referenced (2+):** 97.4% F500 ATS adoption + Workday >40% (pin.com + matchr.io); Workday/Greenhouse enterprise dominance (pin.com + hrstechspace.com + jobwizard.ai).
- **Single-source, NEEDS VERIFICATION:** the entire Pin share table; "98% of F500 run every resume through an ATS before a human sees it"; SME 17% figure.
- **Conflict:** Pin's "no platform >16.5%, HHI ~1,000, no incumbent" vs Jobscan's "Workday >40% of F500." Not contradictory — different populations (agency-heavy sourcing sample vs F500). Pin says so explicitly.
- **Source quality:** Wikipedia HIGH but thin and citation-light; pin.com MEDIUM (first-party telemetry, sells a competing product); davron/duperrin MEDIUM (skeptic, but search-firm interest); rest LOW (SEO content marketing).

## GAPS
- **No authoritative vendor count.** Zero source states "N ATS vendors exist." Best evidence: 23 distinct systems observed in one 600-team sample. Total addressable vendor count UNKNOWN.
- **Compliance module unsourced.** Need SHRM/EEOC record-retention or OFCCP documentation to ground it.
- **No primary measurement of human-touch timing** (e.g., time-in-stage before first human view). All figures are adoption proxies, not reading-event telemetry.
- TOOL/PATH FAILED: none. Browser/camo unused per instructions.
- Date caveat: sources are heavily vendor-authored 2026 content; treat all market numbers as marketing-adjacent.