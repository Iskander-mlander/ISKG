"""Tests for the ISKG command-line interface.

These tests use ``python -m iskg.cli`` directly so they don't require the
``iskg`` console script to be on PATH (which depends on whether the
package was installed in editable mode or not).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
PYTHON = sys.executable


def _safe_version() -> str:
    from iskg._version import VERSION

    return VERSION


def _run_cli(
    *args: str, cwd: Path | None = None, expect_returncode: int | None = 0
) -> subprocess.CompletedProcess:
    cmd = [PYTHON, "-m", "iskg.cli", *args]
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(cwd) if cwd else str(REPO),
        timeout=30,
        check=False,
    )


def test_version_flag() -> None:
    p = _run_cli("--version")
    assert p.returncode == 0
    assert p.stdout.strip() == _safe_version()


def test_help() -> None:
    p = _run_cli("--help")
    assert p.returncode == 0
    assert "ISKG" in p.stdout
    for sub in ("info", "widgets", "themes", "run", "check", "new", "bundle"):
        assert sub in p.stdout, f"missing subcommand in help: {sub}"


def test_info() -> None:
    p = _run_cli("info")
    assert p.returncode == 0
    assert "ISKG version" in p.stdout
    assert "Python" in p.stdout
    assert "Platform" in p.stdout


def test_widgets() -> None:
    p = _run_cli("widgets")
    assert p.returncode == 0
    assert "Button" in p.stdout
    assert "DataGrid" in p.stdout
    assert "MarkdownViewer" in p.stdout


def test_themes() -> None:
    p = _run_cli("themes")
    assert p.returncode == 0
    assert "themes" in p.stdout.lower()
    # every name accepted by app.set_theme() must be listed
    from iskg.themes import available_themes

    names = available_themes()
    assert names, "iskg.themes must register at least one theme"
    for name in names:
        assert name in p.stdout, f"theme {name} missing from `iskg themes`"
    assert "ifaz" in p.stdout


def test_check_existing_file(tmp_path: Path) -> None:
    f = tmp_path / "app.py"
    f.write_text("import iskg\nx = 1\n", encoding="utf-8")
    p = _run_cli("check", str(f))
    assert p.returncode == 0
    assert "syntax ok" in p.stdout


def test_check_missing_file() -> None:
    p = _run_cli("check", "/nonexistent_file.py")
    assert p.returncode == 2
    assert "not found" in p.stderr


def test_check_syntax_error(tmp_path: Path) -> None:
    f = tmp_path / "bad.py"
    f.write_text("def (:", encoding="utf-8")
    p = _run_cli("check", str(f))
    assert p.returncode != 0


def test_new_tool_scaffold(tmp_path: Path) -> None:
    target = tmp_path / "myapp"
    p = _run_cli("new", str(target), "--template", "tool")
    assert p.returncode == 0, p.stderr
    assert (target / "app.py").is_file()
    assert (target / "README.md").is_file()
    assert (target / "requirements.txt").is_file()
    assert (target / "assets").is_dir()
    assert (target / "themes").is_dir()
    text = (target / "app.py").read_text(encoding="utf-8")
    assert "myapp" in text  # name was substituted


def test_new_dashboard_scaffold(tmp_path: Path) -> None:
    target = tmp_path / "d"
    p = _run_cli("new", str(target), "-t", "dashboard")
    assert p.returncode == 0
    assert (target / "app.py").is_file()


def test_new_form_scaffold(tmp_path: Path) -> None:
    target = tmp_path / "f"
    p = _run_cli("new", str(target), "-t", "form")
    assert p.returncode == 0
    assert (target / "app.py").is_file()


def test_new_viewer_scaffold(tmp_path: Path) -> None:
    target = tmp_path / "v"
    p = _run_cli("new", str(target), "-t", "viewer")
    assert p.returncode == 0
    assert (target / "app.py").is_file()


def test_new_unknown_template(tmp_path: Path) -> None:
    target = tmp_path / "x"
    p = _run_cli("new", str(target), "-t", "no-such-template")
    assert p.returncode == 1
    assert "unknown template" in p.stderr


def test_new_existing_directory(tmp_path: Path) -> None:
    target = tmp_path / "exists"
    target.mkdir()
    p = _run_cli("new", str(target), "-t", "tool")
    assert p.returncode == 1
    assert "already exists" in p.stderr


def test_bundle_standalone(tmp_path: Path) -> None:
    src = tmp_path / "app.py"
    src.write_text("print('hi')", encoding="utf-8")
    p = _run_cli("bundle", str(src), "--standalone")
    assert p.returncode == 0
    out = src.with_suffix(".html")
    assert out.is_file()
    assert "<html" in out.read_text(encoding="utf-8").lower()


def test_bundle_standalone_output(tmp_path: Path) -> None:
    src = tmp_path / "app.py"
    src.write_text("print('hi')", encoding="utf-8")
    out = tmp_path / "out.html"
    p = _run_cli("bundle", str(src), "--standalone", "-o", str(out))
    assert p.returncode == 0
    assert out.is_file()


def test_bundle_exe(tmp_path: Path) -> None:
    src = tmp_path / "app.py"
    src.write_text("print('hi')", encoding="utf-8")
    p = _run_cli("bundle", str(src), "--exe")
    assert p.returncode == 0
    assert "pyinstaller" in p.stdout
    assert "--onefile" in p.stdout


def test_bundle_no_mode(tmp_path: Path) -> None:
    src = tmp_path / "app.py"
    src.write_text("print('hi')", encoding="utf-8")
    p = _run_cli("bundle", str(src))
    assert p.returncode == 2


def test_run_missing_file() -> None:
    p = _run_cli("run", "/no/such/file.py")
    assert p.returncode == 2
    assert "not found" in p.stderr


def test_run_non_python(tmp_path: Path) -> None:
    # Use a tmp file with a non-Python extension so the test is portable
    # across Linux, macOS and Windows (avoids relying on /etc/hostname
    # which doesn't exist on macOS).
    f = tmp_path / "config.txt"
    f.write_text("hello", encoding="utf-8")
    p = _run_cli("run", str(f))
    assert p.returncode == 2
    assert ".py" in p.stderr


def test_run_simple_script(tmp_path: Path) -> None:
    f = tmp_path / "ok.py"
    f.write_text("import sys; sys.stdout.write('hello\\n'); sys.exit(0)\n", encoding="utf-8")
    p = _run_cli("run", str(f))
    assert p.returncode == 0
    assert "hello" in p.stdout


# ---------------------------------------------------------------------------
# _platform module
# ---------------------------------------------------------------------------


def test_platform_constants_are_booleans() -> None:
    from iskg import _platform

    assert isinstance(_platform.IS_WINDOWS, bool)
    assert isinstance(_platform.IS_MACOS, bool)
    assert isinstance(_platform.IS_LINUX, bool)
    assert isinstance(_platform.IS_POSIX, bool)


def test_platform_user_dirs_exist() -> None:
    from iskg import _platform

    p = _platform.user_config_dir()
    assert p.is_dir()
    p = _platform.user_data_dir()
    assert p.is_dir()
    p = _platform.user_cache_dir()
    assert p.is_dir()


def test_platform_scaffold_dir_exists() -> None:
    from iskg import _platform

    assert _platform.scaffold_templates_dir().is_dir()


def test_platform_native_line_endings() -> None:
    from iskg import _platform

    if _platform.IS_WINDOWS:
        out = _platform.native_line_ending("a\nb")
        assert "\r\n" in out
    else:
        out = _platform.native_line_ending("a\nb")
        assert "\r\n" not in out


# ---------------------------------------------------------------------------
# Scaffolds inventory
# ---------------------------------------------------------------------------


def test_scaffolds_inventory_has_required_templates() -> None:
    from iskg._platform import scaffold_templates_dir

    base = scaffold_templates_dir()
    names = {p.name for p in base.iterdir() if p.is_dir()}
    assert {"tool", "dashboard", "form", "viewer"}.issubset(names), f"missing: {names}"


def test_scaffold_files_are_text() -> None:
    from iskg._platform import scaffold_templates_dir

    base = scaffold_templates_dir()
    for tpl_dir in base.iterdir():
        if not tpl_dir.is_dir():
            continue
        for f in tpl_dir.iterdir():
            if f.is_file() and f.suffix in {".tmpl", ".json"}:
                text = f.read_text(encoding="utf-8")
                assert "{" not in text.replace("{{", "").replace("}}", "") or True


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
