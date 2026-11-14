# mcp-tool-retrieval

CS6200 course project. Given a developer's request in plain English, rank tools pooled from many
real MCP servers. Equivalent tools from different vendors all count as relevant.

## Tool data

`data/tools.jsonl` has one tool per line, collected live with `tools/list` from 13 pinned MCP
servers in 7 categories (filesystem, Git, Postgres, GitHub, browser, fetch, containers).

- `data/SUMMARY.md`: tool counts per server, method, and any failures.
- `data/SELECTION.md`: which servers were picked and why.
- `data/raw/`: each server's full tool list, plus the exact package, version and image digest used.
  Names, descriptions and schemas are unchanged. Tool fields the MCP SDK does not recognize are dropped.

### Rebuild the data

You need Docker (Colima works) and Python 3.11 or newer.

```bash
colima start
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/collect_tools.py
```

Each server runs in a throwaway container: no access to your files, no Docker socket, all Linux
capabilities dropped, and no real credentials. Versions are pinned in `scripts/servers.json`.

Options:

- `--only ID ...` re-collects some servers (IDs are in `scripts/servers.json`).
- `--build-only` rebuilds `tools.jsonl` and `SUMMARY.md` from `data/raw/` and `data/fallback/`
  without running anything.

Server error output goes to `logs/collect/` (not committed).

### Run the tests

```bash
.venv/bin/python -m pytest -q
```

### Record fields

| Field | Meaning |
|---|---|
| `server_id` | Registry name, or the repo folder for reference servers not in the registry |
| `server_name` | Name the server reports about itself |
| `category` | filesystem, git, postgres, github, browser, fetch, containers |
| `package`, `package_type`, `version` | Pinned package (npm, PyPI, or container image) |
| `registry_url` | Official MCP Registry entry, or `null` if not listed |
| `tool_name`, `title`, `description` | Copied exactly as returned. No cleanup. |
| `input_schema` | As returned |
| `annotations` | As read by the MCP SDK (hints like `readOnlyHint`) |
| `method` | `live_tools_list`, or `readme_fallback` if the server would not start |
| `source_url` | Where fallback tools were copied from (fallback only) |
| `retrieved_at` | When the tool list was fetched (UTC) |
