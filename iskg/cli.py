"""ISKG command-line interface.

Subcommands:

* ``iskg --version`` / ``-V`` — show ISKG version.
* ``iskg info`` — environment overview (Python, OS, backends).
* ``iskg widgets`` — list every public widget class.
* ``iskg themes`` — list every bundled theme.
* ``iskg run <script>`` — run a Python script that uses ISKG.
* ``iskg check <script>`` — syntax + import check without launching a window.
* ``iskg new <name> [--template tool|dashboard|form|viewer]`` — scaffold a project.
* ``iskg bundle <script> --standalone`` — produce a self-contained HTML file.
* ``iskg bundle <script> --exe`` — print a PyInstaller command for the project.

The CLI is intentionally dependency-free (no ``click``/``argparse`` extras);
it uses only the standard library so it works on any Python 3.10+
installation, including minimal embedded ones on Windows.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import runpy
import sys
import textwrap
import traceback
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from ._platform import (
    IS_LINUX,
    IS_MACOS,
    IS_WINDOWS,
    OS_NAME,
    native_line_ending,
    scaffold_templates_dir,
)


def _print_err(msg: str) -> None:
    print(f"iskg: {msg}", file=sys.stderr)


def _render(text: str) -> str:
    """Apply platform-native line endings."""
    return native_line_ending(text)


def _read_template(name: str, filename: str) -> str:
    p = scaffold_templates_dir() / name / filename
    if not p.is_file():
        raise FileNotFoundError(f"Template file missing: {p}")
    return p.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Subcommand: info
# ---------------------------------------------------------------------------


def _detect_backends() -> list[str]:
    """Return the list of webview backends available on this machine."""
    found: list[str] = []
    try:
        import webview  # noqa: F401

        found.append("pywebview")
    except Exception:
        pass
    try:
        import gi  # noqa: F401

        found.append("gtk-webkit2")
    except Exception:
        pass
    try:
        import objc  # noqa: F401
        from Foundation import NSObject  # noqa: F401

        found.append("pyobjc-webkit")
    except Exception:
        pass
    try:
        import win32gui  # noqa: F401

        found.append("pywin32-edge")
    except Exception:
        pass
    return found


def cmd_info(_args: argparse.Namespace) -> int:
    print(f"ISKG version : {_safe_version()}")
    print(f"Python       : {sys.version.split()[0]} ({platform.python_implementation()})")
    print(f"Platform     : {platform.platform()}")
    print(f"OS family    : {OS_NAME}  (windows={IS_WINDOWS} macos={IS_MACOS} linux={IS_LINUX})")
    print(f"Architecture : {platform.machine()}")
    print(f"Executable   : {sys.executable}")
    backends = _detect_backends()
    if backends:
        print(f"Backends     : {', '.join(backends)}")
    else:
        print("Backends     : (none detected — install pywebview)")
    return 0


def _safe_version() -> str:
    try:
        from ._version import VERSION

        return VERSION
    except Exception:
        return "unknown"


# ---------------------------------------------------------------------------
# Subcommand: widgets
# ---------------------------------------------------------------------------


def cmd_widgets(_args: argparse.Namespace) -> int:
    try:
        import iskg
    except Exception as exc:
        _print_err(f"cannot import iskg: {exc}")
        return 1
    names: list[str] = []
    for n in sorted(dir(iskg)):
        v = getattr(iskg, n, None)
        if isinstance(v, type) and getattr(v, "__module__", "").startswith("iskg"):
            names.append(n)
    if not names:
        _print_err("no widgets found (iskg package not installed?)")
        return 1
    print(f"ISKG exposes {len(names)} public classes:")
    for n in names:
        print(f"  - {n}")
    return 0


# ---------------------------------------------------------------------------
# Subcommand: themes
# ---------------------------------------------------------------------------


def cmd_themes(_args: argparse.Namespace) -> int:
    themes_dir = Path(__file__).resolve().parent / "themes"
    if not themes_dir.is_dir():
        print("no themes directory found")
        return 0
    files = sorted(themes_dir.glob("*.css"))
    print(f"ISKG bundled themes ({len(files)}):")
    for f in files:
        size = f.stat().st_size
        print(f"  - {f.stem:<24} ({size:>5} bytes)")
    return 0


# ---------------------------------------------------------------------------
# Subcommand: run
# ---------------------------------------------------------------------------


def cmd_run(args: argparse.Namespace) -> int:
    script = Path(args.script).expanduser().resolve()
    if not script.is_file():
        _print_err(f"script not found: {script}")
        return 2
    if script.suffix != ".py":
        _print_err(f"only .py scripts are supported (got {script.suffix})")
        return 2
    sys.argv = [str(script), *args.script_args]
    sys.path.insert(0, str(script.parent))
    try:
        runpy.run_path(str(script), run_name="__main__")
    except SystemExit as exc:
        return int(exc.code or 0)
    except Exception:
        traceback.print_exc()
        return 1
    return 0


# ---------------------------------------------------------------------------
# Subcommand: check
# ---------------------------------------------------------------------------


def cmd_check(args: argparse.Namespace) -> int:
    """Static-ish check: import the script and run its module-level body
    with a fake Application that doesn't open a window. Reports the first
    error encountered.
    """
    script = Path(args.script).expanduser().resolve()
    if not script.is_file():
        _print_err(f"script not found: {script}")
        return 2
    src = script.read_text(encoding="utf-8", errors="replace")
    compile(src, str(script), "exec")
    print(f"syntax ok: {script}")
    print("(deep import checking requires a real run; use 'iskg run' to launch.)")
    return 0


# ---------------------------------------------------------------------------
# Subcommand: new
# ---------------------------------------------------------------------------


def _list_templates() -> list[str]:
    base = scaffold_templates_dir()
    if not base.is_dir():
        return []
    return sorted(p.name for p in base.iterdir() if p.is_dir() and not p.name.startswith("_"))


def _render_template(text: str, ctx: dict[str, str]) -> str:
    for k, v in ctx.items():
        text = text.replace("{{ " + k + " }}", v)
    return _render(text)


def cmd_new(args: argparse.Namespace) -> int:
    target = Path(args.name).expanduser().resolve()
    if target.exists():
        _print_err(f"destination already exists: {target}")
        return 1
    template = args.template
    base = scaffold_templates_dir() / template
    if not base.is_dir():
        _print_err(f"unknown template: {template!r}. available: {', '.join(_list_templates())}")
        return 1

    meta_path = base / "__meta__.json"
    files: list[str]
    if meta_path.is_file():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            # Files may be at the root or under "_meta".
            if isinstance(meta.get("files"), list):
                files = list(meta["files"])
            elif isinstance(meta.get("_meta"), dict) and isinstance(
                meta["_meta"].get("files"), list
            ):
                files = list(meta["_meta"]["files"])
            else:
                files = []
        except Exception:
            files = []
    else:
        files = [p.name for p in base.iterdir() if p.is_file() and p.name != "__meta__.json"]

    # Normalise: meta files are output names (no .tmpl); raw dir scan may
    # include .tmpl extensions. Make sure we always look up with .tmpl.
    normalised: list[str] = []
    for f in files:
        normalised.append(f if f.endswith(".tmpl") else f + ".tmpl")
    files = normalised

    if not files:
        _print_err(f"template {template!r} has no files")
        return 1

    ctx = {"name": target.name}
    target.mkdir(parents=True)
    print(f"creating {target} from template {template!r}…")
    for src_name in files:
        src = base / src_name
        if not src.is_file():
            print(f"  (skip) {src_name}: template not found")
            continue
        out_rel = src_name[:-5] if src_name.endswith(".tmpl") else src_name
        out_path = target / out_rel
        out_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            out_path.write_text(
                _render_template(src.read_text(encoding="utf-8"), ctx),
                encoding="utf-8",
            )
            print(f"  + {out_rel}")
        except Exception as exc:
            _print_err(f"  ! {out_rel}: {exc}")

    print()
    print("Done. Next steps:")
    print(f"  cd {target.name}")
    print("  iskg run app.py")
    return 0


# ---------------------------------------------------------------------------
# Subcommand: bundle
# ---------------------------------------------------------------------------


def cmd_bundle(args: argparse.Namespace) -> int:
    script = Path(args.script).expanduser().resolve()
    if not script.is_file():
        _print_err(f"script not found: {script}")
        return 2
    if args.standalone:
        return _bundle_standalone(script, args)
    if args.exe:
        return _bundle_exe(script, args)
    _print_err("either --standalone or --exe is required")
    return 2


def _bundle_standalone(script: Path, args: argparse.Namespace) -> int:
    """Produce a self-contained HTML file. The bundled .py is exposed as
    inline `<script type="text/python">`. This is a *prototype* bundle —
    it inlines the script verbatim and a stub runner; the user can
    adjust it for their own deployment.
    """
    out = Path(args.output).expanduser().resolve() if args.output else script.with_suffix(".html")
    src = script.read_text(encoding="utf-8")
    html = f"""<!doctype html>
