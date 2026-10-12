# Focused implementation

Activation: the user authorizes a repair or feature with a sufficiently clear contract.

Required evidence: affected source, known callers, expected behavior, reproduction where available, and existing changes.

Investigation: inspect interfaces and relevant tests before choosing a fix. Check boundary inputs; avoid silently broadening behavior.

Actions: make the smallest maintainable correction consistent with local conventions. Preserve unrelated changes and avoid opportunistic refactors or dependency upgrades.

Verification: run the regression case and relevant existing checks, then inspect the final diff for unintended changes.

Failure handling: treat a failed candidate as incomplete. Reassess the cause and report remaining failures or blockers honestly.

Expected output: focused patch, behavior explanation, known impact and validation scope.
