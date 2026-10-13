# Standalone investigation foundation

The requested standalone web agent now has an internal backend investigation step. It accepts a ZIP as bytes, an explicit file-selection list, a task and one of the thirteen workflow IDs. It reads the corresponding shared reference, submits selected text to the provider and validates the resulting source citations. It does not yet expose a browser upload endpoint or execute commands, apply patches or test model proposals.

`backend.workspace.ingest_zip` never extracts the archive. It returns only selected UTF-8 text and its SHA-256 hashes. Limits: 2 MiB archive, 200 entries, 30 selected files and 16,000 selected bytes. Unsafe paths, case collisions, links/special entries, encrypted archives, excluded paths, binary data and common secret patterns are rejected. Secret detection is heuristic and cannot establish that arbitrary content is nonconfidential. The caller must approve source submission; archive selection alone is not permission to send private files to a trial service.

`backend.investigate.investigate` makes one bounded inference request. Repository text is explicitly marked untrusted evidence, separate from task and workflow guidance. This prompt boundary reduces instruction confusion; it does not prove resistance to prompt injection. The returned JSON must contain a summary, findings with valid selected-file line locations, proposed checks and limitations. Citation validation checks existence and line bounds, not whether claims are true. The outer result always states unverified source analysis, zero executed commands and zero applied changes. Generated text remains untrusted and must be rendered literally by a future frontend.

Internal synthetic check, after configuring `NVIDIA_API_KEY`:

```powershell
python -m backend.investigate --smoke
```

The command builds an in-memory two-line synthetic Python file and asks about an optional discount. It never uploads this repository. No real project or account credentials are included in the prompt.

The [NVIDIA trial integration restrictions](nvidia-backend.md) still apply. A subsequent [internal browser workspace](local-workspace.md) adds authenticated loopback routing and selected-file preview/result review. This backend is separate from static dashboard/plugin downloads. Public provider access, production authentication/usage controls, an agent tool loop, patch review and isolated test execution remain required for the complete browser workflow.
