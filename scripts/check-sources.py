#!/usr/bin/env python3
"""check-sources.py — re-probe every URL registered in docs/SOURCES.md (AGENT_CONTRACT C4, C6.3).

Design decisions that are deliberate, not incidental:

* **Offline by default.** The recorded status is printed and compared; nothing is fetched unless
  `--probe` is passed. Reason: our pre-push path must not depend on third parties (a single expired
  key blocked every push once — issue #204 in the parent project). `--probe` is a manual/CI-cron
  action, never a commit hook.
* **One request per URL per run, per host serialised.** A 403/401 is recorded as `walled`, never as
  `dead`: a wall is a rung in the fetch ladder, not an absence (C6.3).
* **Content-length delta and body-hash prefix** are recorded, so "the page is still there but now
  says something else" is detectable — a silently rewritten pricing page is a silent fact change.
* **404/410 → `dead`, 401/403/429/5xx → `walled`, timeout/DNS → `unreachable`.** The four are
  different facts and the JSON keeps them apart.

Writes: docs/source-status.json (committed; this is the "since last check" baseline).
Exit codes: 0 = all ok or unchanged, 1 = a registered source is dead/unreachable, 2 = usage error.
No third-party imports.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import ssl
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "docs" / "SOURCES.md"
STATUS = ROOT / "docs" / "source-status.json"

URL_RE = re.compile(r"https?://[^\s|<>)\]]+")
# The probe manifest is a plain "ID  URL" line block (NOT a markdown table row), so that a URL
# lives next to its id without duplicating the source row that scripts/provenance.py counts.
MANIFEST_RE = re.compile(r"^((?:EU|ISO|EV)-[0-9]{2})[ \t]+(https?://\S+|local:\S+)\s*$", re.M)
REGISTERED_RE = re.compile(r"^\|\s*((?:EU|ISO|EV)-[0-9]{2})\s*\|", re.M)
UA = "Mozilla/5.0 (X11; Linux x86_64) ariadne-source-check/1.0 (+docs/SOURCES.md)"


def urls_by_id(text: str) -> dict[str, list[str]]:
    """Read the probe manifest. A source with no manifest line is a defect, not a skip."""
    out: dict[str, list[str]] = {}
    for sid, url in MANIFEST_RE.findall(text):
        out.setdefault(sid, []).append(url.rstrip(".,;"))
    return out


def classify(code: int | None, err: str | None) -> str:
    if err:
        low = err.lower()
        if "timed out" in low or "timeout" in low:
            return "unreachable"
        if "not known" in low or "name or service" in low or "nodename" in low:
            return "unreachable"
        return "unreachable"
    if code in (404, 410):
        return "dead"
    if code in (401, 403, 407, 429) or (code is not None and 500 <= code < 600):
        return "walled"
    if code is not None and 200 <= code < 400:
        return "ok"
    return "walled"


def probe_local(rel: str) -> dict:
    """In-repo artifact: cannot 404 over the network, but it CAN be deleted from the tree."""
    path = ROOT / rel
    if path.is_file():
        return {"http": None, "kind": "ok", "bytes_read": path.stat().st_size, "sha256_64k": None,
                "elapsed_s": 0.0, "error": None}
    return {"http": None, "kind": "dead", "bytes_read": 0, "sha256_64k": None, "elapsed_s": 0.0,
            "error": f"missing local artifact: {rel}"}


def probe(url: str, timeout: float) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/pdf,*/*"})
    ctx = ssl.create_default_context()
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            body = r.read(65536)
            return {
                "http": int(getattr(r, "status", 0) or 0),
                "kind": classify(int(getattr(r, "status", 0) or 0), None),
                "bytes_read": len(body),
                "sha256_64k": hashlib.sha256(body).hexdigest()[:16],
                "elapsed_s": round(time.time() - t0, 2),
                "error": None,
            }
    except urllib.error.HTTPError as e:
        return {"http": int(e.code), "kind": classify(int(e.code), None), "bytes_read": 0,
                "sha256_64k": None, "elapsed_s": round(time.time() - t0, 2), "error": f"HTTP {e.code}"}
    except Exception as e:  # noqa: BLE001 - every failure must be recorded, never swallowed
        return {"http": None, "kind": classify(None, str(e)), "bytes_read": 0,
                "sha256_64k": None, "elapsed_s": round(time.time() - t0, 2), "error": str(e)[:200]}


def main() -> int:
    ap = argparse.ArgumentParser(description="Re-probe the sources registered in docs/SOURCES.md.")
    ap.add_argument("--probe", action="store_true", help="actually fetch (default: report recorded state)")
    ap.add_argument("--timeout", type=float, default=20.0)
    ap.add_argument("--only", default=None, help="comma-separated source ids to probe")
    ap.add_argument("--write", action="store_true", help="update docs/source-status.json")
    args = ap.parse_args()

    if not SOURCES.is_file():
        print(f"FAIL: {SOURCES} does not exist", file=sys.stderr)
        return 2
    text = SOURCES.read_text(encoding="utf-8", errors="replace")
    registered = urls_by_id(text)
    declared = set(REGISTERED_RE.findall(text))
    # A registered source with no manifest line would otherwise be silently un-probeable — the
    # "skipped sources never print READY" failure. It is a defect and it fails the run.
    unprobeable = sorted(declared - set(registered))
    ghosts = sorted(set(registered) - declared)  # manifest line for a source with no row
    prev = json.loads(STATUS.read_text()) if STATUS.is_file() else {}
    only = {s.strip() for s in args.only.split(",")} if args.only else None

    if unprobeable:
        print("FAIL: registered but not probeable (no manifest line): " + ", ".join(unprobeable),
              file=sys.stderr)
        return 1
    if ghosts:
        print("FAIL: manifest entry with no SOURCES.md row (delete it or register it): "
              + ", ".join(ghosts), file=sys.stderr)
        return 1

    if not args.probe:
        print(f"{'id':<7} {'kind':<12} {'http':<5} url")
        for sid in sorted(registered):
            for url in registered[sid]:
                rec = prev.get(sid, {}).get(url, {})
                print(f"{sid:<7} {rec.get('kind', 'unprobed'):<12} {str(rec.get('http') or '—'):<5} {url[:110]}")
        print("\nrecorded state only. Pass --probe to fetch (one request per URL, serialised).")
        return 0

    out: dict = dict(prev)
    failures: list[tuple[str, str, str]] = []
    for sid in sorted(registered):
        if only and sid not in only:
            continue
        out.setdefault(sid, {})
        for url in registered[sid]:
            res = probe_local(url[6:]) if url.startswith("local:") else probe(url, args.timeout)
            old = prev.get(sid, {}).get(url)
            delta = ""
            if old and old.get("bytes_read") and res.get("bytes_read"):
                d = res["bytes_read"] - old["bytes_read"]
                if d:
                    delta = f"  len {d:+d}"
            changed = old and old.get("sha256_64k") and res.get("sha256_64k") and old["sha256_64k"] != res["sha256_64k"]
            print(f"{sid:<7} {res['kind']:<12} {str(res['http'] or '—'):<5} {url[:96]}{delta}{'  CONTENT-CHANGED' if changed else ''}")
            if res["kind"] in ("dead", "unreachable"):
                failures.append((sid, url, res.get("error") or res["kind"]))
            out[sid][url] = res
            if not url.startswith("local:"):
                time.sleep(1.0)  # never hammer: one request per second across all hosts

    if args.write:
        STATUS.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"\nwrote {STATUS.relative_to(ROOT)}")

    if failures:
        print("\nSources that are dead/unreachable — their claims keep their grade only for the time",
              "they were read, and may not support a new claim until re-sourced (C6.3):", file=sys.stderr)
        for sid, url, err in failures:
            print(f"  {sid} {err}  {url}", file=sys.stderr)
        return 1
    print("\nOK: every probed source answered (walls counted as answers, not absences).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
