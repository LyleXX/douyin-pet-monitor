from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENTRYPOINT = ROOT / "app" / "cli.py"
BUILD_ROOT = ROOT / "build"
DIST_DIR = BUILD_ROOT / "backend-dist"
WORK_DIR = BUILD_ROOT / "backend-build"
SPEC_DIR = BUILD_ROOT / "backend-spec"
TAURI_BIN_DIR = ROOT / "desktop" / "src-tauri" / "binaries"


def binary_name() -> str:
    return "douyin-backend.exe" if os.name == "nt" else "douyin-backend"


def tauri_target_triple() -> str:
    if sys.platform == "darwin":
        machine = os.uname().machine
        return "aarch64-apple-darwin" if machine == "arm64" else "x86_64-apple-darwin"
    if sys.platform == "win32":
        return "x86_64-pc-windows-msvc"
    if sys.platform.startswith("linux"):
        return "x86_64-unknown-linux-gnu"
    raise RuntimeError(f"Unsupported platform for Tauri sidecar: {sys.platform}")


def build_pyinstaller() -> None:
    subprocess.run(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            "--noconfirm",
            "--clean",
            "--onefile",
            "--log-level",
            "WARN",
            "--name",
            "douyin-backend",
            "--paths",
            str(ROOT),
            "--distpath",
            str(DIST_DIR),
            "--workpath",
            str(WORK_DIR),
            "--specpath",
            str(SPEC_DIR),
            str(ENTRYPOINT),
        ],
        check=True,
        cwd=ROOT,
    )


def copy_sidecar() -> Path:
    built_binary = DIST_DIR / binary_name()
    if not built_binary.exists():
        raise FileNotFoundError(f"Expected PyInstaller binary missing: {built_binary}")

    TAURI_BIN_DIR.mkdir(parents=True, exist_ok=True)
    suffix = ".exe" if os.name == "nt" else ""
    destination = TAURI_BIN_DIR / f"douyin-backend-{tauri_target_triple()}{suffix}"
    shutil.copy2(built_binary, destination)
    return destination


def main() -> int:
    build_pyinstaller()
    destination = copy_sidecar()
    print(f"Built sidecar: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
