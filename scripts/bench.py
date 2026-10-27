#!/usr/bin/env python3
"""bench.py: run the gold benchmark and fail on a regression (docs/08 M-1, M-2 half).

    python scripts/bench.py                 # table + verdict
    python scripts/bench.py --json          # machine-readable report
    python scripts/bench.py --write         # refresh data/gold/results.json (the published artefact)
    python scripts/bench.py --check         # compare against data/gold/thresholds.json and exit 1 on
                                            # any field whose recall or precision dropped below the
                                            # recorded floor, or on any forbidden-value emission

Why a *gate* and not just a report: a number nobody compares against is a number that silently
decays. `thresholds.json` is a ratchet: each entry sits a little under what was last measured, so an
improvement passes and a regression stops the build. Edit it deliberately, in the commit that explains
why, never to make a red build green (AGENT_CONTRACT C2.4).

Exit codes: 0 within thresholds, 1 regression or forbidden emission or broken fixture, 2 usage error.
No third-party imports, no network. Deterministic: same tree, same numbers.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from ariadne_ats import bench  # noqa: E402

RESULTS = ROOT / "data" / "gold" / "results.json"
THRESHOLDS = ROOT / "data" / "gold" / "thresholds.json"


def table(report: dict) -> str:
    out = [f"gold corpus: {report['accuracy']['fixtures']} fixtures, "
           f"languages {' '.join(report['corpus']['languages'])}"]
    out.append("")
    out.append("field-level extraction accuracy (micro-averaged over the corpus)")
    out.append(f"  {'field':<10} {'tp':>4} {'fp':>4} {'fn':>4} {'precision':>10} {'recall':>8} "
               f"{'f1':>6} {'exact':>6}")
    for field_name, s in report["accuracy"]["fields"].items():
        out.append(f"  {field_name:<10} {s['tp']:>4} {s['fp']:>4} {s['fn']:>4} {s['precision']:>10.3f} "
                   f"{s['recall']:>8.3f} {s['f1']:>6.3f} {s['exact_match_fixtures']:>3}/{s['fixtures']}")
    out.append("")
    out.append("per language (recall / precision)")
    for lang, fields in report["accuracy"]["languages"].items():
        row = "  " + f"{lang:<4}"
        for k in ("employer", "title", "date", "skill", "contact"):
            row += f"  {k[:4]} {fields[k]['recall']:.2f}/{fields[k]['precision']:.2f}"
        out.append(row)
    out.append("")
    out.append("requirement weighting in job descriptions")
    jd = report["jd"]
    out.append(f"  {jd['fixtures']} fixtures; weights expected {jd['expected_weights']} "
               f"actual {jd['actual_weights']}; cue accuracy {jd['weight_cue_accuracy']}, "
               f"fixtures exactly matching {jd['fixtures_exactly_matching']}")
    out.append("")
    out.append("stability under competence-preserving perturbation")
    out.append(f"  anchor advertisement: {report['stability']['anchor_jd']}")
    out.append(f"  {'transform':<24} {'n':>3} {'competence kept':>16} {'fact retention':>15} "
               f"{'max |dcos|':>11} {'rank inversion':>15}")
    for name, t in report["stability"]["transforms"].items():
        out.append(f"  {name:<24} {t['fixtures_applied']:>3} "
                   f"{str(t['competence_preserved_all']):>16} {str(t['mean_fact_retention']):>15} "
                   f"{t['max_abs_cosine_delta']:>11} {str(t['ranking_inversion_rate']):>15}")
        if t["broken_fixtures"]:
            out.append(f"      fixture bug (competence changed, so the transform is wrong, not the parser): "
                       f"{', '.join(t['broken_fixtures'])}")
    viol = report["accuracy"]["forbidden_violations"]
    out.append("")
    out.append(f"forbidden emissions (values that must never be emitted): {len(viol)}")
    for v in viol[:20]:
        out.append(f"  {v}")
    misses = {k: s["misses"] for k, s in report["accuracy"]["fields"].items() if s["misses"]}
    if misses:
        out.append("")
        out.append("what was missed, by field (first 8 each)")
        for k, v in misses.items():
            out.append(f"  {k}: " + ", ".join(v[:8]) + (f" (+{len(v) - 8} more)" if len(v) > 8 else ""))
    return "\n".join(out)


def check(report: dict, thresholds_path: Path) -> tuple[list[str], list[str]]:
    """Compare the report to the ratchet. Returns (failures, notes)."""
    if not thresholds_path.is_file():
        return [f"{thresholds_path.relative_to(ROOT)} is missing; the gate cannot be vacuous"], []
    floors = json.loads(thresholds_path.read_text(encoding="utf-8"))
    fails: list[str] = []
    notes: list[str] = []
    for field_name, floor in floors.get("fields", {}).items():
        s = report["accuracy"]["fields"].get(field_name)
        if s is None:
            fails.append(f"{field_name}: no such field in the report")
            continue
        for key in ("precision", "recall"):
            if key in floor and s[key] < floor[key]:
                fails.append(f"{field_name}.{key} {s[key]:.3f} < floor {floor[key]:.3f}")
    stability = floors.get("stability", {})
    for name, rule in stability.items():
        t = report["stability"]["transforms"].get(name)
        if t is None:
            fails.append(f"stability.{name}: transform gone from perturb.TRANSFORMS")
            continue
        if t["broken_fixtures"]:
            fails.append(f"stability.{name}: competence changed in "
                         f"{', '.join(t['broken_fixtures'])} - the transform is not competence-preserving")
        if rule.get("fact_retention_min") is not None and t["mean_fact_retention"] is not None:
            if t["mean_fact_retention"] < rule["fact_retention_min"]:
                fails.append(f"stability.{name}.fact_retention {t['mean_fact_retention']} < "
                             f"{rule['fact_retention_min']}")
        if rule.get("ranking_inversion_rate_max") is not None:
            if (t["ranking_inversion_rate"] or 0) > rule["ranking_inversion_rate_max"]:
                fails.append(f"stability.{name}.ranking_inversion_rate "
                             f"{t['ranking_inversion_rate']} > {rule['ranking_inversion_rate_max']}")
    if report["accuracy"]["forbidden_violations"] and floors.get("forbidden_violations_max", 0) == 0:
        fails.append(f"{len(report['accuracy']['forbidden_violations'])} forbidden emission(s): "
                     + "; ".join(report["accuracy"]["forbidden_violations"][:5]))
    for note in floors.get("known_gaps", []):
        notes.append(str(note))
    return fails, notes


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Run the gold benchmark.")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write", action="store_true", help=f"write {RESULTS.relative_to(ROOT)}")
    ap.add_argument("--check", action="store_true", help=f"enforce {THRESHOLDS.relative_to(ROOT)}")
    ap.add_argument("--seed-thresholds", action="store_true", help=argparse.SUPPRESS)
    args = ap.parse_args(argv)

    try:
        report = bench.full_report()
    except ValueError as e:
        print(f"FAIL: {e}", file=sys.stderr)
        return 2

    if args.seed_thresholds:
        floors = {"comment": "ratchet floors, seeded from the first measurement; see the file header "
                             "in scripts/bench.py for the rule",
                  "forbidden_violations_max": 0,
                  "fields": {k: {"precision": round(s["precision"] - 0.02, 3),
                                 "recall": round(s["recall"] - 0.02, 3)}
                             for k, s in report["accuracy"]["fields"].items()},
                  "stability": {k: {"fact_retention_min": round((v["mean_fact_retention"] or 1) - 0.02, 3),
                                    "ranking_inversion_rate_max": round((v["ranking_inversion_rate"] or 0) + 0.02, 3)}
                                for k, v in report["stability"]["transforms"].items()},
                  "known_gaps": []}
        THRESHOLDS.write_text(json.dumps(floors, indent=2) + "\n", encoding="utf-8")
        print(f"seeded {THRESHOLDS.relative_to(ROOT)}")
        return 0

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(table(report))

    if args.write:
        report["generated"] = {"utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                              "command": "python scripts/bench.py --write",
                              "note": "deterministic given the tree; the timestamp records when the "
                                      "published artefact was refreshed, not a claim about the parser"}
        RESULTS.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"\nwrote {RESULTS.relative_to(ROOT)}", file=sys.stderr)

    if args.check:
        fails, notes = check(report, THRESHOLDS)
        print()
        for n in notes:
            print(f"note: {n}")
        if fails:
            for f in fails:
                print(f"FAIL {f}", file=sys.stderr)
            print("\nThe benchmark gate measures extraction quality; a red run means the parser got "
                  "worse, not that a claim lost its citation.", file=sys.stderr)
            return 1
        print("OK: every field is at or above its recorded floor; no forbidden emission.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
