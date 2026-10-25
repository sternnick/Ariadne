"""ariadne_ats — the Ariadne package (renamed from `ats_research` 2026-10-25, D-015).

Honest public surface. Everything exported here exists and is importable.

Implemented:
    textutil.normalize / tokenize / content_words / sentences / ngrams
    textutil.bullets_of / detect_sections / heading_of / looks_multicolumn
    lexical.Tfidf (fit / vector / cosine / compare), jaccard, overlap_coefficient

Not implemented yet -- deliberately NOT imported, because importing names that do not
exist made `import ats_research` (now `ariadne_ats`) raise (fixed 2026-10-25, see docs/00-audit.md A-7):
    parse_resume, parse_job, Resume, Role, JobDescription      -> A1
    score, ScoreResult, lint, Finding                            -> A2
    propose, Proposal, Fact, check_support, SupportReport        -> A3
    HashingEmbedder, OpenAICompatibleEmbedder                    -> A2/A3

Known limitations of what is here are stated in each module's docstrings, and are
itemised with measurements in docs/00-audit.md section A.
"""
from . import errors, evidence, extract, jd, layout, lexical, perturb, segment, textutil
from .errors import Code, ParseFailure, ParseIssue, ParseReport, Severity
from .evidence import Fact, Ledger, LedgerDelta, build_ledger
from .extract import Extraction, extract as extract_text
from .jd import JobDescription, Requirement, build_jd
from .layout import LayoutReport, analyze as analyze_layout
from .lexical import Tfidf, jaccard, overlap_coefficient
from .segment import Section, segment as segment_sections
from .textutil import content_words, ngrams, normalize, sentences, term_frequencies, tokenize

__all__ = [
    "textutil", "lexical", "extract", "layout", "segment", "evidence", "jd", "perturb", "errors",
    "Tfidf", "jaccard", "overlap_coefficient",
    "Code", "Severity", "ParseIssue", "ParseFailure", "ParseReport",
    "Fact", "Ledger", "LedgerDelta", "build_ledger",
    "Extraction", "extract_text", "LayoutReport", "analyze_layout",
    "Section", "segment_sections", "JobDescription", "Requirement", "build_jd",
    "normalize", "tokenize", "content_words", "sentences", "ngrams", "term_frequencies",
]
__version__ = "0.1.0"

# `cli` is importable but not imported here, so `import ariadne_ats` stays free of argparse.
# The console entry point resolves it directly: ariadne_ats.cli:main.
