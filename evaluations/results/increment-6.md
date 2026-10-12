# Increment 6: stronger package validation — 2026-10-13

Expanded package validation from core skill links to inline links in README, references, templates, documentation, integrations and evaluation documents. Added duplicate/non-string/unsupported metadata checks, encoded path-escape detection, unsafe document-path rejection, UTF-8 errors, bounded document reads and an explicit document-count limit. Optional document directories may be absent; traversal errors are reported.

Executed with Python 3.12.14 on Windows:

- `python -m unittest discover -s tests -v`: 30 tests ran; 28 passed and 2 real symlink checks were skipped because creation was unavailable.
- `python scripts/validate_package.py .`: valid, no errors.

New checks exercise invalid metadata, duplicate fields, unsupported scalar structures, broken documentation and helper links, percent-encoded path escapes, unsupported schemes, oversized/non-UTF-8 documents, quoted destinations with spaces, fenced examples and document-limit failures. Existing inventory, Git inspection and checkout checks remain passing.

Limitations: validation supports a documented subset of flat string YAML and inline Markdown links. It does not validate reference-style links, HTML links, anchors, remote availability or runtime activation. Real symlink/junction handling remains unverified in this restricted environment. Document reading is bounded; directory enumeration itself is not a sandbox against adversarial or concurrently changing filesystems. Independent agent evaluation remains an open gate.
