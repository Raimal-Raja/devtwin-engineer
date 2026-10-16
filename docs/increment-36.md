# Increment 36 — Repository plugin distribution and handover

The public repository now includes the Codex and Claude marketplace manifests and an embedded, self-contained DevTwin plugin generated from the canonical skill allowlist. Publisher metadata names Raimal Raja. Existing marketplace identity and version remain stable; no formal release tag or license is introduced.

Runtime-specific setup covers repository and local-checkout installation, skill-only alternatives, restart/discovery, and the distinction between plugin instructions and the independent Docker web backend. The published-distribution checker compares a fresh build with checked-in bytes and detects unexpected plugin files. It is included in the combined project gates.

Final local validation passed: 152 Python cases (150 passed, two Windows symlink skips), all 22 web tests, canonical package validation, all 13 capability resource sets, published-plugin consistency, and skill archive extraction/integrity. Native Codex local registration, installation, and enabled-plugin listing passed in an isolated temporary home. Claude runtime execution remains deferred; no Claude runtime result is claimed. Remote GitHub installation is checked after publication separately.

A first installed-content comparison used raw bytes and failed on intentional CRLF-to-LF normalization. Repeating with normalized UTF-8 text confirmed the installed canonical skill and updated setup guide were preserved. This was a verification correction, not a runtime behavior claim.

## Published installation and Claude validation follow-up

After commit `5a48eab` was pushed, Codex successfully registered `Raimal-Raja/devtwin-engineer`, installed `devtwin-engineer@devtwin-engineer-local`, and listed it as enabled in a fresh temporary home. This verifies the actual GitHub distribution path, not just the local checkout.

A fresh account-free Claude native validation was attempted through official npm packages 2.1.301 and 2.1.263. Both downloads stalled with incomplete 500-byte executable placeholders; invoking the latest placeholder returned an invalid-OS-executable error. The stalled npm requests were stopped. Consequently there is no fresh Claude native validation or execution claim for this increment. Earlier native validation evidence remains historical; current manifests, source paths, embedded resources, and hashes passed local distribution checks.

The final static download build succeeded at `dist/devtwin-handover-36`. Plugin ZIP SHA-256: `4ee56888a2cd6496c62c9bbb53baa0a2a2c4cfb985964575af598d12efd29997`. Skill ZIP SHA-256: `a7e921916d89e09a44ecd97c9b46fc589785a9c71a9dfde442be8fceb983f1a1`. These are local artifacts; the older public catalog deployment was not updated in this increment.