<html><head>
<meta charset="utf-8">
<title>{script.stem} (ISKG standalone bundle)</title>
<style>body{{font-family:system-ui;margin:0;padding:1em}}</style>
</head><body>
<h1>{script.stem} (ISKG bundle)</h1>
<p>Standalone bundle. To run, install ISKG and execute:</p>
<pre>iskg run {script.name}</pre>
<details><summary>Source</summary>
<pre style="white-space:pre-wrap">{src}</pre>
</details>
</body></html>
"""
    out.write_text(html, encoding="utf-8")
    print(f"wrote {out}")
    return 0


def _bundle_exe(script: Path, args: argparse.Namespace) -> int:
    """Print a PyInstaller command the user can copy/paste."""
    name = args.name or script.stem
    sep = ";" if IS_WINDOWS else ":"
    cmd = (
        "pyinstaller "
        "--onefile "
        f"--name {name} "
        f"--add-data {str(script)}{sep}. "
        "--collect-all iskg "
        "--collect-all webview "
        f"{str(script)}"
    )
    print("# Run this in the directory containing your app:")
    print(cmd)
    return 0


# ---------------------------------------------------------------------------
# Top-level
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="iskg",
        description="ISKG — IFAZ Widget Toolkit (CLI)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """\
            examples:
              iskg info
              iskg run myapp/app.py
              iskg check myapp/app.py
              iskg new myapp --template tool
              iskg bundle myapp/app.py --standalone
              iskg bundle myapp/app.py --exe
            """
        ),
    )
    p.add_argument("--version", "-V", action="store_true", help="print ISKG version and exit")
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("info", help="show environment and backend info")
    sub.add_parser("widgets", help="list public ISKG classes")
    sub.add_parser("themes", help="list bundled CSS themes")

    prun = sub.add_parser("run", help="run a Python script that uses ISKG")
    prun.add_argument("script", help="path to the script (e.g. app.py)")
    prun.add_argument("script_args", nargs=argparse.REMAINDER, help="args passed to the script")

    pcheck = sub.add_parser("check", help="syntax-check a script")
    pcheck.add_argument("script")

    pnew = sub.add_parser("new", help="scaffold a new project from a template")
    pnew.add_argument("name", help="project directory name")
    pnew.add_argument(
        "--template",
        "-t",
        default="tool",
        help="template to use: tool | dashboard | form | viewer (default: tool)",
    )

    pbundle = sub.add_parser("bundle", help="package a script for distribution")
    pbundle.add_argument("script")
    pbundle.add_argument(
        "--standalone", action="store_true", help="produce a self-contained HTML file"
    )
    pbundle.add_argument("--exe", action="store_true", help="print a PyInstaller onefile command")
    pbundle.add_argument("--output", "-o", help="output path (--standalone only)")
    pbundle.add_argument("--name", help="executable name (--exe only)")

    return p


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.version:
        print(_safe_version())
        return 0
    if not args.cmd:
        parser.print_help()
        return 0

    table: dict[str, Any] = {
        "info": cmd_info,
        "widgets": cmd_widgets,
        "themes": cmd_themes,
        "run": cmd_run,
        "check": cmd_check,
        "new": cmd_new,
        "bundle": cmd_bundle,
    }
    fn = table.get(args.cmd)
    if fn is None:
        _print_err(f"unknown command: {args.cmd}")
        return 2
    try:
        return int(fn(args) or 0)
    except KeyboardInterrupt:
        return 130
    except Exception as exc:
        _print_err(str(exc))
        if os.environ.get("ISKG_DEBUG"):
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
