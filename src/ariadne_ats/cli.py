"""Command-line entry point: `ariadne`.

Scope discipline: this CLI exposes only what the package actually does today — text
normalisation, tokenisation, section detection, and a TF-IDF comparison with term-level
evidence. It deliberately has no "score my CV" command, because Ariadne does not yet
produce a score and a CLI flag that pretends otherwise would be a stub (AGENT_CONTRACT
C7.7) and, worse, a user-facing claim (C8).

Exit codes: 0 success, 1 usage/data error, 2 internal error.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .evidence import build_ledger
from .jd import build_jd
from .lexical import Tfidf
from .layout import analyze as analyze_layout
from .segment import segment as segment_sections
from .textutil import normalize, tokenize

# CLI-level stop list. NOT a claim about what an ATS filters: it exists so that `compare` does not
# answer with "the / is / and". Any real stop list is corpus-dependent and belongs to A1.
_STOP = set("""a an and are as at be been but by for from has have he her his i if in into is it its
of on or our she that the their them then there these they this to was we were what when which who
will with you your""".split())


def _read(path: str) -> str:
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(path)
    return p.read_text(encoding="utf-8", errors="replace")


def cmd_inspect(args: argparse.Namespace) -> int:
    raw = _read(args.file)
    text = normalize(raw)
    sections_list = segment_sections(text, analyze_layout(raw)[1])
    sections = {s.kind: s.body for s in sections_list}
    out = {
        "file": args.file,
        "characters": len(text),
        "tokens": len(tokenize(text)),
        "sections": {k: len(v.splitlines()) for k, v in sections.items()},
        "heads": sorted(sections),
        "columns_suspected": analyze_layout(raw)[0].columns_suspected,
        "note": (
            "columns_suspected comes from ariadne_ats.layout on the RAW extraction: tabs and runs "
            "of 3+ spaces are the signal, and normalize() destroys both, which is why the detector "
            "runs first (audit P3)."
        ),
    }
    print(json.dumps(out, indent=2))
    return 0


def cmd_parse(args: argparse.Namespace) -> int:
    """Extract, detect layout damage, segment, and emit the evidence ledger."""
    led = build_ledger(args.file)
    if args.json:
        import json as _json

        print(_json.dumps(led.to_resume_json(), indent=2))
        return 0
    print(json_summary(led.summary()))
    return 0


def json_summary(d: dict) -> str:
    import json as _json

    return _json.dumps(d, indent=2)


def cmd_jd(args: argparse.Namespace) -> int:
    text = _read(args.file)
    doc = build_jd(text, source=Path(args.file).name).to_jd_json()
    print(json_summary(doc) if args.json else json_summary(doc["custom"]["ariadne.provenance"]))
    return 0


def cmd_compare(args: argparse.Namespace) -> int:
    a, b = _read(args.a), _read(args.b)
    tf = Tfidf(stop=_STOP)
    result = tf.compare(normalize(a), normalize(b), top=args.top)
    result["note"] = (
        "Document similarity only: cosine over TF-IDF terms. No background corpus is shipped, so "
        "IDF carries no market signal in the two-document case (docs/00-audit.md P7). This is not "
        "a score, an ATS verdict, or a prediction."
    )
    print(json.dumps(result, indent=2))
    return 0


def cmd_bench(args: argparse.Namespace) -> int:
    """Score the parser against data/gold/. The subject of the measurement is the software."""
    from . import bench as _bench

    report = _bench.full_report()
    if args.json:
        print(json.dumps(report, indent=2))
        return 0
    acc = report["accuracy"]["fields"]
    print(json.dumps({"corpus": report["corpus"]["fixtures"], "fields": {
        k: {"precision": v["precision"], "recall": v["recall"], "f1": v["f1"]}
        for k, v in acc.items()}}, indent=2))
    print("Measured on the synthetic gold corpus only (data/gold/manifest.json); these are not "
          "accuracy figures for any real CV, and the corpus was written by the same session that "
          "wrote the rules. See docs/02 2.6.", file=sys.stderr)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="ariadne",
        description="Ariadne — transparent, dependency-free measurement of how a parser reads a CV.",
    )
    p.add_argument("--version", action="version", version=f"ariadne {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    i = sub.add_parser("inspect", help="normalise a document and report tokens and sections")
    i.add_argument("file")
    i.set_defaults(func=cmd_inspect)

    p2 = sub.add_parser("parse", help="parse a document into the evidence ledger")
    p2.add_argument("file")
    p2.add_argument("--json", action="store_true", help="emit the full JSON Resume document")
    p2.set_defaults(func=cmd_parse)

    j = sub.add_parser("jd", help="extract requirements from a job description")
    j.add_argument("file")
    j.add_argument("--json", action="store_true", help="emit the full jd.json document")
    j.set_defaults(func=cmd_jd)

    b = sub.add_parser("bench", help="score the parser against data/gold/ (the software, not a CV)")
    b.add_argument("--json", action="store_true", help="full machine-readable report")
    b.set_defaults(func=cmd_bench)

    c = sub.add_parser("compare", help="TF-IDF cosine similarity between two documents, with evidence")
    c.add_argument("a")
    c.add_argument("b")
    c.add_argument("--top", type=int, default=20)
    c.set_defaults(func=cmd_compare)
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except FileNotFoundError as e:
        print(f"ariadne: no such file: {e}", file=sys.stderr)
        return 1
    except Exception as e:  # noqa: BLE001 - visible failure, never a silent exit 0 (C7.7)
        print(f"ariadne: {type(e).__name__}: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
