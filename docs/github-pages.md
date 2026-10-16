# GitHub Pages deployment

The public static catalog and setup dashboard is published at:

https://raimal-raja.github.io/devtwin-engineer/

The site contains workflow search/filtering, runtime/OS-specific setup, current skill and plugin ZIP downloads, and local task-handoff generation. It contains no model keys, workspace tokens, or uploaded project files. It does not execute repository investigations or tests. The independent local Docker web application remains separate.

## Publishing source

GitHub Pages serves the root of the dedicated `gh-pages` branch. Only the generated static output is published. `.nojekyll` disables Jekyll processing, and relative asset/download URLs support the `/devtwin-engineer/` project path.

Build a fresh output directory from `main`:

```sh
python scripts/build_web.py . dist/github-pages-new
```

The output includes the site and validated plugin/skill downloads. Publish that output to `gh-pages` while preserving branch history. Changes to `main` do not automatically update the deployment branch; build and publish again to refresh the site. Never copy `.env.docker`, container configuration, credentials, or the whole working directory into the Pages branch.

See [GitHub Pages publishing-source guidance](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).

## Deployment verification — 2026-10-16

GitHub reported the first deployment as `built` for commit `4c86557f2ae72d296cd4cdfa760f44941384f5a4` on `gh-pages`. The served HTML, CSS, JavaScript modules, icon, and both download ZIPs returned HTTP 200 and matched the generated build byte-for-byte. All 22 web tests and the three focused web-build/plugin tests passed. This is HTTP/artifact verification; no fresh interactive browser acceptance is claimed.
