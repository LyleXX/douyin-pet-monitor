from __future__ import annotations

import re
from pathlib import Path


WORKFLOW_PATH = Path(".github/workflows/package-desktop.yml")


def _matrix_blocks(text: str) -> dict[str, str]:
    blocks: dict[str, str] = {}
    current_os = ""
    current_lines: list[str] = []

    for line in text.splitlines():
        match = re.match(r"\s+- os:\s+(.+)\s*$", line)
        if match:
            if current_os:
                blocks[current_os] = "\n".join(current_lines)
            current_os = match.group(1).strip()
            current_lines = [line]
            continue
        if current_os:
            current_lines.append(line)

    if current_os:
        blocks[current_os] = "\n".join(current_lines)
    return blocks


def _bundle_value(block: str) -> str:
    match = re.search(r"^\s+bundles:\s+(.+)\s*$", block, flags=re.MULTILINE)
    if not match:
        raise AssertionError(f"Missing bundles value in matrix block:\n{block}")
    return match.group(1).strip()


def main() -> int:
    text = WORKFLOW_PATH.read_text(encoding="utf-8")
    blocks = _matrix_blocks(text)

    assert _bundle_value(blocks["macos-14"]) == "app,dmg"
    assert _bundle_value(blocks["windows-latest"]) == "nsis"
    assert "bundle/nsis/*.exe" in blocks["windows-latest"]
    assert "bundle/dmg/*.dmg" in blocks["macos-14"]
    print("package workflow ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
