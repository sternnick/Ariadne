"""A validate-against-schema test that does not need the `jsonschema` package.

The schemas are shipped as artifacts (they are the interface a caller codes against), so they must be
tested — but adding `jsonschema` as a dependency to check our own output would be the tail wagging the
dog (`D-016`). This module implements the small, well-defined subset the schemas use: `type`,
`required`, `properties`, `items`, `enum`, `minimum`, `exclusiveMinimum`, `maximum`, `minLength`,
`additionalProperties` (ignored, i.e. permissive). Anything the schemas grow beyond that subset must
extend this validator — deliberately, in the same change.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS = ROOT / "schemas"

_TYPES = {
    "object": dict,
    "array": list,
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "null": type(None),
}


def _type_ok(value, spec) -> bool:
    names = spec if isinstance(spec, list) else [spec]
    for name in names:
        expected = _TYPES.get(name)
        if expected is None:
            continue
        if name == "integer" and isinstance(value, bool):
            continue
        if isinstance(value, expected):
            return True
    return False


def validate(instance, schema: dict, path: str = "$") -> list[str]:
    errors: list[str] = []
    if "type" in schema and not _type_ok(instance, schema["type"]):
        return [f"{path}: expected type {schema['type']}, got {type(instance).__name__}"]

    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: {instance!r} not in {schema['enum']}")

    if isinstance(instance, str) and "minLength" in schema and len(instance) < schema["minLength"]:
        errors.append(f"{path}: shorter than minLength {schema['minLength']}")

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: below minimum {schema['minimum']}")
        if "exclusiveMinimum" in schema and instance <= schema["exclusiveMinimum"]:
            errors.append(f"{path}: not above exclusiveMinimum {schema['exclusiveMinimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{path}: above maximum {schema['maximum']}")

    if isinstance(instance, dict):
        for key in schema.get("required", []):
            if key not in instance:
                errors.append(f"{path}: missing required property {key!r}")
        for key, sub in schema.get("properties", {}).items():
            if key in instance:
                errors.extend(validate(instance[key], sub, f"{path}.{key}"))

    if isinstance(instance, list) and "items" in schema:
        for i, item in enumerate(instance):
            errors.extend(validate(item, schema["items"], f"{path}[{i}]"))
    return errors


def load(name: str) -> dict:
    return json.loads((SCHEMAS / name).read_text(encoding="utf-8"))


def test_resume_document_validates_against_its_schema(fixtures):
    from ariadne_ats.evidence import build_ledger

    doc = build_ledger(fixtures["clean"]).to_resume_json()
    errors = validate(doc, load("resume.schema.json"))
    assert not errors, "resume.json does not match schemas/resume.schema.json:\n  " + "\n  ".join(errors)


def test_jd_document_validates_against_its_schema():
    from ariadne_ats.jd import build_jd

    text = """Senior Backend Engineer

Requirements
- Must have 5 years of Python experience
- Required: Kubernetes and PostgreSQL in production
- Nice to have: Terraform experience

About you
- You have shipped billing systems at scale
"""
    doc = build_jd(text, source="jd.txt").to_jd_json()
    errors = validate(doc, load("jd.schema.json"))
    assert not errors, "jd.json does not match schemas/jd.schema.json:\n  " + "\n  ".join(errors)
    assert doc["custom"]["ariadne.provenance"]["counts"]["must"] >= 2


def test_validator_rejects_a_deliberately_broken_document(fixtures):
    """A validator that cannot fail is decoration."""
    from ariadne_ats.evidence import build_ledger

    doc = build_ledger(fixtures["clean"]).to_resume_json()
    doc["custom"]["ariadne.provenance"]["facts"][0]["confidence"] = 7.5
    errors = validate(doc, load("resume.schema.json"))
    assert errors, "schema accepted confidence = 7.5"


def test_schema_files_are_valid_json():
    for name in ("resume.schema.json", "jd.schema.json"):
        schema = load(name)
        assert schema["$schema"].startswith("http://json-schema.org/draft-07")
        assert schema["type"] == "object"
