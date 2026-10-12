# Local helpers

## Metadata inventory

```sh
python scripts/collect_context.py . --max-entries 1000 --max-scan 5000 --max-depth 8 --max-file-bytes 1048576
```

This helper returns JSON paths, file sizes, traversal counts, truncation and errors. It reads filesystem metadata, not file contents; does not execute repository commands; and never intentionally follows symbolic links or Windows reparse points. Root links and junctions are rejected. Common generated directories and secret/log filenames are excluded. These exclusions are not a guarantee that all sensitive filenames are hidden; keep output local unless reviewed for sharing.

Limits bound emitted entries, scanned directory entries, descent depth, and included file size. Oversized files are omitted. A limit reached during traversal sets `truncated`; this is a partial inventory. Entries within each scanned directory are sorted, but the selected subset at the scan limit depends on filesystem enumeration order. Concurrent filesystem replacement is not sandboxed; use a stable, trusted local checkout.

Exit code 0 means inventory completed (possibly truncated), 1 means traversal errors were recorded, and 2 means invalid root or arguments. Permission failures report error types rather than raw sensitive error messages.

## Package validation and checkout evaluation

Use `validate_package.py` for package structure and local skill links. Use `evaluate_checkout.py` only against trusted synthetic exercises, as described in the [evaluation guide](evaluation.md). Neither helper establishes automatic runtime discovery or general benchmark performance.
