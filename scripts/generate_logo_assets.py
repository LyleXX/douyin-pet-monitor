from __future__ import annotations

import math
import shutil
import struct
import subprocess
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ICONS_DIR = ROOT / "desktop" / "src-tauri" / "icons"
ASSETS_DIR = ROOT / "desktop" / "src" / "assets"


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def _hex_color(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[index : index + 2], 16) for index in (0, 2, 4))


def _mix(left: tuple[int, int, int], right: tuple[int, int, int], amount: float) -> tuple[int, int, int]:
    return tuple(round(left[index] * (1 - amount) + right[index] * amount) for index in range(3))


def _blend(
    base: tuple[int, int, int, int],
    color: tuple[int, int, int],
    alpha: float,
) -> tuple[int, int, int, int]:
    alpha = _clamp(alpha)
    inverse = 1 - alpha
    return (
        round(base[0] * inverse + color[0] * alpha),
        round(base[1] * inverse + color[1] * alpha),
        round(base[2] * inverse + color[2] * alpha),
        round(base[3] * inverse + 255 * alpha),
    )


def _rounded_rect_alpha(x: float, y: float, left: float, top: float, width: float, height: float, radius: float) -> float:
    cx = left + width / 2
    cy = top + height / 2
    dx = abs(x - cx) - (width / 2 - radius)
    dy = abs(y - cy) - (height / 2 - radius)
    outside = math.hypot(max(dx, 0), max(dy, 0))
    inside = min(max(dx, dy), 0)
    distance = outside + inside - radius
    return _clamp(0.5 - distance)


def _line_alpha(x: float, y: float, start: tuple[float, float], end: tuple[float, float], width: float) -> float:
    sx, sy = start
    ex, ey = end
    vx = ex - sx
    vy = ey - sy
    length_sq = vx * vx + vy * vy
    if length_sq == 0:
        return 0.0
    t = _clamp(((x - sx) * vx + (y - sy) * vy) / length_sq)
    px = sx + t * vx
    py = sy + t * vy
    distance = math.hypot(x - px, y - py)
    return _clamp(width / 2 + 0.5 - distance)


def _circle_alpha(x: float, y: float, cx: float, cy: float, radius: float) -> float:
    distance = math.hypot(x - cx, y - cy)
    return _clamp(radius + 0.5 - distance)


def _png_bytes(width: int, height: int, rgba: bytes) -> bytes:
    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    scanlines = bytearray()
    stride = width * 4
    for row in range(height):
        scanlines.append(0)
        scanlines.extend(rgba[row * stride : (row + 1) * stride])

    return b"".join(
        [
            b"\x89PNG\r\n\x1a\n",
            chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)),
            chunk(b"IDAT", zlib.compress(bytes(scanlines), 9)),
            chunk(b"IEND", b""),
        ]
    )


def generate_icon(path: Path, size: int = 1024) -> None:
    teal = _hex_color("#0f766e")
    deep = _hex_color("#123a43")
    amber = _hex_color("#f2b84b")
    cream = _hex_color("#fff8e7")
    mint = _hex_color("#d6eeea")

    pixels = bytearray(size * size * 4)
    for y in range(size):
        for x in range(size):
            nx = x / (size - 1)
            ny = y / (size - 1)
            bg = _mix(teal, deep, (nx + ny) / 2)
            alpha = _rounded_rect_alpha(x, y, 48, 48, size - 96, size - 96, 220)
            pixel = (bg[0], bg[1], bg[2], round(255 * alpha))

            glow = _circle_alpha(x, y, size * 0.76, size * 0.22, size * 0.15) * alpha
            pixel = _blend(pixel, amber, glow * 0.9)

            card = _rounded_rect_alpha(x, y, size * 0.17, size * 0.21, size * 0.66, size * 0.63, size * 0.08) * alpha
            pixel = _blend(pixel, mint, card * 0.18)

            for bx, by, bw, bh in [
                (0.26, 0.58, 0.11, 0.20),
                (0.43, 0.48, 0.11, 0.30),
                (0.60, 0.37, 0.11, 0.41),
            ]:
                bar = _rounded_rect_alpha(
                    x,
                    y,
                    size * bx,
                    size * by,
                    size * bw,
                    size * bh,
                    size * 0.035,
                ) * alpha
                pixel = _blend(pixel, cream, bar * 0.94)

            points = [
                (size * 0.24, size * 0.69),
                (size * 0.42, size * 0.56),
                (size * 0.58, size * 0.61),
                (size * 0.77, size * 0.39),
            ]
            for start, end in zip(points, points[1:]):
                line = _line_alpha(x, y, start, end, size * 0.045) * alpha
                pixel = _blend(pixel, amber, line)
            for point in points:
                dot = _circle_alpha(x, y, point[0], point[1], size * 0.052) * alpha
                pixel = _blend(pixel, amber, dot)

            index = (y * size + x) * 4
            pixels[index : index + 4] = bytes(pixel)

    path.write_bytes(_png_bytes(size, size, bytes(pixels)))


