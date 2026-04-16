#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.image_tools import THUMBS_DIR_NAME, create_thumbnail  # noqa: E402

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate thumbnails for already uploaded work images.",
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=PROJECT_ROOT / "assets" / "works",
        help="Directory with original images (default: assets/works).",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=640,
        help="Thumbnail width in px (default: 640).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate thumbnails even if they already exist.",
    )
    return parser.parse_args()


def list_original_images(source_dir: Path) -> list[Path]:
    images: list[Path] = []

    for path in sorted(source_dir.iterdir()):
        if not path.is_file():
            continue
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        images.append(path)

    return images


def main() -> int:
    args = parse_args()
    source_dir = args.source.resolve()

    if not source_dir.exists() or not source_dir.is_dir():
        print(f"Source directory not found: {source_dir}")
        return 1

    thumbs_dir = source_dir / THUMBS_DIR_NAME
    thumbs_dir.mkdir(parents=True, exist_ok=True)

    created = 0
    skipped = 0
    failed = 0

    for image_path in list_original_images(source_dir):
        thumbnail_path = thumbs_dir / f"{image_path.stem}.webp"

        if thumbnail_path.exists() and not args.force:
            skipped += 1
            continue

        try:
            create_thumbnail(image_path, source_dir, width=args.width)
            created += 1
        except OSError as error:
            failed += 1
            print(f"FAILED: {image_path.name} ({error})")

    print(
        f"Done. created={created}, skipped={skipped}, failed={failed}, source={source_dir}",
    )
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
