#!/usr/bin/env python3
"""Collect live MCP tool definitions (tools/list) from pinned servers.

Each server runs in its own throwaway container (no host mounts, no Docker socket,
all capabilities dropped). This script runs on the host and talks to each server
over stdio with the official MCP Python SDK.

Usage:
    python scripts/collect_tools.py              # collect every server in scripts/servers.json
    python scripts/collect_tools.py --only ID..  # re-collect some servers
    python scripts/collect_tools.py --build-only # rebuild outputs from data/raw and data/fallback
"""
from __future__ import annotations

import argparse
import asyncio
import json
import shlex
import subprocess
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "scripts" / "servers.json"
DATA = ROOT / "data"
RAW_DIR = DATA / "raw"
FALLBACK_DIR = DATA / "fallback"
LOG_DIR = ROOT / "logs" / "collect"
REGISTRY_API = "https://registry.modelcontextprotocol.io/v0.1/servers"
PREFIX = "mcp-collect-"
NETWORK = "mcp-collect"


def registry_url(name: str | None, version: str) -> str | None:
    """Official MCP Registry URL for one server version, or None if the server is not listed."""
    if not name:
        return None
    return f"{REGISTRY_API}/{quote(name, safe='')}/versions/{quote(version, safe='')}"


def docker_args(server: dict, network: str) -> list[str]:
    """Arguments for `docker run` that start one server, locked down, talking over stdin/stdout."""
    args = [
        "run", "-i", "--rm", "--init",
        "--name", f"{PREFIX}{server['id']}",
        "--network", network,
        "--cap-drop=ALL",
        "--security-opt=no-new-privileges",
    ]
    for key, value in (server.get("env") or {}).items():
        args += ["-e", f"{key}={value}"]
    args.append(server["image"])
    command = list(server.get("command") or [])
    if server.get("setup"):
        args += ["sh", "-c", f"{server['setup']} && exec {shlex.join(command)}"]
    else:
        args += command
    return args


def tool_to_record(
    tool: dict,
    server: dict,
    server_name: str,
    retrieved_at: str,
    method: str = "live_tools_list",
    source_url: str | None = None,
) -> dict:
    """One JSONL record. Text fields are copied exactly as returned; nothing is cleaned up."""
    return {
        "server_id": server["server_id"],
        "server_name": server_name,
        "category": server["category"],
        "package": server["package"],
        "package_type": server["package_type"],
        "version": server["version"],
        "registry_url": registry_url(server.get("registry_name"), server["version"]),
        "tool_name": tool["name"],
        "title": tool.get("title"),
        "description": tool.get("description"),
        "input_schema": tool.get("inputSchema"),
        "annotations": tool.get("annotations"),
        "method": method,
        "source_url": source_url,
        "retrieved_at": retrieved_at,
    }


def build_records(servers: list[dict], raw: dict[str, dict], fallback: dict[str, dict]) -> list[dict]:
    """Live results first; a fallback file is used only for a server whose live run failed.

    Live records carry the package and version saved when the tools were collected,
    not whatever servers.json says today.
    """
    records = []
    for server in servers:
        live = raw.get(server["id"])
        if live and live.get("status") == "ok":
            used = live.get("config") or server
            records += [tool_to_record(t, used, live["server_name"], live["retrieved_at"]) for t in live["tools"]]
        elif server["id"] in fallback:
            fb = fallback[server["id"]]
            records += [
                tool_to_record(t, server, fb["server_name"], fb["retrieved_at"], "readme_fallback", fb["source_url"])
                for t in fb["tools"]
            ]
    return records


async def list_all_tools(session) -> list:
    """Call tools/list until the server stops returning a next cursor."""
    from mcp import types

    tools, cursor = [], None
    while True:
        params = types.PaginatedRequestParams(cursor=cursor) if cursor else None
        result = await session.list_tools(params=params)
        tools.extend(result.tools)
        cursor = result.next_cursor
        if not cursor:
            return tools


# ---------------------------------------------------------------- runtime (needs Docker)


