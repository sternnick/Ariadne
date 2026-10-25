"""A structural test for the claim that Ariadne does not profile a natural person.

WHY THIS IS A TEST AND NOT A PROMISE
------------------------------------
Regulation (EU) 2024/1689, Annex III, point 4(a) covers AI systems "intended to be used for the
recruitment or selection of natural persons, in particular … to analyse and filter job applications,
and to evaluate candidates". Art. 6(2) makes Annex III systems high-risk, and Art. 6(3) offers a
derogation for narrow/improving/preparatory tasks — but the final subparagraph of Art. 6(3) closes
it absolutely:

    "Notwithstanding the first subparagraph, an AI system referred to in Annex III shall always be
     considered to be high-risk where the AI system performs profiling of natural persons."

So a tailoring tool that infers *characteristics of the person* (potential, aptitude, personality,
seniority "read between the lines", culture fit, emotion, demographic attributes) would be
high-risk per se, and no amount of human review would cure it: WP251rev.01 says "human involvement
does not necessarily take the activity out of the [profiling] definition" (§II). See
docs/09-eu-legal-compliance.md §1.2 for the full analysis and [EU-01]/[EU-10] for the texts.

DOES SCORING FIT-TO-JD COUNT AS PROFILING?
------------------------------------------
This is the honest boundary case, and the answer is not a slogan.

GDPR Art. 4(4) defines profiling as automated processing used "to evaluate certain personal aspects
relating to a natural person, in particular to analyse or predict aspects concerning that natural
person's performance at work, economic situation, health, personal preferences, interests,
reliability, behaviour, location or movements". A *match score between a CV and a job description*
is uncomfortably close to "evaluating performance at work" if it is read as a judgement about the
person.

The distinction this project relies on — and which this test enforces structurally — is:

  * We compute a **document-similarity measurement**: lexical overlap (TF-IDF cosine) and term
    presence between two texts the user supplied. Its inputs are the user's own document and the
    user's chosen advertisement; its output is a number plus the *terms* that produced it.
  * We do **not** infer, predict or store any attribute of the person (no traits, no potential, no
    demographics, no emotion, no seniority inference beyond literal tokens), and we do not produce
    a candidate evaluation for a selecting party.

That keeps the output on the "measurement of documents" side of the line rather than the
"evaluation of a person" side. It is a design position, not a court ruling: if we ever ship
person-level inference, this test is the thing that should fail loudly *before* the product does.

The second half of the legal exposure is Art. 3(12) (intended purpose): classification follows what
we say the system is for, "as specified in the instructions for use, promotional or sales materials
and statements, as well as in the technical documentation". So the test also asserts that the
declared purpose statement still says what we think it says — a marketing rewrite that drifts the
purpose is a classification change, and it should break the build, not a lawyer's afternoon.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "ariadne_ats"
LEGAL = ROOT / "docs" / "09-eu-legal-compliance.md"

# Tokens that would indicate person-level inference rather than document measurement. Kept as
# whole-word matches so "age" does not fire on "package"/"language" and "race" does not fire on
# "trace"/"brace".
BANNED_INFERENCE = [
    "personality", "aptitude", "temperament", "emotional intelligence", "eq_score",
    "culture fit", "culture_fit", "culturefit", "potential_score", "promotability",
    "leadership_potential", "flight risk", "flightrisk", "reliability_score",
    "emotion", "sentiment_score", "affect_score", "deception", "trustworthiness",
    "ethnicity", "ethnic", "race", "racial", "gender", "sex", "religion", "religious",
    "disability", "disabled", "pregnancy", "marital", "nationality", "age", "birth",
    "health", "diagnosis", "sexual_orientation", "photo_score", "attractiveness",
]

# A person-level judgement API would look like this. We assert none exists.
BANNED_CALLABLES = [
    "assess_candidate", "score_candidate", "rank_candidates", "evaluate_person",
    "infer_traits", "predict_performance", "profile_person", "score_person",
]


def python_files() -> list[Path]:
    files = sorted(SRC.rglob("*.py"))
    assert files, f"no source files found under {SRC}"
    return files


def code_only(path: Path) -> str:
    """Strip docstrings and comments: the words may appear in a legal explanation, but a
    docstring that *names* a banned concept is not an implementation of it."""
    text = path.read_text(encoding="utf-8")
    text = re.sub(r'"""[\s\S]*?"""', "", text)
    text = re.sub(r"'''[\s\S]*?'''", "", text)
    text = re.sub(r"#[^\n]*", "", text)
    return text


def test_no_person_attribute_inference_in_code():
    hits = []
    for path in python_files():
        code = code_only(path).lower()
        for token in BANNED_INFERENCE:
            pattern = r"\b" + re.escape(token.replace("_", "[_ ]")) + r"\b"
            if re.search(pattern, code):
                hits.append(f"{path.relative_to(ROOT)}: {token}")
    assert not hits, (
        "Person-attribute inference found in code. That is profiling (GDPR Art. 4(4)) and, for an "
        "Annex III system, forecloses the Art. 6(3) derogation absolutely (Reg. 2024/1689 Art. 6(3) "
        "final subparagraph):\n  " + "\n  ".join(hits)
    )


def test_no_person_level_scoring_api():
    names = []
    for path in python_files():
        code = code_only(path)
        for token in BANNED_CALLABLES:
            if re.search(r"\bdef\s+" + re.escape(token) + r"\b", code):
                names.append(f"{path.relative_to(ROOT)}: def {token}")
    assert not names, (
        "A person-level scoring callable exists. Ariadne measures a document against an "
        "advertisement; it must not evaluate a person:\n  " + "\n  ".join(names)
    )


def test_scoring_surface_is_text_similarity_only():
    """The one comparative surface that exists today must stay term-based and inspectable."""
    import sys

    sys.path.insert(0, str(ROOT / "src"))
    from ariadne_ats.lexical import Tfidf  # noqa: PLC0415 - intentional: import under test

    tf = Tfidf(["machine learning python docker", "docker kubernetes pipelines data"])
    result = tf.compare("python docker pipelines", "machine learning kubernetes")

    allowed = {"cosine", "shared_terms", "contributions", "missing_from_a", "terms_a", "terms_b"}
    assert set(result) <= allowed, f"compare() grew a non-similarity field: {set(result) - allowed}"
    assert 0.0 <= result["cosine"] <= 1.0
    assert all(isinstance(t, str) for t in result["shared_terms"])
    assert all(isinstance(v, float) for v in result["contributions"].values())
    # It must explain itself in words, not in a verdict about a human.
    for term in result["shared_terms"] + result["missing_from_a"]:
        assert re.fullmatch(r"[a-z0-9][a-z0-9.+#/ -]*", term), f"non-literal term: {term!r}"


def test_declared_purpose_still_carries_the_no_profiling_constraint():
    """Art. 3(12): intended purpose is fixed by what we *say*. Guard the sentence that says it."""
    assert LEGAL.is_file(), "docs/09-eu-legal-compliance.md is the classification instrument; missing"
    text = LEGAL.read_text(encoding="utf-8")
    required = [
        "always be considered to be high-risk where the AI system performs profiling",
        "does not evaluate personal aspects of the person",
        "Annex III, point 4(a)",
    ]
    missing = [r for r in required if r not in text]
    assert not missing, (
        "The intended-purpose / no-profiling statement changed. Classification follows our own "
        "documentation (Reg. 2024/1689 Art. 3(12)), so this is a legal change, not an editorial "
        "one. Restore the statement or record a new classification assessment (Art. 6(4)):\n  "
        + "\n  ".join(missing)
    )


def identifiers_only(path: Path) -> str:
    """Names, not prose and not data. 'profile' is a legitimate CV *section name* (and is in
    SECTION_HEADINGS); an identifier called profile_* is a different thing entirely."""
    code = code_only(path)
    code = re.sub(r'"[^"\n]*"', "", code)      # drop string literals
    code = re.sub(r"'[^'\n]*'", "", code)
    return code


@pytest.mark.parametrize("word", ["profile", "profiling", "profil"])
def test_no_person_profiling_identifier(word: str):
    """An identifier that names person-profiling is the first sign of scope creep."""
    hits = []
    for path in python_files():
        code = identifiers_only(path)
        for m in re.finditer(r"\b(?:def|class)\s+([A-Za-z_]*)", code):
            if word in m.group(1).lower():
                hits.append(f"{path.relative_to(ROOT)}: {m.group(0).strip()}")
            # module-level function/variable names
        for m in re.finditer(r"\b([A-Za-z_]*(?:profile|profil)[A-Za-z_]*)\s*=", code):
            hits.append(f"{path.relative_to(ROOT)}: {m.group(1)} =")
    assert not hits, (
        "Ariadne must not implement person profiling (Reg. 2024/1689 Art. 6(3) final subparagraph; "
        "GDPR Art. 4(4)). If this is deliberate it needs an Art. 6(4) assessment first:\n  "
        + "\n  ".join(sorted(set(hits)))
    )
