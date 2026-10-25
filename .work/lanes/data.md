

**Role adopted: repo-analyst/scout** — the only artifact is a recovered transcript; nothing external re-fetched (4 tool calls used).

**Source file:** `.work/rescue/data.txt` (85 lines; ends mid-token inside the JSON Resume "certificates" table — the transcript is truncated). No `## SAY` lines exist; every claim rests on CALL/RESULT lines.

**Distilled data/taxonomy assets**

- JSON Resume schema v1.7.0, "14 sections, every one optional", plain Draft-07 JSON Schema, ISO 8601 dates [PROVEN] (https://jsonresume.org/schema/)
- JSON Resume top-level sections enumerated: basics, objective, work, volunteer, education, awards, certificates, publications, skills, languages, interests, references, projects, meta, custom [PROVEN] (https://jsonresume.org/schema/)
- `basics` fields: name, label, image, email, phone, url, summary, location{address,postalCode,city,countryCode ISO-3166-1 ALPHA-2,region}, profiles[]{network,username,url}, custom [PROVEN] (https://jsonresume.org/schema/)
- `work` fields: name, location, description, position, url, startDate, endDate, summary, highlights[], keywords[] ("Skills, tools or technologies used in this role"), custom [PROVEN] (https://jsonresume.org/schema/)
- `volunteer` = organization, location, position, url, startDate, endDate, summary, highlights[], custom; `education` = institution, location, url, area, studyType, startDate, endDate, score, courses[], summary, custom [PROVEN] (https://jsonresume.org/schema/)
- `awards` = title, date, awarder, summary, custom; `certificates` = name, date (table cut off) [PROVEN] (https://jsonresume.org/schema/)
- `custom` object is the sanctioned extension point at root/basics/any entry; "tools should preserve it unchanged" — parse-safe extension mechanism [PROVEN] (https://jsonresume.org/schema/)
- JSON Resume licence: NOT-IN-FILE (page body states none)
- ESCO access is via "an Application Programming Interface" providing different classification versions [SNIPPET-ONLY] (https://esco.ec.europa.eu/en/use-esco/use-esco-services-api ; https://esco.ec.europa.eu/en/use-esco/use-esco-services-api/esco-web-service-api ; https://esco.ec.europa.eu/en/about-esco/escopedia/escopedia/esco-api)
- ESCO v1.2.1 lists 13,939 skills and 3,039 occupations — competitor-blog figure [SNIPPET-ONLY] (https://hirelayer.co/blog/skills-taxonomy-api-comparison)
- ESCO REST API covers 27 languages; per-API confidence 0.80–0.90 for `search_onet`/`search_esco`/`get_esco_occupation` [SNIPPET-ONLY] (https://dl.acm.org/doi/full/10.1145/3786335.3813207)
- ESCO classification landing page cited only inside a snippet [SNIPPET-ONLY] (https://esco.ec.europa.eu/en/classification) ; ESCO v1.2 launch deck [SNIPPET-ONLY] (https://esco.ec.europa.eu/system/files/2024-05/V1.2%20Launch%20-%20ESCO%20SEC%20combined%20-%20final%20clean.pdf)
- ESCO licence/terms: NOT-IN-FILE
- O*NET Web Services appears **only** as words inside a search query and inside snippets; no working endpoint, size, licence or field list is in the file [NOT-IN-FILE] (only fragment `...onetcenter.org/bright/current/mnm_outlook.html` inside [SNIPPET-ONLY] https://www.lsc.edu/degrees/cyber-security-certificate/ and .../cyber-defense-certificate/)
- O*NET used as a sampling frame: "35 selected O*NET occupations" [SNIPPET-ONLY] (https://arxiv.org/html/2605.26329v1)
- Lightcast JPA endpoint `POST https://api.lightcast.io/jpa/postings` with accept/content-type JSON headers — seen only in a snippet's curl block [SNIPPET-ONLY] (https://docs.lightcast.io/lightcast-api/reference/jpa_post_postings)
- HF dataset `datasetmaster/resumes`: "merged collection of real and synthetic resume data in JSON format… normalized to a common schema"; row flagged `weak / entity_mismatch`; no size, no licence [SNIPPET-ONLY] (https://huggingface.co/datasets/datasetmaster/resumes)
- Kaggle Resume Dataset (labeled resumes across job categories) named only in prose, no URL, no licence [SNIPPET-ONLY] (https://everyonewhocode.com/real-world-ai-projects-that-get-you-hired/)
- Kaggle Piramal ML Hackathon resume dataset, bare host `kaggle.com/datasets/abhishekgautam12/piramal-ml-hackathon-resume-dataset` [SNIPPET-ONLY] (https://www.mdpi.com/2079-9292/14/14/2787)
- Labeled resume–vacancy corpus "over 7,000 resume–vacancy pairs" [SNIPPET-ONLY] (https://www.researchgate.net/publication/396317231_Smart_Application_for Recruiting_…_Siamese_Neural_Network_Architecture)
- Licence determination deferred to an external "licensing guide"; no asset licence proven anywhere [SNIPPET-ONLY] (https://arxiv.org/html/2406.12031v1)
- Local repo state (bash `ls -R`, PROVEN): `/tmp/ats-research/data/sources/2026-10-25-jobSuit-ai-demo-transcript.md` is the **only** file under `data/`; `data/corpora`, `docs`, `examples`, `scripts`, `src/ats_research`, `tests` are all empty; a top-level `LICENSE` exists but is never read. Only other local hit: `domain-pool.md:54` → https://huggingface.co/blog [PROVEN]

**GAPS:** no page body was ever fetched except jsonresume.org/schema (the only PROVEN asset); all taxonomy sizes/licences are snippet-grade and single-engine (`single_engine_only` warning on every search); the JSON Resume query returned `count: 0` so RenderCV/typst/parse-safe-PDF are NOT-IN-FILE; O*NET endpoint/auth/fields entirely absent; HF row flagged `entity_mismatch` → treat as unverified; transcript truncates before publications/skills/languages/projects/meta fields.

**NUMBERS:** 1.7.0 schema version (measured/published); 14 sections (schema's own count — marketing-ish, nav lists 15 incl. `custom`); Draft-07 (spec); 13,939 skills / 3,039 occupations ESCO v1.2.1 (**vendor/competitor-blog marketing figure**); 27 languages ESCO (third-party paper, measured); 0.80–0.90 confidence (measured in ACM paper); 7,000+ resume–vacancy pairs (measured, research); 35 O*NET occupations (measured); 15657 = `content_chars` of fetched page (measured tool output); 9000 `max_chars`, 6/8/0 result `count`, max_results 6/8, 14 & 12 hidden rows, scores 1.0/0.5/0.333/0.25/0.2/0.166/0.125/0.111/0.09/0.071/0.062 (tool telemetry, not asset facts); 2000/40/30/25 = `head`/`grep -m` limits; RFC 3986, ISO-3166-1, ISO 8601 (standards); 12345, 712-117-2923, 3.67/4.0, 2014-06-29, 2023-04, 2-3 sentences (schema examples, illustrative); #317/#316/#309/#293/#292 (schema issue refs); :54 (line number).