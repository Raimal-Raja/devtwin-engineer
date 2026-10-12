# Local helpers

## Metadata inventory

```sh
python scripts/collect_context.py . --max-entries 1000 --max-scan 5000 --max-depth 8 --max-file-bytes 1048576
```

This helper returns JSON paths, file sizes, traversal counts, truncation and errors. It reads filesystem metadata, not file contents; does not execute repository commands; and never intentionally follows symbolic links or Windows reparse points. Root links and junctions are rejected. Common generated directories and secret/log filenames are excluded. These exclusions are not a guarantee that all sensitive filenames are hidden; keep output local unless reviewed for sharing.

Limits bound emitted entries, scanned directory entries, descent depth, and included file size. Oversized files are omitted. A limit reached during traversal sets `truncated`; this is a partial inventory. Entries within each scanned directory are sorted, but the selected subset at the scan limit depends on filesystem enumeration order. Concurrent filesystem replacement is not sandboxed; use a stable, trusted local checkout.

Exit code 0 means inventory completed (possibly truncated), 1 means traversal errors were recorded, and 2 means invalid root or arguments. Permission failures report error types rather than raw sensitive error messages.

## Git change summary

```sh
python scripts/inspect_changes.py . --max-entries 1000
```

Returns JSON paths and Git status codes for staged, unstaged, renamed and untracked entries. It reads no diffs or file contents into the report. Optional index locks, filesystem-monitor commands, untracked-cache updates and configured content-filter commands are disabled. Inherited `GIT_*` environment variables are removed to keep inspection on the requested checkout. The helper does not run hooks, install dependencies or mutate target files.

Inspection covers the whole working tree even when called from a subdirectory. Untracked directories are grouped and submodule contents are excluded. `index` and `working_tree` contain porcelain v1 status characters; `??` marks untracked paths. Renames include `original_path`. The output entry limit sets `truncated` while `total_changes` counts all reported Git entries. Git's captured output itself is not size-bounded; commands have a 30-second timeout. Paths may be sensitive, so review output before sharing.

Exit code 0 means inspection succeeded; 2 means an inaccessible/non-Git root, missing Git executable, invalid arguments or command failure. Errors deliberately omit repository-controlled stderr. Disabling content filters can cause files that require those filters to appear modified; treat this as conservative status evidence and review with appropriate trusted tooling. Only stable, trusted local checkouts are supported; this is not isolation against concurrent repository/configuration replacement.

## Package validation and checkout evaluation

`check_project.py .` runs the local development gates in sequence and returns a JSON report. It validates metadata and links, runs trusted project tests in a separate process, then builds and verifies a temporary archive. Failed, empty or entirely skipped suites fail the gate; partial skips remain visible. Test stdout/stderr is captured in the test log. Test execution has a 120-second timeout. This command is for trusted project source because tests execute Python code.

`verify_archive.py ARCHIVE.zip` checks paths, portable filenames, entry/size limits, duplicate/case-colliding names, symlink entries, manifest membership and hashes. It validates links after copying checked payloads into a temporary directory, without executing archived Python. Integrity is not authenticity: a manifest can be replaced alongside malicious files, so no signature verification is claimed.

Use `validate_package.py` for package structure, metadata and inline local links in SKILL.md, README.md, references, templates, docs, integrations and evaluation documents. It rejects linked paths outside the package, symlink/reparse documents, unsupported URI schemes, unreadable UTF-8 and documents larger than 1 MiB. It checks at most 1,000 documents and treats exceeding that limit as incomplete validation. Optional document directories may be absent. Private evaluation results and bytecode directories are excluded.

The supported frontmatter is deliberately a subset: flat scalar string fields, with required `name` and `description`; plain strings, JSON-style double-quoted strings and YAML-style single-quoted strings are accepted. Duplicate fields, blank descriptions, block/nested structures and non-string scalars are rejected. This is not a general YAML parser or full runtime conformance validator. Inline links are checked, including angle-bracket destinations with spaces and encoded paths; fenced examples are ignored. Reference-style links, HTML links, heading anchors and remote availability are not validated. Exit status is 0 for valid or 1 for errors, with JSON diagnostics.

Use `evaluate_checkout.py` only against trusted synthetic exercises, as described in the [evaluation guide](evaluation.md). Neither helper establishes automatic runtime discovery or general benchmark performance.
