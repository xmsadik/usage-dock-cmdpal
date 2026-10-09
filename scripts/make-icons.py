"""Regenerate the package icons in src/ClaudeUsage/Assets.

Usage: python scripts/make-icons.py   (needs Pillow)

The mark is a slate rounded square with a half-circle gauge: a white track, a green filled part
and a white needle. Everything is drawn at 1024 px and downsampled, so small sizes stay smooth.
"""

import math
from pathlib import Path

from PIL import Image, ImageDraw

ASSETS = Path(__file__).resolve().parent.parent / "src" / "ClaudeUsage" / "Assets"
BASE = 1024
TILE = (44, 62, 80, 255)  # slate
INK = (255, 255, 255, 255)
TRACK = (255, 255, 255, 90)
FILL = (34, 197, 94, 255)  # green: usage within limits
FILLED = 0.4  # share of the gauge that is filled


def dot(d: ImageDraw.ImageDraw, x: float, y: float, r: float, fill: tuple[int, ...]) -> None:
    d.ellipse((x - r, y - r, x + r, y + r), fill=fill)


def arc(d: ImageDraw.ImageDraw, cx: float, cy: float, r: float, start: float, end: float,
        width: float, fill: tuple[int, ...]) -> None:
    """Arc with round caps; angles in degrees, PIL convention (0 = east, clockwise)."""
    d.arc((cx - r, cy - r, cx + r, cy + r), start, end, fill=fill, width=int(width))
    mid = r - width / 2
    for a in (start, end):
        dot(d, cx + mid * math.cos(math.radians(a)), cy + mid * math.sin(math.radians(a)), width / 2, fill)


def icon(size: int) -> Image.Image:
    img = Image.new("RGBA", (BASE, BASE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, BASE - 1, BASE - 1), radius=int(BASE * 0.22), fill=TILE)

    # Gauge from west (180°) over the top to east (360°), centre a little below the middle.
    cx, cy, r, w = BASE * 0.5, BASE * 0.64, BASE * 0.36, BASE * 0.11
    split = 180 + 180 * FILLED
    track = Image.new("RGBA", (BASE, BASE), (0, 0, 0, 0))
    arc(ImageDraw.Draw(track), cx, cy, r, 180, 360, w, TRACK)
    img.alpha_composite(track)
    arc(d, cx, cy, r, 180, split, w, FILL)

    # Needle pointing at the end of the filled part, with a hub.
    length = r - w * 1.35
    tip = (cx + length * math.cos(math.radians(split)), cy + length * math.sin(math.radians(split)))
    d.line([(cx, cy), tip], fill=INK, width=int(BASE * 0.07))
    dot(d, tip[0], tip[1], BASE * 0.035, INK)
    dot(d, cx, cy, BASE * 0.085, INK)

    return img.resize((size, size), Image.LANCZOS)


def centered(width: int, height: int, mark: int) -> Image.Image:
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    img.alpha_composite(icon(mark), ((width - mark) // 2, (height - mark) // 2))
    return img


def main() -> None:
    squares = {
        "StoreLogo.png": 50,
        "LockScreenLogo.scale-200.png": 48,
        "Square44x44Logo.scale-200.png": 88,
        "Square44x44Logo.targetsize-24_altform-unplated.png": 24,
        "Square150x150Logo.scale-200.png": 300,
    }
    for name, size in squares.items():
        icon(size).save(ASSETS / name)

    centered(620, 300, 200).save(ASSETS / "Wide310x150Logo.scale-200.png")
    centered(1240, 600, 360).save(ASSETS / "SplashScreen.scale-200.png")
    print(f"Wrote {len(squares) + 2} icons to {ASSETS}")


if __name__ == "__main__":
    main()
