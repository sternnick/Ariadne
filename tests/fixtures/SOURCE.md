```
Last verified: 2026-10-25
Reviewed by:   Ariadne (principal)
```

Synthetic fixtures. No real CV is used anywhere in this repository (DECISIONS D-011).

| file | shape it exercises |
|---|---|
| `clean_single_column.txt` | baseline: headings, marked bullets, skills list |
| `two_column_tabs.txt` | tab-aligned two-column extraction (MULTICOLUMN_FLATTENED) |
| `table_heavy.txt` | table-shaped rows (TABLE_STRUCTURE); compiled to `.docx` in `tests/conftest.py` |
| `malformed.docx` | not a zip: must fail with CORRUPT_DOCUMENT, never a guess |
| `image_only.pdf` | a PDF with no text layer: NO_TEXT_LAYER (or PDF_BACKEND_MISSING without a backend) |

These are **not** representative of any population. They exist to exercise named failure codes, and
their facts are invented for the purpose.
