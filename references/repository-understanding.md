# Repository understanding

Activation: explanation or the beginning of unfamiliar Python repair work.

Required evidence: applicable instructions, current edits, packaging/test configuration, entry points, and source locations supporting the requested behavior.

Investigation: inventory relevant paths without reading secrets or generated trees. When useful, run the package's [metadata inventory helper](../scripts/collect_context.py) on the target root; inspect its truncation and errors, and keep output local. The helper reads no source content. Trace imports and callers from the affected entry point. Identify existing tests and conventions. Separate direct call evidence from inferred runtime reachability.

Actions: provide a concise map; explanation tasks remain read-only. For repairs, record existing edits before proceeding.

Verification: reconcile the map with imports and test references. Execute code only when authorized and appropriate for the repository.

Failure handling: name inaccessible files, absent tools, dynamic paths, and unsupported frameworks rather than inventing an architecture.

Expected output: relevant structure, behavior path, test command candidate, and uncertainty.
