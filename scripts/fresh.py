#!/usr/bin/env python3
"""fresh.py — freshness table for docs/ (AGENT_CONTRACT C3 + C4).

Every doc that carries claims must declare, in its first lines:

    Last verified: YYYY-MM-DD
    Reviewed by:   <agent|person>

Two clocks apply:
  * 90 days — the general staleness rule (C3.3).
  * 30 days — for claims about live third-party surfaces: prices, plan tiers, star counts,
    vendor behaviour, schema versions, endpoints (C3.4). A doc opts into the short clock by
    naming such a surface in its `Live surfaces:` line, e.g.

        Live surfaces: vendor pricing, GitHub star counts

Exit codes: 0 = all fresh and well-formed, 1 = a doc is stale or missing its header,
2 = usage/structure error. `--strict` also fails a doc that is merely *near* stale (>=80%).

No third-party imports. No network. Read-only.
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
GENERAL_DAYS = 90
LIVE_DAYS = 30
NEAR = 0.8

DATE_RE = re.compile(r"^Last verified:\s*(\d{4}-\d{2}-\d{2})\s*$", re.M)
REVIEWED_RE = re.compile(r"^Reviewed by:\s*(\S.{0,80}?)\s*$", re.M)
LIVE_RE = re.compile(r"^Live surfaces:\s*(.+?)\s*$", re.M)


def parse_header(text: str) -> tuple[dt.date | None, str | None, str | None]:
    d = DATE_RE.search(text)
    r = REVIEWED_RE.search(text)
    live = LIVE_RE.search(text)
    date = None
    if d:
        try:
            date = dt.date.fromisoformat(d.group(1))
        except ValueError:
            date = None
    return date, (r.group(1) if r else None), (live.group(1) if live else None)


def main() -> int:
    ap = argparse.ArgumentParser(description="Report doc freshness and enforce the C3 clocks.")
    ap.add_argument("--docs", type=Path, default=DOCS)
    ap.add_argument("--today", type=str, default=None, help="override today (YYYY-MM-DD), for tests")
    ap.add_argument("--strict", action="store_true", help="also fail docs at >=80%% of their clock")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    today = dt.date.fromisoformat(args.today) if args.today else dt.date.today()
    if not args.docs.is_dir():
        print(f"FAIL: {args.docs} is not a directory", file=sys.stderr)
        return 2

    rows, bad = [], []
    for path in sorted(args.docs.rglob("*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        date, reviewer, live = parse_header(text)
        rel = str(path.relative_to(ROOT))
        if date is None or reviewer is None:
            bad.append((rel, "missing " + ("Last verified" if date is None else "Reviewed by")))
            rows.append((rel, str(date or "—"), "—", "—", "NO HEADER", live or ""))
            continue
        age = (today - date).days
        clock = LIVE_DAYS if live else GENERAL_DAYS
        stale = age > clock
        near = (not stale) and age >= clock * NEAR
        if stale:
            bad.append((rel, f"stale: {age}d > {clock}d clock"))
        elif near and args.strict:
            bad.append((rel, f"near-stale: {age}d of {clock}d"))
        rows.append((rel, date.isoformat(), str(age), f"{clock}d", "STALE" if stale else ("near" if near else "fresh"), live or ""))

    if not args.quiet:
        w = [max(len(r[i]) for r in rows + [("file", "last verified", "age", "clock", "state", "live surfaces")]) for i in range(6)]
        hdr = ("file", "last verified", "age", "clock", "state", "live surfaces")
        print("  ".join(h.ljust(w[i]) for i, h in enumerate(hdr)))
        print("  ".join("-" * w[i] for i in range(6)))
        for r in rows:
            print("  ".join(str(c).ljust(w[i]) for i, c in enumerate(r)))
        print(f"\ntoday: {today.isoformat()}  docs: {len(rows)}  general clock: {GENERAL_DAYS}d  live clock: {LIVE_DAYS}d")

    if bad:
        print("", file=sys.stderr)
        for rel, why in bad:
            print(f"FAIL {rel}: {why}", file=sys.stderr)
        return 1
    if not args.quiet:
        print("OK: every doc is dated, attributed and within its clock.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