def resize_png(source: Path, output: Path, size: int) -> None:
    subprocess.run(["sips", "-z", str(size), str(size), str(source), "--out", str(output)], check=True, capture_output=True)


def write_ico(png_paths: list[Path], output: Path) -> None:
    header = struct.pack("<HHH", 0, 1, len(png_paths))
    entries = bytearray()
    data = bytearray()
    offset = 6 + 16 * len(png_paths)

    for png_path in png_paths:
        png = png_path.read_bytes()
        size = 0 if "256" in png_path.name else int(png_path.stem.split("x")[0])
        entries.extend(struct.pack("<BBBBHHII", size, size, 0, 0, 1, 32, len(png), offset))
        data.extend(png)
        offset += len(png)

    output.write_bytes(header + entries + data)


def write_svg(output: Path) -> None:
    output.write_text(
        """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" role="img" aria-label="达人榜单">
  <defs>
    <linearGradient id="bg" x1="12" y1="12" x2="116" y2="116" gradientUnits="userSpaceOnUse">
      <stop stop-color="#0f766e"/>
      <stop offset="1" stop-color="#123a43"/>
    </linearGradient>
  </defs>
  <rect x="8" y="8" width="112" height="112" rx="28" fill="url(#bg)"/>
  <circle cx="96" cy="30" r="18" fill="#f2b84b"/>
  <rect x="32" y="72" width="15" height="26" rx="5" fill="#fff8e7"/>
  <rect x="56" y="58" width="15" height="40" rx="5" fill="#fff8e7"/>
  <rect x="80" y="42" width="15" height="56" rx="5" fill="#fff8e7"/>
  <path d="M30 88 L54 70 L74 77 L98 49" fill="none" stroke="#f2b84b" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
""",
        encoding="utf-8",
    )


def main() -> None:
    ICONS_DIR.mkdir(parents=True, exist_ok=True)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    source = ICONS_DIR / "icon.png"
    generate_icon(source)

    for size in [16, 32, 64, 128, 256, 512]:
        resize_png(source, ICONS_DIR / f"{size}x{size}.png", size)
    resize_png(source, ICONS_DIR / "128x128@2x.png", 256)

    iconset = ICONS_DIR / "icon.iconset"
    if iconset.exists():
        shutil.rmtree(iconset)
    iconset.mkdir()
    iconset_map = {
        "icon_16x16.png": 16,
        "icon_16x16@2x.png": 32,
        "icon_32x32.png": 32,
        "icon_32x32@2x.png": 64,
        "icon_128x128.png": 128,
        "icon_128x128@2x.png": 256,
        "icon_256x256.png": 256,
        "icon_256x256@2x.png": 512,
        "icon_512x512.png": 512,
        "icon_512x512@2x.png": 1024,
    }
    for name, size in iconset_map.items():
        resize_png(source, iconset / name, size)

    subprocess.run(["iconutil", "-c", "icns", str(iconset), "-o", str(ICONS_DIR / "icon.icns")], check=True)
    write_ico([ICONS_DIR / "32x32.png", ICONS_DIR / "256x256.png"], ICONS_DIR / "icon.ico")
    write_svg(ASSETS_DIR / "logo.svg")
    shutil.rmtree(iconset)


if __name__ == "__main__":
    main()
