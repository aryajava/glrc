from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageOps

DEFAULT_SIZES = (16, 24, 32, 48, 64, 128, 256)


def _parse_sizes(value: str) -> tuple[int, ...]:
    parts = [p.strip() for p in value.split(",") if p.strip()]
    sizes = tuple(sorted({int(p) for p in parts}))
    if not sizes:
        raise ValueError("No icon sizes provided")
    if any(s <= 0 for s in sizes):
        raise ValueError("Sizes must be positive integers")
    return sizes


def _strip_metadata(image: Image.Image) -> Image.Image:
    # Rebuild image bytes to remove EXIF/text metadata payload.
    raw = image.convert("RGBA").tobytes()
    return Image.frombytes("RGBA", image.size, raw)


def _make_square_canvas(image: Image.Image, edge: int) -> Image.Image:
    if image.width == edge and image.height == edge:
        return image

    # Pad keeps aspect ratio and allows upscaling to ensure max icon size exists.
    return ImageOps.pad(
        image,
        (edge, edge),
        method=Image.Resampling.LANCZOS,
        color=(0, 0, 0, 0),
        centering=(0.5, 0.5),
    )


def generate_icon(source: Path, target: Path, sizes: Iterable[int]) -> None:
    sizes = tuple(sorted(set(int(s) for s in sizes)))
    with Image.open(source) as img:
        oriented = ImageOps.exif_transpose(img)
        stripped = _strip_metadata(oriented)

    max_edge = max(sizes)
    square = _make_square_canvas(stripped, max_edge)

    # Some small source logos may still decode below target size in certain PIL paths.
    # Force exact edge for deterministic ICO generation.
    if square.size != (max_edge, max_edge):
        square = square.resize((max_edge, max_edge), Image.Resampling.LANCZOS)

    target.parent.mkdir(parents=True, exist_ok=True)
    square.save(target, format="ICO", sizes=[(s, s) for s in sizes])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Generate a multi-size .ico from a PNG/JPG source with auto orientation "
            "and stripped metadata."
        )
    )
    parser.add_argument("--source", default="logo.png", help="Source image path")
    parser.add_argument("--target", default="logo.ico", help="Target .ico path")
    parser.add_argument(
        "--sizes",
        default=",".join(str(s) for s in DEFAULT_SIZES),
        help="Comma-separated icon sizes, e.g. 16,24,32,48,64,128,256",
    )

    args = parser.parse_args()
    sizes = _parse_sizes(args.sizes)

    src = Path(args.source)
    dst = Path(args.target)
    if not src.exists():
        raise SystemExit(f"Source image not found: {src}")

    generate_icon(src, dst, sizes)
    print(f"Generated {dst} from {src} with sizes: {sizes}")
