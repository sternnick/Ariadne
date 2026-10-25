#!/usr/bin/env python3
"""provenance.py — bidirectional citation check (AGENT_CONTRACT C4).

Every `[Xn]` id cited in docs/**/*.md must resolve to a row in docs/SOURCES.md, and every row in
docs/SOURCES.md must be cited at least once in docs/. An uncited source is either deleted or used;
a dangling id is a hard failure. No third-party imports, no network, no writes.

Exit codes: 0 = clean, 1 = violation, 2 = usage/structure error.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
SOURCES = DOCS / "SOURCES.md"

# Ids are [PREFIX-NN]: EU-01, ISO-03, EV-24. Deliberately narrow so prose brackets like
# [HYPOTHESIS], [OPEN], [PROVEN] and markdown links never match.
ID_RE = re.compile(r"\[((?:EU|ISO|EV)-[0-9]{2})\]")
ROW_RE = re.compile(r"^\|\s*((?:EU|ISO|EV)-[0-9]{2})\s*\|", re.M)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def main() -> int:
    ap = argparse.ArgumentParser(description="Check docs <-> SOURCES.md citation integrity.")
    ap.add_argument("--docs", type=Path, default=DOCS)
    ap.add_argument("--sources", type=Path, default=SOURCES)
    ap.add_argument("-q", "--quiet", action="store_true")
    args = ap.parse_args()

    if not args.sources.is_file():
        print(f"FAIL: {args.sources} does not exist", file=sys.stderr)
        return 2
    sources_text = read(args.sources)
    registered = ROW_RE.findall(sources_text)
    if not registered:
        print("FAIL: no source rows found in SOURCES.md", file=sys.stderr)
        return 2
    dupes = {i for i in registered if registered.count(i) > 1}
    if dupes:
        print(f"FAIL: duplicate source ids in SOURCES.md: {sorted(dupes)}", file=sys.stderr)
        return 1

    cited: dict[str, list[str]] = {}
    doc_files = sorted(p for p in args.docs.rglob("*.md") if p != args.sources)
    for path in doc_files:
        for sid in ID_RE.findall(read(path)):
            cited.setdefault(sid, []).append(str(path.relative_to(ROOT)))

    known = set(registered)
    dangling = {sid: files for sid, files in cited.items() if sid not in known}
    uncited = sorted(known - set(cited))

    if not args.quiet:
        print(f"sources registered : {len(known)}")
        print(f"docs scanned       : {len(doc_files)}")
        print(f"ids cited          : {len(cited)}")
        for sid in sorted(known & set(cited)):
            print(f"  {sid:<7} <- {', '.join(sorted(set(cited[sid])))}")

    failed = False
    if dangling:
        failed = True
        print("\nFAIL: cited but not in SOURCES.md (dangling id):", file=sys.stderr)
        for sid, files in sorted(dangling.items()):
            print(f"  {sid} in {', '.join(sorted(set(files)))}", file=sys.stderr)
    if uncited:
        failed = True
        print("\nFAIL: registered but never cited in docs/ (delete it or use it):", file=sys.stderr)
        for sid in uncited:
            print(f"  {sid}", file=sys.stderr)
    if failed:
        return 1
    if not args.quiet:
        print("\nOK: bidirectional citation check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
