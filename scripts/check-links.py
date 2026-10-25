#!/usr/bin/env python3
"""check-links.py — dead-link sweep across tracked markdown (AGENT_CONTRACT C4, CI gate).

Checks **relative** links and backticked repo paths only. External URLs are the job of
scripts/check-sources.py, which is deliberately offline in CI: a build must not fail because a
third party had a bad afternoon.

What counts as a link:
  * markdown `[text](path)` where `path` is relative (not http/https/mailto/#anchor)
  * `docs/x.md`, `scripts/y.py`, `src/…`, `tests/…` inside backticks — the way our own docs
    reference files in prose

A link is *dead* if the target does not exist in the working tree. Anchor-only links (`#section`)
are ignored, and so is anything inside a fenced code block, because a code sample can legitimately
contain a path that does not exist.

Exit: 0 clean, 1 dead links found, 2 usage error.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MD_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)")
TICK_PATH = re.compile(r"`((?:docs|scripts|src|tests|data)/[A-Za-z0-9_./-]+\.[A-Za-z0-9]+)`")
FENCE = re.compile(r"```.*?```", re.S)
SKIP_PREFIX = ("http://", "https://", "mailto:", "#")

# A document may legitimately NAME a file that does not exist yet — that is how the audit and the
# ISO table record a missing artifact ("Missing artifact: `docs/aims/ai-risk-assessment.md`"). The
# marker must be on the same line as the path, so a real broken link cannot hide behind prose.
ABSENCE_MARKERS = ("Missing artifact", "not yet created", "does not exist yet", "to be written")


def tracked_markdown() -> list[Path]:
    out = subprocess.run(["git", "ls-files", "*.md"], cwd=ROOT, capture_output=True, text=True)
    if out.returncode != 0:
        return sorted(ROOT.rglob("*.md"))
    return [ROOT / line for line in out.stdout.splitlines() if line.strip()]


def main() -> int:
    ap = argparse.ArgumentParser(description="Fail on dead relative links in tracked markdown.")
    ap.add_argument("--all", action="store_true", help="scan the working tree, not just git-tracked files")
    args = ap.parse_args()

    files = sorted(ROOT.rglob("*.md")) if args.all else tracked_markdown()
    files = [f for f in files if ".git/" not in str(f) and "/.work/rescue/" not in str(f)]
    dead: list[tuple[str, str]] = []
    checked = 0

    for path in files:
        text = FENCE.sub("", path.read_text(encoding="utf-8", errors="replace"))
        targets: list[tuple[str, str]] = []  # (target, line context)
        for line in text.splitlines():
            for m in MD_LINK.finditer(line):
                t = m.group(1).split("#", 1)[0]
                if t and not t.startswith(SKIP_PREFIX):
                    targets.append((t, line))
            for t in TICK_PATH.findall(line):
                targets.append((t, line))
        for t, line in targets:
            t = t.rstrip(".,;:)")
            if not t:
                continue
            if any(marker in line for marker in ABSENCE_MARKERS):
                continue
            checked += 1
            candidate = (path.parent / t) if not t.startswith("/") else (ROOT / t.lstrip("/"))
            if not (candidate.exists() or (ROOT / t).exists()):
                dead.append((str(path.relative_to(ROOT)), t))

    print(f"scanned {len(files)} markdown file(s), {checked} relative link target(s)")
    if dead:
        print("\nDEAD LINKS:", file=sys.stderr)
        for src, t in dead:
            print(f"  {src} -> {t}", file=sys.stderr)
        return 1
    print("OK: no dead relative links.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
