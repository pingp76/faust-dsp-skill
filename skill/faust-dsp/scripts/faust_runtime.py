#!/usr/bin/env python3
"""Install, start, call, and stop a local faust-mcp runtime for this skill."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional


UPSTREAM_REPO = "https://github.com/sletz/faust-mcp.git"
UPSTREAM_REF = "main"
SCHEMA_VERSION = "faust-dsp-skill/1"


def cache_root() -> Path:
    root = os.environ.get("FAUST_DSP_SKILL_CACHE")
    if root:
        return Path(root).expanduser()
    xdg = os.environ.get("XDG_CACHE_HOME")
    if xdg:
        return Path(xdg).expanduser() / "faust-dsp-skill"
    return Path.home() / ".cache" / "faust-dsp-skill"


def repo_dir() -> Path:
    return cache_root() / "faust-mcp"


def venv_python() -> Path:
    return cache_root() / "venv" / "bin" / "python"


def state_path() -> Path:
    return cache_root() / "runtime.json"


def log_path(kind: str) -> Path:
    return cache_root() / f"{kind}.log"


def run(cmd: list[str], cwd: Optional[Path] = None, env: Optional[dict[str, str]] = None) -> None:
    subprocess.run(cmd, cwd=cwd, env=env, check=True)


def output(cmd: list[str], cwd: Optional[Path] = None, env: Optional[dict[str, str]] = None) -> str:
    return subprocess.check_output(cmd, cwd=cwd, env=env, text=True)


def ensure_repo(update: bool = False) -> None:
    cache_root().mkdir(parents=True, exist_ok=True)
    dest = repo_dir()
    if not dest.exists():
        run(["git", "clone", "--depth", "1", "--branch", UPSTREAM_REF, UPSTREAM_REPO, str(dest)])
        return
    if update:
        run(["git", "fetch", "--depth", "1", "origin", UPSTREAM_REF], cwd=dest)
        run(["git", "checkout", "FETCH_HEAD"], cwd=dest)


def ensure_venv() -> None:
    cache_root().mkdir(parents=True, exist_ok=True)
    py = venv_python()
    if not py.exists():
        run([sys.executable, "-m", "venv", str(cache_root() / "venv")])
    run([str(py), "-m", "pip", "install", "--upgrade", "pip"])
    run([str(py), "-m", "pip", "install", "-r", str(repo_dir() / "requirements.txt")])


def ensure_browser_ui_deps() -> None:
    ui_dir = repo_dir() / "ui"
    if not ui_dir.exists():
        return
    if (ui_dir / "node_modules" / "@grame" / "faustwasm").exists():
        return
    npm = shutil.which("npm")
    if not npm:
        raise SystemExit("npm is required for the browser runtime UI dependencies")
    run([npm, "install"], cwd=ui_dir)


def ensure_all(args: argparse.Namespace) -> None:
    ensure_repo(update=args.update)
    if not args.skip_python_deps:
        ensure_venv()
    if args.with_browser_ui and not args.skip_node_deps:
        ensure_browser_ui_deps()
    py = str(venv_python()) if venv_python().exists() else None
    print(json.dumps({"status": "ok", "repo": str(repo_dir()), "python": py}, indent=2))


def python_cmd() -> str:
    py = venv_python()
    return str(py) if py.exists() else sys.executable


def base_env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("TMPDIR", str(cache_root() / "tmp"))
    Path(env["TMPDIR"]).mkdir(parents=True, exist_ok=True)
    return env


def read_state() -> Optional[dict]:
    path = state_path()
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def write_state(state: dict) -> None:
    cache_root().mkdir(parents=True, exist_ok=True)
    state_path().write_text(json.dumps(state, indent=2), encoding="utf-8")


def process_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def wait_for_port(host: str, port: int, timeout: float = 20.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)
            if sock.connect_ex((host, port)) == 0:
                return True
        time.sleep(0.2)
    return False


def runtime_command(kind: str) -> tuple[list[str], Optional[int], dict[str, str]]:
    env = base_env()
    env["MCP_TRANSPORT"] = "sse"
    env.setdefault("MCP_HOST", "127.0.0.1")
    env.setdefault("MCP_PORT", "8000")
    if kind == "browser":
        env.setdefault("BROWSER_UI_PORT", "8010")
        env.setdefault("BROWSER_UI_ROOT", str(repo_dir()))
        return [python_cmd(), "faust_browser_server.py"], int(env["BROWSER_UI_PORT"]), env
    if kind == "node":
        env.setdefault("FAUST_UI_PORT", "8787")
        env.setdefault("WEBAUDIO_ROOT", str(repo_dir() / "external" / "node-web-audio-api"))
        return [python_cmd(), "faust_node_server.py"], int(env["MCP_PORT"]), env
    if kind == "cpp":
        return [python_cmd(), "faust_server.py"], int(env["MCP_PORT"]), env
    if kind == "daw":
        return [python_cmd(), "faust_server_daw.py"], int(env["MCP_PORT"]), env
    raise ValueError(f"unknown runtime kind: {kind}")


def start_runtime(args: argparse.Namespace) -> None:
    ensure_repo(update=False)
    if not args.skip_python_deps:
        ensure_venv()
    if args.kind == "browser" and not args.skip_node_deps:
        ensure_browser_ui_deps()
    state = read_state()
    if state and process_alive(int(state.get("pid", -1))):
        print(json.dumps({"status": "already_running", **state}, indent=2))
        return

    cmd, ready_port, env = runtime_command(args.kind)
    log_file = log_path(args.kind)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    log = log_file.open("a", encoding="utf-8")
    proc = subprocess.Popen(
        cmd,
        cwd=repo_dir(),
        env=env,
        stdout=log,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=True,
    )
    state = {
        "schema_version": SCHEMA_VERSION,
        "owner": "faust-dsp-skill",
        "kind": args.kind,
        "pid": proc.pid,
        "pgid": os.getpgid(proc.pid),
        "repo": str(repo_dir()),
        "mcp_url": f"http://{env['MCP_HOST']}:{env['MCP_PORT']}/sse",
        "ui_url": f"http://127.0.0.1:{ready_port}/" if args.kind in ("browser", "node") else None,
        "log": str(log_file),
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    write_state(state)
    if ready_port and not wait_for_port("127.0.0.1", ready_port, timeout=args.timeout):
        print(json.dumps({"status": "starting", "warning": "port not ready before timeout", **state}, indent=2))
        return
    print(json.dumps({"status": "started", **state}, indent=2))


def stop_runtime(args: argparse.Namespace) -> None:
    state = read_state()
    if not state:
        print(json.dumps({"status": "not_running"}, indent=2))
        return
    if state.get("owner") != "faust-dsp-skill":
        raise SystemExit("Refusing to stop a runtime not owned by faust-dsp-skill")
    pid = int(state.get("pid", -1))
    pgid = int(state.get("pgid", -1))
    if pid > 0 and process_alive(pid):
        try:
            os.killpg(pgid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        deadline = time.time() + args.timeout
        while time.time() < deadline and process_alive(pid):
            time.sleep(0.2)
        if process_alive(pid):
            os.killpg(pgid, signal.SIGKILL)
    state_path().unlink(missing_ok=True)
    print(json.dumps({"status": "stopped", "previous": state}, indent=2))


def status_runtime(_: argparse.Namespace) -> None:
    state = read_state()
    if not state:
        print(json.dumps({"status": "not_running"}, indent=2))
        return
    alive = process_alive(int(state.get("pid", -1)))
    print(json.dumps({"status": "running" if alive else "stale", **state}, indent=2))


def analyze(args: argparse.Namespace) -> None:
    ensure_repo(update=False)
    if not args.skip_python_deps:
        ensure_venv()
    server = "faust_server_daw.py" if args.runtime == "daw" else "faust_server.py"
    cmd = [
        python_cmd(),
        "stdio_client_example.py",
        "--server",
        server,
        "--tool",
        "compile_and_analyze",
        "--dsp",
        str(Path(args.dsp).expanduser()),
        "--tmpdir",
        str(cache_root() / "tmp"),
    ]
    if args.input_source:
        cmd.extend(["--input-source", args.input_source])
    if args.input_freq is not None:
        cmd.extend(["--input-freq", str(args.input_freq)])
    if args.input_file:
        cmd.extend(["--input-file", args.input_file])
    run(cmd, cwd=repo_dir(), env=base_env())


def call_tool(args: argparse.Namespace) -> None:
    state = read_state()
    if not state or not process_alive(int(state.get("pid", -1))):
        raise SystemExit("No running runtime. Run: python3 scripts/faust_runtime.py start --kind browser")
    cmd = [python_cmd(), "sse_client_example.py", "--url", state["mcp_url"], "--tool", args.tool]
    if args.dsp:
        cmd.extend(["--dsp", str(Path(args.dsp).expanduser())])
    if args.name:
        cmd.extend(["--name", args.name])
    if args.extra and args.extra[0] == "--":
        args.extra = args.extra[1:]
    cmd.extend(args.extra)
    run(cmd, cwd=repo_dir(), env=base_env())


def with_runtime(args: argparse.Namespace) -> None:
    start_args = argparse.Namespace(
        kind=args.kind,
        timeout=args.timeout,
        skip_python_deps=args.skip_python_deps,
        skip_node_deps=args.skip_node_deps,
    )
    start_runtime(start_args)
    try:
        if args.command and args.command[0] == "--":
            args.command = args.command[1:]
        if not args.command:
            raise SystemExit("with-runtime requires a command to run")
        run(args.command)
    finally:
        stop_runtime(argparse.Namespace(timeout=5.0))


def doctor(_: argparse.Namespace) -> None:
    checks = {
        "git": shutil.which("git"),
        "python": sys.executable,
        "faust": shutil.which("faust"),
        "g++": shutil.which("g++"),
        "node": shutil.which("node"),
        "repo": str(repo_dir()) if repo_dir().exists() else None,
        "venv_python": str(venv_python()) if venv_python().exists() else None,
        "state": read_state(),
    }
    print(json.dumps(checks, indent=2, default=str))


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage the Faust DSP skill runtime")
    sub = parser.add_subparsers(required=True)

    p = sub.add_parser("ensure", help="Clone faust-mcp and install Python dependencies")
    p.add_argument("--update", action="store_true")
    p.add_argument("--skip-python-deps", action="store_true")
    p.add_argument("--skip-node-deps", action="store_true")
    p.add_argument("--with-browser-ui", action="store_true")
    p.set_defaults(func=ensure_all)

    p = sub.add_parser("doctor", help="Print dependency and runtime status")
    p.set_defaults(func=doctor)

    p = sub.add_parser("start", help="Start a background runtime")
    p.add_argument("--kind", choices=["browser", "node", "cpp", "daw"], default="browser")
    p.add_argument("--timeout", type=float, default=20.0)
    p.add_argument("--skip-python-deps", action="store_true")
    p.add_argument("--skip-node-deps", action="store_true")
    p.set_defaults(func=start_runtime)

    p = sub.add_parser("stop", help="Stop the owned background runtime")
    p.add_argument("--timeout", type=float, default=5.0)
    p.set_defaults(func=stop_runtime)

    p = sub.add_parser("status", help="Show runtime status")
    p.set_defaults(func=status_runtime)

    p = sub.add_parser("analyze", help="Run one-shot offline compile_and_analyze")
    p.add_argument("--dsp", required=True)
    p.add_argument("--runtime", choices=["cpp", "daw"], default="cpp")
    p.add_argument("--input-source", choices=["none", "sine", "noise", "file"])
    p.add_argument("--input-freq", type=float)
    p.add_argument("--input-file")
    p.add_argument("--skip-python-deps", action="store_true")
    p.set_defaults(func=analyze)

    p = sub.add_parser("call", help="Call a tool on the running SSE runtime")
    p.add_argument("--tool", required=True)
    p.add_argument("--dsp")
    p.add_argument("--name")
    p.add_argument("extra", nargs=argparse.REMAINDER)
    p.set_defaults(func=call_tool)

    p = sub.add_parser("with-runtime", help="Start a runtime, run a command, then stop it")
    p.add_argument("--kind", choices=["browser", "node", "cpp", "daw"], default="browser")
    p.add_argument("--timeout", type=float, default=20.0)
    p.add_argument("--skip-python-deps", action="store_true")
    p.add_argument("--skip-node-deps", action="store_true")
    p.add_argument("command", nargs=argparse.REMAINDER)
    p.set_defaults(func=with_runtime)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
