# Increment 36 — Repository plugin distribution and handover

The public repository now includes the Codex and Claude marketplace manifests and an embedded, self-contained DevTwin plugin generated from the canonical skill allowlist. Publisher metadata names Raimal Raja. Existing marketplace identity and version remain stable; no formal release tag or license is introduced.

Runtime-specific setup covers repository and local-checkout installation, skill-only alternatives, restart/discovery, and the distinction between plugin instructions and the independent Docker web backend. The published-distribution checker compares a fresh build with checked-in bytes and detects unexpected plugin files. It is included in the combined project gates.

Final local validation passed: 152 Python cases (150 passed, two Windows symlink skips), all 22 web tests, canonical package validation, all 13 capability resource sets, published-plugin consistency, and skill archive extraction/integrity. Native Codex local registration, installation, and enabled-plugin listing passed in an isolated temporary home. Claude runtime execution remains deferred; no Claude runtime result is claimed. Remote GitHub installation is checked after publication separately.

A first installed-content comparison used raw bytes and failed on intentional CRLF-to-LF normalization. Repeating with normalized UTF-8 text confirmed the installed canonical skill and updated setup guide were preserved. This was a verification correction, not a runtime behavior claim.