def sh(*cmd: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(list(cmd), check=check, capture_output=True, text=True)


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def cleanup() -> None:
    """Remove containers and the network from this or an earlier (crashed) run."""
    ids = sh("docker", "ps", "-aq", "--filter", f"name=^{PREFIX}", check=False).stdout.split()
    if ids:
        sh("docker", "rm", "-f", *ids, check=False)
    sh("docker", "network", "rm", NETWORK, check=False)


def start_postgres(pg: dict) -> None:
    """Throwaway Postgres on a private network, for the Postgres servers to connect to."""
    sh("docker", "network", "create", NETWORK)
    sh("docker", "run", "-d", "--name", f"{PREFIX}pg", "--network", NETWORK,
       "-e", f"POSTGRES_PASSWORD={pg['password']}", pg["image"])
    for _ in range(90):
        ready = sh("docker", "exec", f"{PREFIX}pg", "pg_isready", "-h", "127.0.0.1", "-U", "postgres", check=False)
        if ready.returncode == 0:
            return
        time.sleep(1)
    raise RuntimeError("throwaway Postgres did not become ready")


def describe(exc: BaseException) -> str:
    while isinstance(exc, BaseExceptionGroup) and exc.exceptions:
        exc = exc.exceptions[0]
    return f"{type(exc).__name__}: {exc}"


def log_tail(path: Path, n: int = 5) -> list[str]:
    lines = [ln.strip() for ln in path.read_text(encoding="utf-8", errors="replace").splitlines() if ln.strip()]
    return lines[-n:]


async def collect_server(server: dict, network: str, log_path: Path, timeout_s: float) -> dict:
    import anyio
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    params = StdioServerParameters(command="docker", args=docker_args(server, network))
    started = time.monotonic()
    with log_path.open("w", encoding="utf-8") as errlog:
        try:
            with anyio.fail_after(timeout_s):
                async with stdio_client(params, errlog=errlog) as (read, write):
                    async with ClientSession(read, write) as session:
                        init = await session.initialize()
                        tools = await list_all_tools(session)
        except Exception as exc:  # report this server and move on to the next one
            errlog.flush()
            return {
                "status": "failed",
                "error": describe(exc)[:300],
                "stderr_tail": log_tail(log_path),
                "seconds": round(time.monotonic() - started, 1),
            }
    return {
        "status": "ok",
        "retrieved_at": now_utc(),
        "server_name": init.server_info.name,
        "server_version": init.server_info.version,
        "protocol_version": init.protocol_version,
        "seconds": round(time.monotonic() - started, 1),
        "tools": [t.model_dump(by_alias=True, mode="json", exclude_none=True) for t in tools],
    }


def load_json_dir(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    return {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in sorted(path.glob("*.json"))}


def image_digest(image: str) -> str:
    out = sh("docker", "image", "inspect", "--format", "{{index .RepoDigests 0}}", image, check=False)
    return out.stdout.strip() or "unknown"


def cell(text: object) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


RUN_KEYS = ("package", "package_type", "version", "image", "setup", "command", "env")


def is_stale(raw_entry: dict, server: dict) -> bool:
    """True if the server's settings in servers.json changed after its tools were collected."""
    used = raw_entry.get("config")
    return bool(used) and any(used.get(k) != server.get(k) for k in RUN_KEYS)


def summary_markdown(config: dict, raw: dict, fallback: dict, records: list[dict]) -> str:
    """Built only from saved results, so it never needs Docker."""
    servers = config["servers"]
    counts = Counter(r["server_id"] for r in records)
    methods = {r["server_id"]: r["method"] for r in records}
    lines = [
        "# Tool collection summary",
        "",
        f"Generated by `scripts/collect_tools.py` on {now_utc()}. "
        f"{len(records)} tools from {len(counts)} of {len(servers)} servers.",
        "",
        "| Server | Category | Package | Version | Tools | Method | Notes |",
        "|---|---|---|---|---|---|---|",
    ]
    digests = {}
    for s in servers:
        r = raw.get(s["id"], {})
        used = r.get("config") or s
        if r.get("status") == "ok":
            note = f"live, {r.get('seconds')}s, server reports `{r.get('server_name')}` {r.get('server_version')}"
            if is_stale(r, s):
                note = (f"**STALE**: collected with `{used['package']}` {used['version']}, but servers.json has "
                        f"changed since. Re-run with `--only {s['id']}`. ") + note
            if r.get("image_digest"):
                digests[used["image"]] = r["image_digest"]
        elif s["id"] in fallback:
            note = f"live run failed ({r.get('error', 'not run')}); tools taken from {fallback[s['id']]['source_url']}"
        else:
            note = f"**FAILED**: {r.get('error', 'not run')}"
        lines.append(
            f"| {cell(s['server_id'])} | {s['category']} | {used['package_type']}: `{used['package']}` "
            f"| {used['version']} | {counts.get(s['server_id'], 0)} | {methods.get(s['server_id'], '-')} | {cell(note)} |"
        )
    lines += ["", "## Container images used (digest saved at collection time)", ""]
    lines += [f"- `{img}` = `{digest}`" for img, digest in sorted(digests.items())]
    return "\n".join(lines) + "\n"


def write_outputs(config: dict) -> list[dict]:
    raw = load_json_dir(RAW_DIR)
    fallback = load_json_dir(FALLBACK_DIR)
    records = build_records(config["servers"], raw, fallback)
    DATA.mkdir(exist_ok=True)
    with (DATA / "tools.jsonl").open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    (DATA / "SUMMARY.md").write_text(summary_markdown(config, raw, fallback, records), encoding="utf-8")
    return records


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", nargs="+", metavar="ID", help="collect only these server ids")
    ap.add_argument("--timeout", type=float, default=300.0, help="seconds allowed per server (default 300)")
    ap.add_argument("--build-only", action="store_true", help="rebuild outputs without running any server")
    args = ap.parse_args(argv)
    config = json.loads(CONFIG.read_text(encoding="utf-8"))

    if not args.build_only:
        unknown = set(args.only or []) - {s["id"] for s in config["servers"]}
        if unknown:
            ap.error(f"unknown server ids: {sorted(unknown)}")
        servers = [s for s in config["servers"] if not args.only or s["id"] in args.only]
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        cleanup()
        try:
            # Pull first so download time does not count against a server's timeout,
            # and so the digest saved with each result is the image that actually ran.
            images = sorted({s["image"] for s in servers} | {config["postgres"]["image"]})
            for img in images:
                print(f"pulling {img} ...", flush=True)
                sh("docker", "pull", "-q", img, check=False)
            digests = {img: image_digest(img) for img in images}
            start_postgres(config["postgres"])
            for s in servers:
                print(f"{s['id']}: collecting ...", flush=True)
                result = asyncio.run(collect_server(s, NETWORK, LOG_DIR / f"{s['id']}.log", args.timeout))
                result = {"config": s, "image_digest": digests[s["image"]], **result}
                (RAW_DIR / f"{s['id']}.json").write_text(
                    json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
                )
                print(f"{s['id']}: {result['status']}, {len(result.get('tools', []))} tools", flush=True)
        finally:
            cleanup()

    records = write_outputs(config)
    print(f"wrote {len(records)} tools to data/tools.jsonl and data/SUMMARY.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
