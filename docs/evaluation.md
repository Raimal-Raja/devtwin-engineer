# Repeatable core evaluation

The runner prepares synthetic library exercises and checks candidate repairs. It does not start an agent, supply a correction, or score narrative claims.

```sh
python scripts/evaluate_checkout.py prepare .workspaces/core-001
python scripts/evaluate_checkout.py check .workspaces/core-001
```

The first check should fail for the broken checkout. Give a fresh agent session the generated request and target directory, plus the canonical SKILL.md when evaluating skill-enabled behavior. Keep evaluator-side acceptance code and manifest outside the agent's target directory. They are not securely hidden by filesystem isolation; avoid describing this as a blinded benchmark unless the evaluator actually enforces separation.

After the agent works, run `check` again and preserve its JSON output in private results when needed. Only check trusted synthetic copies: the runner executes candidate Python and tests, and is not a sandbox for unknown repositories. It creates no model calls or network requests. Exit status is 0 for prepared/passed, 1 for failed, and 2 for blocked. Existing preparation directories are never overwritten. Checks have a 30-second timeout per command and retain actual command output.

Apply the [core rubric](../evaluations/rubrics/core.md) to the session's actual transcript and diff. Failed checks and blocked interpreters must remain visible in the final report. A blocked harness does not demonstrate that an agent handles a blocked environment correctly.

For baseline comparison, prepare separate fresh copies and use the same model, budget, tools, inputs, and acceptance checks; omit the skill from baseline sessions. Record runtime version, elapsed time, costs when observable, and failures. This development fixture must not later be counted as an independent held-out task.
