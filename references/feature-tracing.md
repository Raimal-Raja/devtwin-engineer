# Feature tracing (draft workflow)

Activation: a request to explain a Python behavior from an entry point through its relevant handlers, functions and data consumers. Explanation stays read-only.

Required evidence: entry-point location, import resolution (including aliases), direct calls, data passed across boundaries, relevant tests, and any dynamic dispatch or external integrations that prevent a complete trace.

Investigation: start from the named behavior, not a full repository map. Resolve an imported symbol to its defining module before treating a name match as a call. Follow the inputs and outputs needed to explain the behavior. Search for registration, callback and interface implementations when dispatch is indirect. Label a configured default separately from every possible runtime target.

Actions: present a short supported path with source locations, branch conditions and data contracts. Do not execute unknown application startup code merely to obtain a diagram. Run a synthetic example only when the environment and task authorize it.

Verification: reconcile the trace with existing tests or an executed example. State whether each edge is supported by source, observed execution, or inference. A text search establishes a candidate reference, not runtime reachability.

Failure handling: report unresolved imports, missing configuration, unavailable services and dynamically registered targets. Do not silently omit those boundaries or claim the trace is exhaustive.

Example: explaining order submission should connect the service to invoice creation, resolve its aliased pricing import, and distinguish the default receipt renderer from an extensible registry.

Failure case: a plugin can register a new renderer after startup; source for the default renderer does not establish the behavior of that plugin.

Expected output: relevant behavior path, inputs/outputs and branches, source locations, actual checks, and unresolved boundaries. Broader independent and Claude evaluation remain pending.
