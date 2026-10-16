# GitHub Pages deployment

The public static catalog and setup dashboard is published at:

https://raimal-raja.github.io/devtwin-engineer/

The site contains three navigable views: Welcome (creator photo, CV-based biography, public professional links, and plugin setup), Project Explorer (local-workspace launch guide), and Workflows (search/filter, task handoff, and downloads). It follows the warm off-white, deep green, and orange design of the local app. It contains no model keys, workspace tokens, or uploaded project files. It does not execute repository investigations or tests. The independent local Docker web application remains separate.

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

The initial Pages deployment mistakenly used the older catalog-only design. Increment 38 replaces it with the proposed creator welcome and three-view structure while preserving the distinction between static guidance and local backend execution.

## Corrected welcome deployment — 2026-10-16

Deployment commit `a4e2744df6b6f54c5d5a230142ae4f819d2548b7` completed successfully. The live browser displayed Raimal Raja’s portrait and biography, public links, the updated visual design, and Codex/Claude setup controls. Navigation to Project Explorer and Workflows was checked, then the welcome view was restored. A real full-page capture is included in the README. The build checks cover the creator content, all three view containers, the portrait payload, unique IDs, and local asset references. Three focused Python package/build tests and all 22 web tests passed.
