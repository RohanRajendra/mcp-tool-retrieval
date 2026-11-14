import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import collect_tools as ct  # noqa: E402

SERVER = {
    "id": "demo",
    "server_id": "io.github.demo/demo-mcp",
    "category": "filesystem",
    "registry_name": "io.github.demo/demo-mcp",
    "package_type": "npm",
    "package": "@demo/demo-mcp",
    "version": "1.2.3",
    "image": "node:24-bookworm",
    "setup": "mkdir -p /tmp/empty",
    "command": ["npx", "-y", "@demo/demo-mcp@1.2.3", "/tmp/empty"],
    "env": {"DEMO_TOKEN": "dummy"},
}


def test_tool_to_record_keeps_description_exact():
    text = "  Line one\n\tLine two – ü émoji 🚀  \n"
    tool = {"name": "read_thing", "description": text, "inputSchema": {"type": "object"}}
    rec = ct.tool_to_record(tool, SERVER, "demo-server", "2026-11-13T00:00:00Z")
    assert rec["description"] == text
    assert rec["tool_name"] == "read_thing"
    assert rec["input_schema"] == {"type": "object"}
    assert rec["method"] == "live_tools_list"
    assert rec["version"] == "1.2.3"
    assert rec["server_id"] == "io.github.demo/demo-mcp"
    assert rec["server_name"] == "demo-server"
    assert rec["registry_url"] == (
        "https://registry.modelcontextprotocol.io/v0.1/servers/io.github.demo%2Fdemo-mcp/versions/1.2.3"
    )


def test_tool_to_record_missing_description_is_none():
    tool = {"name": "no_desc", "inputSchema": {"type": "object"}}
    rec = ct.tool_to_record(tool, SERVER, "demo-server", "2026-11-13T00:00:00Z")
    assert rec["description"] is None


def test_docker_args_are_locked_down():
    args = ct.docker_args(SERVER, "mcp-collect")
    assert args[:2] == ["run", "-i"]
    for flag in ["--rm", "--init", "--cap-drop=ALL", "--security-opt=no-new-privileges"]:
        assert flag in args
    for bad in ["-v", "--volume", "--mount", "--privileged"]:
        assert bad not in args
    assert not any("docker.sock" in a for a in args)
    assert ["--network", "mcp-collect"] == args[args.index("--network"): args.index("--network") + 2]
    assert "DEMO_TOKEN=dummy" in args
    # setup runs first in a shell, then the server replaces the shell
    assert args[-3:] == ["sh", "-c", "mkdir -p /tmp/empty && exec npx -y @demo/demo-mcp@1.2.3 /tmp/empty"]
    assert args[args.index("node:24-bookworm") + 1] == "sh"


def test_docker_args_without_setup_runs_command_directly():
    server = {**SERVER, "setup": None, "image": "ghcr.io/demo/demo:1.2.3", "command": []}
    args = ct.docker_args(server, "mcp-collect")
    assert args[-1] == "ghcr.io/demo/demo:1.2.3"


def test_registry_url_is_none_when_not_listed():
    assert ct.registry_url(None, "1.0.0") is None


def test_servers_json_pins_every_version():
    import json

    config = json.loads((Path(__file__).resolve().parents[1] / "scripts" / "servers.json").read_text())
    servers = config["servers"]
    assert len(servers) == 13
    assert len({s["id"] for s in servers}) == 13
    for s in servers:
        pins = {
            "npm": f"{s['package']}@{s['version']}",
            "pypi": f"{s['package']}=={s['version']}",
            "oci": f"{s['package']}:{s['version']}",
        }
        pin = pins[s["package_type"]]
        assert pin in s["command"] or pin == s["image"], s["id"]
        assert ":latest" not in s["image"] and "@latest" not in " ".join(s["command"]), s["id"]


def test_build_records_uses_fallback_only_when_live_failed():
    a = {**SERVER, "id": "a", "server_id": "a"}
    b = {**SERVER, "id": "b", "server_id": "b"}
    c = {**SERVER, "id": "c", "server_id": "c"}
    tool = {"name": "t", "description": "d", "inputSchema": {}}
    raw = {
        "a": {"status": "ok", "server_name": "A", "retrieved_at": "T1", "tools": [tool]},
        "b": {"status": "failed", "error": "boom"},
        "c": {"status": "failed", "error": "boom"},
    }
    fallback = {
        "a": {"server_name": "A-readme", "source_url": "https://x/a", "retrieved_at": "T0", "tools": [tool]},
        "b": {"server_name": "B", "source_url": "https://x/b", "retrieved_at": "T2", "tools": [tool, tool]},
    }
    recs = ct.build_records([a, b, c], raw, fallback)
    assert [(r["server_id"], r["method"]) for r in recs] == [
        ("a", "live_tools_list"),
        ("b", "readme_fallback"),
        ("b", "readme_fallback"),
    ]
    assert recs[0]["source_url"] is None and recs[0]["server_name"] == "A"
    assert recs[1]["source_url"] == "https://x/b" and recs[1]["retrieved_at"] == "T2"


NEWER = {**SERVER, "version": "2.0.0", "command": ["npx", "-y", "@demo/demo-mcp@2.0.0", "/tmp/empty"]}
RAW_FROM_OLD_RUN = {
    "demo": {
        "status": "ok",
        "server_name": "S",
        "retrieved_at": "T",
        "config": SERVER,
        "image_digest": "node@sha256:abc",
        "tools": [{"name": "t", "inputSchema": {}}],
    }
}


def test_build_records_uses_config_saved_at_collection_time():
    rec = ct.build_records([NEWER], RAW_FROM_OLD_RUN, {})[0]
    assert rec["version"] == "1.2.3"
    assert rec["registry_url"].endswith("/versions/1.2.3")


def test_summary_flags_stale_raw_and_needs_no_docker(monkeypatch):
    def no_docker(*args, **kwargs):
        raise AssertionError("building outputs must not call docker")

    monkeypatch.setattr(ct, "sh", no_docker)
    config = {"servers": [NEWER], "postgres": {"image": "postgres:16"}}
    records = ct.build_records(config["servers"], RAW_FROM_OLD_RUN, {})
    md = ct.summary_markdown(config, RAW_FROM_OLD_RUN, {}, records)
    assert "STALE" in md
    assert "node@sha256:abc" in md


def test_list_all_tools_follows_cursor():
    pages = {
        None: SimpleNamespace(tools=["a", "b"], next_cursor="p2"),
        "p2": SimpleNamespace(tools=["c"], next_cursor=None),
    }

    class FakeSession:
        async def list_tools(self, *, params=None):
            return pages[params.cursor if params else None]

    assert asyncio.run(ct.list_all_tools(FakeSession())) == ["a", "b", "c"]
