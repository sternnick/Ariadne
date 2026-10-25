

Role adopted: repo-analyst/research-rescuer — distilling one recovered transcript, read-only.

**Rezi** — https://www.rezi.ai/pricing [PROVEN, full page body captured]
- Free tier $0: 1 Resume, 1 AI Interview, 3 PDF Downloads, Standard Format Templates, AI Resume Writer/Editor ("No payment required") (https://www.rezi.ai/pricing)
- Pro $29/month: unlimited resumes/interviews/PDF downloads, all templates, Rezi Score, Keyword Targeting (https://www.rezi.ai/pricing)
- Lifetime plan "Buy for $149"; Enterprise "$99 / month per 200 users" (https://www.rezi.ai/pricing)
- Rezi Score / AI Keyword Targeting / Real Time Content Analysis graded "Limited" on Free vs "Full" on paid; Resume Review "From $8" on Free, "1 per month" on paid (https://www.rezi.ai/pricing)
- Scoring/conversion claim: "62% of Rezi users land an interview"; footer "62.18% review rate for applicants" (https://www.rezi.ai/pricing)
- Volume claims: "Join over 4,510,834 job seekers helped since September 2019", "Join 4+ million users", "land jobs at 1,000+ companies", Trustpilot "4.7 / 5.0 · 250 reviews" (https://www.rezi.ai/pricing)
- Disclaimer wording actually present: page title "All Plans Include A 30-Day Money Back Guarantee"; "free to start, no card required"; testimonial attributed "United States via Trustpilot"; "© 2026 Rezi" (https://www.rezi.ai/pricing)

**Teal** — https://www.tealhq.com/pricing [page body PROVEN for marketing/nav; prices SNIPPET-ONLY from greps]
- Prices SNIPPET-ONLY: "$13 per week Unlimited Resumes", "$13 Every 7 Days ($1.85 a day)", "$29 Every 30 days", "$79 Every 90 days ($0.87 a day)", "($0.96 a day)" (https://www.tealhq.com/pricing)
- Footnote fragment SNIPPET-ONLY: "* when your subscription will be cancelled, upon which your account will revert back to the free plan" (https://www.tealhq.com/pricing)
- Scoring products PROVEN: "Resume Job Description Match … personalized Match Score", "ATS Resume Checker — Quickly check your current resume score", "Resume Keyword Scanner" (https://www.tealhq.com/pricing)
- Marketing counts PROVEN: "2,000+ resume examples", "1,500+ cover letter examples", "1,500+ CV samples", "100+ … cover letter templates", "900+ synonyms", career guides "over 500 roles", "Millions of jobs" (https://www.tealhq.com/pricing)

**Kickresume** — https://www.kickresume.com/en/pricing/ [cookie/privacy body PROVEN; all prices SNIPPET-ONLY]
- SNIPPET-ONLY: "€8 / month … Pay €96 every 12 months"; "€18 / month … Pay €54 every 3 months"; "€24 / month"; free "€0 / month … 4 basic resume templates"; "€26 / resume English & Spanish" (https://www.kickresume.com/en/pricing/)
- SNIPPET-ONLY referral wording: "€120 in Premium gift vouchers for your friends", "€72 in Premium gift vouchers", "€120). Opt for the yearly (5 friends) or quarterl…" (https://www.kickresume.com/en/pricing/)
- Privacy disclaimer PROVEN: "we'll never share your resumes and cover letters with recruiters or job sites" + cookie categories Necessary/Performance/Marketing (https://www.kickresume.com/en/pricing/)

**Enhancv** — https://www.enhancv.com/pricing [page body PROVEN; prices broken in raw HTML]
- Free Plan "€0 Valid for 7 days": all templates, basic sections, "Enhancv branding", "Maximum 12 section items" (https://www.enhancv.com/pricing)
- Title "Starting from $16.50 and 7-Day Free Plan"; Pro Quarterly renders as "€ NaN - SAVE NaN% … €0 billed every 3 months" — price is JS-injected, raw HTML has no real number (https://www.enhancv.com/pricing)
- Pro Quarterly features: "300 resumes and cover letters", "Real-time content suggestions", "ATS check (Applicant Tracking System)", "No branding", "Unlimited section items" (https://www.enhancv.com/pricing)

**Jobscan** — https://www.jobscan.co/pricing [NOT-IN-FILE for pricing]
- curl HTTP 200 returned only 6,653 bytes whose extracted text was " Jobscan "; browser_navigate redirected to https://app.jobscan.co/plan with `content_chars:0, looks_empty:true`; camo_navigate returned title "Just a moment..." (Cloudflare wall). No Jobscan price or score claim exists in this file.

**Transcript shape**
- The lane wrote **zero `## SAY` notes** — 7 `## CALL` / 7 `## RESULT` only. There is no analyst interpretation, no comparison, no conclusion. The lane died mid-task on the Jobscan bot-wall.
- First call was `ls /tmp/ats-research` + `cat $PI_CODING_AGENT_DIR/trusted-sources.md` (generic AI-doc/NIST/arXiv source table) — unrelated to ATS vendors, no pricing value.

GAPS:
- No Jobscan pricing, free tier, or resume-score methodology anywhere in the file.
- No disclaimer anywhere stating how "62%", "62.18%", or "Match Score" is computed; no methodology or accuracy caveat captured.
- Teal and Kickresume prices are grep fragments, not verified page body; Enhancv's real Pro price never rendered ("NaN").
- No annual/monthly equivalence math, no currency-normalisation (€ vs $), no seat-based Rezi Enterprise terms beyond "per 200 users".
- No second capture of the Rezi "70%" fragment that floats orphaned above the SSO row.

NUMBERS:
- 0 / $0 — Rezi Free tier price (vendor)
- 1, 1, 3 — Rezi Free limits: resumes, AI interviews, PDF downloads (vendor)
- 29 / $29 — Rezi Pro monthly (vendor)
- 149 / $149 — Rezi lifetime one-off (vendor)
- 99 / $99, 200 — Rezi Enterprise monthly per 200 users (vendor)
- 8 / "$8" — Rezi resume review starting price (vendor)
- 62% , 62.18% — Rezi interview-success / "review rate" (vendor marketing)
- 4,510,834 — Rezi users helped since Sept 2019 (vendor marketing)
- 4+ million — Rezi users (vendor marketing)
- 1,000+ — hiring companies (vendor marketing)
- 4.7 / 5.0 and 250 — Trustpilot rating and review count (vendor-displayed third-party)
- 42 — days in testimonial (vendor anecdote)
- 30 — money-back guarantee days (vendor)
- 2026 — "© 2026 Rezi" (fact)
- 2,000+ / 1,500+ / 1,500+ / 100+ / 900+ / 500 / "Millions" — Teal content counts (vendor marketing)
- 13, 29, 79 / 1.85, 0.96, 0.87 — Teal cadence prices, SNIPPET-ONLY (vendor)
- 8, 18, 24, 26, 0 / 96, 54, 72, 120 — Kickresume € monthly/quarterly/annual, per-resume, voucher totals, SNIPPET-ONLY (vendor)
- 14- / 40 — Kickresume truncated fragment counts, meaning unknown (SNIPPET-ONLY)
- 16.50 ($), 0 (€), 7 (days), 12 (max section items), 300 (resumes) — Enhancv (vendor; NaN = unrendered)
- 6,653 / 132,108 / 133,391 / 167,816 — curl'd HTML byte sizes (measured)
- 5,737 / 5,840 / 0 — captured content_chars (measured); 25 — curl timeout seconds and UA string "126" (tooling)
- 0 — count of `## SAY` notes in the file (measured, proven)