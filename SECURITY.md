# Security policy

```
Last verified: 2026-10-25
Reviewed by:   Ariadne (principal)
```

## Reporting a vulnerability

Open a **private** security advisory on this repository:
`https://github.com/sternnick/Ariadne/security/advisories/new`

If you cannot use advisories, open an issue containing only the sentence *"security report available
on request"* and **no details**, and a private channel will be opened. Do not put a working exploit, a
real person's data, or a credential in a public issue or PR.

**What to expect:** an acknowledgement within 7 days, an assessment within 30. This is a
single-maintainer research project; there is no bug bounty, and no SLA should be inferred beyond that.

## Scope

In scope:

* the `ariadne_ats` package — extraction, layout detection, segmentation, the evidence ledger, the JD
  extractor, the CLI;
* the gate scripts in `scripts/` (a gate that can be silently bypassed is a security issue here);
* workflows in `.github/` and the hook in `.githooks/`;
* anything that lets a document influence behaviour it should not — e.g. **indirect prompt injection
  through CV or JD text**, which is a named, benchmarked attack class ([EV-09]);

Out of scope:

* **the legal analysis in `docs/09`** — it is a research artefact about EU instruments, not advice,
  and not a security surface;
* third-party sites referenced in `docs/` (report those to their owners);
* vulnerabilities requiring a compromised local machine or an already-malicious dependency — the
  package has **no runtime dependencies** by design (`D-016`), so there is no dependency surface to
  report;
* the absence of features: no scoring exists yet, so "the score is wrong" is not a vulnerability
  (it is `docs/08` M-2).

## What this project holds

By design: **nothing about a real person.** The corpus is synthetic (`D-011`), the package makes no
network call, and no credential is required to run it. If you find real personal data in this
repository, that is a security report — treat it as one.
