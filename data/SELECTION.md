# Server selection

Starter set for the tool collection, chosen on 2026-11-13. Servers were found through the official
MCP Registry (`https://registry.modelcontextprotocol.io`, API `v0.1`, searched by name). The three
reference servers from `modelcontextprotocol/servers` are **not listed** in the registry (see below).

## How the servers were chosen

1. Listed in the official registry with status `active` and a local (stdio) package: npm, PyPI, or a container image.
2. Actively maintained: a release in 2026.
3. Runs without a paid account.
4. Most-used option wins a tie (npm or PyPI downloads in the week before 2026-11-13).
5. For filesystem and Git, a second vendor whose tools are named and described differently from the
   reference server. These give the cross-vendor duplicates that make the task hard.

## Servers

| Category | Server | Package | Version | Why this one |
|---|---|---|---|---|
| Filesystem | Reference (`modelcontextprotocol/servers`) | npm `@modelcontextprotocol/server-filesystem` | 2.3.0 | Required by the handoff. ~1.35M downloads/week. |
| Filesystem | `io.github.j0hanz/filesystem-mcp` | npm `@j0hanz/filesystem-mcp` | 2.20.0 | Most-used non-reference filesystem server in the registry (~2.5k/week); released 2026-11-11. |
| Git | Reference (`modelcontextprotocol/servers`) | PyPI `mcp-server-git` | 2026.11.11 | Required by the handoff. ~97k downloads/week. |
| Git | `io.github.cyanheads/git-mcp-server` | npm `@cyanheads/git-mcp-server` | 2.15.3 | Most-used Git server in the registry (~4.2k/week); broad tool set. |
| Postgres | `io.github.YawLabs/postgres-mcp` | npm `@yawlabs/postgres-mcp` | 0.13.12 | Query, schema, explain and health tools; released 2026-11-12 (~1.9k/week). |
| Postgres (extra) | `io.github.antonorlov/mcp-postgres-server` | npm `mcp-postgres-server` | 0.3.1 | Second vendor for Postgres (~1.4k/week). |
| GitHub | `io.github.github/github-mcp-server` | image `ghcr.io/github/github-mcp-server` | 2.1.0 | GitHub's official server. |
| Browser | `io.github.microsoft/playwright-mcp` | npm `@playwright/mcp` | 0.0.85 | Microsoft's official Playwright server; most used (~10.6M/week). |
| Browser (extra) | `io.github.ChromeDevTools/chrome-devtools-mcp` | npm `chrome-devtools-mcp` | 1.13.0 | Second large vendor (Google Chrome DevTools team, ~2.3M/week). |
| Fetch | Reference (`modelcontextprotocol/servers`) | PyPI `mcp-server-fetch` | 2026.11.11 | Required by the handoff. |
| Fetch | `io.github.YawLabs/fetch-mcp` | npm `@yawlabs/fetch-mcp` | 0.8.7 | Most-used non-paid fetch server with a local package (~2.2k/week). |
| Containers | `io.github.L337-org/docker-mcp-server` | PyPI `docker-mcp-server` | 2.3.0 | Broad Docker server (containers, images, Compose); released 2026-11-09. |
| Containers (extra) | `io.github.ofershap/docker` | npm `mcp-docker-server` | 1.0.1 | Second vendor for containers (~1.5k/week). |

"Extra" servers go beyond the handoff's minimum. They add cross-vendor duplicates in Postgres,
browser and containers too.

## Result

All 13 servers returned their tool list live (`tools/list`), 384 tools in total. No fallback was
needed. Counts are in `SUMMARY.md`.

Examples of cross-vendor duplicates in the data:

| Capability | Reference server | Other vendor |
|---|---|---|
| Move or rename a file | `move_file` (filesystem) | `move` (j0hanz) |
| File size and dates | `get_file_info` (filesystem) | `stat` (j0hanz) |
| List a folder | `list_directory` (filesystem) | `list` (j0hanz) |
| Working tree status | `git_status` (git) | `git_status` (cyanheads) |
| Commit history | `git_log` (git) | `git_log` (cyanheads) |

## Reference servers are not in the registry

Searches for `modelcontextprotocol`, `filesystem`, `server-git` and `fetch` on 2026-11-13 returned no
entry for the reference filesystem, Git or fetch servers. They are recorded with `registry_url: null`
and a `server_id` that names their folder in the `modelcontextprotocol/servers` repo.

## Run settings

Every server runs with its default settings, so the tool list is what a new user gets.

- Filesystem servers: one empty allowed folder (`/tmp/empty`). No read-only mode.
- Git servers: an empty Git repo (`/tmp/repo`).
- Postgres servers: a throwaway local Postgres 16 container.
- GitHub server: no token (it supports logging in on first use) and its default toolsets.
- Docker servers: no access to any Docker daemon (for safety).

## Alternatives considered

- Filesystem: `@agent-infra/mcp-server-filesystem` (ByteDance; registry pins only "latest", ~600/week),
  `filesystem-mcp` (domdomegg, ~120/week).
- Git: `@selfagency/git-mcp` (~125/week), `@infoinlet/mcp-git` (read-only).
- Postgres: several read-only "drop-in" replacements for the archived reference server.
- Fetch: `defuddle-fetch-mcp-server` (~110/week), `@j0hanz/fetch-url-mcp` (~95/week). Many registry
  fetch servers are hosted, paid (x402) services.
- Containers: `@alisaitteke/docker-mcp`, `@hypnosis/docker-mcp-server`, `@paretools/docker` (fewer downloads).
